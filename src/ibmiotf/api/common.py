import requests
import logging

class ApiClient():
    def __init__(self, options, logger=None):
        self.__options = options

        # Configure logging
        if logger is None:
            logger = logging.getLogger(self.__module__+"."+self.__class__.__name__)
            logger.setLevel(logging.INFO)

        self.logger = logger

        if 'auth-key' not in self.__options or self.__options['auth-key'] is None:
            raise ibmiotf.ConfigurationException("Missing required property for API key based authentication: auth-key")
        if 'auth-token' not in self.__options or self.__options['auth-token'] is None:
            raise ibmiotf.ConfigurationException("Missing required property for API key based authentication: auth-token")

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
    

class IterableList(object):
    def __init__(self, apiClient, castToClass, url, sort=None):
        self.apiClient = apiClient
        self.castToClass = castToClass
        self.url = url
        self.sort = sort
        
        # For paging through the API
        self.limit = 50
        self.bookmark = None
        self.listBuffer = []
        self.noMoreResults = False
        
    def __iter__(self):
        return self
    
    # Python 2.x
    def next(self):
        if len(self.listBuffer) == 0 and not self.noMoreResults:
            # We need to make an api call
            apiResponse = self._makeApiCall(parameters = {"_limit": self.limit, "_bookmark": self.bookmark, "_sort": self.sort})
            self.listBuffer = apiResponse["results"]
            
            if "bookmark" in apiResponse:
                self.bookmark = apiResponse["bookmark"]
            else:
                self.noMoreResults = True
        
        if len(self.listBuffer) > 0:
            return self.castToClass(self.apiClient, self.listBuffer.pop(0))
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
        r = self.apiClient.get(self.url, parameters)
        if r.status_code == 200:
            return r.json()
        else:
            raise Exception("HTTP %s %s" % (r.status_code, r.text))

