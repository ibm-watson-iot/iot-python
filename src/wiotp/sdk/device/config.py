# *****************************************************************************
# Copyright (c) 2014, 2019 IBM Corporation and other Contributors.
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

from wiotp.sdk import ConfigurationException


class DeviceClientConfig(defaultdict):
    def __init__(self, **kwargs):
        # Validate the arguments
        if "identity" not in kwargs:
            raise ConfigurationException("Missing identity from configuration")
        if "orgId" not in kwargs["identity"] or kwargs["identity"]["orgId"] is None:
            raise ConfigurationException("Missing identity.orgId from configuration")
        if "typeId" not in kwargs["identity"] or kwargs["identity"]["typeId"] is None:
            raise ConfigurationException("Missing identity.typeId from configuration")
        if "deviceId" not in kwargs["identity"] or kwargs["identity"]["deviceId"] is None:
            raise ConfigurationException("Missing identity.deviceId from configuration")

        # Authentication is not supported for quickstart
        if kwargs["identity"]["orgId"] == "quickstart":
            if "auth" in kwargs:
                raise ConfigurationException("Quickstart service does not support device authentication")
        else:
            if "auth" not in kwargs:
                raise ConfigurationException("Missing auth from configuration")
            if "token" not in kwargs["auth"] or kwargs["auth"]["token"] is None:
                raise ConfigurationException("Missing auth.token from configuration")

        if "options" in kwargs and "mqtt" in kwargs["options"]:
            # validate port
            if "port" in kwargs["options"]["mqtt"] and kwargs["options"]["mqtt"]["port"] is not None:
                if not isinstance(kwargs["options"]["mqtt"]["port"], int):
                    raise ConfigurationException("Optional setting options.mqtt.port must be a number if provided")
            # Validate cleanStart
            if "cleanStart" in kwargs["options"]["mqtt"] and not isinstance(
                kwargs["options"]["mqtt"]["cleanStart"], bool
            ):
                raise ConfigurationException("Optional setting options.mqtt.cleanStart must be a boolean if provided")

        # Set defaults for optional configuration
        if "options" not in kwargs:
            kwargs["options"] = {}

        if "domain" not in kwargs["options"] or kwargs["options"]["domain"] is None:
            kwargs["options"]["domain"] = "internetofthings.ibmcloud.com"

        if "logLevel" not in kwargs["options"] or kwargs["options"]["logLevel"] is None:
            kwargs["options"]["logLevel"] = logging.INFO

        if "mqtt" not in kwargs["options"]:
            kwargs["options"]["mqtt"] = {}

        if "port" not in kwargs["options"]["mqtt"]:
            kwargs["options"]["mqtt"]["port"] = None

        if "transport" not in kwargs["options"]["mqtt"] or kwargs["options"]["mqtt"]["transport"] is None:
            kwargs["options"]["mqtt"]["transport"] = "tcp"

        if "cleanStart" not in kwargs["options"]["mqtt"]:
            kwargs["options"]["mqtt"]["cleanStart"] = False

        if "sessionExpiry" not in kwargs["options"]["mqtt"]:
            kwargs["options"]["mqtt"]["sessionExpiry"] = 3600

        if "keepAlive" not in kwargs["options"]["mqtt"]:
            kwargs["options"]["mqtt"]["keepAlive"] = 60

        if "caFile" not in kwargs["options"]["mqtt"]:
            kwargs["options"]["mqtt"]["caFile"] = None

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
    def caFile(self):
        return self["options"]["mqtt"]["caFile"]


