import uuid
from ibmiotf import ConfigurationException



# *****************************************************************************
# Copyright (c) 2014, 2018 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

from collections import defaultdict
import os
import yaml

from ibmiotf import ConfigurationException

class ApplicationClientConfig(defaultdict):
    def __init__(self, **kwargs):
        # Note: Authentication is not supported for quickstart
        if 'auth' in kwargs:
            if 'key' not in kwargs['auth'] or kwargs['auth']['key'] is None:
                raise ConfigurationException("Missing auth.key from configuration")
            if 'token' not in kwargs['auth'] or kwargs['auth']['token'] is None:
                raise ConfigurationException("Missing auth.token from configuration")
        
        if 'options' in kwargs and 'mqtt' in kwargs['options']:
            if 'port' in kwargs['options']['mqtt'] and kwargs['options']['mqtt']['port'] is not None:
                if not isinstance(kwargs['options']['mqtt']['port'], int):
                    raise ConfigurationException("Optional setting options.port must be a number if provided")
            if 'cleanSession' in kwargs['options']['mqtt'] and not isinstance(kwargs['options']['mqtt']['cleanSession'], bool):
                raise ConfigurationException("Optional setting options.cleanSession must be a boolean if provided")
        
        # Set defaults for optional configuration
        if 'identity' not in kwargs:
            kwargs['identity'] = {}

        if 'appId' not in kwargs['identity']:
            kwargs['identity']['appId'] = str(uuid.uuid4())

        if 'options' not in kwargs:
            kwargs['options'] = {}

        if 'mqtt' not in kwargs['options']:
            kwargs['options']['mqtt'] = {}
        
        if "domain" not in kwargs['options']:
            kwargs['options']['domain'] = "internetofthings.ibmcloud.com"
        
        if "cleanSession" not in kwargs['options']['mqtt']:
            kwargs['options']['mqtt']['cleanSession'] = True

        if "port" not in kwargs['options']['mqtt']:
            # None allows the underlying MQTT client to auto-select the port
            kwargs['options']['mqtt']['port'] = None
        
        if "transport" not in kwargs['options']['mqtt']:
            kwargs['options']['mqtt']['transport'] = 'tcp'

        if "sharedSubscription" not in kwargs['options']['mqtt']:
            kwargs['options']['mqtt']['sharedSubscription'] = False

        if 'http' not in kwargs['options']:
            kwargs['options']['http'] = {}

        if "verifyCertificate" not in kwargs['options']['http']:
            kwargs['options']['http']['verifyCertificate'] = True

        dict.__init__(self, **kwargs)
    

    def isQuickstart(self):
        return self.orgId == "quickstart"

    @property
    def orgId(self):
        # Get the orgId from the apikey (format: a-orgid-randomness)
        return self.apiKey.split("-")[1] if (self.apiKey is not None) else "quickstart"
    @property
    def appId(self):
        return self["identity"]["appId"]
    @property
    def clientId(self):
        clientIdPrefix = "A" if (self.sharedSubscription is True) else "a"
        return "%s:%s:%s" % (clientIdPrefix, self.orgId, self.appId) 
    
    @property
    def apiKey(self):
        return self["auth"]["key"] if ("auth" in self) else None
    @property
    def apiToken(self):
        return self["auth"]["token"] if ("auth" in self) else None
    
    @property
    def username(self):
        return self.apiKey
    @property
    def password(self):
        return self.apiToken

    @property
    def credentials(self):
        return (self.apiKey, self.apiToken)


    @property
    def domain(self):
        return self["options"]["domain"]
    @property
    def host(self):
        return self.orgId + "." + self.domain

    @property
    def port(self):
        return self["options"]["mqtt"]["port"]
    @property
    def transport(self):
        return self["options"]["mqtt"]["transport"]
    @property
    def cleanSession(self):
        return self["options"]["mqtt"]["cleanSession"]
    @property
    def sharedSubscription(self):
        return self["options"]["mqtt"]["sharedSubscription"]
    @property
    def caFile(self):
        return self["options"]["mqtt"]["caFile"]

    @property
    def verifyCertificate(self):
        return self["options"]["http"]["verifyCertificate"]

    @property
    def verify(self):
        # Alias for self.verifyCertificate
        return self.verifyCertificate


def ParseEnvVars():
    """
    Parse environment variables into a Python dictionary suitable for passing to the 
    device client constructor as the `options` parameter

    - `WIOTP_APP_ID`
    - `WIOTP_API_KEY`
    - `WIOTP_API_TOKEN`
    - `WIOTP_DOMAIN` (optional)
    - `WIOTP_MQTT_PORT` (optional)
    - `WIOTP_MQTT_TRANSPORT` (optional)
    - `WIOTP_MQTT_CAFILE` (optional)
    - `WIOTP_MQTT_CLEANSESSION` (optional)
    - `WIOTP_HTTP_VERIFYCERT` (optional)
    """

    # Auth
    authKey   = os.getenv("WIOTP_API_KEY", None)
    authToken = os.getenv("WIOTP_API_TOKEN", None)
    # Identity
    appId    = os.getenv("WIOTP_TYPE_ID", str(uuid.uuid4()))
    # Options
    domain    = os.getenv("WIOTP_DOMAIN", None)
    port      = os.getenv("WIOTP_MQTT_PORT", None)
    transport = os.getenv("WIOTP_MQTT_TRANSPORT", None)
    caFile    = os.getenv("WIOTP_MQTT_CAFILE", None)
    sharedSubs   = os.getenv("WIOTP_MQTT_SHAREDSUBS", "False")
    cleanSession = os.getenv("WIOTP_MQTT_CLEANSESSION", "True")
    verifyCert = os.getenv("WIOTP_HTTP_VERIFYCERT", "True")
    
    if port is not None:
        try:
            port = int(port)
        except ValueError as e:
            raise ConfigurationException("Missing WIOTP_PORT must be a number")

    cfg = {
        'identity': {
            'appId': appId
        },
        'options': {
            'domain': domain,
            'mqtt': {
                'port': port,
                'transport': transport,
                'caFile': caFile,
                'sharedSubscription': sharedSubs in ["True", "true", "1"],
                'cleanSession': cleanSession in ["True", "true", "1"]
            },
            "http": {
                "verifyCertificate": verifyCert in ["True", "true", "1"]
            }
        }
    }

    # Quickstart doesn't support auth, so ensure we only add this if it's defined
    if authToken is not None:
        cfg['auth'] = { 'key': authKey, 'token': authToken }
    
    return cfg


def ParseConfigFile(configFilePath):
    """
    Parse a yaml configuration file into a Python dictionary suitable for passing to the 
    device client constructor as the `options` parameter
    
    # Example Configuration File
    
    identity:
      appId: myApp
    auth:
      key: a-23gh56-sdsdajhjnee
      token: Ab$76s)asj8_s5
    options:
      domain: internetofthings.ibmcloud.com
      mqtt:
        port: 8883
        transport: tcp
        cleanSession: true
        sharedSubscription: false
        caFile: /path/to/certificateAuthorityFile.pem
      http:
        verifyCertificate: True    
    """
    
    try:
        with open(configFilePath) as f:
            data = yaml.load(f)
    # In 3.3, IOError became an alias for OSError, and FileNotFoundError is a subclass of OSError
    except (OSError, IOError) as e:
        reason = "Error reading device configuration file '%s' (%s)" % (configFilePath, e)
        raise ConfigurationException(reason)

    return data
