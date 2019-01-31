# *****************************************************************************
# Copyright (c) 2018 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import wiotp.sdk.application
import os

class AbstractTest(object):

    WIOTP_API_KEY=os.getenv("WIOTP_API_KEY")
    WIOTP_API_TOKEN=os.getenv("WIOTP_API_TOKEN")

    CLOUDANT_HOST=os.getenv("CLOUDANT_HOST")
    CLOUDANT_PORT=os.getenv("CLOUDANT_PORT")
    CLOUDANT_USERNAME=os.getenv("CLOUDANT_USERNAME")
    CLOUDANT_PASSWORD=os.getenv("CLOUDANT_PASSWORD")


    EVENTSTREAMS_API_KEY=os.getenv("EVENTSTREAMS_API_KEY")
    EVENTSTREAMS_ADMIN_URL=os.getenv("EVENTSTREAMS_ADMIN_URL")
    EVENTSTREAMS_BROKER1=os.getenv("EVENTSTREAMS_BROKER1")
    EVENTSTREAMS_BROKER2=os.getenv("EVENTSTREAMS_BROKER2")
    EVENTSTREAMS_BROKER3=os.getenv("EVENTSTREAMS_BROKER3")
    EVENTSTREAMS_BROKER4=os.getenv("EVENTSTREAMS_BROKER4")
    EVENTSTREAMS_BROKER5=os.getenv("EVENTSTREAMS_BROKER5")
    EVENTSTREAMS_USER=os.getenv("EVENTSTREAMS_USER")
    EVENTSTREAMS_PASSWORD=os.getenv("EVENTSTREAMS_PASSWORD")

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

    if CLOUDANT_HOST is None:
        raise Exception("CLOUDANT_HOST environment variable is not set")
    if CLOUDANT_PORT is None:
        raise Exception("CLOUDANT_PORT environment variable is not set")
    if CLOUDANT_USERNAME is None:
        raise Exception("CLOUDANT_USERNAME environment variable is not set")
    if CLOUDANT_PASSWORD is None:
        raise Exception("CLOUDANT_PASSWORD environment variable is not set")

    options = {'auth': { 'key': WIOTP_API_KEY, 'token': WIOTP_API_TOKEN}}
    appClient = wiotp.sdk.application.ApplicationClient(options)

