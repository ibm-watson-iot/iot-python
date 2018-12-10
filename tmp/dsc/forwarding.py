    """
    ===========================================================================
    Information Management Historical Data Storage Extension APIs
    ===========================================================================
    """
    # Historian connectors forwarding rules URLs
    allHistorianConnectorForwardingRulesUrl = "https://%s/api/v0002/historianconnectors/%s/forwardingrules"
    oneHistorianConnectorForwardingRulesUrl = "https://%s/api/v0002/historianconnectors/%s/forwardingrules/%s"

        
    def list(self, connectorId, nameFilter=None, typeFilter=None, enabledFilter=None, destinationNameFilter=None, limit=None, bookmark=None):
        """
        Gets List of Historian connectors Forwarding rules.
        A forwarding rule is used to configure which data (events or state data) are written to which destinations.
        The forwarding rules endpoint returns the list of all of the forwarding rules that the have been configured a historian connector.
        
        Parameters:
            - connectorId(string) -                 Id of the connector
            - nameFilter(string) -                  Filter the results by the specified name
            - typeFilter(string) -                  Filter the results by the specified type, Available values : event, state
            - enabledFilter(boolean) -              Filter the results by the enabled flag 
            - destinationNameFilter(string) -       Filter the results by the service id
            - limit(number) -                       Max number of results returned, defaults 25
            - bookmark(string) -                    used for paging through results
        
        Throws APIException on failure.
        """
        
        allHistConnReq = ApiClient.allHistorianConnectorForwardingRulesUrl % self.host
        
        if nameFilter or typeFilter or limit or connectorId or (enabledFilter == True) or (enabledFilter == False) or bookmark:
            allHistConnReq += "?"
            isQueryParamAdded = False
            
            if nameFilter:
                allHistConnReq += "name=%s" % nameFilter
                isQueryParamAdded = True
            
            if typeFilter:
                if isQueryParamAdded:
                    allHistConnReq += "&"
                allHistConnReq += "type=%s" % typeFilter
                isQueryParamAdded = True

            if bookmark:
                if isQueryParamAdded:
                    allHistConnReq += "&"
                allHistConnReq += "_bookmark=%s" % bookmark
                isQueryParamAdded = True
            
            if limit:
                if isQueryParamAdded:
                    allHistConnReq += "&"
                allHistConnReq += "_limit=%s" % limit
                isQueryParamAdded = True

            if destinationNameFilter:
                if isQueryParamAdded:
                    allHistConnReq += "&"
                allHistConnReq += "destinationName=%s" % destinationNameFilter
                isQueryParamAdded = True
                
            if enabledFilter:
                if isQueryParamAdded:
                    allHistConnReq += "&"
                allHistConnReq += "enabled=true"
            else:
                if isQueryParamAdded:
                    allHistConnReq += "&"
                allHistConnReq += "enabled=false"
        
        resp = requests.get(allHistConnReq, auth=self.credentials, verify=self.verify)
        status = resp.status_code

        if status == 200:
            self.logger.debug("Historian connectors forwarding rules retrieved")
            return resp.json()
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", resp)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", resp)
        elif status == 404:
            raise ibmiotf.APIException(404, "Error. Not Found", resp)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", resp)
        else:
            raise ibmiotf.APIException(status, "Unexpected error", resp)
        
    
    def get(self, connectorId, forwardingRuleId):
        """
        Retrieve the forwarding rule with the specified id.
        Parameters:
            - connectorId (String), Connector Id which is a UUID
            - forwardingRuleId (String), id of the forwarding rule
        Throws APIException on failure.

        """
        
        oneReq = ApiClient.oneHistorianConnectorForwardingRulesUrl % (self.host, connectorId, forwardingRuleId)
        resp = requests.get(oneReq, auth=self.credentials, verify=self.verify)
        status = resp.status_code

        if status == 200:
            self.logger.debug("Historian connector forwarding rule for the given Id[%s] is retrieved." % forwardingRuleId)
            return resp.json()
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", resp)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", resp)
        elif status == 404:
            raise ibmiotf.APIException(404, "Error. Historian connector forwarding rule not found", resp)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", resp)
        else:
            raise ibmiotf.APIException(status, "Unexpected error", resp)
            
    def add(self, connectorId, name, description, destinationName, type, selector, enabled):
        """
        Create a forwarding rule for the historian connector. 
        The structure of the selector property will depend on the type of the forwarding rule.
        Parameters:
            - name (string) - Name of the service
            - description (string) - Description of the rule
            - destinationName (string) - Name of the destination
            - type (string) - Type should be event or state.
            - selector (json) - json object of the selector
            - enabled (boolean) - rule is enabled or not 
        Throws APIException on failure
        """

        postReq = ApiClient.allHistorianConnectorForwardingRulesUrl % (self.host, connectorId)

        try:
            bodyStr = json.dumps({
                "name" : name,
                "destinationName" : destinationName,
                "type" : type,
                "selector" : selector,
                "description" : description,
                "enabled" : enabled
            })
            
        except Exception as exc:
            raise ibmiotf.APIException(-1, "Exception formatting the body to JSON", exc)
            
        resp = requests.post(postReq, auth=self.credentials, headers={"Content-Type":"application/json"}, data=bodyStr,
               verify=self.verify)
        status = resp.status_code

        if status == 201:
            self.logger.debug("Historian connector  forwarding rule is created.")
            return resp.json()
        elif status == 400:
            raise ibmiotf.APIException(400, "Invalid request (No body, invalid JSON, unexpected key, bad value).", resp)
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", resp)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", resp)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", resp)
        else:
            raise ibmiotf.APIException(status, "Unexpected error", resp)
            
    def update(self, connectorId, forwardingRuleId, name, description, destinationName, selector, enabled):
        """
        Updates the forwarding rule
        if description is empty, the existing description will be removed.
        Parameters:
            - connectorId (String), Connnector Id which is a UUID
            - forwardingRuleId (String), Id of the forwarding rule
            - name (string) - Name of the service
            - description (string) - description of the service
            - destinationName (string) - name of the destination
            - selector(json) - json object fo the selector
            - enabled (boolean) - enabled
        Throws APIException on failure.

        """
        
        req = ApiClient.oneHistorianConnectorForwardingRulesUrl % (self.host, connectorId, forwardingRuleId)
        
        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        status = resp.status_code

        if status == 200:
            connectorBody = resp.json()
        else:
            raise ibmiotf.APIException(status, "Error occurred while fetching connector with id[%s]" % connectorId, resp)
            
        if name:
            connectorBody['name'] = name
        
        if description:
            connectorBody['description'] = description
        
        if destinationName:
            connectorBody['destinationName'] = destinationName

        if enabled:
            connectorBody['enabled'] = enabled

        if selector:
            connectorBody['selector'] = selector
        
        try:
            bodyJson = json.dumps(connectorBody)
        except Exception as exc:
            raise ibmiotf.APIException(-1, "Exception formatting the body to JSON", exc)
        
        resp = requests.put(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=bodyJson,
               verify=self.verify)
        status = resp.status_code
        if status == 200:
            self.logger.debug("Historian connector forwarding rule is updated.")
            return resp.json()
        elif status == 400:
            raise ibmiotf.APIException(400, "Invalid request (No body, invalid JSON, unexpected key, bad value).", resp)
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", resp)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", resp)
        elif status == 404:
            raise ibmiotf.APIException(404, "Error. forwarding rule not found", resp)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", resp)
        else:
            raise ibmiotf.APIException(status, "Unexpected error", resp)
            
    
    def delete(self, connectorId, forwardingRuleId):
        """
        Deletes Historian connector forwarding rule with given id
        Parameters:
            - connectorId (string) - id of the Historian connector
            - forwardingRuleId (string) - id of the forwarding rule
        Throws APIException on failure
        """
        
        deleteReq = ApiClient.oneHistorianConnectorForwardingRulesUrl % (self.host, connectorId, forwardingRuleId)
    
        resp = requests.delete(deleteReq, auth=self.credentials, verify=self.verify)
        status = resp.status_code
        
        if status == 204:
            self.logger.debug("Historian connector forwarding rule for the given Id[%s] is deleted." % forwardingRuleId)
            return resp
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", resp)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", resp)
        elif status == 404:
            raise ibmiotf.APIException(404, "Error. Connector not found", resp)
        elif status == 405:
            raise ibmiotf.APIException(404, "The service with the specified uuid is not an external service, it is an automatically bound service. Automatically bound services cannot be deleted and can only be unbound using the Watson IoT Platform Dashboard UI.", resp)
        elif status == 409:
            raise ibmiotf.APIException(409, "The service with the specified id is currently being referenced by another object.", resp)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", resp)
        else:
            raise ibmiotf.APIException(status, "Unexpected error", resp)