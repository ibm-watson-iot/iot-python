# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import requests
import logging
import json
from datetime import datetime
from collections import defaultdict
from wiotp.sdk.exceptions import ApiException
import iso8601


from wiotp.sdk.exceptions import ConfigurationException


class ApiClient:
    def __init__(self, config, logger=None):
        self._config = config

        # Configure logging
        if logger is None:
            logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)
            logger.setLevel(logging.INFO)

        self.logger = logger

        if self._config.apiKey is None:
            raise ConfigurationException("Missing required property for API key based authentication: auth-key")
        if self._config.apiToken is None:
            raise ConfigurationException("Missing required property for API key based authentication: auth-token")

        # To support development systems this can be overridden to False
        if not self._config.verify:
            from requests.packages.urllib3.exceptions import InsecureRequestWarning

            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def get(self, url, parameters=None):
        resp = requests.get(
            "https://%s/%s" % (self._config.host, url),
            auth=self._config.credentials,
            params=parameters,
            verify=self._config.verify,
        )
        resp.encoding = "utf-8"
        return resp

    def delete(self, url):
        resp = requests.delete(
            "https://%s/%s" % (self._config.host, url), auth=self._config.credentials, verify=self._config.verify
        )
        resp.encoding = "utf-8"
        return resp

    def patch(self, url, data):
        resp = requests.patch(
            "https://%s/%s" % (self._config.host, url),
            auth=self._config.credentials,
            data=json.dumps(data, cls=DateTimeEncoder),
            headers={"content-type": "application/json"},
            verify=self._config.verify,
        )
        resp.encoding = "utf-8"
        return resp

    def post(self, url, data):
        resp = requests.post(
            "https://%s/%s" % (self._config.host, url),
            auth=self._config.credentials,
            data=json.dumps(data, cls=DateTimeEncoder),
            headers={"content-type": "application/json"},
            verify=self._config.verify,
        )
        resp.encoding = "utf-8"
        return resp

    def postMultipart(self, url, multipart_data):
        resp = requests.post(
            "https://%s/%s" % (self._config.host, url),
            auth=self._config.credentials,
            data=multipart_data,
            headers={"Content-Type": multipart_data.content_type},
            verify=self._config.verify,
        )
        resp.encoding = "utf-8"
        return resp

    def put(self, url, data):
        resp = requests.put(
            "https://%s/%s" % (self._config.host, url),
            auth=self._config.credentials,
            data=json.dumps(data, cls=DateTimeEncoder),
            headers={"content-type": "application/json"},
            verify=self._config.verify,
        )
        resp.encoding = "utf-8"
        return resp

    def putMultipart(self, url, multipart_data):
        resp = requests.put(
            "https://%s/%s" % (self._config.host, url),
            auth=self._config.credentials,
            data=multipart_data,
            headers={"Content-Type": multipart_data.content_type},
            verify=self._config.verify,
        )
        resp.encoding = "utf-8"
        return resp


class IterableSimpleList(object):
    def __init__(self, apiClient, castToClass, url, filters=None, passApiClient=True):
        self._apiClient = apiClient
        self._castToClass = castToClass
        self._url = url
        self._passApiClient = passApiClient

        self._listBuffer = []
        self._noMoreResults = False

    def __iter__(self):
        return self

    # Python 2.x
    def next(self):
        if len(self._listBuffer) == 0 and not self._noMoreResults:
            # We need to make an api call
            apiResponse = self._makeApiCall()

            self._listBuffer = apiResponse
            # We read all the results in one call so there are no more available to fetch
            self._noMoreResults = True

        if len(self._listBuffer) > 0:
            if self._passApiClient:
                return self._castToClass(apiClient=self._apiClient, **self._listBuffer.pop(0))
            else:
                return self._castToClass(**self._listBuffer.pop(0))
        else:
            raise StopIteration

    # Python 3.x
    def __next__(self):
        return self.next()

    def _makeApiCall(self, parameters=None):
        """
        Retrieve bulk objects
        It accepts a list of parameters
        In case of failure it throws Exception
        """
        r = self._apiClient.get(self._url, parameters)
        if r.status_code == 200:
            return r.json()
        else:
            raise Exception("Unexpected response from API (%s) = %s %s" % (self._url, r.status_code, r.text))


