# Data Store Connectors

Data store connectors can only be configured after you have set up one or more [service bindings](bindings.md):

## Cloudant Connector

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
        "password": "password"
    }
}

cloudantService = appClient.serviceBindings.create(serviceBinding)

# Create the connector
connector = self.appClient.dsc.create(
    name="connector1", type="cloudant", serviceId=cloudantService.id, timezone="UTC",
    description="A test connector", enabled=True
)

# Create a destination under the connector
destination1 = connector.destinations.create(name="all-data", bucketInterval="DAY")

# Create a rule under the connector, that routes all events to the destination
rule1 = connector.rules.createEventRule(
    name="allevents", destinationName=destination1.name, typeId="*", eventId="*",
    description="Send all events", enabled=True
)
# Create a second rule under the connector, that routes all state to the same destination
rule2 = connector.rules.createStateRule(
    name="allstate", destinationName=destination1.name, logicalInterfaceId="*",
    description="Send all state", enabled=True,
)
```

## Event Streams Connector

```python
import wiotp.sdk.application
from wiotp.sdk.api.services import EventStreamsServiceBindingCredentials, EventStreamsServiceBindingCreateRequest

options = wiotp.sdk.application.parseEnvVars()
appClient = wiotp.sdk.application.ApplicationClient(options)

serviceBinding = {
    "name": "test-eventstreams",
    "description": "Test EventStreams instance",
    "type": "eventstreams",
    "credentials": {
        "api_key": "EVENTSTREAMS_API_KEY",
        "user": "EVENTSTREAMS_USER",
        "password": "EVENTSTREAMS_PASSWORD",
        "kafka_admin_url": "EVENTSTREAMS_ADMIN_URL",
        "kafka_brokers_sasl": [
            "EVENTSTREAMS_BROKER1",
            "EVENTSTREAMS_BROKER2",
        ],
    },
}

eventStreamsService = appClient.serviceBindings.create(serviceBinding)

# Create the connector
connector = self.appClient.dsc.create(
    name="connectorES", type="eventstreams", serviceId=eventStreamsService.id, timezone="UTC",
    description="A test event streams connector", enabled=True
)

# Create a destination under the connector
destination1 = connector.destinations.create(name="all-data", partitions=3)

# Create a rule under the connector, that routes all events to the destination
rule1 = connector.rules.createEventRule(
    name="allevents", destinationName=destination1.name, typeId="*", eventId="*",
    description="Send all events", enabled=True
)
# Create a second rule under the connector, that routes all state to the same destination
rule2 = connector.rules.createStateRule(
    name="allstate", destinationName=destination1.name, logicalInterfaceId="*",
    description="Send all state", enabled=True
)
```

## DB2 Connector

```python
import wiotp.sdk.application

options = wiotp.sdk.application.parseEnvVars()
appClient = wiotp.sdk.application.ApplicationClient(options)

credentials = {
  "hostname": "DB2_HOST",
  "port": "DB2_PORT",
  "username": "DB2_USERNAME",
  "password": "DB2_PASSWORD",
  "https_url": "DB2_HTTPS_URL",
  "ssldsn": "DB2_SSL_DSN",
  "host": "DB2_HOST",
  "uri": "DB2_URI",
  "db": "DB2_DB",
  "ssljdbcurl": "DB2_SSLJDCURL",
  "jdbcurl": "DB2_JDBCURL"
}

serviceBinding = {
    "name": "test-db2",
    "description": "Test DB2 instance",
    "type": "db2",
    "credentials": credentials
}

db2Service = appClient.serviceBindings.create(serviceBinding)

# Create the connector
connector = self.appClient.dsc.create(
    name="connectorDB2",
    type="db2",
    serviceId=db2Service.id,
    timezone="UTC",
    description="A test connector",
    enabled=True
)

# Create a destination under the connector
columns = [
    {"name": "TEMPERATURE_C", "type": "REAL", "nullable": False},
    {"name": "HUMIDITY", "type": "INTEGER", "nullable": True},
    {"name": "TIMESTAMP", "type": "TIMESTAMP", "nullable": False},
]

destination1 = connector.destinations.create(name="test_destination_db2", columns=columns)

# Create a rule under the connector, that routes all state to the same destination
# We can only forward state to a db2 connector, not the raw events
ruleConfiguration={
    "columnMappings": {
        "TEMPERATURE_C": "$event.state.temp.C",
        "HUMIDITY": "$event.state.humidity",
        "TIMESTAMP": "$event.timestamp"
    }
}

rule = connector.rules.createStateRule(
    name="Environment State Forwarding Rule",
    destinationName=destination1.name,
    logicalInterfaceId="123456789012345678901234",
    description="Write environment state to target table",
    enabled=True,
    configuration=ruleConfiguration
)
```

## Postgres Connector

```python
import wiotp.sdk.application

options = wiotp.sdk.application.parseEnvVars()
appClient = wiotp.sdk.application.ApplicationClient(options)

credentials = {
  "hostname": "POSTGRES_HOSTNAME",
  "port": "POSTGRES_PORT",
  "username": "POSTGRES_USERNAME",
  "password": "POSTGRES_PASSWORD",
  "certificate": "POSTGRES_CERTIFICATE",
  "database": "POSTGRES_DATABASE"
}

serviceBinding = {
    "name": "test-postgres",
    "description": "Test Postgres instance",
    "type": "postgres",
    "credentials": credentials
}

postgresService = appClient.serviceBindings.create(serviceBinding)

# Create the connector
connector = self.appClient.dsc.create(
    name="connectorPostgres",
    type="postgres",
    serviceId=postgresService.id,
    timezone="UTC",
    description="A test connector",
    enabled=True
)

# Create a destination under the connector
columns = [
    {"name": "TEMPERATURE_C", "type": "REAL", "nullable": False},
    {"name": "HUMIDITY", "type": "INTEGER", "nullable": True},
    {"name": "TIMESTAMP", "type": "TIMESTAMP", "nullable": False},
]

destination1 = connector.destinations.create(name="test_destination_postgres", columns=columns)

# Create a rule under the connector, that routes all state to the same destination
# We can only forward state to a postgres connector, not the raw events
ruleConfiguration={
    "columnMappings": {
        "TEMPERATURE_C": "$event.state.temp.C",
        "HUMIDITY": "$event.state.humidity",
        "TIMESTAMP": "$event.timestamp"
    }
}

rule = connector.rules.createStateRule(
    name="Environment State Forwarding Rule",
    destinationName=destination1.name,
    logicalInterfaceId="123456789012345678901234",
    description="Write environment state to target table",
    enabled=True,
    configuration=ruleConfiguration
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
    typeId="*",
    eventId="*",
    description="Send all events",
    enabled=True
)

# Create a second rule under the connector, that routes all state to the same destination
rule2 = createdConnector.rules.createStateRule(
    name="allstate",
    destinationName="all-data",
    logicalInterfaceId="*",
    description="Send all state",
    enabled=True,
)
```
