import json
from collections import defaultdict

from ibmiotf.api.common import IterableList

class DeviceUid(defaultdict):
    def __init__(self, typeId, deviceId):
        dict.__init__(self, typeId=typeId, deviceId=deviceId)
    
    @property
    def typeId(self):
        return self["typeId"]
        
    @property
    def deviceId(self):
        return self["deviceId"]
    
class DeviceCreateRequest(defaultdict):
    def __init__(self, typeId, deviceId, authToken = None, deviceInfo = None, location = None, metadata=None):
        dict.__init__(
            self, 
            typeId=typeId,
            deviceId=deviceId,
            authToken=authToken,
            deviceInfo=deviceInfo, 
            location=location, 
            metadata=metadata
        )
    
    @property
    def typeId(self):
        return self["typeId"]
    @property
    def deviceId(self):
        return self["deviceId"]
    @property
    def authToken(self):
        return self["authToken"]
    @property
    def deviceInfo(self):
        return DeviceInfo(**self["deviceInfo"])
    @property
    def location(self):
        return self["location"]
    @property
    def metadata(self):
        return self["metadata"]
    
class DeviceInfo(defaultdict):
    def __init__(self, description=None, deviceClass=None, fwVersion=None, hwVersion=None, manufacturer=None, model=None, serialNumber=None, descriptiveLocation=None):
        dict.__init__(
            self, 
            description=description,
            deviceClass=deviceClass,
            fwVersion=fwVersion,
            hwVersion=hwVersion, 
            manufacturer=manufacturer, 
            model=model, 
            serialNumber=serialNumber,
            descriptiveLocation=descriptiveLocation
        )
    
    @property
    def description(self):
        return self["description"]
    @property
    def deviceClass(self):
        return self["deviceClass"]
    @property
    def fwVersion(self):
        return self["fwVersion"]
    @property
    def hwVersion(self):
        return self["hwVersion"]
    @property
    def manufacturer(self):
        return self["manufacturer"]
    @property
    def model(self):
        return self["model"]
    @property
    def serialNumber(self):
        return self["serialNumber"]
    @property
    def descriptiveLocation(self):
        return self["descriptiveLocation"]

    
class Device(object):
    def __init__(self, apiClient, data):
        self._apiClient = apiClient
        self._data = data
        
        if not set(['clientId', 'deviceId', 'typeId']).issubset(data):
            raise Exception("Data passed to Device is not correct: %s" % (json.dumps(data, sort_keys=True)))
            
        
        #{u'clientId': u'xxxxxxxxx',
        # u'deviceId': u'xxxxxxx',
        # u'deviceInfo': {u'description': u'None (xxxxxxxx)',
        #                 u'deviceClass': u'None',
        #                 u'fwVersion': u'xxxxx',
        #                 u'hwVersion': u'xxxxx',
        #                 u'manufacturer': u'xxxx.',
        #                 u'model': u'xxxx',
        #                 u'serialNumber': u'xxxxxxxxx'},
        # u'metadata': {},
        # u'refs': {u'diag': {u'errorCodes': u'/api/v0002/device/types/xxx/devices/xxxx/diag/errorCodes',
        #                     u'logs': u'/api/v0002/device/types/xxx/devices/xxxx/diag/logs'},
        #           u'location': u'/api/v0002/device/types/xxxx/devices/xxxx/location',
        #           u'mgmt': u'/api/v0002/device/types/xx/devices/xxxx/mgmt'},
        # u'registration': {u'auth': {u'id': u'xxxxxx',
        #                             u'type': u'person'},
        #                   u'date': u'2015-09-18T06:44:02.000Z'},
        # u'status': {u'alert': {u'enabled': False,
        #                        u'timestamp': u'2016-01-21T02:25:55.543Z'}},
        # u'typeId': u'vm'}
    
    @property
    def clientId(self):
        return self._data["clientId"]
         
    @property
    def deviceId(self):
        return self._data["deviceId"]
    
    @property
    def metadata(self):
        return self._data["metadata"]
    
    @property
    def deviceInfo(self):
        # Unpack the deviceInfo dictionary into keyword arguments so that we 
        # can return a DeviceIngo object instead of a plain dictionary
        return DeviceInfo(**self._data["deviceInfo"])
    
    @property
    def typeId(self):
        return self._data["typeId"]
            
    def __str__(self):
        return json.dumps(self._data, sort_keys=True)
    
    def __repr__(self):
        return json.dumps(self._data, sort_keys=True, indent=2)
    
    def json(self):
        return self._data
    
    
class IterableDeviceList(IterableList):
    def __init__(self, apiClient, typeId=None):
        if typeId is None:
            super(IterableDeviceList, self).__init__(apiClient, Device, 'api/v0002/bulk/devices', 'typeId,deviceId')
        else:
            super(IterableDeviceList, self).__init__(apiClient, Device, 'api/v0002/device/types/%s/devices/' % (typeId), 'deviceId')


