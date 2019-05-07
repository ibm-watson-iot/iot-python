# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

from datetime import datetime
import pytz

try:
    from wiotp.sdk import Message, MessageCodec
except ImportError:
    # This part is only required to run the sample from within the samples
    # directory when the module itself is not installed.
    import sys
    import os
    import inspect

    cmd_subfolder = os.path.realpath(
        os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../src"))
    )
    if cmd_subfolder not in sys.path:
        sys.path.insert(0, cmd_subfolder)
    from wiotp.sdk import Message


class MyCodec(MessageCodec):
    """
    Dedicated encoder for supporting a very specific dataset, serialises a dictionary object
    of the following format:
        {
            'hello' : 'world',
            'x' : 10
        }

    into a simple comma-seperated message:
        world,10
    """

    @staticmethod
    def encode(data=None, timestamp=None):
        return data["hello"] + "," + str(data["x"])

    @staticmethod
    def decode(message):
        """
        The decoder understands the comma-seperated format produced by the encoder and
        allocates the two values to the correct keys:
            data['hello'] = 'world'
            data['x'] = 10

        """
        (hello, x) = message.payload.split(",")

        data = {}
        data["hello"] = hello
        data["x"] = x

        timestamp = datetime.now(pytz.timezone("UTC"))

        return Message(data, timestamp)
