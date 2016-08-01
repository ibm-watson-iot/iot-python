# *****************************************************************************
# Copyright (c) 2016 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#   Lokesh K Haralakatta - Initial Contribution
# *****************************************************************************

# Import required modules
import ibmiotf.device
import ibmiotf.application
import ibmiotf.api
import logging

# Declare and Define instanaces to None
managedClient=None
apiClient=None
options=None

# Define paths of valid config files
deviceFile="../../test/device.conf"
appConfFile="../../test/application.conf"

# Setup logger instance, not set to avoid log messages on std out
logger = logging.getLogger("dmeSample")
logger.setLevel(logging.NOTSET)

# Parse device config file
options = ibmiotf.device.ParseConfigFile(deviceFile)

# Get deviceType and deviceId values from parsed data
deviceType = options['type']
deviceId = options['id']

# Create ManagedClient Instance,connect 
managedClient = ibmiotf.device.ManagedClient(options,logger)
managedClient.connect()

# Parse application config file
options = ibmiotf.application.ParseConfigFile(appConfFile)

# Create an apiClient Instance
apiClient = ibmiotf.api.ApiClient(options,logger)

# Define the DME Action Data in proper JSON format
dmeData = {"bundleId": "example-dme-actions-v1",
           "displayName": {"en_US": "example-dme Actions v1"},
           "version": "1.0","actions": {"installPlugin": {
           "actionDisplayName": { "en_US": "Install Plug-in"},
           "parameters": [ { "name": "pluginURI",
                             "value": "http://example.dme.com",
                            "required": "true" } ] } } }

# Create DME Package using API Method
addResult = apiClient.createDeviceManagementExtensionPkg(dmeData)

# Define callback to carry out requested DME Action
def doDMEAction(topic,data,reqId):
    print("In DME Action Callabck")
    print("Received topic = "+topic)
    print("Received reqId = "+reqId)
    print("Received data = %s" %data)
    return True

# Register above define function as DME callback function
managedClient.dmeActionCallback = doDMEAction;

# Send Manage Request to IoT Platform with indicating support of DME Actions by the Device
managedClient.manage(lifetime=0,supportDeviceMgmtExtActions=True,bundleId='example-dme-actions-v1')

# Define details of DM request containing DME Action,devices and parameters
mgmtRequest = {"action": "example-dme-actions-v1/installPlugin",
               "parameters": [{ "name": "pluginURI",
                                 "value": "http://example.dme.com",}],
               "devices": [{ "typeId": deviceType, "deviceId": deviceId }]}

# Send DM Request for DME Action of installPlugin using API Method
initResult = apiClient.initiateDeviceManagementRequest(mgmtRequest)
reqId = initResult['reqId']

# Here you should be able to see the result from registerd DME callback function
# Device Client sends response to IoT Platform with RC=200 indicating success of the DME Action

# It's time of clear of DME and DM request from the IoT Platform
apiClient.deleteDeviceManagementExtensionPkg('example-dme-actions-v1')
apiClient.deleteDeviceManagementRequest(reqId)

# Get out of Manage Mode and Disconnect the client
managedClient.unmanage()
managedClient.disconnect()
