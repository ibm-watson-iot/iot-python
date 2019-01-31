# Data Store Connectors

- You can have multiple connectors (up to 10, depending on your service plan) of mixed types (cloudant/eventstreams). This means 6 combined, not 6 of each.
- Each connector can have multiple destinations and forwarding rules defined (up to 100 of each, depending on your service plan) 
- Each forwarding rule can only route to a single destination, but multiple rules can reference the same destination

!!! warning
    Don't use this yet, there is a bug in the DSC API paging code, that this client library exposed which would result in an infinite loop in your code if you use the `dsc`, or `dsc[connectorId].rules` iterators

```python
import wiotp.sdk.application

options = wiotp.sdk.application.parseEnvVars()
appClient = wiotp.sdk.application.ApplicationClient(options)

serviceBinding = {
    "name": "test-cloudant",  "description": "Test Cloudant instance", "type": "cloudant", 
    "credentials": { "host": "hostname", "port": 443, "username": "username", "password": "password" }
}

cloudantService = appClient.serviceBindings.create(serviceBinding)

# Create the connector
connector = self.appClient.dsc.create(
    name="connector1", serviceId=createdService.id, timezone="UTC", description="A test connector", enabled=True
)

# Create a destination under the connector
destination1 = createdConnector.destinations.create(name="all-data", bucketInterval="DAY")

# Create a rule under the connector, that routes all events to the destination
rule1 = createdConnector.rules.createEventRule(
    name="allevents", destinationName=destination1.name, description="Send all events", enabled=True, typeId="*", eventId="*"
)
# Create a second rule under the connector, that routes all state to the same destination
rule2 = createdConnector.rules.createStateRule(
    name="allstate", destinationName=destination1.name, description="Send all state", enabled=True, logicalInterfaceId="*"
)
```


## Service Bindings

Service bindings can be established with Cloudant and EventStreams:

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


## Connectors

```python
import wiotp.sdk.application

options = wiotp.sdk.application.parseEnvVars()
appClient = wiotp.sdk.application.ApplicationClient(options)

# Create the connector
serviceId = "xxx"
connector = appClient.dsc.create(
    name="test-connector-cloudant", serviceId=serviceId, timezone="UTC", description="A test connector", enabled=True
)

print(" - " + connector.name)
print(" - " + connector.connectorType)
print(" - Enabled: " + connector.enabled)
```


## Destinations

```python
import wiotp.sdk.application

options = wiotp.sdk.application.parseEnvVars()
appClient = wiotp.sdk.application.ApplicationClient(options)

connectorId = "xxx"
connector = appClient.dsc[connectorId]

# Create a destination under the connector
destination1 = connector.destinations.create(name=destinationName, bucketInterval="DAY")

```

!!! tip
    Destinations are immutable.  If you want to change where you send events to:
    
    - Create a new destination
    - Update the forwarding rule to reference the new destination
    - Delete the old destination


## Forwarding Rules

```python
import wiotp.sdk.application

options = wiotp.sdk.application.parseEnvVars()
appClient = wiotp.sdk.application.ApplicationClient(options)

# Note: This code assumes a destination named "all-data" has already been created under this connector
connectorId = "xxx"
connector = appClient.dsc[connectorId]

# Create a rule under the connector, that routes all events to the destination
rule1 = connector.rules.createEventRule(
    name="allevents", 
    destinationName="all-data", 
    description="Send all events", 
    enabled=True, 
    typeId="*", 
    eventId="*"
)

# Create a second rule under the connector, that routes all state to the same destination
rule2 = createdConnector.rules.createStateRule(
    name="allstate", 
    destinationName="all-data", 
    description="Send all state", 
    enabled=True, 
    logicalInterfaceId="*"
)
```

!!! tip
    Two different rules can forward to the same destination, but if you want to forward the same content to two different destinations you would create two forwarding rules with the same configuration, each referencing a different destination.


