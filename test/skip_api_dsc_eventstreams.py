import uuid
from datetime import datetime
from nose.tools import *
from nose import SkipTest

import testUtils
import time

from wiotp.sdk.api.services import EventStreamsServiceBindingCredentials, EventStreamsServiceBindingCreateRequest
from wiotp.sdk.exceptions import ApiException

# Blocked waiting for https://github.ibm.com/wiotp/tracker/issues/1829

class TestDscEventStreams(testUtils.AbstractTest):
    
    # =========================================================================
    # Set up services
    # =========================================================================
    def testCleanup(self):
        for c in self.appClient.dsc.connectors:
            if c.name == "test-connector-eventstreams":
                print("Deleting old test connector instance: %s" % (c))
                del self.appClient.dsc.connectors[c.id]

        for s in self.appClient.serviceBindings:
            if s.name == "test-eventstreams":
                print("Deleting old test instance: %s" % (s))
                del self.appClient.serviceBindings[s.id]
        

    def testCreateDeleteService1(self):
        serviceBinding = {
            "name": "test-eventstreams", 
            "description": "Test EventStreams instance",
            "type": "eventstreams", 
            "credentials": {
                "api_key": self.EVENTSTREAMS_API_KEY,
                "user": self.EVENTSTREAMS_USER,
                "password": self.EVENTSTREAMS_PASSWORD,
                "kafka_admin_url": self.EVENTSTREAMS_ADMIN_URL,
                "kafka_brokers_sasl": [
                    self.EVENTSTREAMS_BROKER1,
                    self.EVENTSTREAMS_BROKER2,
                    self.EVENTSTREAMS_BROKER3,
                    self.EVENTSTREAMS_BROKER4,
                    self.EVENTSTREAMS_BROKER5
                ]
            }
        }

        createdService = self.appClient.serviceBindings.create(serviceBinding)

        assert_equals(createdService.name, "test-eventstreams")
        assert_equals(createdService.bindingMode, "manual")
        assert_equals(createdService.bindingType, "eventstreams")
        assert_equals(createdService.description, "Test EventStreams instance")
        assert_true(isinstance(createdService.created, datetime))
        assert_true(isinstance(createdService.updated, datetime))

        time.sleep(10)
        del self.appClient.serviceBindings[createdService.id]

    
    def testCreateService2(self):
        serviceBinding = EventStreamsServiceBindingCreateRequest(
            name="test-eventstreams", 
            description="Test EventStreams instance",
            credentials=EventStreamsServiceBindingCredentials(
                api_key=self.EVENTSTREAMS_API_KEY,
                user=self.EVENTSTREAMS_USER,
                password=self.EVENTSTREAMS_PASSWORD,
                kafka_admin_url=self.EVENTSTREAMS_ADMIN_URL,
                kafka_brokers_sasl=[
                    self.EVENTSTREAMS_BROKER1,
                    self.EVENTSTREAMS_BROKER2,
                    self.EVENTSTREAMS_BROKER3,
                    self.EVENTSTREAMS_BROKER4,
                    self.EVENTSTREAMS_BROKER5
                ]
            )
        )

        createdService = self.appClient.serviceBindings.create(serviceBinding)

        assert_equals(createdService.name, "test-eventstreams")
        assert_equals(createdService.bindingMode, "manual")
        assert_equals(createdService.bindingType, "eventstreams")
        assert_equals(createdService.description, "Test EventStreams instance")
        assert_true(isinstance(createdService.created, datetime))
        assert_true(isinstance(createdService.updated, datetime))

        createdConnector = self.appClient.dsc.connectors.create(
            name="test-connector-eventstreams", 
            serviceId=createdService.id, 
            timezone="UTC", 
            description="A test connector", 
            enabled=True
        )

        assert_true(isinstance(createdConnector.created, datetime))
        assert_equals("A test connector", createdConnector.description)
        assert_equals(createdService.id, createdConnector.serviceId)
        assert_equals("eventstreams", createdConnector.connectorType)
        assert_true(isinstance(createdConnector.updated, datetime))
        assert_equals("test-connector-eventstreams", createdConnector.name)
        assert_equals(False, createdConnector.adminDisabled)
        assert_equals(True, createdConnector.enabled)
        assert_equals(self.WIOTP_API_KEY, createdConnector.updatedBy)
        assert_equals(self.WIOTP_API_KEY, createdConnector.createdBy)
        assert_equals("UTC", createdConnector.timezone)

        try:
            del self.appClient.serviceBindings[createdService.id]
        except ApiException as exception:
            # You should not be able to delete this binding as there is a connector associated with it
            assert_equals("CUDSS0021E", exception.id)
        
        del self.appClient.dsc.connectors[createdConnector.id]
        del self.appClient.serviceBindings[createdService.id]
    