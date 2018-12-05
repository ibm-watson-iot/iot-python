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

class DeviceClientConfig(defaultdict):
    def __init__(self, **kwargs):
        # Validate the arguments
        if 'identity' not in kwargs:
            raise ConfigurationException("Missing identity from configuration")
        if 'orgId' not in kwargs['identity'] or kwargs['identity']['orgId'] is None:
            raise ConfigurationException("Missing identity.orgId from configuration")
        if 'typeId' not in kwargs['identity'] or kwargs['identity']['typeId'] is None:
            raise ConfigurationException("Missing identity.typeId from configuration")
        if 'deviceId' not in kwargs['identity'] or kwargs['identity']['deviceId'] is None:
            raise ConfigurationException("Missing identity.deviceId from configuration")
        
        # Authentication is not supported for quickstart
        if kwargs['identity']['orgId'] is "quickstart":
            if 'auth' in kwargs:
                raise ConfigurationException("Quickstart service does not support device authentication")
        else:
            if 'auth' not in kwargs:
                raise ConfigurationException("Missing auth from configuration")
            if 'token' not in kwargs['auth'] or kwargs['auth']['token'] is None:
                raise ConfigurationException("Missing auth.token from configuration")
        
        if 'options' in kwargs and 'mqtt' in kwargs['options']:
            if 'port' in kwargs['options']['mqtt'] and kwargs['options']['mqtt']['port'] is not None:
                if not isinstance(kwargs['options']['mqtt']['port'], int):
                    raise ConfigurationException("Optional setting options.port must be a number if provided")
            if 'cleanSession' in kwargs['options']['mqtt'] and not isinstance(kwargs['options']['mqtt']['cleanSession'], bool):
                raise ConfigurationException("Optional setting options.cleanSession must be a boolean if provided")
        
        # Set defaults for optional configuration
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
        
        dict.__init__(self, **kwargs)
    
    def isQuickstart(self):
        return self["identity"]["orgId"] == "quickstart"

    @property
    def orgId(self):
        return self["identity"]["orgId"]
    @property
    def typeId(self):
        return self["identity"]["typeId"]
    @property
    def deviceId(self):
        return self["identity"]["deviceId"]
    @property
    def clientId(self):
        return "d:%s:%s:%s" % (self["identity"]["orgId"], self["identity"]["typeId"], self["identity"]["deviceId"]) 
    
    @property
    def username(self):
        return "use-token-auth" if ("auth" in self) else None
    @property
    def password(self):
        return self["auth"]["token"] if ("auth" in self) else None
            
    @property
    def domain(self):
        return self["options"]["domain"]

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
    def caFile(self):
        return self["options"]["mqtt"]["caFile"]


def ParseEnvVars():
    """
    Parse environment variables into a Python dictionary suitable for passing to the 
    device client constructor as the `options` parameter

    **Identity**
    - `WIOTP_ORG_ID`
    - `WIOTP_TYPE_ID`
    - `WIOTP_DEVICE_ID`
    
    **Auth**
    - `WIOTP_AUTH_TOKEN`
    
    **Advanced Options**
    - `WIOTP_DOMAIN` (optional)
    - `WIOTP_MQTT_PORT` (optional)
    - `WIOTP_MQTT_TRANSPORT` (optional)
    - `WIOTP_MQTT_CAFILE` (optional)
    - `WIOTP_MQTT_CLEANSESSION` (optional)


    ```python
    import ibmiotf.device
    
    try:
        options = ibmiotf.device.ParseEnvVars()
        client = ibmiotf.device.Client(options)
    except ibmiotf.ConnectionException  as e:
        pass
        
    ```
    """

    # Identify
    orgId     = os.getenv("WIOTP_ORG_ID", None)
    typeId    = os.getenv("WIOTP_TYPE_ID", None)
    deviceId  = os.getenv("WIOTP_DEVICE_ID", None)
    # Auth
    authToken = os.getenv("WIOTP_AUTH_TOKEN", None)
    # Options
    domain    = os.getenv("WIOTP_DOMAIN", None)
    port      = os.getenv("WIOTP_MQTT_PORT", None)
    transport = os.getenv("WIOTP_MQTT_TRANSPORT", None)
    caFile    = os.getenv("WIOTP_MQTT_CAFILE", None)
    cleanSession = os.getenv("WIOTP_MQTT_CLEANSESSION", "True")
    
    if orgId is None:
        raise ConfigurationException("Missing WIOTP_ORG_ID environment variable")
    if typeId is None:
        raise ConfigurationException("Missing WIOTP_TYPE_ID environment variable")
    if deviceId is None:
        raise ConfigurationException("Missing WIOTP_DEVICE_ID environment variable")
    if orgId is not "quickstart" and authToken is None:
        raise ConfigurationException("Missing WIOTP_AUTH_TOKEN environment variable")
    if port is not None:
        try:
            port = int(port)
        except ValueError as e:
            raise ConfigurationException("Missing WIOTP_PORT must be a number")

    cfg = {
        'identity': {
            'orgId': orgId,
            'typeId': typeId,
            'deviceId': deviceId
        },
        'options': {
            'domain': domain,
            'mqtt': {
                'port': port,
                'transport': transport,
                'caFile': caFile,
                'clean-session': cleanSession in ["True", "true", "1"]
            }
        }
    }

    # Quickstart doesn't support auth, so ensure we only add this if it's defined
    if authToken is not None:
        cfg['auth'] = { 'token': authToken }
    
    return cfg


def ParseConfigFile(configFilePath):
    """
    Parse a yaml configuration file into a Python dictionary suitable for passing to the 
    device client constructor as the `options` parameter
    
    ```python
    import ibmiotf.device
    
    try:
        options = ibmiotf.device.ParseConfigFile(configFilePath)
        client = ibmiotf.device.Client(options)
    except ibmiotf.ConnectionException  as e:
        pass
        
    ```
    
    # Example Configuration File
    
    ```yaml
    identity:
      orgId: org1id
      typeId: raspberry-pi-3
      deviceId: 00ef08ac05
    auth:
      token: Ab$76s)asj8_s5
    options:
      domain: internetofthings.ibmcloud.com
      mqtt:
        port: 8883
        transport: tcp
        cleanSession: true
        caFile: /path/to/certificateAuthorityFile.pem
    ```
    
    **Advanced Options**
    
    - `options.domain` Defaults to `internetofthings.ibmcloud.com`
    - `options.mqtt.port` Defaults to `8883`    
    - `options.mqtt.transport` Defaults to `tcp`    
    - `options.mqtt.caFile` Defaults to `messaging.pem` inside this module    
    - `options.mqtt.cleanSession` Defaults to `false`
    """
    
    try:
        with open(configFilePath) as f:
            data = yaml.load(f)
    except IOError as e:
        reason = "Error reading device configuration file '%s' (%s)" % (configFilePath, e[1])
        raise ConfigurationException(reason)

    return data
