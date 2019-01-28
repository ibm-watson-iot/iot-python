import uuid
from datetime import datetime
from nose.tools import *
from nose import SkipTest

import testUtils

from wiotp.sdk.api.services import CloudantServiceBindingCredentials, CloudantServiceBindingCreateRequest
class TestRegistryDevicetypes(testUtils.AbstractTest):
    
    # =========================================================================
    # Set up services
    # =========================================================================
    def testCleanup(self):
        servicesList = self.appClient.serviceBindings.list()

        for s in servicesList:
            if s.name == "test-cloudant":
                print("Deleting old test instance: %s" % (s))
                self.appClient.serviceBindings.delete(s.id)
        

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

        successfulDelete = self.appClient.serviceBindings.delete(createdService.id)
        assert_true(successfulDelete)

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

        self.cloudantService = createdService

    def testSetupConnector(self):
        pass

    def testDeleteService2(self):
        successfulDelete = self.appClient.serviceBindings.delete(self.cloudantService.id)
        assert_true(successfulDelete)
