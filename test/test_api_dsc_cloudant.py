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
class TestDscCloudant(testUtils.AbstractTest):

    # =========================================================================
    # Set up services
    # =========================================================================
    def testCleanup(self):
        for c in self.appClient.dsc:
            if c.name == "test-connector-cloudant":
                print("Deleting old test connector instance: %s" % (c))
                del self.appClient.dsc[c.id]

        for s in self.appClient.serviceBindings:
            if s.name == "test-cloudant":
                print("Deleting old test service instance: %s" % (s))
                del self.appClient.serviceBindings[s.id]

    def testCreateDeleteService1(self):
        serviceBinding = {
            "name": "test-cloudant",
            "description": "Test Cloudant instance",
            "type": "cloudant",
            "credentials": {
                "host": self.CLOUDANT_HOST,
                "port": self.CLOUDANT_PORT,
                "username": self.CLOUDANT_USERNAME,
                "password": self.CLOUDANT_PASSWORD,
            },
        }

        createdService = self.appClient.serviceBindings.create(serviceBinding)

        assert createdService.name == "test-cloudant"
        assert createdService.bindingMode == "manual"
        assert createdService.bindingType == "cloudant"
        assert createdService.description == "Test Cloudant instance"
        assert isinstance(createdService.created, datetime)
        assert isinstance(createdService.updated, datetime)

        # Can we search for it
        count = 0
        for s in self.appClient.serviceBindings.find(nameFilter="test-cloudant"):
            assert s.name == "test-cloudant"
            assert createdService.id == s.id
            count += 1
        assert count == 1

        del self.appClient.serviceBindings[createdService.id]

    def testCreateService2(self):
        serviceBinding = CloudantServiceBindingCreateRequest(
            name="test-cloudant",
            description="Test Cloudant instance",
            credentials=CloudantServiceBindingCredentials(
                host=self.CLOUDANT_HOST,
                port=self.CLOUDANT_PORT,
                username=self.CLOUDANT_USERNAME,
                password=self.CLOUDANT_PASSWORD,
            ),
        )

        createdService = self.appClient.serviceBindings.create(serviceBinding)

        assert createdService.name == "test-cloudant"
        assert createdService.bindingMode == "manual"
        assert createdService.bindingType == "cloudant"
        assert createdService.description == "Test Cloudant instance"
        assert isinstance(createdService.created, datetime)
        assert isinstance(createdService.updated, datetime)

        createdConnector = self.appClient.dsc.create(
            name="test-connector-cloudant",
            type="cloudant",
            serviceId=createdService.id,
            timezone="UTC",
            description="A test connector",
            enabled=True,
        )

        assert isinstance(createdConnector.created, datetime)
        assert "A test connector" == createdConnector.description
        assert createdService.id == createdConnector.serviceId
        assert "cloudant" == createdConnector.connectorType
        assert isinstance(createdConnector.updated, datetime)
        assert "test-connector-cloudant" == createdConnector.name
        assert False == createdConnector.adminDisabled
        assert True == createdConnector.enabled
        assert self.WIOTP_API_KEY == createdConnector.updatedBy
        assert self.WIOTP_API_KEY == createdConnector.createdBy
        assert "UTC" == createdConnector.timezone
        assert None == createdConnector.configuration

        # Create a destination under the connector
        destination1 = createdConnector.destinations.create(name="test-destination-cloudant1", bucketInterval="DAY")
        destination2 = createdConnector.destinations.create(
            name="test-destination-cloudant2", bucketInterval="DAY", retentionDays=60
        )
        destination3 = createdConnector.destinations.create(name="test-destination-cloudant3", bucketInterval="WEEK")
        destination4 = createdConnector.destinations.create(name="test-destination-cloudant4", bucketInterval="MONTH")

        count = 0
        for d in createdConnector.destinations:
            count += 1
            assert d.bucketInterval is not None
            assert d.partitions is None
            if d.name == "test-destination-cloudant2":
                assert d.retentionDays == 60
            else:
                assert d.retentionDays is None
        assert count == 4

        with pytest.raises(ApiException) as e:
            del self.appClient.serviceBindings[createdService.id]
            # You should not be able to delete this binding as there is a connector associated with it
            assert e.value.id == "CUDSS0021E"

        # Create Forwarding Rules

        rule1 = createdConnector.rules.createEventRule(
            name="test-rule-cloudant1",
            destinationName=destination1.name,
            typeId="*",
            eventId="*",
            description="Test rule 1",
            enabled=True,
        )

        assert destination1.name == rule1.destinationName
        assert "*" == rule1.typeId
        assert "*" == rule1.eventId
        assert rule1.name == "test-rule-cloudant1"
        assert rule1.destinationName == destination1.name
        assert rule1.description == "Test rule 1"
        assert rule1.selector == {"deviceType": "*", "eventId": "*"}
        assert rule1.logicalInterfaceId == None
        assert rule1.columnMappings == None
        assert rule1.enabled == True
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
            assert "*" == r.typeId
            assert "event" == r.ruleType
        assert count == 1

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

    def testCloudantServiceBindingParametersNone(self):
        with pytest.raises(Exception) as e:
            CloudantServiceBindingCredentials()
            assert "host, port, username, & password are required parameters for a Cloudant Service Binding: " in str(
                e.value
            )

    def testCloudantURL(self):
        try:
            test = CloudantServiceBindingCredentials(host=1, port=2, username=3, password=4)
            test.url()
            assert False == True
        except:
            assert True

    def testCloudantHost(self):
        try:
            test = CloudantServiceBindingCredentials(host=1, port=2, username=3, password=4)
            test.host()
            assert False == True
        except:
            assert True

    def testCloudantPort(self):
        try:
            test = CloudantServiceBindingCredentials(host=1, port=2, username=3, password=4)
            test.port()
            assert False == True
        except:
            assert True

    def testCloudantUsername(self):
        try:
            test = CloudantServiceBindingCredentials(host=1, port=2, username=3, password=4)
            test.username()
            assert False == True
        except:
            assert True

    def testCloudantPassword(self):
        try:
            test = CloudantServiceBindingCredentials(host=1, port=2, username=3, password=4)
            test.password()
            assert False == True
        except:
            assert True
