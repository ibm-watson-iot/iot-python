# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import wiotp.sdk.application
import pytest
import os
import sys
import pprint
import iso8601
import json
import time
from datetime import datetime, date, timedelta

# grab the api key and token from env vars
WIOTP_API_KEY = os.getenv("WIOTP_API_KEY")
WIOTP_API_TOKEN = os.getenv("WIOTP_API_TOKEN")

# alternatively supply an api key and token
# WIOTP_API_KEY=("WIOTP_API_KEY")
# WIOTP_API_TOKEN=("WIOTP_API_TOKEN")

try:
    ORG_ID = WIOTP_API_KEY.split("-")[1]
except:
    ORG_ID = None

if WIOTP_API_KEY is None:
    raise Exception("WIOTP_API_KEY environment variable is not set")
if WIOTP_API_TOKEN is None:
    raise Exception("WIOTP_API_TOKEN environment variable is not set")
if ORG_ID is None:
    raise Exception("Unable to set ORG_ID from WIOTP_API_KEY")


options = wiotp.sdk.application.parseEnvVars()

# uncomment this if you are having trouble connecting and need to verify your options
# pprint.pprint(options)

# create application client with options
appClient = wiotp.sdk.application.ApplicationClient(options)


"""
Call device connectivity status APIs
"""
# gets client connection status for all clients, 25 at a time
response = appClient.registry.clientConnectivityStatus.getClientConnectionStates()
print("All clients connection status response: %s" % (response))

# gets client connection status for all connected clients
response = appClient.registry.clientConnectivityStatus.getConnectedClientConnectionStates()
print("All connected clients connection status response: %s" % (response))

# gets the connection state of a particular client id, returns 404 if client id is not found
# returns 404 if clientid in question is not found
response = appClient.registry.clientConnectivityStatus.getClientConnectionState("fakeId")
print("Specified client's connection status response: %s" % (response))

# checks for clients that have connected in the last two days
iso8601DateTwoDaysAgo = datetime.now() - timedelta(days=2)
response = appClient.registry.clientConnectivityStatus.getRecentClientConnectionStates(
    iso8601DateTwoDaysAgo.isoformat()
)
print("All recent clients connection status response: %s" % (response))

"""
When persistent monitoring is required, subscribing to the status monitoring topic is recommended.
Uncomment this and replace typeId and deviceId for a specific device or leave blank to subscribe to all.
"""
appClient.connect()
appClient.subscribeToDeviceStatus("typeId", "deviceId")

while True:
    # stay connected while listening to device status
    time.sleep(1)
