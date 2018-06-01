import json
from collections import defaultdict

from ibmiotf.api.common import IterableList
from ibmiotf.api.registry.devices import Devices

class DeviceTypes(defaultdict):
    
    def __init__(self, apiClient):
        self.apiClient = apiClient
    
    def __contains__(self, key):
        """
        get a device type from the registry
        """
        
        url = 'api/v0002/device/types/%s' % (key)

        r = self.apiClient.get(url)
        if r.status_code == 200:
            return True
        elif r.status_code == 404:
            return False
        else:
            raise Exception("HTTP %s %s" % (r.status_code, r.text))
    
    def __getitem__(self, key):
        """
        get a device type from the registry
        """
        url = 'api/v0002/device/types/%s' % (key)

        r = self.apiClient.get(url)
        if r.status_code == 200:
            return DeviceType(self.apiClient, r.json())
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
        delete a device type
        """
        url = 'api/v0002/device/types/%s' % (key)

        r = self.apiClient.delete(url)
        if r.status_code != 204:
            raise Exception("HTTP %s %s" %(r.status_Code, r.text))
    
    def __missing__(self, key):
        """
        device type does not exist
        """
        raise Exception("Device type %s does not exist" % (key))
    
    def __iter__(self, *args, **kwargs):
        """
        iterate through all devices
        """
        return IterableDeviceTypeList(self.apiClient)



class IterableDeviceTypeList(IterableList):
    def __init__(self, apiClient):
        super(IterableDeviceTypeList, self).__init__(apiClient, DeviceType, 'api/v0002/device/types')
              
      

        
class DeviceType():
    def __init__(self, apiClient, data):
        self._data = data
        #{"classId": "Device", "createdDateTime": "2016-01-23T16:34:46+00:00", "description": 
        #"Extended color light", "deviceInfo": {"description": "Extended color light", "manufacturer": "Philips", "model": "LCT003"}, 
        #"id": "LCT003", "refs": {"logicalInterfaces": "api/v0002/device/types/LCT003/logicalinterfaces", "mappings": 
        #"api/v0002/device/types/LCT003/mappings", "physicalInterface": "api/v0002/device/types/LCT003/physicalinterface"}, 
        #"updatedDateTime": "2017-02-27T10:27:04.221Z"}
        
        self.devices = Devices(apiClient, data["id"])
        
    @property
    def id(self):
        return self._data["id"]
            
    @property
    def classId(self):
        return self._data["classId"]
    
    def __str__(self):
        return json.dumps(self._data, sort_keys=True)
    
    def __repr__(self):
        return json.dumps(self._data, sort_keys=True, indent=2)
    
    @property
    def json(self):
        return self._data
    
