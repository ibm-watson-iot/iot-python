# Application SDK

The `wiotp.sdk.application` package contains the following:

The client implementations:

- `wiotp.sdk.application.ApplicationClient`

Support classes for working with the data model:

- `wiotp.sdk.application.Command`
- `wiotp.sdk.application.Event`
- `wiotp.sdk.application.Status`

Support methods for handling device configuration:

- `wiotp.sdk.application.parseConfigFile`
- `wiotp.sdk.application.parseEnvVars`


## Configuration

Application configuration is passed to the client via the `config` parameter when you create the client instance.  See the [configure applications](config.md) section for full details of all available options, and the built-in support for YAML file and environment variable sourced configuration.

```python
myConfig = { 
    "auth" {
        "key": "a-org1id-y67si9et"
        "token": "Ab$76s)asj8_s5"
    }
}
client = wiotp.sdk.application.ApplicationClient(config=myConfig)
```


## Connectivity

`connect()` & `disconnect()` methods are used to manage the MQTT connection to IBM Watson IoT Platform that allows the application to 
handle commands and device events.

Applications have three flavours of real-time data to work with once they have established an MQTT connection, for more information on each of these subjects see the relavent section of the documentation:

- [Device Events](mqtt/events.md)
- [Device Commands](mqtt/commands.md)
- [Device Status Updates](mqtt/status.md)
