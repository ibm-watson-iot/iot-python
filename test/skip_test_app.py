# *****************************************************************************
# Copyright (c) 2016 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#   Lokesh Haralakatta  - Initial Contribution
# *****************************************************************************

import ibmiotf.application
from ibmiotf import *
from nose.tools import *
import testUtils


class TestApplication(testUtils.AbstractTest):
    appClient = None
    httpClient = None

    @classmethod
    def setup_class(self):
        self.appClient = ibmiotf.application.Client(self.appOptions)
        self.httpClient = ibmiotf.application.HttpClient(self.appOptions)
        self.appClient.connect()

        assert_true(self.appClient.subscribeToDeviceEvents())
        assert_true(self.appClient.subscribeToDeviceStatus())
        assert_true(self.appClient.subscribeToDeviceCommands())

    @classmethod
    def teardown_class(self):
        self.appClient.disconnect()

    def testQuickStartInstance(self):
        client  = ibmiotf.application.Client({})
        assert_is_instance(client , ibmiotf.application.Client)
        assert_equals(client.organization,"quickstart")

        client  = ibmiotf.application.Client({"org": "quickstart", "type": "standalone","id": "MyFirstDevice"})
        hclient  = ibmiotf.application.HttpClient({"org": "quickstart", "type": "standalone","id": "MyFirstDevice"})

        assert_is_instance(client , ibmiotf.application.Client)
        assert_is_instance(hclient , ibmiotf.application.HttpClient)

        assert_equals(client.organization,"quickstart")
        assert_equals(client.clientId , "a:quickstart:MyFirstDevice")

        assert_false(client.subscribeToDeviceEvents())
        assert_false(client.subscribeToDeviceStatus())
        assert_false(client.subscribeToDeviceCommands())

        commandData={'rebootDelay' : 50}
        assert_false(client.publishCommand(self.deviceType, self.deviceId, "reboot", "json", commandData))

    def testApplicationClientInstance(self):
        client  = ibmiotf.application.Client({"org": self.org, "type": self.deviceType, "id": self.deviceId,
                                              "auth-method": "token", "auth-token": self.authToken, "auth-key":self.authKey})
        assert_is_instance(client , ibmiotf.application.Client)

        assert_equals(client.clientId , "A:"+self.org+":"+self.deviceId)

    @raises(Exception)
    def testMissingAuthToken1(self):
        with assert_raises(ConfigurationException) as e:
            ibmiotf.application.Client({"org": self.org, "type": self.deviceType, "id": self.deviceId,
                                        "auth-method": "token", "auth-token": None, "auth-key":self.authKey})
        assert_equal(e.exception.msg, 'Missing required property for API key based authentication: auth-token')

    @raises(Exception)
    def testMissingAuthToken2(self):
        with assert_raises(ConfigurationException) as e:
            ibmiotf.application.Client({"org": self.org, "type": self.deviceType, "id": self.deviceId,
                                        "auth-method": "token", "auth-key":self.authKey})
        assert_equal(e.exception.msg, 'Missing required property for API key based authentication: auth-token')

    @raises(Exception)
    def testMissingConfigFile(self):
        appConfFile="InvalidFile.out"
        with assert_raises(ConfigurationException) as e:
            ibmiotf.application.ParseConfigFile(appConfFile)
        assert_equal(e.exception.msg, 'Error reading device configuration file')

    @raises(Exception)
    def testInvalidConfigFile(self):
        appConfFile="nullValues.conf"
        with assert_raises(AttributeError) as e:
            ibmiotf.application.ParseConfigFile(appConfFile)
        assert_equal(e.exception, AttributeError)

    @raises(Exception)
    def testNotAuthorizedConnect(self):
        client = ibmiotf.application.Client({"org": self.org, "type": self.deviceType, "id": self.deviceId,
                                              "auth-method": "token", "auth-token": "MGhUxxxxxxxx6keG(l", "auth-key":self.authKey})
        with assert_raises(ConnectionException) as e:
            client.connect()
        assert_equal(e.exception, ConnectionException)
        assert_equal(e.exception.msg,'Not authorized')

    @raises(Exception)
    def testMissingMessageEncoder(self):
        with assert_raises(MissingMessageDecoderException)as e:
            myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
            self.appClient.publishEvent(self.deviceType,self.deviceId,"missingMsgEncode", "jason", myData)
        assert_equals(e.exception, MissingMessageEncoderException)

    def testPublishEvent(self):
        def appEventPublishCallback():
            print("Application Publish Event done!!!")

        myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
        assert(self.appClient.publishEvent(self.deviceType,self.deviceId,"testPublishEvent", "json", myData, on_publish=appEventPublishCallback))

    def testPublishOverHTTPs(self):
        myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
        assert_equals(self.httpClient.publishEvent(self.deviceType,self.deviceId,"testPublishEventHTTPs", myData),200)

        myCMD={'command':'Reboot'}
        assert_equals(self.httpClient.publishCommand(self.deviceType,self.deviceId,"testPublishCMDHTTPQS", myCMD),200)

    def testPublishOverHTTPQS(self):
        hclient  = ibmiotf.application.HttpClient({"org": "quickstart", "type": "standalone","id": "MyFirstDevice"})
        myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
        assert_equals(hclient.publishEvent(self.deviceType,self.deviceId,"testPublishEventHTTPQS", myData),200)

        myCMD={'command':'Reboot'}
        assert_equals(hclient.publishCommand(self.deviceType,self.deviceId,"testPublishCMDHTTPQS", myCMD),200)

    @raises(Exception)
    def testMissingMessageEncoderForPublishCommand(self):
        with assert_raises(MissingMessageDecoderException)as e:
            commandData={'rebootDelay' : 50}
            self.appClient.publishCommand(self.deviceType, self.deviceId, "reboot", "jason", commandData)
        assert_equals(e.exception, MissingMessageEncoderException)

    def testPublishCommand(self):
        def appCmdPublishCallback():
            print("Application Publish Command done!!!")

        commandData={'rebootDelay' : 50}
        assert_true(self.appClient.publishCommand(self.deviceType, self.deviceId, "reboot", "json", commandData, on_publish=appCmdPublishCallback))