class Devices(defaultdict):
    """
    Use the global unique identifier of a device, it's `clientId` to address devices. 
    
    # Delete
    
    ```python
    del devices["d:orgId:typeId:deviceId"]
    ```
    
    # Get
    Use the global unique identifier of a device, it's `clientId`. 
    
    ```python
    device = devices["d:orgId:typeId:deviceId"]
    print(device.clientId)
    print(device)
    
    # Is a device registered?
    
    ```python
    if "d:orgId:typeId:deviceId" in devices:
        print("The device exists")
    ```
    
    # Iterate through all registered devices
    
    ```python
    for device in devices:
        print(device)
    ```
    
    """
    # https://docs.python.org/2/library/collections.html#defaultdict-objects
    def __init__(self, apiClient, typeId=None):
        self._apiClient = apiClient
        self.typeId = typeId
    
    def __contains__(self, key):
        """
        get a device from the registry
        """
        if self.typeId is None:
            (classIdentifier, orgId, typeId, deviceId) = key.split(":")
            deviceUrl = 'api/v0002/device/types/%s/devices/%s' % (typeId, deviceId)
        else:
            deviceUrl = 'api/v0002/device/types/%s/devices/%s' % (self.typeId, key)
        
        r = self._apiClient.get(deviceUrl)
        if r.status_code == 200:
            return True
        elif r.status_code == 404:
            return False
        else:
            raise Exception("HTTP %s %s" % (r.status_code, r.text))
    
    def __getitem__(self, key):
        """
        get a device from the registry
        """
        if self.typeId is None:
            (classIdentifier, orgId, typeId, deviceId) = key.split(":")
            deviceUrl = 'api/v0002/device/types/%s/devices/%s' % (typeId, deviceId)
        else:
            deviceUrl = 'api/v0002/device/types/%s/devices/%s' % (self.typeId, key)

        r = self._apiClient.get(deviceUrl)
        if r.status_code == 200:
            return Device(self._apiClient, r.json())
        elif r.status_code == 404:
            self.__missing__(key)
        else:
            raise Exception("HTTP %s %s" % (r.status_code, r.text))
    
    def __setitem__(self, key, value):
        """
        register a new device
        """
        raise Exception("Unable to register or update a device via this interface at the moment.")
    
    def __delitem__(self, key):
        """
        delete a device
        """
        if self.typeId is None:
            (classIdentifier, orgId, typeId, deviceId) = key.split(":")
            deviceUrl = 'api/v0002/device/types/%s/devices/%s' % (typeId, deviceId)
        else:
            deviceUrl = 'api/v0002/device/types/%s/devices/%s' % (self.typeId, key)

        r = self._apiClient.delete(deviceUrl)
        if r.status_code != 204:
            raise Exception("HTTP %s %s" %(r.status_Code, r.text))
    
    def __missing__(self, key):
        """
        device does not exist
        """
        raise Exception("Device %s does not exist" % (key))

    def __iter__(self, *args, **kwargs):
        """
        iterate through all devices
        """
        return IterableDeviceList(self._apiClient, self.typeId)
    
    
    def create(self, devices):
        """
        Register one or more new devices, each request can contain a maximum of 512KB.
        The response body will contain the generated authentication tokens for all devices.
        You must make sure to record these tokens when processing the response.
        We are not able to retrieve lost authentication tokens
        It accepts accepts a list of devices (List of Dictionary of Devices)
        """
        
        if not isinstance(devices, list):
            listOfDevices = [devices]
        else:
            listOfDevices = devices
            
        r = self._apiClient.post('api/v0002/bulk/devices/add', listOfDevices)

        if r.status_code == 201:
            print("All devices created successfully")
            return r.json()
        if r.status_code == 202:
            print("Some devices created successfully")
            return r.json()
        else:
            raise Exception("HTTP %s %s"% (r.status_code, r.text))

    def update(self, deviceUid, metadata = None, deviceInfo = None, status = None):
        deviceUrl = 'api/v0002/device/types/%s/devices/%s' % (deviceUid.typeId, deviceUid.deviceId)

        data = {'status' : status, 'deviceInfo' : deviceInfo, 'metadata': metadata}
        
        r = self._apiClient.put(deviceUrl, data)
        if r.status_code == 200:
            return Device(self._apiClient, r.json())
        else:
            raise Exception("HTTP %s %s" % (r.status_code, r.text))

    def delete(self, devices):
        """
        Delete multiple devices, each request can contain a maximum of 512Kb
        It accepts accepts a list of devices (List of Dictionary of Devices)
        In case of failure it throws APIException
        """
        if not isinstance(devices, list):
            listOfDevices = [devices]
        else:
            listOfDevices = devices
            
        r = self._apiClient.post('api/v0002/bulk/devices/remove', listOfDevices)

        if r.status_code == 200:
            print("All devices deleted successfully")
            return r.json()
        if r.status_code == 202:
            print("Some devices deleted successfully")
            return r.json()
        else:
            raise Exception("HTTP %s %s"% (r.status_code, r.text))
