# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import json
import iso8601
from datetime import datetime

from wiotp.sdk.exceptions import ApiException
from wiotp.sdk.api.services.credentials import CloudantServiceBindingCredentials, EventStreamsServiceBindingCredentials
from collections import defaultdict


class ServiceBindingCreateRequest(defaultdict):
    def __init__(self, **kwargs):
        dict.__init__(self, **kwargs)
    
class CloudantServiceBindingCreateRequest(ServiceBindingCreateRequest):
    def __init__(self, **kwargs):
        if not set(['name', 'credentials', 'description']).issubset(kwargs):
            raise Exception("name, credentials, & description are required parameters for creating a Cloudant Service Binding: %s" % (json.dumps(kwargs, sort_keys=True)))
        
        # Convert credentials to CloudantServiceBindingCredentials for validation 
        if not isinstance(kwargs['credentials'], CloudantServiceBindingCredentials):
            kwargs['credentials'] = CloudantServiceBindingCredentials(**kwargs["credentials"])
        
        kwargs['type'] = "cloudant"
        
        ServiceBindingCreateRequest.__init__(self, **kwargs)

class EventStreamsServiceBindingCreateRequest(ServiceBindingCreateRequest):
    def __init__(self, **kwargs):
        if not set(['name', 'credentials', 'description']).issubset(kwargs):
            raise Exception("name, credentials, & description are required parameters for creating a Cloudant Service Binding: %s" % (json.dumps(kwargs, sort_keys=True)))
        
        # Convert credentials to CloudantServiceBindingCredentials for validation 
        if not isinstance(kwargs['credentials'], CloudantServiceBindingCredentials):
            kwargs['credentials'] = CloudantServiceBindingCredentials(**kwargs["credentials"])
        
        kwargs['type'] = "cloudant"
        
        ServiceBindingCreateRequest.__init__(self, **kwargs)


class ServiceBinding(defaultdict):
    """
    u'bindingMode': u'manual',
               u'bound': True,
               u'created': u'2019-01-28T15:10:22.011+0000',
               u'createdBy': u'a-hldtxx-tp3lq5g00b',
               u'description': u'Test Cloudant instance',
               u'id': u'5dc40598-5dc0-4b4f-b5fc-b339da66d684',
               u'name': u'test-cloudant',
               u'type': u'cloudant',
               u'updated': u'2019-01-28T15:10:22.011+0000',
               u'updatedBy': u'a-hldtxx-tp3lq5g00b'}
    """
    def __init__(self, **kwargs):
        if 'created' in kwargs and not isinstance(kwargs['created'], datetime):
            kwargs['created'] = iso8601.parse_date(kwargs['created']) 
            
        if 'updated' in kwargs and not isinstance(kwargs['updated'], datetime):
            kwargs['updated'] = iso8601.parse_date(kwargs['updated'])

        dict.__init__(self, **kwargs)

    @property
    def bindingMode(self):
        return self["bindingMode"]
    @property
    def bound(self):
        return self["bound"]
    @property
    def created(self):
        return self["created"]
    @property
    def createdBy(self):
        return self["createdBy"]
    @property
    def description(self):
        return self["description"]
    @property
    def id(self):
        return self["id"]
    @property
    def name(self):
        return self["name"]
    @property
    def bindingType(self):
        return self["type"]
    @property
    def updated(self):
        return self["updated"]
    @property
    def updatedBy(self):
        return self["updatedBy"]

    def __str__(self):
        return "[" + self["id"] + "] " + self["name"] + " (" + self["bindingMode"] + " binding)"

    def __repr__(self):
        return json.dumps(self, sort_keys=True, indent=2)
    
    def json(self):
        return json.dumps(self, sort_keys=True, indent=2)

class ServiceBindings(object):

    allServicesUrl = "https://%s/api/v0002/s2s/services"
    oneServiceUrl = "https://%s/api/v0002/s2s/services/%s"
    
    def __init__(self, apiClient):
        self._apiClient = apiClient

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
        
        url = "api/v0002/s2s/services"
        
        queryParms = {}
        if nameFilter:
            queryParms["name"] = nameFilter
        if typeFilter:
            queryParms["type"] = typeFilter
        if bindingModeFilter:
            queryParms["bindingMode"] = bindingModeFilter
        if boundFilter:
            queryParms["bound"] = boundFilter
        

        r = self._apiClient.get(url, parameters=queryParms)
        if r.status_code == 200:
            responseList = []
            for entry in r.json()["results"]:
                responseList.append(ServiceBinding(**entry))
            return responseList
        else:
            raise ApiException(r)

    
    def get(self, serviceId):
        """
        Retrieve the service with the specified id.
        Parameters:
            - serviceId (String), Service Id which is a UUID
        Throws APIException on failure.

        """

        url = "api/v0002/s2s/services/%s" % (serviceId)

        r = self._apiClient.get(url)
        if r.status_code == 200:
            return ServiceBinding(**r.json())
        if r.status_code == 404:
            return None
        else:
            raise ApiException(r)

            
    def create(self, serviceBinding):
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
        if not isinstance(serviceBinding, ServiceBindingCreateRequest):
            if serviceBinding["type"] == "cloudant":
                serviceBinding = CloudantServiceBindingCreateRequest(**serviceBinding)
            elif serviceBinding["type"] == "eventstreams":
                pass
                # serviceBinding = CloudantServiceBindingCreateRequest(**serviceBinding)
            else:
                raise Exception("Unsupported service binding type")

        url = "api/v0002/s2s/services"

        r = self._apiClient.post(url, data=serviceBinding)
        if r.status_code == 201:
            return ServiceBinding(**r.json())
        else:
            raise ApiException(r)

            
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

        url = "api/v0002/s2s/services/%s" % (serviceId)

        serviceBody = {}
        serviceBody['name'] = serviceName
        serviceBody['description'] = description
        serviceBody['credentials'] = credentials

        r = self._apiClient.put(url, data=serviceBody)
        if r.status_code == 200:
            return ServiceBinding(**r.json())
        else:
            raise ApiException(r)
        
    
    def delete(self, serviceId):
        """
        Deletes service with service id
        Parameters:
            - serviceId (string) - Service id of the service
        Throws APIException on failure
        """

        url = "api/v0002/s2s/services/%s" % (serviceId)

        r = self._apiClient.delete(url)
        if r.status_code == 204:
            return True
        else:
            raise ApiException(r)
        
    
