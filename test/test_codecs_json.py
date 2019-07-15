# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************


import json
import os
import testUtils
import pytest

from wiotp.sdk import InvalidEventException, JsonCodec


class DummyPahoMessage(object):
    def __init__(self, object):
        self.payload = bytearray()
        try:
            self.payload.extend(json.dumps(object))
        except:
            # python 3
            self.payload.extend(map(ord, json.dumps(object)))


class NonJsonDummyPahoMessage(object):
    def __init__(self, object):
        self.payload = bytearray()
        try:
            self.payload.extend(object)
        except:
            # python 3
            self.payload.extend(map(ord, object))


class TestDevice(testUtils.AbstractTest):
    def testJsonObject(self):
        message = JsonCodec.decode(DummyPahoMessage({"foo": "bar"}))
        assert isinstance(message.data, dict)
        assert message.data["foo"] == "bar"

    def testJsonString(self):
        message = JsonCodec.decode(DummyPahoMessage("bar"))
        try:
            assert isinstance(message.data, unicode)
        except NameError as e:
            # Python 3
            assert isinstance(message.data, str)

    def testJsonBoolean(self):
        message = JsonCodec.decode(DummyPahoMessage(False))
        assert isinstance(message.data, bool)

    def testJsonInt(self):
        message = JsonCodec.decode(DummyPahoMessage(1))
        assert isinstance(message.data, int)

    def testInvalidJson(self):
        with pytest.raises(InvalidEventException):
            message = JsonCodec.decode(NonJsonDummyPahoMessage("{sss,eee}"))
