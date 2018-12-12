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
import logging
import uuid

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

        if "domain" not in kwargs['options']:
            kwargs['options']['domain'] = "internetofthings.ibmcloud.com"
        
        if "logLevel" not in kwargs['options']:
            kwargs['options']['logLevel'] = logging.INFO

        if 'mqtt' not in kwargs['options']:
            kwargs['options']['mqtt'] = {}
        
        if "port" not in kwargs['options']['mqtt']:
            kwargs['options']['mqtt']['port'] = None
        
        if "transport" not in kwargs['options']['mqtt']:
            kwargs['options']['mqtt']['transport'] = 'tcp'

        if "sharedSubscription" not in kwargs['options']['mqtt']:
            kwargs['options']['mqtt']['sharedSubscription'] = False

        if "cleanStart" not in kwargs['options']['mqtt']:
            kwargs['options']['mqtt']['cleanStart'] = False

        if "sessionExpiry" not in kwargs['options']['mqtt']:
            kwargs['options']['mqtt']['sessionExpiry'] = 3600

        if "keepAlive" not in kwargs['options']['mqtt']:
            kwargs['options']['mqtt']['keepAlive'] = 60

        if "caFile" not in kwargs['options']['mqtt']:
            kwargs['options']['mqtt']['caFile'] = None

        if 'http' not in kwargs['options']:
            kwargs['options']['http'] = {}

        if "verify" not in kwargs['options']['http']:
            kwargs['options']['http']['verify'] = True

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
    def logLevel(self):
        return self["options"]["logLevel"]

    @property
    def port(self):
        return self["options"]["mqtt"]["port"]
    @property
    def transport(self):
        return self["options"]["mqtt"]["transport"]
    @property
    def cleanStart(self):
        return self["options"]["mqtt"]["cleanStart"]
    @property
    def sessionExpiry(self):
        return self["options"]["mqtt"]["sessionExpiry"]
    @property
    def keepAlive(self):
        return self["options"]["mqtt"]["keepAlive"]
    @property
    def sharedSubscription(self):
        return self["options"]["mqtt"]["sharedSubscription"]
    @property
    def caFile(self):
        return self["options"]["mqtt"]["caFile"]

    @property
    def verify(self):
        return self["options"]["http"]["verify"]


def ParseEnvVars():
    """
    Parse environment variables into a Python dictionary suitable for passing to the 
    device client constructor as the `options` parameter

    - `WIOTP_IDENTITY_APPID`
    - `WIOTP_AUTH_KEY`
    - `WIOTP_AUTH_TOKEN`
    - `WIOTP_OPTIONS_DOMAIN` (optional)
    - `WIOTP_OPTIONS_LOGLEVEL` (optional)
    - `WIOTP_OPTIONS_MQTT_PORT` (optional)
    - `WIOTP_OPTIONS_MQTT_TRANSPORT` (optional)
    - `WIOTP_OPTIONS_MQTT_CAFILE` (optional)
    - `WIOTP_OPTIONS_MQTT_CLEANSTART` (optional)
    - `WIOTP_OPTIONS_MQTT_SESSIONEXPIRY` (optional)
    - `WIOTP_OPTIONS_MQTT_KEEPALIVE` (optional)
    - `WIOTP_OPTIONS_MQTT_SHAREDSUBSCRIPTION` (optional)
    - `WIOTP_OPTIONS_HTTP_VERIFY` (optional)
    """

    # Auth
    authKey   = os.getenv("WIOTP_AUTH_KEY", None)
    authToken = os.getenv("WIOTP_AUTH_TOKEN", None)
    # Identity
    appId     = os.getenv("WIOTP_IDENTITY_APPID", str(uuid.uuid4()))
    # Options
    domain        = os.getenv("WIOTP_OPTIONS_DOMAIN", None)
    logLevel      = os.getenv("WIOTP_OPTIONS_LOGLEVEL", "info")
    port          = os.getenv("WIOTP_OPTIONS_MQTT_PORT", None)
    transport     = os.getenv("WIOTP_OPTIONS_MQTT_TRANSPORT", None)
    caFile        = os.getenv("WIOTP_OPTIONS_MQTT_CAFILE", None)
    cleanStart    = os.getenv("WIOTP_OPTIONS_MQTT_CLEANSTART", "True")
    sessionExpiry = os.getenv("WIOTP_OPTIONS_MQTT_SESSIONEXPIRY", "3600")
    keepAlive     = os.getenv("WIOTP_OPTIONS_MQTT_KEEPALIVE", "60")
    sharedSubs    = os.getenv("WIOTP_OPTIONS_MQTT_SHAREDSUBSCRIPTION", "False")
    verifyCert    = os.getenv("WIOTP_OPTIONS_HTTP_VERIFY", "True")
    
    if port is not None:
        try:
            port = int(port)
        except ValueError as e:
            raise ConfigurationException("WIOTP_PORT must be a number")

    try:
        sessionExpiry = int(sessionExpiry)
    except ValueError as e:
        raise ConfigurationException("WIOTP_OPTIONS_MQTT_SESSIONEXPIRY must be a number")
    
    try:
        keepAlive = int(keepAlive)
    except ValueError as e:
        raise ConfigurationException("WIOTP_OPTIONS_MQTT_KEEPAIVE must be a number")

    if logLevel not in ["error", "warning", "info", "debug"]:
        raise ConfigurationException("WIOTP_OPTIONS_LOGLEVEL must be one of error, warning, info, debug")  
    else:
        # Convert log levels from string to int (we need to upper case our strings from the config)
        logLevel = logging.getLevelName(logLevel.upper())
    
    cfg = {
        'identity': {
            'appId': appId
        },
        'options': {
            'domain': domain,
            'logLevel': logLevel,
            'mqtt': {
                'port': port,
                'transport': transport,
                'cleanStart': cleanStart in ["True", "true", "1"],
                'sessionExpiry': sessionExpiry,
                'keepAlive': keepAlive,
                'sharedSubscription': sharedSubs in ["True", "true", "1"],
                'caFile': caFile
            },
            "http": {
                "verify": verifyCert in ["True", "true", "1"]
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
      logLevel: error|warning|info|debug
      mqtt:
        port: 8883
        transport: tcp
        cleanStart: false
        sessionExpiry: 3600
        keepAlive: 60
        sharedSubscription: false
        caFile: /path/to/certificateAuthorityFile.pem
      http:
        verify: true    
    """
    
    try:
        with open(configFilePath) as f:
            data = yaml.load(f)
    except (OSError, IOError) as e:
        # In 3.3, IOError became an alias for OSError, and FileNotFoundError is a subclass of OSError
        reason = "Error reading device configuration file '%s' (%s)" % (configFilePath, e)
        raise ConfigurationException(reason)

    if "options" in data and "logLevel" in data["options"]:
        if data['options']['logLevel'] not in ["error", "warning", "info", "debug"]:
            raise ConfigurationException("Optional setting options.logLevel must be one of error, warning, info, debug")    
        else:
            # Convert log levels from string to int (we need to upper case our strings from the config)
            data['options']['logLevel'] = logging.getLevelName(data['options']['logLevel'].upper())
    
    return data
