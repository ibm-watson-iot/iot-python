# Application Configuration

Application configuration can be broken down into required and optional configuration:

## Required Configuration
- `identity.appId` Your unique application ID.
- `auth.key` An API key authentication token to securely connect your application to Watson IoT Platform.
- `auth.token` The authentication token for the API key you are using.

## Optional Configuration
- `options.domain` A boolean value indicating which Watson IoT Platform domain to connect to (e.g. if you have a dedicated platform instance). Defaults to `internetofthings.ibmcloud.com`
- `options.logLevel` Controls the level of logging in the client, can be set to `error`, `warning`, `info`, or `debug`.  Defaults to `info`.
- `options.http.verify` Allows HTTP certificate verification to be disabled if set to `False`.  You are strongly discouraged from using this in any production usage, this primarily exists as a development aid.  Defaults to `True`
- `options.mqtt.instanceId` Optional instance ID, use if you wish create a multi-instance application which will loadbalance incoming messages.
- `options.mqtt.port` A integer value defining the MQTT port.  Defaults to auto-negotiation.
- `options.mqtt.transport` The transport to use for MQTT connectivity - `tcp` or `websockets`.
- `options.mqtt.cleanStart` A boolean value indicating whether to discard any previous state when reconnecting to the service.  Defaults to `False`.
- `options.mqtt.sessionExpiry` When cleanStart is disabled, defines the maximum age of the previous session (in seconds).  Defaults to `False`.
- `options.mqtt.keepAlive` Control the frequency of MQTT keep alive packets (in seconds).  Details to `60`.
- `options.mqtt.caFile` A String value indicating the path to a CA file (in pem format) to use in verifying the server certificate.  Defaults to `messaging.pem` inside this module.


The config parameter when constructing an instance of `wiotp.sdk.application.ApplicationClient` expects to be passed a dictionary containing this configuration:

```python
myConfig = { 
    "identity": {
        "appId": "app1"
    }.
    "auth" {
        "key": "orgid-h798S783DK"
        "token": "Ab$76s)asj8_s5"
    },
    "options": {
        "domain": "internetofthings.ibmcloud.com",
        "logLevel": "error|warning|info|debug",
        "http": {
            "verify": True|False
        },
        "mqtt": {
            "instanceId": "instance1",
            "port": 8883,
            "transport": "tcp|websockets",
            "cleanStart": True|False,
            "sessionExpiry": 3600,
            "keepAlive": 60,
            "caFile": "/path/to/certificateAuthorityFile.pem"
        }
    }
}
client = wiotp.sdk.application.ApplicationClient(config=myConfig, logHandlers=None)
```

In most cases you will not manually build the `config` dictionary.  Two helper methods are provided to make configuration simple:


## YAML File Support

`wiotp.sdk.application.parseConfigFile()` allows one to easily pass in application configuration from environment variables.

```python
import wiotp.sdk.application

myConfig = wiotp.sdk.application.parseConfigFile("application.yaml")
client = wiotp.sdk.application.ApplicationClient(config=myConfig, logHandlers=None)
```

### Minimal Required Configuration File

```yaml
identity:
    appId: app1
auth:
    key: orgid-h798S783DK
    token: Ab$76s)asj8_s5
```

### Complete Configuration File

This file defines all optional configuration parameters.

```yaml
identity:
    appId: app1
auth:
    key: orgid-h798S783DK
    token: Ab$76s)asj8_s5
options:
    domain: internetofthings.ibmcloud.com
    logLevel: debug
    http:
        verify: True
    mqtt:
        instanceId: instance1
        port: 8883
        transport: tcp
        cleanStart: true
        sessionExpiry: 7200
        keepAlive: 120
        caFile: /path/to/certificateAuthorityFile.pem
```


## Environment Variable Support

`wiotp.sdk.application.parseEnvVars()` allows one to easily pass in device configuration from environment variables.

```python
import wiotp.sdk.application

myConfig = wiotp.sdk.application.parseEnvVars()
client = wiotp.sdk.application.ApplicationClient(config=myConfig, logHandlers=None)
```

### Minimal Required Environment Variables
- `WIOTP_IDENTITY_APPID`
- `WIOTP_AUTH_TOKEN`
- `WIOTP_AUTH_KEY`

### Optional Additional Environment Variables
- `WIOTP_OPTIONS_DOMAIN`
- `WIOTP_OPTIONS_LOGLEVEL`
- `WIOTP_OPTIONS_HTTP_VERIFY`
- `WIOTP_OPTIONS_MQTT_INSTANCEID`
- `WIOTP_OPTIONS_MQTT_PORT`
- `WIOTP_OPTIONS_MQTT_TRANSPORT`
- `WIOTP_OPTIONS_MQTT_CAFILE`
- `WIOTP_OPTIONS_MQTT_CLEANSTART`
- `WIOTP_OPTIONS_MQTT_SESSIONEXPIRY`
- `WIOTP_OPTIONS_MQTT_KEEPALIVE`
