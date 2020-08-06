# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import uuid
from datetime import datetime
import pytest
import testUtils
import time

from wiotp.sdk.api.services import EventStreamsServiceBindingCredentials, EventStreamsServiceBindingCreateRequest
from wiotp.sdk.exceptions import ApiException


@testUtils.oneJobOnlyTest
class TestDscEventStreams(testUtils.AbstractTest):

    # =========================================================================
    # Set up services
    # =========================================================================
    def testCleanup(self):
        for c in self.appClient.dsc:
            if c.name == "test-connector-eventstreams":
                print("Deleting old test connector instance: %s" % (c))
                del self.appClient.dsc[c.id]

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
                    self.EVENTSTREAMS_BROKER5,
                ],
            },
        }

        createdService = self.appClient.serviceBindings.create(serviceBinding)

        assert createdService.name == "test-eventstreams"
        assert createdService.bindingMode == "manual"
        assert createdService.bindingType == "eventstreams"
        assert createdService.description == "Test EventStreams instance"
        assert isinstance(createdService.created, datetime)
        assert isinstance(createdService.updated, datetime)

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
                    self.EVENTSTREAMS_BROKER5,
                ],
            ),
        )

        createdService = self.appClient.serviceBindings.create(serviceBinding)

        assert createdService.name, "test-eventstreams"
        assert createdService.bindingMode, "manual"
        assert createdService.bindingType, "eventstreams"
        assert createdService.description, "Test EventStreams instance"
        assert isinstance(createdService.created, datetime)
        assert isinstance(createdService.updated, datetime)

        createdConnector = self.appClient.dsc.create(
            name="test-connector-eventstreams",
            type="eventstreams",
            serviceId=createdService.id,
            timezone="UTC",
            description="A test connector",
            enabled=True,
        )

        assert isinstance(createdConnector.created, datetime)
        assert "A test connector" == createdConnector.description
        assert createdService.id == createdConnector.serviceId
        assert "eventstreams" == createdConnector.connectorType
        assert isinstance(createdConnector.updated, datetime)
        assert "test-connector-eventstreams" == createdConnector.name
        assert False == createdConnector.adminDisabled
        assert True == createdConnector.enabled
        assert self.WIOTP_API_KEY == createdConnector.updatedBy
        assert self.WIOTP_API_KEY == createdConnector.createdBy
        assert "UTC" == createdConnector.timezone
        assert None == createdConnector.configuration

        with pytest.raises(ApiException) as e:
            del self.appClient.serviceBindings[createdService.id]
            # You should not be able to delete this binding as there is a connector associated with it
            assert "CUDSS0021E" == e.value.id

        del self.appClient.dsc[createdConnector.id]
        del self.appClient.serviceBindings[createdService.id]

    def testEventStreamsServiceBindingParametersNone(self):
        with pytest.raises(Exception) as e:
            EventStreamsServiceBindingCredentials()
            assert (
                "api_key, kakfa_admin_url, host, port, username, & password are required parameters for a Cloudant Service Binding: "
                in str(e.value)
            )

    def testEventStreamsAPIKey(self):
        try:
            test = EventStreamsServiceBindingCredentials(
                api_key=1, kafka_admin_url=1, kafka_brokers_sasl=1, user=1, password=1
            )
            test.api_key()
            assert False == True
        except:
            assert True

    def testEventStreamsKafkaAdminURL(self):
        try:
            test = EventStreamsServiceBindingCredentials(
                api_key=1, kafka_admin_url=1, kafka_brokers_sasl=1, user=1, password=1
            )
            test.kafka_admin_url()
            assert False == True
        except:
            assert True

    def testEventStreamsKafkaBrokersSasl(self):
        try:
            test = EventStreamsServiceBindingCredentials(
                api_key=1, kafka_admin_url=1, kafka_brokers_sasl=1, user=1, password=1
            )
            test.kafka_brokers_sasl()
            assert False == True
        except:
            assert True

    def testEventStreamsUser(self):
        try:
            test = EventStreamsServiceBindingCredentials(
                api_key=1, kafka_admin_url=1, kafka_brokers_sasl=1, user=1, password=1
            )
            test.user()
            assert False == True
        except:
            assert True

    def testEventStreamsPassword(self):
        try:
            test = EventStreamsServiceBindingCredentials(
                api_key=1, kafka_admin_url=1, kafka_brokers_sasl=1, user=1, password=1
            )
            test.password()
            assert False == True
        except:
            assert True
