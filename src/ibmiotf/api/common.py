import requests
import logging
import json

from ibmiotf import ConfigurationException

class ApiClient():
    def __init__(self, options, logger=None):
        self.__options = options

        # Configure logging
        if logger is None:
            logger = logging.getLogger(self.__module__+"."+self.__class__.__name__)
            logger.setLevel(logging.INFO)

        self.logger = logger

        if self.__options.get('auth-key') is None:
            raise ConfigurationException("Missing required property for API key based authentication: auth-key")
        if self.__options.get('auth-token') is None:
            raise ConfigurationException("Missing required property for API key based authentication: auth-token")

        # Get the orgId from the apikey
        self.__options['org'] = self.__options['auth-key'][2:8]

        if "domain" not in self.__options:
            # Default to the domain for the public cloud offering
            self.__options['domain'] = "internetofthings.ibmcloud.com"

        if "host" in self.__options.keys():
            self.host = self.__options['host']
        else:
            self.host = self.__options['org'] + "." + self.__options['domain']
            
        self.credentials = (self.__options['auth-key'], self.__options['auth-token'])

        # To support development systems this can be overridden to False
        self.verify = False
        if not self.verify:
            from requests.packages.urllib3.exceptions import InsecureRequestWarning
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    
    def get(self, url, parameters=None):
        return requests.get("https://%s/%s" % (self.host, url), auth = self.credentials, params = parameters, verify=self.verify)

    def delete(self, url):
        return requests.delete("https://%s/%s" % (self.host, url), auth = self.credentials, verify=self.verify)

    def post(self, url, data):
        return requests.post(
            "https://%s/%s" % (self.host, url), 
            auth = self.credentials, 
            data = json.dumps(data), 
            headers = {'content-type': 'application/json'}, 
            verify=self.verify
        )

    def put(self, url, data):
        return requests.put(
            "https://%s/%s" % (self.host, url), 
            auth = self.credentials, 
            data = json.dumps(data), 
            headers = {'content-type': 'application/json'}, 
            verify=self.verify
        )

class ApiException(Exception):
    """
    Exception raised when any API call fails unexpectedly
    
    # Attributes
    response (requests.Response): See: http://docs.python-requests.org/en/master/api/#requests.Response
    """
    def __init__(self, response):
        self.response = response

    def __str__(self):
        return "Unexpected return code from API: %s (%s) - %s\n%s" % (self.response.status_code, self.response.reason, self.response.url, self.response.text)
    

class IterableList(object):
    def __init__(self, apiClient, castToClass, url, sort=None):
        self._apiClient = apiClient
        self._castToClass = castToClass
        self._url = url
        self._sort = sort
        
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
            # We need to make an api call
            apiResponse = self._makeApiCall(parameters = {"_limit": self._limit, "_bookmark": self._bookmark, "_sort": self._sort})
            self._listBuffer = apiResponse["results"]
            
            if "bookmark" in apiResponse:
                self._bookmark = apiResponse["bookmark"]
            else:
                self._noMoreResults = True
        
        if len(self._listBuffer) > 0:
            return self._castToClass(self._apiClient, self._listBuffer.pop(0))
        else:
            raise StopIteration
    
    # Python 3.x
    def __next__(self):
        return self.next()
        
    def _makeApiCall(self, parameters = None):
        """
        Retrieve bulk devices
        It accepts accepts a list of parameters
        In case of failure it throws APIException
        """
        r = self._apiClient.get(self._url, parameters)
        if r.status_code == 200:
            return r.json()
        else:
            raise Exception("HTTP %s %s" % (r.status_code, r.text))
