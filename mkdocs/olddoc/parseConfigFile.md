<h1 id="ibmiotf.device.ParseConfigFile">ParseConfigFile</h1>

```python
ParseConfigFile(configFilePath)
```

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

__Example Configuration File__


device.yaml
```
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

