import requests
import logging
import json
from datetime import datetime

from wiotp.sdk.exceptions import ConfigurationException

class ApiClient():
    def __init__(self, config, logger=None):
        self._config = config

        # Configure logging
        if logger is None:
            logger = logging.getLogger(self.__module__+"."+self.__class__.__name__)
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
            auth = self._config.credentials, 
            params = parameters, 
            verify=self._config.verify
        )
        resp.encoding="utf-8"
        return resp

    def delete(self, url):
        resp = requests.delete(
            "https://%s/%s" % (self._config.host, url), 
            auth = self._config.credentials, 
            verify = self._config.verify
        )
        resp.encoding="utf-8"
        return resp

    def post(self, url, data):
        resp = requests.post(
            "https://%s/%s" % (self._config.host, url), 
            auth = self._config.credentials, 
            data = json.dumps(data, cls=DateTimeEncoder), 
            headers = {'content-type': 'application/json'}, 
            verify = self._config.verify
        )
        resp.encoding="utf-8"
        return resp

    def put(self, url, data):
        resp = requests.put(
            "https://%s/%s" % (self._config.host, url), 
            auth = self._config.credentials, 
            data = json.dumps(data, cls=DateTimeEncoder), 
            headers = {'content-type': 'application/json'}, 
            verify = self._config.verify
        )
        resp.encoding="utf-8"
        return resp



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
                for param in self._filters:
                    parameters[param] = self._filters[param]

            # We need to make an api call
            apiResponse = self._makeApiCall(parameters = parameters)
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
        
    def _makeApiCall(self, parameters = None):
        """
        Retrieve bulk devices
        It accepts accepts a list of parameters
        In case of failure it throws Exception
        """
        print("Making api call %s // %s ..." % (self._url, parameters))
        r = self._apiClient.get(self._url, parameters)
        if r.status_code == 200:
            print(json.dumps(r.json()))
            return r.json()
        else:
            raise Exception("HTTP %s %s" % (r.status_code, r.text))


class DateTimeEncoder(json.JSONEncoder):
    '''
    See: https://stackoverflow.com/a/27058505/3818286
    '''
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        #return json.JSONEncoder.default(self, o)
        return super(DateTimeEncoder, self).default(o)
