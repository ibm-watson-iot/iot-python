import uuid
from datetime import datetime
from nose.tools import *
from nose import SkipTest

import testUtils
import time

from wiotp.sdk.api.services import CloudantServiceBindingCredentials, CloudantServiceBindingCreateRequest
from wiotp.sdk.exceptions import ApiException

# Blocked waiting for https://github.ibm.com/wiotp/tracker/issues/1829

class TestDscCloudant(testUtils.AbstractTest):
    
    # =========================================================================
    # Set up services
    # =========================================================================
    def testCleanup(self):
        for c in self.appClient.dsc.connectors:
            if c.name == "test-connector-cloudant":
                print("Deleting old test connector instance: %s" % (c))
                del self.appClient.dsc.connectors[c.id]

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
                "password": self.CLOUDANT_PASSWORD
            }
        }

        createdService = self.appClient.serviceBindings.create(serviceBinding)

        assert_equals(createdService.name, "test-cloudant")
        assert_equals(createdService.bindingMode, "manual")
        assert_equals(createdService.bindingType, "cloudant")
        assert_equals(createdService.description, "Test Cloudant instance")
        assert_true(isinstance(createdService.created, datetime))
        assert_true(isinstance(createdService.updated, datetime))

        # Can we search for it
        count = 0
        for s in self.appClient.serviceBindings.find(nameFilter="test-cloudant"):
            assert_equals("test-cloudant", s.name)
            assert_equals(createdService.id, s.id)
            count += 1
        assert_equals(1, count)

        del self.appClient.serviceBindings[createdService.id]

    def testCreateService2(self):
        serviceBinding = CloudantServiceBindingCreateRequest(
            name="test-cloudant", 
            description="Test Cloudant instance",
            credentials=CloudantServiceBindingCredentials(
                host = self.CLOUDANT_HOST,
                port = self.CLOUDANT_PORT,
                username = self.CLOUDANT_USERNAME,
                password = self.CLOUDANT_PASSWORD
            )
        )

        createdService = self.appClient.serviceBindings.create(serviceBinding)

        assert_equals(createdService.name, "test-cloudant")
        assert_equals(createdService.bindingMode, "manual")
        assert_equals(createdService.bindingType, "cloudant")
        assert_equals(createdService.description, "Test Cloudant instance")
        assert_true(isinstance(createdService.created, datetime))
        assert_true(isinstance(createdService.updated, datetime))

        createdConnector = self.appClient.dsc.connectors.create(
            name="test-connector-cloudant", 
            serviceId=createdService.id, 
            timezone="UTC", 
            description="A test connector", 
            enabled=True
        )

        assert_true(isinstance(createdConnector.created, datetime))
        assert_equals("A test connector", createdConnector.description)
        assert_equals(createdService.id, createdConnector.serviceId)
        assert_equals("cloudant", createdConnector.connectorType)
        assert_true(isinstance(createdConnector.updated, datetime))
        assert_equals("test-connector-cloudant", createdConnector.name)
        assert_equals(False, createdConnector.adminDisabled)
        assert_equals(True, createdConnector.enabled)
        assert_equals(self.WIOTP_API_KEY, createdConnector.updatedBy)
        assert_equals(self.WIOTP_API_KEY, createdConnector.createdBy)
        assert_equals("UTC", createdConnector.timezone)


        # Create a destination under the connector
        destination1 = createdConnector.destinations.create(name="test-destination-cloudant1", bucketInterval="DAY")
        destination2 = createdConnector.destinations.create(name="test-destination-cloudant2", bucketInterval="DAY")
        destination3 = createdConnector.destinations.create(name="test-destination-cloudant3", bucketInterval="WEEK")
        destination4 = createdConnector.destinations.create(name="test-destination-cloudant4", bucketInterval="MONTH")

        count = 0
        for d in createdConnector.destinations:
            count += 1
            assert_true(d.bucketInterval is not None)
            assert_true(d.partitions is None)
        assert_equals(4, count)

        try:
            del self.appClient.serviceBindings[createdService.id]
        except ApiException as exception:
            # You should not be able to delete this binding as there is a connector associated with it
            assert_equals("CUDSS0021E", exception.id)

        # Create Forwarding Rules
        
        rule1 = createdConnector.rules.createEventRule(
            name="test-rule-cloudant1", 
            destinationName=destination1.name, 
            description="Test rule 1", 
            enabled=True,
            typeId="*",
            eventId="*"
        )
        assert_equals(destination1.name, rule1.destinationName)
        assert_equals("*", rule1.typeId)
        assert_equals("*", rule1.eventId)

        try:
            del createdConnector.destinations[destination1.name]
        except ApiException as exception:
            # You should not be able to delete this destination as there is a rule associated with it
            assert_equals("CUDDSC0104E", exception.id)


        
        count = 0
        for r in createdConnector.rules:
            count += 1
            if count > 10:
                print("Count > 10")
                break
            assert_equals("*", r.typeId)
            assert_equals("event", r.ruleType)
        assert_equals(1, count)
        

        del createdConnector.rules[rule1.id]

        # Test deleting the destinations
        for d in createdConnector.destinations:
            print("Deleting destination %s under connector %s" % (d.name, createdConnector.name))
            del createdConnector.destinations[d.name]

        # Confirm there are 0 destinations
        count = 0
        for d in createdConnector.destinations:
            count += 1
        assert_equals(0, count)


        # Deleting the connector will delete all the destinations and forwarding rules too
        del self.appClient.dsc.connectors[createdConnector.id]
        del self.appClient.serviceBindings[createdService.id]