class IterableList(object):
    def __init__(self, apiClient, castToClass, url, sort=None, filters=None, passApiClient=True):
        self._apiClient = apiClient
        self._castToClass = castToClass
        self._url = url
        self._sort = sort
        self._filters = filters
        self._passApiClient = passApiClient

        # For paging through the API
        self._limit = 50
        self._bookmark = None
        self._listBuffer = []
        self._noMoreResults = False

    def __iter__(self):
        return self

    # Python 2.x
    def next(self):
        if len(self._listBuffer) == 0 and not self._noMoreResults:
            parameters = {"_limit": self._limit, "_bookmark": self._bookmark}
            if self._sort is not None:
                parameters["_sort"] = self._sort

            if self._filters is not None:
                # print("Filters: %s " % self._filters)
                for param in self._filters:
                    # print("Filter param: %s " % param)
                    parameters[param] = self._filters[param]

            # We need to make an api call
            apiResponse = self._makeApiCall(parameters=parameters)
            self._listBuffer = apiResponse["results"]

            if "bookmark" in apiResponse:
                self._bookmark = apiResponse["bookmark"]
            else:
                self._noMoreResults = True

        if len(self._listBuffer) > 0:
            if self._passApiClient:
                return self._castToClass(apiClient=self._apiClient, **self._listBuffer.pop(0))
            else:
                return self._castToClass(**self._listBuffer.pop(0))
        else:
            raise StopIteration

    # Python 3.x
    def __next__(self):
        return self.next()

    def _makeApiCall(self, parameters=None):
        """
        Retrieve bulk objects
        It accepts a list of parameters
        In case of failure it throws Exception
        """
        r = self._apiClient.get(self._url, parameters)
        if r.status_code == 200:
            return r.json()
        else:
            raise Exception("Unexpected response from API (%s) = %s %s" % (self._url, r.status_code, r.text))


# define the common properties found on most Rest API Items
class RestApiItemBase(defaultdict):
    def __init__(self, apiClient, **kwargs):
        self._apiClient = apiClient
        dict.__init__(self, **kwargs)

    @property
    def id(self):
        return self["id"]

    @property
    def name(self):
        return self["name"]

    @property
    def description(self):
        return self["description"]

    @property
    def created(self):
        return iso8601.parse_date(self["created"])

    @property
    def createdBy(self):
        return self["createdBy"]

    @property
    def updated(self):
        return iso8601.parse_date(self["updated"])

    @property
    def updatedBy(self):
        return self["updatedBy"]


"""
This should be instantiated as a class property, 
it uses the instance parameter to access instance specific values  TBD describe!!!
"""


class RestApiModifiableProperty(property):
    def __init__(self, castToClass):
        self._castToClass = castToClass

    def __get__(self, instance, type=None):
        url = self.getUrl(instance)
        # TBD debug print ("Get, Instance, instance: %s, Owner: %s, URL: %s" % (instance, type, url))

        r = self.getApiClient(instance).get(url)
        if r.status_code == 200:
            return self._castToClass(apiClient=self.getApiClient(instance), **r.json())
        else:
            raise ApiException(r)

    def __set__(self, instance, value):
        url = self.getUrl(instance)
        # TBD debug print ("Set, Instance, instance: %s, \nOwner: %s, URL: %s, Value: %s" % (instance, type, url, value))

        r = self.getApiClient(instance).post(url, data=value)
        if r.status_code == 201:
            return self._castToClass(apiClient=self.getApiClient(instance), **r.json())
        else:
            raise ApiException(r)

    def __delete__(self, instance):
        # TBD debug print ("Delete, Instance, instance: %s" % (instance))
        url = self.getUrl(instance)

        r = self.getApiClient(instance).delete(url)
        if r.status_code != 204:
            raise ApiException(r)


