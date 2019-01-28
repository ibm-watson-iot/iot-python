    """
    ===========================================================================
    Information Management Historical Data Storage Extension APIs
    ===========================================================================
    """

    # Historian connectors Destinations URLs
    allHistorianConnectorDestinationsUrl = "https://%s/api/v0002/historianconnectors/%s/destinations"
    oneHistorianConnectorDestinationUrl = "https://%s/api/v0002/historianconnectors/%s/destinations/%s"
    
    
    def list(self, connectorId, nameFilter=None):
        """
        Gets the List of Historian connector's destinations.
        A destination is used to configure a specific location to write to on the target service for the historian connector. 
        For example, if the target service on the historian connector is eventstreams, a destination would be used to configure an individual topic to write data to.
        The destinations endpoint returns the list of all of the destinations that the have been configured for a historian connector.
        
        Parameters:
            - connectorId (string) -    id of the historian connector
            - nameFilter(string) -      Filter the results by the specified name
        
        Throws APIException on failure.
        """
        
        allReq = ApiClient.allHistorianConnectorDestinationsUrl % (self.host, connectorId)
        
        if nameFilter:
            allReq += "?name=%s" % nameFilter
                    
        resp = requests.get(allReq, auth=self.credentials, verify=self.verify)
        status = resp.status_code

        if status == 200:
            self.logger.debug("Historian connector's destinations are retrieved")
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
        
    
    def get(self, connectorId, destinationName):
        """
        Retrieve the destination with the specified name for the given connector Id.
        Parameters:
            - connectorId (String), Connector Id which is a UUID
            - destinationName (String), Name of the destination
        Throws APIException on failure.

        """
        
        oneReq = ApiClient.oneHistorianConnectorDestinationUrl % (self.host, connectorId, destinationName)
        resp = requests.get(oneReq, auth=self.credentials, verify=self.verify)
        status = resp.status_code

        if status == 200:
            self.logger.debug("Historian connector's destination for the given name[%s] is retrieved." % destinationName)
            return resp.json()
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", resp)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", resp)
        elif status == 404:
            raise ibmiotf.APIException(404, "Error. Historian connector destination not found", resp)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", resp)
        else:
            raise ibmiotf.APIException(status, "Unexpected error", resp)
            
    def add(self, connectorId, name, type, configuration):
        """
        Create a destination for the historian connector. 
        The structure of the configuration property will depend on the type of the target service.
        Parameters:
            - connectorId (string) - Id of the connector
            - name (string) - Name of the service
            - type (string) - must be either eventstreams or cloudant
            - configuration (json) - destination json object 
            
        Throws APIException on failure
        """

        postReq = ApiClient.allHistorianConnectorDestinationsUrl % (self.host, connectorId)

        try:
            bodyStr = json.dumps({
                "name" : name,
                "type" : type,
                "configuration" : configuration
            })
            
        except Exception as exc:
            raise ibmiotf.APIException(-1, "Exception formatting the body to JSON", exc)
            
        resp = requests.post(postReq, auth=self.credentials, headers={"Content-Type":"application/json"}, data=bodyStr,
               verify=self.verify)
        status = resp.status_code

        if status == 201:
            self.logger.debug("Historian connector destination is created.")
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
            
    
    def delete(self, connectorId, destinationName):
        """
        Deletes Historian connector destination
        Parameters:
            - connectorId (string) - id of the Historian connector
            - destinationName (string) - name of the destination
        Throws APIException on failure
        """
        
        oneReq = ApiClient.oneHistorianConnectorDestinationUrl % (self.host, connectorId, destinationName)    
        resp = requests.delete(oneReq, auth=self.credentials, verify=self.verify)
        status = resp.status_code
        
        if status == 200:
            self.logger.debug("Historian connector destination[%s] for the given Id[%s] is deleted." % (destinationName, connectorId))
            return resp
        elif status == 204:
            self.logger.debug("Historian connector destination[%s] for the given Id[%s] is deleted." % (destinationName, connectorId))
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
