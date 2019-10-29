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
from wiotp.sdk.api.services import CloudantServiceBindingCredentials, CloudantServiceBindingCreateRequest
from wiotp.sdk.exceptions import ApiException


@testUtils.oneJobOnlyTest
class TestDscDb2(testUtils.AbstractTest):

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

    def testCreateDeleteService1(self):
        serviceBinding = {
            "name": "test-db2",
            "description": "Test DB2 instance",
            "type": "db2",
            "credentials": {
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
        }

        createdService = self.appClient.serviceBindings.create(serviceBinding)

        assert createdService.name == "test-db2"
        assert createdService.bindingMode == "manual"
        assert createdService.bindingType == "db2"
        assert createdService.description == "Test DB2 instance"
        assert isinstance(createdService.created, datetime)
        assert isinstance(createdService.updated, datetime)

        # Can we search for it
        count = 0
        for s in self.appClient.serviceBindings.find(nameFilter="test-db2"):
            assert s.name == "test-db2"
            assert createdService.id == s.id
            count += 1
        assert count == 1

        del self.appClient.serviceBindings[createdService.id]

    def testServiceDestinationAndRule(self):
        serviceBinding = {
            "name": "test-db2",
            "description": "Test DB2 instance",
            "type": "db2",
            "credentials": {
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
        }
        createdService = self.appClient.serviceBindings.create(serviceBinding)

        assert createdService.name == "test-db2"
        assert createdService.bindingMode == "manual"
        assert createdService.bindingType == "db2"
        assert createdService.description == "Test DB2 instance"
        assert isinstance(createdService.created, datetime)
        assert isinstance(createdService.updated, datetime)

        createdConnector = self.appClient.dsc.create(
            name="test-connector-db2",
            type="db2",
            serviceId=createdService.id,
            timezone="UTC",
            description="A test connector",
            enabled=True,
            configuration={"schemaName": "wiotp_test"},
        )

        assert isinstance(createdConnector.created, datetime)
        assert "A test connector" == createdConnector.description
        assert createdService.id == createdConnector.serviceId
        assert "db2" == createdConnector.connectorType
        assert isinstance(createdConnector.updated, datetime)
        assert "test-connector-db2" == createdConnector.name
        assert False == createdConnector.adminDisabled
        assert True == createdConnector.enabled
        assert self.WIOTP_API_KEY == createdConnector.updatedBy
        assert self.WIOTP_API_KEY == createdConnector.createdBy
        assert "UTC" == createdConnector.timezone

        # Create a destination under the connector
        # destination1 = createdConnector.destinations.create(name="test_destination_db2", columns= [{name="TEMPERATURE_C", type="REAL", nullable= 1}])
        columns1 = [{"name": "TEMPERATURE_C", "type": "REAL", "nullable": False}]
        columns2 = [
            {"name": "TEMPERATURE_C", "type": "REAL", "nullable": False},
            {"name": "HUMIDITY", "type": "INTEGER", "nullable": True},
            {"name": "TIMESTAMP", "type": "TIMESTAMP", "nullable": False},
        ]

        destination1 = createdConnector.destinations.create(name="test_destination_db2", columns=columns1)
        destination2 = createdConnector.destinations.create(name="test_destination_db2_2", columns=columns2)

        count = 0
        for d in createdConnector.destinations:
            count += 1
            if d.name == "test_destination_db2":
                assert d.columns == columns1
            if d.name == "test_destination_db2_2":
                assert d.columns == columns2

        assert count == 2

        with pytest.raises(ApiException) as e:
            del self.appClient.serviceBindings[createdService.id]
            # You should not be able to delete this binding as there is a connector associated with it
            assert e.value.id == "CUDSS0021E"

        # Create Forwarding Rules
        columnMapping1 = {"TEMPERATURE_C": "$event.state.temp.C"}

        rule1 = createdConnector.rules.createStateRule(
            name="test-rule-db2-1",
            destinationName=destination1.name,
            description="Test rule 1",
            enabled=True,
            logicalInterfaceId="*",
            configuration={"columnMappings": columnMapping1},
        )

        assert destination1.name == rule1.destinationName
        assert "*" == rule1.logicalInterfaceId
        assert rule1.name == "test-rule-db2-1"
        assert rule1.destinationName == destination1.name
        assert rule1.description == "Test rule 1"
        assert rule1.selector == {"logicalInterfaceId": "*"}
        assert rule1.enabled == True
        assert rule1.columnMappings == columnMapping1
        assert isinstance(rule1.id, str)
        assert isinstance(rule1.updated, datetime)
        assert isinstance(rule1.created, datetime)

        with pytest.raises(ApiException) as e:
            del createdConnector.destinations[destination1.name]
            # You should not be able to delete this destination as there is a rule associated with it
            assert "CUDDSC0104E" == e.value.id

        count = 0
        for r in createdConnector.rules:
            count += 1
            if count > 10:
                print("Count > 10")
                break
            assert "*" == r.logicalInterfaceId
            assert "state" == r.ruleType
        assert count == 1

        del createdConnector.rules[rule1.id]

        # Test deleting the destinations
        for d in createdConnector.destinations:
            print("Deleting destination %s under connector %s" % (d.name, createdConnector.name))
            del createdConnector.destinations[d.name]

        # Confirm there are 0 destinations
        count = 0
        for d in createdConnector.destinations:
            count += 1
        assert count == 0

        # Deleting the connector will delete all the destinations and forwarding rules too
        del self.appClient.dsc[createdConnector.id]
        del self.appClient.serviceBindings[createdService.id]
