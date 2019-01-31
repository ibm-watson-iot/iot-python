# Data Store Connectors

Data store connectors can only be configured after you have set up one or more [service bindings](bindings.md):


!!! warning
    Don't use the dsc package yet, there is a bug in the DSC API paging code, that this client library exposed which would result in an infinite loop in your code if you use the `dsc`, or `dsc[connectorId].rules` iterators


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


## Connectors

!!! tip
    You can have multiple connectors (up to 10, depending on your service plan) of mixed types (Cloudant or EventStreams). This means 10 combined, not 10 of each.

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

Each connector can have multiple destinations defined (up to 100 depending on your service plan) 

!!! tip
    Destinations are immutable.  If you want to change where you send events to:
    
    - Create a new destination
    - Update the forwarding rule to reference the new destination
    - Delete the old destination


```python
import wiotp.sdk.application

options = wiotp.sdk.application.parseEnvVars()
appClient = wiotp.sdk.application.ApplicationClient(options)

connectorId = "xxx"
connector = appClient.dsc[connectorId]

# Create a destination under the connector
destination1 = connector.destinations.create(name=destinationName, bucketInterval="DAY")

```


## Forwarding Rules

Forwarding rules configure what kind of data and the scope of the data that is sent to a destination.  Each connector can have multiple forwarding rules defined (up to 100 depending on your service plan) 

!!! tip
    Each forwarding rule can only route to a single destination, but multiple rules can reference the same destination


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
