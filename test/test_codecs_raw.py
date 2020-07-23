# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************


import os
import testUtils
import pytest

from wiotp.sdk import InvalidEventException, RawCodec


class NonJsonDummyPahoMessage(object):
    def __init__(self, object):
        self.payload = bytearray()
        try:
            self.payload.extend(object)
        except:
            # python 3
            self.payload.extend(map(ord, object))

class NonByteDummyPahoMessage(object):
    def __init__(self, object):
        self.payload = "not a byteArray"

class TestDevice(testUtils.AbstractTest):
    def testFileObject(self):
        cwd = os.getcwd()
        fileContent = None
        with open("%s/README.md" % cwd, "rb") as fileIn:
            fileContent = fileIn.read()

        assert fileContent is not None

        encodedPayload = RawCodec.encode(fileContent, None)
        message = RawCodec.decode(NonJsonDummyPahoMessage(encodedPayload))
        assert isinstance(message.data, (bytes, bytearray))
        assert message.data == fileContent

    def testInvalidRawEncode(self):
        with pytest.raises(InvalidEventException) as e:
            message = RawCodec.encode(NonByteDummyPahoMessage("{sss,eee}"))
        assert e.value.reason == "Unable to encode data, it is not a bytearray"

    def testInvalidRawDecode(self):
        with pytest.raises(InvalidEventException) as e:
            message = RawCodec.decode(NonByteDummyPahoMessage("{sss,eee}"))
        assert e.value.reason == "Unable to decode message, it is not a bytearray"


