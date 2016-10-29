# *****************************************************************************
# Copyright (c) 2016 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#   Lokesh Haralakatta
# *****************************************************************************
'''
    This module contains the utility methods that are common to python client library
'''

def getContentType(dataFormat):
    '''
       Method to detect content type using given data format
    '''
    # Default content type is json
    contentType = "application/json"
    if dataFormat == "text":
        contentType = "text/plain; charset=utf-8"
    elif dataFormat == "xml":
        contentType = "application/xml"
    elif dataFormat == "bin":
        contentType = "application/octet-stream"
    else:
        contentType = "application/json"
    # Return derived content type
    return contentType

    
