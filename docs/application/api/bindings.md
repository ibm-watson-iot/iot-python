# Service Bindings

Service bindings can be established with Cloudant and EventStreams, service bindings are required to allow the configuration of [data store connectors](dsc.md):

```python
import wiotp.sdk.application

options = wiotp.sdk.application.parseEnvVars()
appClient = wiotp.sdk.application.ApplicationClient(options)

serviceBinding = {
    "name": "test-cloudant", 
    "description": "Test Cloudant instance",
    "type": "cloudant", 
    "credentials": {
        "host": "hostname",
        "port": 443,
        "username": "username",
        "password": "password
    }
}

cloudantService = appClient.serviceBindings.create(serviceBinding)

serviceBinding = {
    "name": "test-eventstreams", 
    "description": "Test EventStreams instance",
    "type": "eventstreams", 
    "credentials": {
        "api_key": "myapikey",
        "user": "myusername,
        "password": "mypassword",
        "kafka_admin_url": "myurl",
        "kafka_brokers_sasl": [ "broker1", "broker2", "broker3", "broker4", "broker5" ]
    }
}

eventstreamsService = appClient.serviceBindings.create(serviceBinding)
```

Finding service bindings

```python
import wiotp.sdk.application

options = wiotp.sdk.application.parseEnvVars()
appClient = wiotp.sdk.application.ApplicationClient(options)

# Iterate through all service bindings
for s in appClient.serviceBindings:
    print(s.name)
    print(" - " + s.description)
    print(" - " + s.type)
    print()

print()

# Iterate through service bindings of type "cloudant"
for s in appClient.serviceBindings.find(typeFilter="cloudant"):
    print(s.name)
    print(" - " + s.description)
    print(" - " + s.type)
    print()
```
