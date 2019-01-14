    """
    ===========================================================================
    Information Management Historical Data Storage Extension APIs
    ===========================================================================
    """
    
    # Historian connectors URLs
    allHistorianConnectorsUrl = "https://%s/api/v0002/historianconnectors"
    oneHistorianConnectorUrl = "https://%s/api/v0002/historianconnectors/%s"
    
    def list(self, nameFilter=None, typeFilter=None, enabledFilter=None, serviceId=None, limit=None, bookmark=None):
        """
        Gets the list of Historian connectors, they are used to configure the Watson IoT Platform to store IoT data in compatible services.
        
        Parameters:
        
            - nameFilter(string) -      Filter the results by the specified name
            - typeFilter(string) -      Filter the results by the specified type, Available values : cloudant, eventstreams
            - enabledFilter(boolean) -  Filter the results by the enabled flag 
            - serviceId(string) -       Filter the results by the service id
            - limit(number) -           Max number of results returned, defaults 25
            - bookmark(string) -        used for paging through results
        
        Throws APIException on failure.
        """
        
        allHistConnReq = ApiClient.allHistorianConnectorsUrl % self.host
        
        if nameFilter or typeFilter or limit or serviceId or (enabledFilter == True) or (enabledFilter == False) or bookmark:
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

            if serviceId:
                if isQueryParamAdded:
                    allHistConnReq += "&"
                allHistConnReq += "serviceId=%s" % serviceId
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
            self.logger.debug("Historian connectors retrieved")
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
        
    
    def get(self, connectorId):
        """
        Retrieve the connector with the specified id.
        Parameters:
            - connectorId (String), Connector Id which is a UUID
        Throws APIException on failure.

        """
        
        oneHistConnReq = ApiClient.oneHistorianConnectorUrl % (self.host, connectorId)
        resp = requests.get(oneHistConnReq, auth=self.credentials, verify=self.verify)
        status = resp.status_code

        if status == 200:
            self.logger.debug("Historian connector for the given Id[%s] is retrieved." % connectorId)
            return resp.json()
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", resp)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", resp)
        elif status == 404:
            raise ibmiotf.APIException(404, "Error. Historian connector not found", resp)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", resp)
        else:
            raise ibmiotf.APIException(status, "Unexpected error", resp)
            
    def add(self, name, serviceId, timezone, description, enabled):
        """
        Create a connector for the organization in the Watson IoT Platform. 
        The connector must reference the target service that the Watson IoT Platform will store the IoT data in.
        Parameters:
            - name (string) - Name of the service
            - serviceId (string) - must be either eventstreams or cloudant
            - timezone (json) - Should have a valid structure for the service type.
            - description (string) - description of the service
            - enabled (boolean) - enabled
        Throws APIException on failure
        """

        postHistConnReq = ApiClient.allHistorianConnectorsUrl % self.host

        try:
            bodyStr = json.dumps({
                "name" : name,
                "description" : description,
                "serviceId" : serviceId,
                "timezone" : timezone,
                "enabled" : enabled
            })
            
        except Exception as exc:
            raise ibmiotf.APIException(-1, "Exception formatting the body to JSON", exc)
            
        resp = requests.post(postHistConnReq, auth=self.credentials, headers={"Content-Type":"application/json"}, data=bodyStr,
               verify=self.verify)
        status = resp.status_code

        if status == 201:
            self.logger.debug("Historian connector is created.")
            return resp.json()
        elif status == 400:
            raise ibmiotf.APIException(400, "Invalid request (No body, invalid JSON, unexpected key, bad value).", resp.json())
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", resp)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", resp)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", resp)
        else:
            raise ibmiotf.APIException(status, "Unexpected error", resp)
            
    def update(self, connectorId, name, description, timezone, enabled):
        """
        Updates the connector with the specified uuid.
        if description is empty, the existing description will be removed.
        Parameters:
            - connector (String), Connnector Id which is a UUID
            - name (string) - Name of the service
            - timezone (json object) - Should have a valid structure for the service type.
            - description (string) - description of the service
            - enabled (boolean) - enabled
        Throws APIException on failure.

        """
        from __builtin__ import str
        
        req = ApiClient.oneHistorianConnectorUrl % (self.host, connectorId)
        
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
        
        if timezone:
            connectorBody['timezone'] = timezone

        if enabled:
            connectorBody['enabled'] = enabled
        
        try:
            bodyJson = json.dumps(connectorBody)
        except Exception as exc:
            raise ibmiotf.APIException(-1, "Exception formatting the body to JSON. Err: %s" % str(exc), None)
        
        resp = requests.put(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=bodyJson,
               verify=self.verify)
        status = resp.status_code
        if status == 200:
            self.logger.debug("Historian connector details for the given Id[%s] is updated." % connectorId)
            return resp.json()
        elif status == 400:
            raise ibmiotf.APIException(400, "Invalid request (No body, invalid JSON, unexpected key, bad value).", resp)
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", resp)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", resp)
        elif status == 404:
            raise ibmiotf.APIException(404, "Error. Service not found", resp)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", resp)
        else:
            raise ibmiotf.APIException(status, "Unexpected error", resp)
            
    
    def delete(self, connectorId):
        """
        Deletes Historian connector with connector id
        Parameters:
            - connectorId (string) - id of the Historian connector
        Throws APIException on failure
        """
        
        deleteConnectorReq = ApiClient.oneHistorianConnectorUrl % (self.host, connectorId)
    
        resp = requests.delete(deleteConnectorReq, auth=self.credentials, verify=self.verify)
        status = resp.status_code
        
        if status == 204:
            self.logger.debug("Historian connector for the given Id[%s] is deleted." % connectorId)
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
            