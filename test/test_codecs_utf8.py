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

from wiotp.sdk import InvalidEventException, Utf8Codec


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
        with open("%s/README.md" % cwd) as fileIn:
            fileContent = fileIn.read()

        assert fileContent is not None

        encodedPayload = Utf8Codec.encode(fileContent, None)

        message = Utf8Codec.decode(NonJsonDummyPahoMessage(encodedPayload))
        assert message.data.__class__.__name__ in ["str", "unicode"]
        assert message.data == fileContent
