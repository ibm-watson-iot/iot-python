# *****************************************************************************
# Copyright (c) 2015, 2018 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import ibmiotf
import json
import requests
import base64
import json
from datetime import datetime

import logging
from symbol import parameters
from requests_toolbelt.multipart.encoder import MultipartEncoder

from ibmiotf.api.registry import Registry
from ibmiotf.api.usage import Usage
from ibmiotf.api.status import Status
from ibmiotf.api.lec import LEC
from ibmiotf.api.mgmt import Mgmt
from ibmiotf.api.common import ApiClient as NewApiClient


class ApiClient():
    #Organization URL
    organizationUrl = 'https://%s/api/v0002/'
    
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
        
        self.newApiClient = NewApiClient(options, self.logger)
        self.registry = Registry(self.newApiClient)
        self.status = Status(self.newApiClient)
        self.usage = Usage(self.newApiClient)
        self.lec = LEC(self.newApiClient)
        self.mgmt = Mgmt(self.newApiClient)



    #This method returns the organization
    def getOrganizationDetails(self):
        """
        Get details about an organization
        It does not need any parameter to be passed
        In case of failure it throws APIException
        """
        if self.__options['org'] is None:
            raise ibmiotf.ConfigurationException("Missing required property: org")
        else:
            url = ApiClient.organizationUrl % (self.host)
        r = requests.get(url, auth=self.credentials, verify=self.verify)
        status = r.status_code
        if status == 200:
            self.logger.debug("Organization retrieved")
            return r.json()
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "The organization does not exist", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)
