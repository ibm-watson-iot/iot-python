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

from wiotp.sdk import InvalidEventException, RawCodec


class NonJsonDummyPahoMessage(object):
    def __init__(self, object):
        self.payload = bytearray()
        try:
            self.payload.extend(object)
        except:
            # python 3
            self.payload.extend(map(ord, object))


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
