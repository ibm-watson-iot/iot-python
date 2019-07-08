# *****************************************************************************
# Copyright (c) 2018 IBM Corporation and other Contributors.
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

oneJobOnlyTest = pytest.mark.skipif(
    sys.version_info < (3, 7),
    reason="Doesn't support running in multiple envs in parallel due to limits on # of service bindings allowed",
)


class AbstractTest(object):

    WIOTP_API_KEY = os.getenv("WIOTP_API_KEY")
    WIOTP_API_TOKEN = os.getenv("WIOTP_API_TOKEN")

    CLOUDANT_HOST = os.getenv("CLOUDANT_HOST", None)
    CLOUDANT_PORT = os.getenv("CLOUDANT_PORT", None)
    CLOUDANT_USERNAME = os.getenv("CLOUDANT_USERNAME", None)
    CLOUDANT_PASSWORD = os.getenv("CLOUDANT_PASSWORD", None)

    EVENTSTREAMS_API_KEY = os.getenv("EVENTSTREAMS_API_KEY")
    EVENTSTREAMS_ADMIN_URL = os.getenv("EVENTSTREAMS_ADMIN_URL")
    EVENTSTREAMS_BROKER1 = os.getenv("EVENTSTREAMS_BROKER1")
    EVENTSTREAMS_BROKER2 = os.getenv("EVENTSTREAMS_BROKER2")
    EVENTSTREAMS_BROKER3 = os.getenv("EVENTSTREAMS_BROKER3")
    EVENTSTREAMS_BROKER4 = os.getenv("EVENTSTREAMS_BROKER4")
    EVENTSTREAMS_BROKER5 = os.getenv("EVENTSTREAMS_BROKER5")
    EVENTSTREAMS_USER = os.getenv("EVENTSTREAMS_USER")
    EVENTSTREAMS_PASSWORD = os.getenv("EVENTSTREAMS_PASSWORD")

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
    # import pprint
    # pprint.pprint(options)
    appClient = wiotp.sdk.application.ApplicationClient(options)
