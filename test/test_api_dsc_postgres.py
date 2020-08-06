# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************
#
import uuid
from datetime import datetime
import testUtils
import time
import pytest
from wiotp.sdk.api.services import (
    CloudantServiceBindingCredentials,
    CloudantServiceBindingCreateRequest,
    PostgresServiceBindingCredentials,
)

from wiotp.sdk.exceptions import ApiException


@testUtils.oneJobOnlyTest
class TestDscPostgres(testUtils.AbstractTest):
    def checkPostgresService(self, service, name, description):
        assert service.name == name
        assert service.bindingMode == "manual"
        assert service.bindingType == "postgres"
        assert service.description == description
        assert isinstance(service.created, datetime)
        assert isinstance(service.updated, datetime)
        assert self.WIOTP_API_KEY == service.updatedBy
        assert self.WIOTP_API_KEY == service.createdBy
        assert service.bound == True

    def createAndCheckPostgresService(self, name, description, credentials):
        serviceBinding = {"name": name, "description": description, "type": "postgres", "credentials": credentials}
        createdService = self.appClient.serviceBindings.create(serviceBinding)

        self.checkPostgresService(createdService, name, description)

        # Can we search for it
        count = 0
        for s in self.appClient.serviceBindings.find(nameFilter=name):
            assert s.name == name
            assert createdService.id == s.id
            count += 1
        assert count == 1

        return createdService

    def updateAndCheckPostgresService(self, service, name, description, credentials):
        updatedService = self.appClient.serviceBindings.update(service.id, "postgres", name, credentials, description)

        self.checkPostgresService(updatedService, name, description)

        return updatedService

    def checkPostgresConnector(self, createdConnector, name, description, serviceId, timezone, configuration):
        assert isinstance(createdConnector.created, datetime)
        assert description == createdConnector.description
        assert serviceId == createdConnector.serviceId
        # TBD assert configuration == createdConnector.configuration
        assert "postgres" == createdConnector.connectorType
        assert isinstance(createdConnector.updated, datetime)
        assert name == createdConnector.name
        assert False == createdConnector.adminDisabled
        assert True == createdConnector.enabled
        assert self.WIOTP_API_KEY == createdConnector.updatedBy
        assert self.WIOTP_API_KEY == createdConnector.createdBy
        assert "UTC" == createdConnector.timezone

    def createAndCheckPostgresConnector(self, name, description, serviceId, timezone, configuration=None):
        createdConnector = self.appClient.dsc.create(
            name=name,
            type="postgres",
            description=description,
            serviceId=serviceId,
            timezone=timezone,
            enabled=True,
            configuration=configuration,
        )
        print("Created connector: %s" % createdConnector)
        self.checkPostgresConnector(createdConnector, name, description, serviceId, timezone, configuration)

        # Can we search for it
        count = 0
        for s in self.appClient.dsc.find(nameFilter=name):
            assert s.name == name
            assert createdConnector.id == s.id
            count += 1
        assert count == 1

        # Can we search for it with all the filters
        count = 0
        for s in self.appClient.dsc.find(nameFilter=name, typeFilter="postgres", enabledFilter="true"):
            assert s.name == name
            assert createdConnector.id == s.id
            count += 1
        assert count == 1

        count = 0
        for s in self.appClient.dsc.find(nameFilter=name, serviceId=serviceId):
            assert s.name == name
            assert createdConnector.id == s.id
            count += 1
        assert count == 1

        return createdConnector

    def updateAndCheckPostgresConnector(self, connector, name, description, serviceId, timezone, configuration=None):
        updatedConnector = self.appClient.dsc.update(
            connectorId=connector.id,
            name=name,
            type="postgres",
            description=description,
            serviceId=serviceId,
            timezone=timezone,
            enabled=True,
            configuration=configuration,
        )

        self.checkPostgresConnector(updatedConnector, name, description, serviceId, timezone, configuration)

        return updatedConnector

    # THe columns created should have the same name and nullable status as we specify, but Postgres Can
    # choose to implement the column with different type and/or precision.
    def checkColumns(self, columns1, columns2):

        assert len(columns1) == len(columns2), "Columns arrays are different lengths: %s and %s" % (columns1, columns2)

        for index in range(len(columns1)):
            assert columns1[index]["name"] == columns2[index]["name"].lower()
            assert columns1[index]["nullable"] == columns2[index]["nullable"]

    def createAndCheckPostgresDestination(self, connector, name, columns):
        createdDestination = connector.destinations.create(name=name, columns=columns)

        # print("Created Dest: %s" % createdDestination)
        assert createdDestination.name == name.lower()
        assert createdDestination.destinationType == "postgres"
        assert createdDestination.configuration
        assert createdDestination.partitions == None
        assert createdDestination.bucketInterval == None
        assert createdDestination.retentionDays == None
        self.checkColumns(createdDestination.columns, columns)

        # Can we search for it
        count = 0
        for d in connector.destinations.find(nameFilter=name):
            # print("Fetched Dest: %s" % d)
            if d.name == name.lower():
                assert d.destinationType == "postgres"
                self.checkColumns(d.columns, columns)
                count += 1
        assert count == 1

        return createdDestination

    def checkPostgresForwardingRule(
        self, createdRule, name, destination, description, logicalInterfaceId, columnMappings
    ):
        assert destination.name == createdRule.destinationName
        assert logicalInterfaceId == createdRule.logicalInterfaceId
        assert createdRule.name == name
        assert createdRule.destinationName == destination.name
        assert createdRule.description == description
        assert createdRule.selector == {"logicalInterfaceId": logicalInterfaceId}
        assert createdRule.ruleType == "state"
        assert createdRule.enabled == True
        assert createdRule.columnMappings == columnMappings
        assert createdRule.typeId == None
        assert createdRule.eventId == None
        assert isinstance(createdRule.id, str)
        assert isinstance(createdRule.updated, datetime)
        assert isinstance(createdRule.created, datetime)

    def createAndCheckPostgresForwardingRule(
        self, connector, name, destination, description, logicalInterfaceId, columnMappings
    ):
        createdRule = connector.rules.createStateRule(
            name=name,
            destinationName=destination.name,
            logicalInterfaceId=logicalInterfaceId,
            description=description,
            enabled=True,
            configuration={"columnMappings": columnMappings},
        )

        self.checkPostgresForwardingRule(
            createdRule, name, destination, description, logicalInterfaceId, columnMappings
        )

        # Can we search for it
        count = 0
        for r in connector.rules.find():
            # print("Fetched Rule: %s" % r)
            if r.name == name:
                self.checkPostgresForwardingRule(r, name, destination, description, logicalInterfaceId, columnMappings)
                count += 1
        assert count == 1

        # Can we search for it with all the filters
        count = 0
        for r in connector.rules.find(
            nameFilter=name, typeFilter="state", destinationNameFilter=destination.name, enabledFilter="true"
        ):
            if r.name == name:
                self.checkPostgresForwardingRule(r, name, destination, description, logicalInterfaceId, columnMappings)
                count += 1
        assert count == 1

        return createdRule

    def updateAndCheckPostgresForwardingRule(
        self, rule, connector, name, destination, description, logicalInterfaceId, columnMappings
    ):
        updatedRule = connector.rules.update(
            rule.id,
            "state",
            name,
            destination.name,
            {"logicalInterfaceId": logicalInterfaceId},
            description,
            True,
            {"columnMappings": columnMappings},
        )

        self.checkPostgresForwardingRule(
            updatedRule, name, destination, description, logicalInterfaceId, columnMappings
        )

        # Can we search for it
        count = 0
        for r in connector.rules.find():
            # print("Fetched Rule: %s" % r)
            if r.name == name:
                self.checkPostgresForwardingRule(r, name, destination, description, logicalInterfaceId, columnMappings)
                count += 1
        assert count == 1

        return updatedRule

    # =========================================================================
    # Set up services
    # =========================================================================
    def testCleanup(self):
        for c in self.appClient.dsc:
            if c.name == "test-connector-postgres":
                for r in c.rules:
                    print("Deleting old rule: %s, id: %s" % (r.name, r.id))
                    del c.rules[r.id]
                for d in c.destinations:
                    print("Deleting old destination: %s" % (d.name))
                    del c.destinations[d.name]
                print("Deleting old test connector instance: %s, id: %s" % (c.name, c.id))
                del self.appClient.dsc[c.id]

        for s in self.appClient.serviceBindings:
            if s.name == "test-postgres":
                print("Deleting old test service instance: %s, id: %s" % (s.name, s.id))
                del self.appClient.serviceBindings[s.id]

    def testServiceCRUD(self):

        credentials = {
            "hostname": self.POSTGRES_HOSTNAME,
            "port": self.POSTGRES_PORT,
            "username": self.POSTGRES_USERNAME,
            "password": self.POSTGRES_PASSWORD,
            "certificate": self.POSTGRES_CERTIFICATE,
            "database": self.POSTGRES_DATABASE,
        }

        createdService = self.createAndCheckPostgresService("test-postgres", "Test Postgres instance", credentials)

        updatedService = self.updateAndCheckPostgresService(
            createdService, "test-postgres", "Updated Test Postgres instance", credentials
        )

        del self.appClient.serviceBindings[createdService.id]

    def testServiceDestinationAndRule(self):
        createdService = self.createAndCheckPostgresService(
            "test-postgres",
            "Test Postgres instance",
            {
                "hostname": self.POSTGRES_HOSTNAME,
                "port": self.POSTGRES_PORT,
                "username": self.POSTGRES_USERNAME,
                "password": self.POSTGRES_PASSWORD,
                "certificate": self.POSTGRES_CERTIFICATE,
                "database": self.POSTGRES_DATABASE,
            },
        )

        createdConnector = self.createAndCheckPostgresConnector(
            name="test-connector-postgres",
            description="A test connector",
            serviceId=createdService.id,
            timezone="UTC",
            configuration={"schemaName": "iot_python_test"},
        )

        updatedConnector = self.updateAndCheckPostgresConnector(
            connector=createdConnector,
            name="test-connector-postgres",
            description="An Updated test connector",
            serviceId=createdService.id,
            timezone="UTC",
            configuration={"schemaName": "iot_python_test"},
        )
        # Create a destination under the connector
        columns1 = [{"name": "TEMPERATURE_C", "type": "REAL", "nullable": False}]
        columns2 = [
            {"name": "TEMPERATURE_C", "type": "REAL", "nullable": False},
            {"name": "HUMIDITY", "type": "INTEGER", "nullable": True},
            {"name": "TIMESTAMP", "type": "TIMESTAMP", "nullable": False},
        ]

        destination1 = self.createAndCheckPostgresDestination(createdConnector, "test_destination_postgres", columns1)
        destination2 = self.createAndCheckPostgresDestination(createdConnector, "test_destination_postgres_2", columns2)

        count = 0
        for d in createdConnector.destinations:
            count += 1
        assert count == 2

        # You should not be able to update this destination, an exception is expected
        with pytest.raises(Exception) as e:
            updated = createdConnector.destinations.update(destination1.name, {"test_destination_postgres", columns1})

        with pytest.raises(ApiException) as e:
            del self.appClient.serviceBindings[createdService.id]
            # You should not be able to delete this binding as there is a connector associated with it
            assert e.value.id == "CUDSS0021E"

        # Create Forwarding Rules
        columnMapping1 = {"TEMPERATURE_C": "$event.state.temp.C"}
        columnMapping2 = {"TEMPERATURE_C": "$event.state.temp.F/8*5-32"}

        rule1 = self.createAndCheckPostgresForwardingRule(
            createdConnector, "test-rule-postgres-1", destination1, "Test rule 1", "*", columnMapping1
        )

        with pytest.raises(ApiException) as e:
            del createdConnector.destinations[destination1.name]
            # You should not be able to delete this destination as there is a rule associated with it
            assert "CUDDSC0104E" == e.value.id

        rule1 = self.updateAndCheckPostgresForwardingRule(
            rule1, createdConnector, "test-rule-postgres-1", destination1, "Test rule 1 Updated", "*", columnMapping2
        )

        del createdConnector.rules[rule1.id]

        # Test deleting the destinations
        for d in createdConnector.destinations:
            # print("Deleting destination %s under connector %s" % (d.name, createdConnector.name))
            del createdConnector.destinations[d.name]

        # Confirm there are 0 destinations
        count = 0
        for d in createdConnector.destinations:
            count += 1
        assert count == 0

        # Deleting the connector will delete all the destinations and forwarding rules too
        del self.appClient.dsc[createdConnector.id]
        del self.appClient.serviceBindings[createdService.id]

    def testPostgresServiceBindingParametersNone(self):
        with pytest.raises(Exception) as e:
            PostgresServiceBindingCredentials()
            assert (
                "hostname, port, username, password, certificate and database are required paramaters for a PostgreSQL Service Binding: "
                in str(e.value)
            )

    def testPostgresConnection(self):
        try:
            test = PostgresServiceBindingCredentials(
                hostname=1, port=1, username=1, password=1, certificate=1, database=1
            )
            test.connection()
            assert False == True
        except:
            assert True
