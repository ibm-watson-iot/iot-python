import requests
import logging
import json
from datetime import datetime

from ibmiotf import ConfigurationException

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
        if not self._config.verifyCertificate:
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


class ApiException(Exception):
    """
    Exception raised when any API call fails unexpectedly
    
    # Attributes
    response (requests.Response): See: http://docs.python-requests.org/en/master/api/#requests.Response
    """
    def __init__(self, response):
        self.response = response
        
        # {
        #   "violations":[
        #     {
        #       "message":"CUDRS0012E: The severity field has a value that is too high. Specify a value equal to or less than 2.",
        #       "exception":{"id":"CUDRS0012E","properties":["severity","2"]}
        #     }
        #   ],
        #   "message":"CUDRS0007E: The request was not valid. Review the constraint violations provided.",
        #   "exception":{"id":"CUDRS0007E","properties":[]}
        # }
        
        try:
            self.body = self.response.json()
            self.message = self.body.get("message", None)
            self.exception = self.body.get("exception", None)
        except ValueError:
            self.body = None
            self.message = None
            self.exception = None
        
    @property
    def id(self):
        if self.exception is not None:  
            return self.exception.get("id", None)

    @property
    def violations(self):
        violations = self.body.get("violations", None)
        if violations is None:
            return None
        else:
            returnArray = []
            for violation in violations:
                returnArray.append(violation.get("message", None))
            return returnArray
        

    def __str__(self):
        if self.message:
            return self.message 
        else:
            return "Unexpected return code from API: %s (%s) - %s\n%s" % (self.response.status_code, self.response.reason, self.response.url, self.response.text)
    
    def __repr__(self):
        return self.response.__repr__()

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


class DateTimeEncoder(json.JSONEncoder):
    '''
    See: https://stackoverflow.com/a/27058505/3818286
    '''
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        #return json.JSONEncoder.default(self, o)
        return super(DateTimeEncoder, self).default(o)
