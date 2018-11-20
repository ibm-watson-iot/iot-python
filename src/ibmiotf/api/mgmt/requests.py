
class MgmtRequest(defaultdict):
    def getStatus(self, typeId=None, deviceId=None):
        pass
    
class MgmtRequests(defaultdict):
    
    def list(self):
        pass
    
    def initiate(self, request):
        pass
    
    def delete(self, requestId):
        pass
    
    def get(self, requestId):
        pass
    
    
    def getAllDeviceManagementRequests(self):
        """
        Gets a list of device management requests, which can be in progress or recently completed.
        In case of failure it throws APIException
        """
        mgmtRequests = ApiClient.mgmtRequests % (self.host)
        r = requests.get(mgmtRequests, auth=self.credentials, verify=self.verify)

        status = r.status_code

        if status == 200:
            self.logger.debug("Retrieved all device management requests")
            return r.json()
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def initiateDeviceManagementRequest(self, deviceManagementRequest):
        """
        Initiates a device management request, such as reboot.
        In case of failure it throws APIException
        """
        mgmtRequests = ApiClient.mgmtRequests % (self.host)
        r = requests.post(mgmtRequests, auth=self.credentials, data=json.dumps(deviceManagementRequest), headers = {'content-type': 'application/json'}, verify=self.verify)

        status = r.status_code
        if status == 202:
            self.logger.debug("The request has been accepted for processing")
            return r.json()
        elif status == 403:
            raise ibmiotf.APIException(500, "Devices don't support the requested operation", r.json())
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def deleteDeviceManagementRequest(self, requestId):
        """
        Clears the status of a device management request.
        You can use this operation to clear the status for a completed request, or for an in-progress request which may never complete due to a problem.
        It accepts requestId (string) as parameters
        In case of failure it throws APIException
        """
        mgmtRequests = ApiClient.mgmtSingleRequest % (self.host, requestId)
        r = requests.delete(mgmtRequests, auth=self.credentials, verify=self.verify)

        status = r.status_code
        if status == 204:
            self.logger.debug("Request status cleared")
            return True
        #403 and 404 error code needs to be added in Swagger documentation
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "Request Id not found", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def getDeviceManagementRequest(self, requestId):
        """
        Gets details of a device management request.
        It accepts requestId (string) as parameters
        In case of failure it throws APIException
        """
        mgmtRequests = ApiClient.mgmtSingleRequest % (self.host, requestId)
        r = requests.get(mgmtRequests, auth=self.credentials, verify=self.verify)

        status = r.status_code

        if status == 200:
            self.logger.debug("Retrieving single management request")
            return r.json()
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "Request Id not found", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def getDeviceManagementRequestStatus(self, requestId):
        """
        Get a list of device management request device statuses.
        In case of failure it throws APIException
        """
        mgmtRequests = ApiClient.mgmtRequestStatus % (self.host, requestId)
        r = requests.get(mgmtRequests, auth=self.credentials, verify=self.verify)

        status = r.status_code

        if status == 200:
            self.logger.debug("Retrieved all device management request statuses")
            return r.json()
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "Request status not found", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def getDeviceManagementRequestStatusByDevice(self, requestId, typeId, deviceId):
        """
        Get an individual device mangaement request device status.
        In case of failure it throws APIException
        """
        mgmtRequests = ApiClient.mgmtRequestSingleDeviceStatus % (self.host, requestId, typeId, deviceId)
        r = requests.get(mgmtRequests, auth=self.credentials, verify=self.verify)

        status = r.status_code

        if status == 200:
            self.logger.debug("Retrieved device management request status of single device")
            return r.json()
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "Request status not found", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

