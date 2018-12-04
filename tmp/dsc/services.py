    """
    ===========================================================================
    Information Management Historical Data Storage Extension APIs
    ===========================================================================
    """

    # Service to service URLs
    allServicesUrl = "https://%s/api/v0002/s2s/services"
    oneServiceUrl = "https://%s/api/v0002/s2s/services/%s"
    

    
    def list(self, nameFilter=None, typeFilter=None, bindingModeFilter=None, boundFilter=None):
        """
        Gets the list of services that the Watson IoT Platform can connect to. 
        The list can include a mixture of services that are either bound or unbound.
        
        Parameters:
        
            - nameFilter(string) - Filter the results by the specified name
            - typeFilter(string) - Filter the results by the specified type, Available values : cloudant, eventstreams
            - bindingModeFilter(string) - Filter the results by the specified binding mode, Available values : automatic, manual
            - boundFilter(boolean) - Filter the results by the bound flag 
        
        Throws APIException on failure.
        """
        
        allServiceReq = ApiClient.allServicesUrl % self.host
        
        if nameFilter or typeFilter or bindingModeFilter or (boundFilter == True) or (boundFilter == False):
            allServiceReq += "?"
            isQueryParamAdded = False
            
            if nameFilter:
                allServiceReq += "name=%s" % nameFilter
                isQueryParamAdded = True
            
            if typeFilter:
                if isQueryParamAdded:
                    allServiceReq += "&"
                allServiceReq += "type=%s" % typeFilter
                isQueryParamAdded = True
            
            if bindingModeFilter:
                if isQueryParamAdded:
                    allServiceReq += "&"
                allServiceReq += "bindingMode=%s" % bindingModeFilter
                isQueryParamAdded = True
                
            if boundFilter:
                if isQueryParamAdded:
                    allServiceReq += "&"
                allServiceReq += "bound=true"
            else:
                if isQueryParamAdded:
                    allServiceReq += "&"
                allServiceReq += "bound=false"
        
        resp = requests.get(allServiceReq, auth=self.credentials, verify=self.verify)
        status = resp.status_code

        if status == 200:
            self.logger.debug("Services retrieved")
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
        
    
    def get(self, serviceId):
        """
        Retrieve the service with the specified id.
        Parameters:
            - serviceId (String), Service Id which is a UUID
        Throws APIException on failure.

        """
        
        oneServiceReq = ApiClient.oneServiceUrl % (self.host, serviceId)
        resp = requests.get(oneServiceReq, auth=self.credentials, verify=self.verify)
        status = resp.status_code

        if status == 200:
            self.logger.debug("Service details for the given Id[%s] is retrieved." % serviceId)
            return resp.json()
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
            
    def add(self, serviceName, serviceType, credentials, description):
        """
        Create a new external service. 
        The service must include all of the details required to connect 
        and authenticate to the external service in the credentials property. 
        Parameters:
            - serviceName (string) - Name of the service
            - serviceType (string) - must be either eventstreams or cloudant
            - credentials (json object) - Should have a valid structure for the service type.
            - description (string) - description of the service
        Throws APIException on failure
        """
        
        postServicesReq = ApiClient.allServicesUrl % self.host
        try:
            bodyJson = json.dumps({
                "name" : serviceName,
                "type" : serviceType,
                "credentials" : credentials,
                "description" : description
            })
        except Exception as exc:
            raise ibmiotf.APIException(-1, "Exception formatting the body to JSON", exc)
        
        resp = requests.post(postServicesReq, auth=self.credentials, headers={"Content-Type":"application/json"}, data=bodyJson,
               verify=self.verify)
        status = resp.status_code

        if status == 201:
            self.logger.debug("Service is created.")
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
            
    def update(self, serviceId, serviceName, credentials, description):
        """
        Updates the service with the specified id.
        if description is empty, the existing description will be removed.
        Parameters:
            - serviceId (String), Service Id which is a UUID
            - serviceName (string), name of service
            - credentials (json), json object of credentials
            - description - description of the service
        Throws APIException on failure.

        """
        
        serviceReq = ApiClient.oneServiceUrl % (self.host, serviceId)
        
        resp = requests.get(serviceReq, auth=self.credentials, verify=self.verify)
        status = resp.status_code

        if status == 200:
            serviceBody = resp.json()
        else:
            raise ibmiotf.APIException(status, "Error occurred while fetching service of id[%s]" % serviceId, resp)
        
        if serviceName:
            serviceBody['name'] = serviceName
        
        if description:
            serviceBody['description'] = description
        
        if credentials:
            serviceBody['credentials'] = credentials
        
        try:
            bodyJson = json.dumps(serviceBody)
        except Exception as exc:
            raise ibmiotf.APIException(-1, "Exception formatting the body to JSON", exc)
        print("bodyJson: %s" % bodyJson)
        
        resp = requests.put(serviceReq, auth=self.credentials, headers={"Content-Type":"application/json"}, data=bodyJson,
               verify=self.verify)
        status = resp.status_code
        if status == 200:
            self.logger.debug("Service details for the given Id[%s] is updated." % serviceId)
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
            
    
    def delete(self, serviceId):
        """
        Deletes service with service id
        Parameters:
            - serviceId (string) - Service id of the service
        Throws APIException on failure
        """
        
        deleteServiceReq = ApiClient.oneServiceUrl % (self.host, serviceId)
    
        resp = requests.delete(deleteServiceReq, auth=self.credentials, verify=self.verify)
        status = resp.status_code
        
        if status == 204:
            self.logger.debug("Service for the given Id[%s] is deleted." % serviceId)
            return resp
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", resp)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", resp)
        elif status == 404:
            raise ibmiotf.APIException(404, "Error. Service not found", resp)
        elif status == 405:
            raise ibmiotf.APIException(404, "The service with the specified uuid is not an external service, it is an automatically bound service. Automatically bound services cannot be deleted and can only be unbound using the Watson IoT Platform Dashboard UI.", resp)
        elif status == 409:
            raise ibmiotf.APIException(409, "The service with the specified id is currently being referenced by another object.", resp)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", resp)
        else:
            raise ibmiotf.APIException(status, "Unexpected error", resp)
            