<h1 id="ibmiotf.device.parseConfigFile">parseConfigFile</h1>

```python
parseConfigFile(configFilePath)
```

Parse a configuration file into a Python dictionary suitable for passing to the
device client constructor as the `options` parameter

Note: Support for this is likely to be removed in favour of
a yaml configuration configuration file as move towards the 1.0 release

```
import ibmiotf.device

try:
    options = ibmiotf.device.ParseConfigFile(configFilePath)
    client = ibmiotf.device.Client(options)
except ibmiotf.ConnectionException  as e:
    pass

```

__Example Configuration File__


```
[device]
org=org1id
type=raspberry-pi-3
id=00ef08ac05
auth-method=token
auth-token=Ab$76s)asj8_s5
clean-session=true/false
domain=internetofthings.ibmcloud.com
port=8883
```

**Required Settings**

- `org`
- `type`
- `id`
- `auth-method`
- `auth-token`

**Optional Settings**

- `clean-session` Defaults to `false`
- `domain` Defaults to `internetofthings.ibmcloud.com`
- `port` Defaults to `8883`

