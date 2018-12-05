<h1 id="ibmiotf.device.ParseEnvVars">ParseEnvVars</h1>

```python
ParseEnvVars()
```

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

