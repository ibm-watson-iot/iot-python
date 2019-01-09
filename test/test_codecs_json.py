# *****************************************************************************
# Copyright (c) 2018 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************


import json
import os
from nose.tools import *
from nose import SkipTest
import logging
import testUtils

from wiotp.sdk import InvalidEventException, JsonCodec

class DummyPahoMessage(object):
    def __init__(self, object):
        self.payload = bytearray()
        try:
            self.payload.extend(json.dumps(object))
        except:
            #python 3
            self.payload.extend(map(ord, json.dumps(object)))

class NonJsonDummyPahoMessage(object):
    def __init__(self, object):
        self.payload = bytearray()
        try:
            self.payload.extend(object)
        except:
            #python 3
            self.payload.extend(map(ord, object))

class TestDevice(testUtils.AbstractTest):
    
    def testJsonObject(self):
        message = JsonCodec.decode(DummyPahoMessage({"foo": "bar"}))
        assert_true(isinstance(message.data, dict))
        assert_equals(message.data["foo"], "bar")
        
    def testJsonString(self):
        message = JsonCodec.decode(DummyPahoMessage("bar"))
        try:
            assert_true(isinstance(message.data, unicode))
        except NameError as e:
            # Python 3
            assert_true(isinstance(message.data, str))
        
    def testJsonBoolean(self):
        message = JsonCodec.decode(DummyPahoMessage(False))
        assert_true(isinstance(message.data, bool))
        
    def testJsonInt(self):
        message = JsonCodec.decode(DummyPahoMessage(1))
        assert_true(isinstance(message.data, int))
    
    @raises(InvalidEventException)
    def testInvalidJson(self):
        message = JsonCodec.decode(NonJsonDummyPahoMessage('{sss,eee}'))
