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

class TestApplication:
    appClient=None

    @classmethod
    def setup_class(self):
        appConfFile="application.conf"
        options = ibmiotf.application.ParseConfigFile(appConfFile)
        self.org = options['auth-key'][2:8]
        self.deviceType = options['type']
        self.deviceId = options['id']
        self.authToken = options['auth-token']
        self.authKey = options['auth-key']

        self.appClient = ibmiotf.application.Client(options)
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
        assert_is_instance(client , ibmiotf.application.Client)
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

    def testPublishEventOverHTTPs(self):
        #Publish JSON Data Over HTTP
        myJData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
        assert_equals(self.appClient.publishEventOverHTTP(self.deviceType,self.deviceId,"JSONOverHTTP", myJData,"json"),200)
        #Publish Text Over HTTP
        myTData='sample text to WIoTP'
        assert_equals(self.appClient.publishEventOverHTTP(self.deviceType,self.deviceId,"TextOverHTTP", myTData,"text"),200)
        #Publish XML Data Over HTTP
        myXData='<?xml version="1.0" encoding="utf-8"?> <data>Sample XML Data to WIOTP</data>'
        assert_equals(self.appClient.publishEventOverHTTP(self.deviceType,self.deviceId,"XMLOverHTTP", myXData,"xml"),200)
        #Publish Binary Data Over HTTP
        myBData= open('./sample.png', 'rb').read()
        assert_equals(self.appClient.publishEventOverHTTP(self.deviceType,self.deviceId,"BinaryOverHTTP", myBData,"bin"),200)

    def testPublishCommandOverHTTPs(self):
        #Publish JSON Data Over HTTP
        myJData={'command':'Reboot'}
        assert_equals(self.appClient.publishCommandOverHTTP(self.deviceType,self.deviceId,"JSONOverHTTP", myJData,"json"),200)
        #Publish Text Over HTTP
        myTData='command:reboot'
        assert_equals(self.appClient.publishCommandOverHTTP(self.deviceType,self.deviceId,"TextOverHTTP", myTData,"text"),200)
        #Publish XML Data Over HTTP
        myXData='<?xml version="1.0" encoding="utf-8"?> <cmd>reboot</cmd>'
        assert_equals(self.appClient.publishCommandOverHTTP(self.deviceType,self.deviceId,"XMLOverHTTP", myXData,"xml"),200)
        #Publish Binary Data Over HTTP
        myBData= 'cmd:reboot'
        assert_equals(self.appClient.publishCommandOverHTTP(self.deviceType,self.deviceId,"BinaryOverHTTP", myBData,"bin"),200)

    def testPublishEventOverHTTPQS(self):
        client  = ibmiotf.application.Client({"org": "quickstart", "type": "standalone","id": "MyFirstDevice"})
        #Publish JSON Data Over HTTP
        myJData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
        assert_equals(client.publishEventOverHTTP("standalone","MyFirstDevice","JSONOverHTTP", myJData,"json"),200)
        #Publish Text Over HTTP
        myTData='sample text to WIoTP'
        assert_equals(client.publishEventOverHTTP("standalone","MyFirstDevice","TextOverHTTP", myTData,"text"),200)
        #Publish XML Data Over HTTP
        myXData='<?xml version="1.0" encoding="utf-8"?> <data>Sample XML Data to WIOTP</data>'
        assert_equals(client.publishEventOverHTTP("standalone","MyFirstDevice","XMLOverHTTP", myXData,"xml"),200)
        #Publish Binary Data Over HTTP
        myBData= open('./sample.png', 'rb').read()
        assert_equals(client.publishEventOverHTTP("standalone","MyFirstDevice","BinaryOverHTTP", myBData,"bin"),200)

    def testPublishCommandOverHTTPQS(self):
        client  = ibmiotf.application.Client({"org": "quickstart", "type": "standalone","id": "MyFirstDevice"})
        #Publish JSON Data Over HTTP
        myJData={'command':'Reboot'}
        assert_equals(client.publishCommandOverHTTP("standalone","MyFirstDevice","JSONOverHTTP", myJData,"json"),200)
        #Publish Text Over HTTP
        myTData='command:reboot'
        assert_equals(client.publishCommandOverHTTP("standalone","MyFirstDevice","TextOverHTTP", myTData,"text"),200)
        #Publish XML Data Over HTTP
        myXData='<?xml version="1.0" encoding="utf-8"?> <cmd>reboot</cmd>'
        assert_equals(client.publishCommandOverHTTP("standalone","MyFirstDevice","XMLOverHTTP", myXData,"xml"),200)
        #Publish Binary Data Over HTTP
        myBData= 'cmd:reboot'
        assert_equals(client.publishCommandOverHTTP("standalone","MyFirstDevice","BinaryOverHTTP", myBData,"bin"),200)

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
