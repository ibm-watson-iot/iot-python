# *****************************************************************************
# Copyright (c) 2018 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import json
from collections import defaultdict

from ibmiotf.api.common import IterableList, ApiException

class DeviceUid(defaultdict):
    def __init__(self, **kwargs):
        if not set(['deviceId', 'typeId']).issubset(kwargs):
            raise Exception("typeId and deviceId are required properties to uniquely identify a device")
        dict.__init__(self, **kwargs)
    
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

class DeviceCreateResponse(defaultdict):
    def __init__(self, **kwargs):
        dict.__init__(self, **kwargs)
    
    @property
    def typeId(self):
        return self["typeId"]
    @property
    def deviceId(self):
        return self["deviceId"]
    @property
    def authToken(self):
        return self["authToken"]

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
        Does a device exist?
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
            raise ApiException(r)
    
    def __getitem__(self, key):
        """
        Get a device from the registry
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
            raise ApiException(r)
    
    def __setitem__(self, key, value):
        """
        Register a new device - not currently supported via this interface, use: `registry.devices.create()`
        """
        raise Exception("Unable to register or update a device via this interface at the moment.")
    
    def __delitem__(self, key):
        """
        Delete a device
        """
        if self.typeId is None:
            (classIdentifier, orgId, typeId, deviceId) = key.split(":")
            deviceUrl = 'api/v0002/device/types/%s/devices/%s' % (typeId, deviceId)
        else:
            deviceUrl = 'api/v0002/device/types/%s/devices/%s' % (self.typeId, key)

        r = self._apiClient.delete(deviceUrl)
        if r.status_code == 404:
            self.__missing__(key)
        elif r.status_code != 204:
            raise ApiException(r)
    
    def __missing__(self, key):
        """
        Device does not exist
        """
        raise KeyError("Device %s does not exist" % (key))

    def __iter__(self, *args, **kwargs):
        """
        Iterate through all devices
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

        if r.status_code in [201, 202]:
            responseList = []
            for entry in r.json():
                responseList.append(DeviceCreateResponse(**entry))
            return responseList
        else:
            raise ApiException(r)


    def update(self, deviceUid, metadata = None, deviceInfo = None, status = None):
        """
        Update an existing device
        """
        
        if not isinstance(deviceUid, DeviceUid) and isinstance(deviceUid, dict):
            deviceUid = DeviceUid(**deviceUid)
        
        deviceUrl = 'api/v0002/device/types/%s/devices/%s' % (deviceUid.typeId, deviceUid.deviceId)

        data = {'status' : status, 'deviceInfo' : deviceInfo, 'metadata': metadata}
        
        r = self._apiClient.put(deviceUrl, data)
        if r.status_code == 200:
            return Device(self._apiClient, r.json())
        else:
            raise ApiException(r)

    
    def delete(self, devices):
        """
        Delete one or more devices, each request can contain a maximum of 512Kb
        It accepts accepts a list of devices (List of Dictionary of Devices)
        In case of failure it throws APIException
        """
        if not isinstance(devices, list):
            listOfDevices = [devices]
        else:
            listOfDevices = devices
            
        r = self._apiClient.post('api/v0002/bulk/devices/remove', listOfDevices)

        if r.status_code in [200, 202]:
            return r.json()
        else:
            raise ApiException(r)