def parseEnvVars():
    """
    Parse environment variables into a Python dictionary suitable for passing to the
    device client constructor as the `options` parameter

    - `WIOTP_IDENTITY_ORGID`
    - `WIOTP_IDENTITY_TYPEID`
    - `WIOTP_IDENTITY_DEVICEID`
    - `WIOTP_AUTH_TOKEN`
    - `WIOTP_OPTIONS_DOMAIN` (optional)
    - `WIOTP_OPTIONS_LOGLEVEL` (optional)
    - `WIOTP_OPTIONS_MQTT_PORT` (optional)
    - `WIOTP_OPTIONS_MQTT_TRANSPORT` (optional)
    - `WIOTP_OPTIONS_MQTT_CAFILE` (optional)
    - `WIOTP_OPTIONS_MQTT_CLEANSTART` (optional)
    - `WIOTP_OPTIONS_MQTT_SESSIONEXPIRY` (optional)
    - `WIOTP_OPTIONS_MQTT_KEEPALIVE` (optional)
    """

    # Identify
    orgId = os.getenv("WIOTP_IDENTITY_ORGID", None)
    typeId = os.getenv("WIOTP_IDENTITY_TYPEID", None)
    deviceId = os.getenv("WIOTP_IDENTITY_DEVICEID", None)
    # Auth
    authToken = os.getenv("WIOTP_AUTH_TOKEN", None)
    # Options
    domain = os.getenv("WIOTP_OPTIONS_DOMAIN", None)
    logLevel = os.getenv("WIOTP_OPTIONS_LOGLEVEL", "info")
    port = os.getenv("WIOTP_OPTIONS_MQTT_PORT", None)
    transport = os.getenv("WIOTP_OPTIONS_MQTT_TRANSPORT", None)
    caFile = os.getenv("WIOTP_OPTIONS_MQTT_CAFILE", None)
    cleanStart = os.getenv("WIOTP_OPTIONS_MQTT_CLEANSTART", "False")
    sessionExpiry = os.getenv("WIOTP_OPTIONS_MQTT_SESSIONEXPIRY", "3600")
    keepAlive = os.getenv("WIOTP_OPTIONS_MQTT_KEEPALIVE", "60")
    caFile = os.getenv("WIOTP_OPTIONS_MQTT_CAFILE", None)

    if orgId is None:
        raise ConfigurationException("Missing WIOTP_IDENTITY_ORGID environment variable")
    if typeId is None:
        raise ConfigurationException("Missing WIOTP_IDENTITY_TYPEID environment variable")
    if deviceId is None:
        raise ConfigurationException("Missing WIOTP_IDENTITY_DEVICEID environment variable")
    if orgId != "quickstart" and authToken is None:
        raise ConfigurationException("Missing WIOTP_AUTH_TOKEN environment variable")
    if port is not None:
        try:
            port = int(port)
        except ValueError as e:
            raise ConfigurationException("WIOTP_OPTIONS_MQTT_PORT must be a number")

    try:
        sessionExpiry = int(sessionExpiry)
    except ValueError as e:
        raise ConfigurationException("WIOTP_OPTIONS_MQTT_SESSIONEXPIRY must be a number")

    try:
        keepAlive = int(keepAlive)
    except ValueError as e:
        raise ConfigurationException("WIOTP_OPTIONS_MQTT_KEEPALIVE must be a number")

    if logLevel not in ["error", "warning", "info", "debug"]:
        raise ConfigurationException("WIOTP_OPTIONS_LOGLEVEL must be one of error, warning, info, debug")
    else:
        # Convert log levels from string to int (we need to upper case our strings from the config)
        logLevel = logging.getLevelName(logLevel.upper())

    cfg = {
        "identity": {"orgId": orgId, "typeId": typeId, "deviceId": deviceId},
        "options": {
            "domain": domain,
            "logLevel": logLevel,
            "mqtt": {
                "port": port,
                "transport": transport,
                "caFile": caFile,
                "cleanStart": cleanStart in ["True", "true", "1"],
                "sessionExpiry": sessionExpiry,
                "keepAlive": keepAlive,
            },
        },
    }

    # Quickstart doesn't support auth, so ensure we only add this if it's defined
    if authToken is not None:
        cfg["auth"] = {"token": authToken}

    return DeviceClientConfig(**cfg)


def parseConfigFile(configFilePath):
    """
    Parse a yaml configuration file into a Python dictionary suitable for passing to the
    device client constructor as the `options` parameter

    # Example Configuration File

    identity:
      orgId: org1id
      typeId: raspberry-pi-3
      deviceId: 00ef08ac05
    auth:
      token: Ab$76s)asj8_s5
    options:
      domain: internetofthings.ibmcloud.com
      logLevel: error|warning|info|debug
      mqtt:
        port: 8883
        transport: tcp
        cleanStart: true
        sessionExpiry: 3600
        keepAlive: 60
        caFile: /path/to/certificateAuthorityFile.pem

    """

    try:
        with open(configFilePath) as f:
            data = yaml.full_load(f)
    except (OSError, IOError) as e:
        # In 3.3, IOError became an alias for OSError, and FileNotFoundError is a subclass of OSError
        reason = "Error reading device configuration file '%s' (%s)" % (configFilePath, e)
        raise ConfigurationException(reason)

    if "options" in data and "logLevel" in data["options"]:
        if data["options"]["logLevel"] not in ["error", "warning", "info", "debug"]:
            raise ConfigurationException("Optional setting options.logLevel must be one of error, warning, info, debug")
        else:
            # Convert log levels from string to int (we need to upper case our strings from the config)
            data["options"]["logLevel"] = logging.getLevelName(data["options"]["logLevel"].upper())

    return DeviceClientConfig(**data)
