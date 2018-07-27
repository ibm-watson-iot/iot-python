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

'''
    This is a sample program to illustrate how Device Management Extension (DME) works.

    In this sample, we are going to show case the implementation for DME action received
    through device management request for changing the publish interval of device events.

    Below descrbed is step-by-step flow followed in this sample program:
        1.  Application Client subscribes to Device Events and registers a
            callback function to be executed on receipt of Device Event from the
            Platform. Initially application client receives the device events
            from device at an interval of 10 Seconds.

        2.  We create DME Package through API call with support for 2 actions -
            installPlugin and updatePublishInterval on the platform. We specify
            the bundle information through proper JSON format as accepted by the
            Platform.

        3.  Device Client sends manage request with support of DME Actions to
            the platform. Device Client registers callback function to be called
            when DME request comes from platform. DME Callback function
            implements action to be taken when received DME Action is
            updatePublishInterval.

        4.  Initially we submit DME action for installPlugin through API Client
            to the platform. Device receives notifcation from the platform on
            request of installPlugin DME Action. Then the DME Callback function
            registered at the device side gets invoked and executes the
            statements implemented for installPlugin Action.

        5.  Initially the device events are getting published at an interval of
            10 Seconds. We have separate thread to publish device events at the
            specified interval of time.

        6.  User is given an option to enter new values for device event publish
            interval from the terminal. As the user provides new valid numeric
            value from the terminal, we capture that and put as part of DME
            request and send to platform for the updatePublishInterval action.

        7.  IoT Platform publishes MQTT message with the requested DME Action
            and the parameters provided in the request to device. DME callback
            function gets called in the device side again.

        8.  With in DME callback function, it detects the requested DME action
            is updatePublishInterval,then cancels the earlier timer object for
            publish event and creates new thread with received publish interval
            value to publish the device events.

        9.  The steps 6 , 7 , 8 are in a loop run repeatedly till user enters q.

        10. Cleanup and Sample Terminates by accepting q from user.
'''
from __future__ import print_function

# Import required modules
import ibmiotf.device
import ibmiotf.application
import ibmiotf.api
import logging
import threading
import json

try:
    raw_input          # Python 2
except NameError:
    raw_input = input  # Python 3


# Define callback for Received Device events at Application Client Side
def deviceEventCallback(event):
    str = "Message from deviceEventCallback: %s event '%s' received from device [%s]: %s"
    print(str % (event.format, event.event, event.device, json.dumps(event.data)))

# Define Function to publish device event after given interval of time
def publishDeviceEvent(dClient,pInterval=10):
    global pThread
    message = {'d': { "status" : "connected" } }
    topic = 'iot-2/evt/status/fmt/json'
    print ("Publishing Device event with data - %s with Interval of %s Seconds" %(message,pInterval))
    dClient.client.publish(topic,payload=json.dumps(message), qos=1, retain=False)
    pThread = threading.Timer(pInterval,publishDeviceEvent, args=[managedClient,pInterval])
    pThread.start()

# Define callback to carry out requested DME Action at Device Client Side
def doDMEAction(topic,data,reqId):
    global pThread
    global pInterval
    global managedClient
    print("In DME Action Callabck")
    print("Received data = %s" %data)
    print("Received topic = %s" %topic)
    if topic.find("installPlugin") != -1:
        print("DME Action requested is installPlugin")
    elif topic.find("updatePublishInterval") != -1:
        print("DME Action requested is updatePublishInterval")
        pInterval = data['d']['fields'][0]['value']
        print("Setting Device Event Publish Interval to %s Seconds" %pInterval)
        pThread.cancel()
        publishDeviceEvent(managedClient,pInterval)

    return True

#Define default publish interval and thread timer object
pInterval = 10
pThread = threading.Timer(pInterval,None)

# Declare and Define instances to None
managedClient=None
apiClient=None
appClient=None
options=None

# Define paths of valid config files
deviceFile="../../test/device.conf"
appConfFile="../../test/application.conf"

# Setup logger instance, not set to avoid log messages on std out
logger = logging.getLogger("dmeSample")
logger.setLevel(logging.NOTSET)

# Parse application conf file and create application instance
options = ibmiotf.application.ParseConfigFile(appConfFile)
appClient = ibmiotf.application.Client(options,logger)

# Create an apiClient Instance
apiClient = ibmiotf.api.ApiClient(options,logger)

# Parse device config file. Get deviceType and deviceId values from parsed data
options = ibmiotf.device.ParseConfigFile(deviceFile)
deviceType = options['type']
deviceId = options['id']

#Connect application client to platform and subscribe to all device events
appClient.connect()
appClient.deviceEventCallback = deviceEventCallback
appClient.subscribeToDeviceEvents()

# Define the DME Action Data in proper JSON format
# We are going to have 2 actions - installPlugin and updatePublishInterval
dmeData = { "bundleId": "example-dme-actions-v1",
            "displayName": {"en_US": "example-dme Actions v1"},
            "version": "1.0","actions": {
            "installPlugin": {
                                "actionDisplayName": { "en_US": "Install Plug-in"},
                                "parameters": [ { "name": "pluginURI",
                                                  "value": "http://example.dme.com",
                                                  "required": "true" } ] },
            "updatePublishInterval": {
                                "actionDisplayName": { "en_US": "Update Pubslish Interval"},
                                "parameters": [ { "name" : "publishInvertval",
                                                  "value": 5,
                                                  "required": "true" } ] }
                                        }
        }

# Create DME Package using API Method
addResult = apiClient.createDeviceManagementExtensionPkg(dmeData)

# Create ManagedClient Instance,connect
managedClient = ibmiotf.device.ManagedClient(options,logger)
managedClient.connect()

# Register above define function as DME callback function
managedClient.dmeActionCallback = doDMEAction;

# Send Manage Request to IoT Platform with indicating support of DME Actions by the Device
managedClient.manage(lifetime=0,supportDeviceMgmtExtActions=True,
                                bundleIds=['example-dme-actions-v1'])

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

# Publish Device Events with initial interval of 10 seconds
publishDeviceEvent(managedClient)

# Loop to run repeatedly to request for DME action based on user Input
# Loop quits when user enters letter q
updPubReqId = None
mgmtRequest = {"action": "example-dme-actions-v1/updatePublishInterval",
               "parameters": [{ "name": "publishInvertval",
                                 "value": 10,}],
               "devices": [{ "typeId": deviceType, "deviceId": deviceId }]}
while(True):
    print("Device events getting published for every %s seconds" %(pInterval))
    print("Enter Seconds to update Publish Interval / q to Quit")
    flag = raw_input("Waiting for your Input  :")
    if flag == 'q':
        pThread.cancel()
        break
    elif flag.isdigit():
        pInterval = int(flag)
        pThread.cancel()
        mgmtRequest['parameters'][0]['value'] = pInterval

        # Delete earlier DME request from platform if any exists
        if updPubReqId is not None:
            apiClient.deleteDeviceManagementRequest(updPubReqId)

        # Send DME request to update publish interval to Platform
        initResult = apiClient.initiateDeviceManagementRequest(mgmtRequest)
        updPubReqId = initResult['reqId']

    else:
        print("Invalid Input, try again!")


# It's time of clear of DME and DM request from the IoT Platform
apiClient.deleteDeviceManagementExtensionPkg('example-dme-actions-v1')
apiClient.deleteDeviceManagementRequest(reqId)
apiClient.deleteDeviceManagementRequest(updPubReqId)

# Get out of Manage Mode and Disconnect the clients
managedClient.unmanage()
managedClient.disconnect()
appClient.disconnect()
