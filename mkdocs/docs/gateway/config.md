# Gateway Configuration

Gateway configuration can be broken down into required and optional configuration:

## Required Configuration
- `identity.orgId` Your organization ID.
- `identity.typeId` The type of the device. Think of the device type is analagous to a model number.
- `identity.deviceId` A unique ID to identify a device. Think of the device id as analagous to a serial number.
- `auth.token` An authentication token to securely connect your device to Watson IoT Platform.

## Optional Configuration
- `options.domain` A boolean value indicating which Watson IoT Platform domain to connect to (e.g. if you have a dedicated platform instance). Defaults to `internetofthings.ibmcloud.com`
- `options.logLevel` Controls the level of logging in the client, can be set to `error`, `warning`, `info`, or `debug`.  Defaults to `info`.
- `options.mqtt.port` A integer value defining the MQTT port.  Defaults to auto-negotiation.
- `options.mqtt.transport` The transport to use for MQTT connectivity - `tcp` or `websockets`.
- `options.mqtt.cleanStart` A boolean value indicating whether to discard any previous state when reconnecting to the service.  Defaults to `False`.
- `options.mqtt.sessionExpiry` When cleanStart is disabled, defines the maximum age of the previous session (in seconds).  Defaults to `False`.
- `options.mqtt.keepAlive` Control the frequency of MQTT keep alive packets (in seconds).  Details to `60`.
- `options.mqtt.caFile` A String value indicating the path to a CA file (in pem format) to use in verifying the server certificate.  Defaults to `messaging.pem` inside this module.


The config parameter when constructing an instance of `wiotp.sdk.gateway.GatewayClient` expects to be passed a dictionary containing this configuration:

```python
myConfig = { 
    "identity": {
        "orgId": "org1id",
        "typeId": "raspberry-pi-3"
        "deviceId": "00ef08ac05"
    }.
    "auth" {
        "token": "Ab$76s)asj8_s5"
    },
    "options": {
        "domain": "internetofthings.ibmcloud.com",
        "logLevel": "error|warning|info|debug",
        "mqtt": {
            "port": 8883,
            "transport": "tcp|websockets",
            "cleanStart": True|False,
            "sessionExpiry": 3600,
            "keepAlive": 60,
            "caFile": "/path/to/certificateAuthorityFile.pem"
        }
    }
}
client = wiotp.sdk.gateway.GatewayClient(config=myConfig, logHandlers=None)
```

In most cases you will not manually build the `config` dictionary.  Two helper methods are provided to make configuration simple:


## YAML File Support

`wiotp.sdk.gateway.parseConfigFile()` allows one to easily pass in gateway configuration from environment variables.

```python
import wiotp.gateway.sdk

myConfig = wiotp.sdk.device.parseConfigFile("gateway.yaml")
client = ibmiotf.gateway.Client(config=myConfig, logHandlers=None)
```

### Minimal Required Configuration File

```yaml
identity:
    orgId: org1id
    typeId: raspberry-pi
    deviceId: 00ef08ac05
auth:
    token: Ab$76s)asj8_s5
```

### Complete Configuration File

This file defines all optional configuration parameters.

```yaml
identity:
    orgId: org1id
    typeId: raspberry-pi
    deviceId: 00ef08ac05
auth:
    token: Ab$76s)asj8_s5
options:
    domain: internetofthings.ibmcloud.com
    logLevel: debug
    mqtt:
        port: 8883
        transport: tcp
        cleanStart: true
        sessionExpiry: 7200
        keepAlive: 120
        caFile: /path/to/certificateAuthorityFile.pem
```


## Environment Variable Support

`wiotp.sdk.gateway.parseEnvVars()` allows one to easily pass in gateway configuration from environment variables.

```python
import wiotp.sdk.gateway

myConfig = wiotp.sdk.gateway.parseEnvVars()
client = wiopt.sdk.gateway.Client(config=myConfig, logHandlers=None)
```

### Minimal Required Environment Variables
- `WIOTP_IDENTITY_ORGID`
- `WIOTP_IDENTITY_TYPEID`
- `WIOTP_IDENTITY_DEVICEID`
- `WIOTP_AUTH_TOKEN`

### Optional Additional Environment Variables
- `WIOTP_OPTIONS_DOMAIN`
- `WIOTP_OPTIONS_LOGLEVEL`
- `WIOTP_OPTIONS_MQTT_PORT`
- `WIOTP_OPTIONS_MQTT_TRANSPORT`
- `WIOTP_OPTIONS_MQTT_CAFILE`
- `WIOTP_OPTIONS_MQTT_CLEANSTART`
- `WIOTP_OPTIONS_MQTT_SESSIONEXPIRY`
- `WIOTP_OPTIONS_MQTT_KEEPALIVE`

