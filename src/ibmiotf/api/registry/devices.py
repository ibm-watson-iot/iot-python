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
    

class Device():
    def __init__(self, apiClient, data):
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
    def typeId(self):
        return self._data["typeId"]
            
    def __str__(self):
        return json.dumps(self._data, sort_keys=True)
    
    def __repr__(self):
        return json.dumps(self._data, sort_keys=True, indent=2)
    
    @property
    def json(self):
        return self._data
    
    
class IterableDeviceList(IterableList):
    def __init__(self, apiClient, typeId=None):
        if typeId is None:
            super(IterableDeviceList, self).__init__(apiClient, Device, 'api/v0002/bulk/devices', 'typeId,deviceId')
        else:
            super(IterableDeviceList, self).__init__(apiClient, Device, 'api/v0002/device/types/%s/devices/' % (typeId), 'deviceId')
        self.apiClient = apiClient


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
        self.apiClient = apiClient
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
        
        r = self.apiClient.get(deviceUrl)
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

        r = self.apiClient.get(deviceUrl)
        if r.status_code == 200:
            return Device(self.apiClient, r.json())
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

        r = self.apiClient.delete(deviceUrl)
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
        return IterableDeviceList(self.apiClient, self.typeId)
    
    
    def create(self, listOfDevices):
        """
        Register multiple new devices, each request can contain a maximum of 512KB.
        The response body will contain the generated authentication tokens for all devices.
        You must make sure to record these tokens when processing the response.
        We are not able to retrieve lost authentication tokens
        It accepts accepts a list of devices (List of Dictionary of Devices)
        In case of failure it throws APIException
        """
        r = self.apiClient.post('api/v0002/bulk/devices/add', listOfDevices)

        if r.status_code == 201:
            print("All devices created successfully")
            return r.json()
        if r.status_code == 202:
            print("Some devices created successfully")
            return r.json()
        else:
            raise Exception("HTTP %s %s"% (r.status_code, r.text))


    def delete(self, listOfDevicesUids):
        """
        Delete multiple devices, each request can contain a maximum of 512Kb
        It accepts accepts a list of devices (List of Dictionary of Devices)
        In case of failure it throws APIException
        """
        r = self.apiClient.post('api/v0002/bulk/devices/remove', listOfDevicesUids)

        if r.status_code == 200:
            print("All devices deleted successfully")
            return r.json()
        if r.status_code == 202:
            print("Some devices deleted successfully")
            return r.json()
        else:
            raise Exception("HTTP %s %s"% (r.status_code, r.text))
