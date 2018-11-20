class MgmtExtension(defaultdict):
    
    def __init__(self):
        pass


class MgmtExtensions(defaultdict):
    
    def list(self):
        pass
    
    def create(self, dmeData):
        pass
    
    def delete(self, bundleId):
        pass
    
    def get(self, bundleId):
        pass
    
    def update(self, bundleId):
        pass
    
    """
    ===========================================================================
    Device Management Extension API
        - List all device management extension packages
        - Create a new device management extension package
        - Delete a device management extension package
        - Get a specific device management extension package
        - Update a device management extension package
    ===========================================================================
    """

    def getAllDeviceManagementExtensionPkgs(self):
        """
        List all device management extension packages
        """
        dmeReq = ApiClient.dmeRequests % (self.host)
        r = requests.get(dmeReq, auth=self.credentials, verify=self.verify)
        status = r.status_code
        if status == 200:
            self.logger.debug("Retrieved all Device Management Extension Packages")
            return r.json()
        else:
            raise ibmiotf.APIException(status,"HTTP Error in getAllDeviceManagementExtensionPkgs", r)

    def createDeviceManagementExtensionPkg(self, dmeData):
        """
        Create a new device management extension package
        In case of failure it throws APIException
        """
        dmeReq = ApiClient.dmeRequests % (self.host)
        r = requests.post(dmeReq, auth=self.credentials, data=json.dumps(dmeData),
                      headers = {'content-type': 'application/json'}, verify=self.verify)
        status = r.status_code
        if status == 201:
            self.logger.debug("The DME package request has been accepted for processing")
            return r.json()
        else:
            raise ibmiotf.APIException(status,"HTTP Error in createDeviceManagementExtensionPkg", r)

    def deleteDeviceManagementExtensionPkg(self, bundleId):
        """
        Delete a device management extension package
        It accepts bundleId (string) as parameters
        In case of failure it throws APIException
        """
        dmeReq = ApiClient.dmeSingleRequest % (self.host, bundleId)
        r = requests.delete(dmeReq, auth=self.credentials, verify=self.verify)
        status = r.status_code
        if status == 204:
            self.logger.debug("Device Management Extension Package removed")
            return True
        else:
            raise ibmiotf.APIException(status,"HTTP Error in deleteDeviceManagementExtensionPkg", r)

    def getDeviceManagementExtensionPkg(self, bundleId):
        """
        Get a specific device management extension package
        It accepts bundleId (string) as parameters
        In case of failure it throws APIException
        """
        dmeReq = ApiClient.dmeSingleRequest % (self.host, bundleId)
        r = requests.get(dmeReq, auth=self.credentials, verify=self.verify)
        status = r.status_code
        if status == 200:
            self.logger.debug("Device Management Extension Package retrieved")
            return r.json()
        else:
            raise ibmiotf.APIException(status,"HTTP Error in getDeviceManagementExtensionPkg", r)

    def updateDeviceManagementExtensionPkg(self, bundleId, dmeData):
        """
        Update a device management extension package
        It accepts bundleId (string) as parameters
        In case of failure it throws APIException
        """
        dmeReq = ApiClient.dmeSingleRequest % (self.host, bundleId)
        r = requests.put(dmeReq, auth=self.credentials, data=json.dumps(dmeData),
                      headers = {'content-type': 'application/json'}, verify=self.verify)
        status = r.status_code
        if status == 200:
            self.logger.debug("Device Management Extension Package updated")
            return r.json()
        else:
            raise ibmiotf.APIException(status,"HTTP Error in updateDeviceManagementExtensionPkg", r)
    
