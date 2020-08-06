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
    DB2ServiceBindingCredentials,
)
from wiotp.sdk.exceptions import ApiException


@testUtils.oneJobOnlyTest
class TestDscDb2(testUtils.AbstractTest):
    def checkDB2Service(self, service, name, description):
        assert service.name == name
        assert service.bindingMode == "manual"
        assert service.bindingType == "db2"
        assert service.description == description
        assert isinstance(service.created, datetime)
        assert isinstance(service.updated, datetime)
        assert self.WIOTP_API_KEY == service.updatedBy
        assert self.WIOTP_API_KEY == service.createdBy
        assert service.bound == True

    def createAndCheckDB2Service(self, name, description, credentials):
        serviceBinding = {"name": name, "description": description, "type": "db2", "credentials": credentials}
        createdService = self.appClient.serviceBindings.create(serviceBinding)

        self.checkDB2Service(createdService, name, description)

        # Can we search for it
        count = 0
        for s in self.appClient.serviceBindings.find(nameFilter=name):
            assert s.name == name
            assert createdService.id == s.id
            count += 1
        assert count == 1

        return createdService

    def updateAndCheckDB2Service(self, service, name, description, credentials):
        updatedService = self.appClient.serviceBindings.update(service.id, "db2", name, credentials, description)

        self.checkDB2Service(updatedService, name, description)

        return updatedService

    def checkDB2Connector(self, createdConnector, name, description, serviceId, timezone, configuration):
        assert isinstance(createdConnector.created, datetime)
        assert description == createdConnector.description
        assert serviceId == createdConnector.serviceId
        # TBD assert configuration == createdConnector.configuration
        assert "db2" == createdConnector.connectorType
        assert isinstance(createdConnector.updated, datetime)
        assert name == createdConnector.name
        assert False == createdConnector.adminDisabled
        assert True == createdConnector.enabled
        assert self.WIOTP_API_KEY == createdConnector.updatedBy
        assert self.WIOTP_API_KEY == createdConnector.createdBy
        assert "UTC" == createdConnector.timezone

    def createAndCheckDB2Connector(self, name, description, serviceId, timezone, configuration=None):
        createdConnector = self.appClient.dsc.create(
            name=name,
            type="db2",
            description=description,
            serviceId=serviceId,
            timezone=timezone,
            enabled=True,
            configuration=configuration,
        )
        print("Created connector: %s" % createdConnector)
        self.checkDB2Connector(createdConnector, name, description, serviceId, timezone, configuration)

        # Can we search for it
        count = 0
        for s in self.appClient.dsc.find(nameFilter=name):
            assert s.name == name
            assert createdConnector.id == s.id
            count += 1
        assert count == 1

        # Can we search for it with all the filters
        count = 0
        for s in self.appClient.dsc.find(nameFilter=name, typeFilter="db2", enabledFilter="true"):
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

    def updateAndCheckDB2Connector(self, connector, name, description, serviceId, timezone, configuration=None):
        updatedConnector = self.appClient.dsc.update(
            connectorId=connector.id,
            name=name,
            type="db2",
            description=description,
            serviceId=serviceId,
            timezone=timezone,
            enabled=True,
            configuration=configuration,
        )

        self.checkDB2Connector(updatedConnector, name, description, serviceId, timezone, configuration)

        return updatedConnector

    # THe columns created shojuld have the same name and nullale status as we specify, but DB2 Can
    # choose to implement the column with different type and/or precision.
    def checkColumns(self, columns1, columns2):

        assert len(columns1) == len(columns2), "Columns arrays are different lengths: %s and %s" % (columns1, columns2)

        for index in range(len(columns1)):
            assert columns1[index]["name"] == columns2[index]["name"]
            assert columns1[index]["nullable"] == columns2[index]["nullable"]

    def createAndCheckDB2Destination(self, connector, name, columns):
        createdDestination = connector.destinations.create(name=name, columns=columns)

        # print("Created Dest: %s" % createdDestination)
        assert createdDestination.name == name.upper()
        assert createdDestination.destinationType == "db2"
        assert createdDestination.configuration
        assert createdDestination.partitions == None
        assert createdDestination.bucketInterval == None
        assert createdDestination.retentionDays == None
        self.checkColumns(createdDestination.columns, columns)

        # Can we search for it
        count = 0
        for d in connector.destinations.find(nameFilter=name):
            # print("Fetched Dest: %s" % d)
            if d.name == name.upper():
                assert d.destinationType == "db2"
                self.checkColumns(d.columns, columns)
                count += 1
        assert count == 1

        return createdDestination

    def checkDB2ForwardingRule(self, createdRule, name, destination, description, logicalInterfaceId, columnMappings):
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

    def createAndCheckDB2ForwardingRule(
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

        self.checkDB2ForwardingRule(createdRule, name, destination, description, logicalInterfaceId, columnMappings)

        # Can we search for it
        count = 0
        for r in connector.rules.find():
            # print("Fetched Rule: %s" % r)
            if r.name == name:
                self.checkDB2ForwardingRule(r, name, destination, description, logicalInterfaceId, columnMappings)
                count += 1
        assert count == 1

        # Can we search for it with all the filters
        count = 0
        for r in connector.rules.find(
            nameFilter=name, typeFilter="state", destinationNameFilter=destination.name, enabledFilter="true"
        ):
            if r.name == name:
                self.checkDB2ForwardingRule(r, name, destination, description, logicalInterfaceId, columnMappings)
                count += 1
        assert count == 1

        return createdRule

    def updateAndCheckDB2ForwardingRule(
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

        self.checkDB2ForwardingRule(updatedRule, name, destination, description, logicalInterfaceId, columnMappings)

        # Can we search for it
        count = 0
        for r in connector.rules.find():
            # print("Fetched Rule: %s" % r)
            if r.name == name:
                self.checkDB2ForwardingRule(r, name, destination, description, logicalInterfaceId, columnMappings)
                count += 1
        assert count == 1

        return updatedRule

    # =========================================================================
    # Set up services
    # =========================================================================
    def testCleanup(self):
        for c in self.appClient.dsc:
            if c.name == "test-connector-db2":
                for r in c.rules:
                    print("Deleting old rule: %s, id: %s" % (r.name, r.id))
                    del c.rules[r.id]
                for d in c.destinations:
                    print("Deleting old destination: %s" % (d.name))
                    del c.destinations[d.name]
                print("Deleting old test connector instance: %s, id: %s" % (c.name, c.id))
                del self.appClient.dsc[c.id]

        for s in self.appClient.serviceBindings:
            if s.name == "test-db2":
                print("Deleting old test service instance: %s, id: %s" % (s.name, s.id))
                del self.appClient.serviceBindings[s.id]

    def testServiceCRUD(self):

        credentials = {
            "hostname": self.DB2_HOST,
            "port": self.DB2_PORT,
            "username": self.DB2_USERNAME,
            "password": self.DB2_PASSWORD,
            "https_url": self.DB2_HTTPS_URL,
            "ssldsn": self.DB2_SSL_DSN,
            "host": self.DB2_HOST,
            "uri": self.DB2_URI,
            "db": self.DB2_DB,
            "ssljdbcurl": self.DB2_SSLJDCURL,
            "jdbcurl": self.DB2_JDBCURL,
        }

        createdService = self.createAndCheckDB2Service("test-db2", "Test DB2 instance", credentials)

        updatedService = self.updateAndCheckDB2Service(
            createdService, "test-db2", "Updated Test DB2 instance", credentials
        )

        del self.appClient.serviceBindings[createdService.id]

    def testServiceDestinationAndRule(self):
        createdService = self.createAndCheckDB2Service(
            "test-db2",
            "Test DB2 instance",
            {
                "hostname": self.DB2_HOST,
                "port": self.DB2_PORT,
                "username": self.DB2_USERNAME,
                "password": self.DB2_PASSWORD,
                "https_url": self.DB2_HTTPS_URL,
                "ssldsn": self.DB2_SSL_DSN,
                "host": self.DB2_HOST,
                "uri": self.DB2_URI,
                "db": self.DB2_DB,
                "ssljdbcurl": self.DB2_SSLJDCURL,
                "jdbcurl": self.DB2_JDBCURL,
            },
        )

        createdConnector = self.createAndCheckDB2Connector(
            name="test-connector-db2",
            description="A test connector",
            serviceId=createdService.id,
            timezone="UTC",
            configuration={"schemaName": "iot_python_test"},
        )

        updatedConnector = self.updateAndCheckDB2Connector(
            connector=createdConnector,
            name="test-connector-db2",
            description="An Updated test connector",
            serviceId=createdService.id,
            timezone="UTC",
            configuration={"schemaName": "iot_python_test"},
        )
        # Create a destination under the connector
        # destination1 = createdConnector.destinations.create(name="test_destination_db2", columns= [{name="TEMPERATURE_C", type="REAL", nullable= 1}])
        columns1 = [{"name": "TEMPERATURE_C", "type": "REAL", "nullable": False}]
        columns2 = [
            {"name": "TEMPERATURE_C", "type": "REAL", "nullable": False},
            {"name": "HUMIDITY", "type": "INTEGER", "nullable": True},
            {"name": "TIMESTAMP", "type": "TIMESTAMP", "nullable": False},
        ]

        destination1 = self.createAndCheckDB2Destination(createdConnector, "test_destination_db2", columns1)
        destination2 = self.createAndCheckDB2Destination(createdConnector, "test_destination_db2_2", columns2)

        count = 0
        for d in createdConnector.destinations:
            count += 1
        assert count == 2

        # You should not be able to update this destination, an exception is expected
        with pytest.raises(Exception) as e:
            updated = createdConnector.destinations.update(destination1.name, {"test_destination_db2", columns1})

        with pytest.raises(ApiException) as e:
            del self.appClient.serviceBindings[createdService.id]
            # You should not be able to delete this binding as there is a connector associated with it
            assert e.value.id == "CUDSS0021E"

        # Create Forwarding Rules
        columnMapping1 = {"TEMPERATURE_C": "$event.state.temp.C"}
        columnMapping2 = {"TEMPERATURE_C": "$event.state.temp.F/8*5-32"}

        rule1 = self.createAndCheckDB2ForwardingRule(
            createdConnector, "test-rule-db2-1", destination1, "Test rule 1", "*", columnMapping1
        )

        with pytest.raises(ApiException) as e:
            del createdConnector.destinations[destination1.name]
            # You should not be able to delete this destination as there is a rule associated with it
            assert "CUDDSC0104E" == e.value.id

        rule1 = self.updateAndCheckDB2ForwardingRule(
            rule1, createdConnector, "test-rule-db2-1", destination1, "Test rule 1 Updated", "*", columnMapping2
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

    def testDB2ServiceBindingCredentialsNone(self):
        with pytest.raises(Exception) as e:
            test = DB2ServiceBindingCredentials()
            assert "username, password, db and ssljdbcurl are required paramaters for a DB2 Service Binding" in str(
                e.value
            )

    def testDB2Username(self):
        try:
            test = DB2ServiceBindingCredentials(username=1, password=1, db=1, ssljdbcurl=1)
            test.username()
            assert False == True
        except:
            assert True

    def testDB2Password(self):
        try:
            test = DB2ServiceBindingCredentials(username=1, password=1, db=1, ssljdbcurl=1)
            test.password()
            assert False == True
        except:
            assert True

    def testDB2DB(self):
        try:
            test = DB2ServiceBindingCredentials(username=1, password=1, db=1, ssljdbcurl=1)
            test.db()
            assert False == True
        except:
            assert True

    def testDB2SslDBCurl(self):
        try:
            test = DB2ServiceBindingCredentials(username=1, password=1, db=1, ssljdbcurl=1)
            test.ssljdbcurl()
            assert False == True
        except:
            assert True
