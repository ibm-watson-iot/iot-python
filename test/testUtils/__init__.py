# *****************************************************************************
# Copyright (c) 2018 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import ibmiotf.application
import os

class AbstractTest(object):

    WIOTP_API_KEY=os.getenv("WIOTP_API_KEY")
    WIOTP_API_TOKEN=os.getenv("WIOTP_API_TOKEN")
    ORG_ID = os.getenv("WIOTP_ORG_ID")
    
    if WIOTP_API_KEY is None:
        raise Exception("WIOTP_API_KEY environment variable is not set")
    if WIOTP_API_TOKEN is None:
        raise Exception("WIOTP_API_TOKEN environment variable is not set")
    if ORG_ID is None:
        raise Exception("WIOTP_ORG_ID environment variable is not set")
    
    options = {'auth-key': WIOTP_API_KEY, 'auth-token': WIOTP_API_TOKEN}
    setupAppClient = ibmiotf.application.Client(options)
    
    registry = setupAppClient.api.registry
    status = setupAppClient.api.status
    usage = setupAppClient.api.usage
    lec = setupAppClient.api.lec