class RestApiDictBase(defaultdict):
    def __init__(self, apiClient, castToClass, listToCast, url, sort=None, filters=None, passApiClient=True):
        self._apiClient = apiClient
        self._castToClass = castToClass
        self._listToCast = listToCast
        self._baseUrl = url
        self._singleItemUrl = url + "/%s"
        self._sort = sort
        self._filters = filters
        self._passApiClient = passApiClient

    def __contains__(self, key):
        """
        Does an Item exist?
        """
        url = self._singleItemUrl % (key)

        r = self._apiClient.get(url)
        if r.status_code == 200:
            return True
        if r.status_code == 404:
            return False
        else:
            raise ApiException(r)

    def __getitem__(self, key):
        """
        Retrieve the Item with the specified id.
        Parameters:
            - key (String), Identity field to access item
        Throws APIException on failure.

        """

        url = self._singleItemUrl % (key)

        r = self._apiClient.get(url)
        if r.status_code == 200:
            return self._castToClass(apiClient=self._apiClient, **r.json())
        if r.status_code == 404:
            self.__missing__(key)
        else:
            raise ApiException(r)

    def __missing__(self, key):
        """
        Item does not exist
        """
        raise KeyError("Item %s does not exist" % (key))

    def __iter__(self, *args, **kwargs):
        """
        Iterate through all Schemas
        """
        return self._listToCast(self._apiClient, self._baseUrl)

    def find(self, query_params={}):
        """
        Gets the list of Schemas, they are used to call specific business logic when data in Watson IoT Platform changes.
        
        Parameters:
        
            - queryParams(dict) - Filter the results by the key-value pairs in the dictionary
        
        Throws APIException on failure.
        """
        return self._listToCast(self._apiClient, self._baseUrl, filters=query_params)


class RestApiDict(RestApiDictBase):
    def __init__(self, apiClient, castToClass, listToCast, url, sort=None, filters=None, passApiClient=True):
        super(RestApiDict, self).__init__(apiClient, castToClass, listToCast, url, sort, filters, passApiClient)

    def __setitem__(self, key, value):
        """
        Register a new Item - not currently supported via this interface
        """
        raise Exception("Unable to register or update a Item via this interface at the moment.")

    def __delitem__(self, key):
        """
        Delete an Item
        """
        url = self._singleItemUrl % (key)

        r = self._apiClient.delete(url)
        if r.status_code == 404:
            self.__missing__(key)
        elif r.status_code != 204 and r.status_code != 200:
            raise ApiException(r)

    def create(self, item):
        """
        Create an Item for the organization in the Watson IoT Platform. 
        Parameters:
            - name (string) - Name of the service
            - type - must be webhook
            - description (string) - description of the service
            - configuration - specifies the JSON Schema configuration required
            - enabled (boolean) - enabled
        Throws APIException on failure
        """
        r = self._apiClient.post(self._baseUrl, data=item)
        if r.status_code == 201:
            if self._passApiClient:
                return self._castToClass(apiClient=self._apiClient, **r.json())
            else:
                return self._castToClass(**r.json())
            return self._castToClass(apiClient=self._apiClient, **r.json())
        else:
            raise ApiException(r)

    def update(self, key, item):
        """
        Updates the Item with the specified key.
        Parameters:
            - key (String), Identity field to access item
            - item, item object to store.
        Throws APIException on failure.

        """
        url = self._singleItemUrl % (key)

        r = self._apiClient.put(url, data=item)
        if r.status_code == 200:
            if self._passApiClient:
                return self._castToClass(apiClient=self._apiClient, **r.json())
            else:
                return self._castToClass(**r.json())
        else:
            raise ApiException(r)


class RestApiDictReadOnly(RestApiDictBase):
    """
    The Active version restricts the ability to directly modify the retrieved item.
    """

    def __init__(self, apiClient, castToClass, listToCast, url, sort=None, filters=None, passApiClient=True):
        super(RestApiDictReadOnly, self).__init__(apiClient, castToClass, listToCast, url, sort, filters, passApiClient)

    def __setitem__(self, key, value):
        """
        Register a new Item - not supported for active item
        """
        raise Exception("Unable to register or update this active item, please modify the draft version.")

    def __delitem__(self, key):
        """
        Delete an Item - not supported for active item
        """
        raise Exception("Unable to delete this active item, please delete the draft version.")

    def create(self, item):
        """
        Create an Item - not supported for CTIVE item
        """
        raise Exception("Unable to delete this active item, please delete the draft version.")

    def update(self, key, item):
        """
        Create an Item - not supported for CTIVE item
        """
        raise Exception("Unable to update this active item, please update and activate the draft version.")


class DateTimeEncoder(json.JSONEncoder):
    """
    See: https://stackoverflow.com/a/27058505/3818286
    """

    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        # return json.JSONEncoder.default(self, o)
        return super(DateTimeEncoder, self).default(o)
