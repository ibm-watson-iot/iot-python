# *****************************************************************************
# Copyright (c) 2016 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html 
#
# Contributors:
#   Amit M Mangalvedkar - Initial Contribution
# *****************************************************************************

import getopt
import time
import sys
import platform
import json
import signal
import subprocess
from uuid import getnode as get_mac


try:
    import ibmiotf.gateway
except ImportError:
    # This part is only required to run the sample from within the samples
    # directory when the module itself is not installed.
    #
    # If you have the module installed, just use "import ibmiotf"
    import os
    import inspect
    cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../../src")))
    if cmd_subfolder not in sys.path:
        sys.path.insert(0, cmd_subfolder)
    import ibmiotf.gateway



def interruptHandler(signal, frame):
    client.disconnect()
    sys.exit(0)


def commandProcessor(cmd):
    print("Command received: %s" % cmd.data)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, interruptHandler)

    organization = ""
    gatewayType = ""
    gatewayId = ""
    gatewayName = platform.node()
    authMethod = "token"
    authToken = ""
    configFilePath = None
        
    # Seconds to sleep so as to check the error state
    interval = 20


    client = None
    simpleGatewayInfo = ibmiotf.gateway.DeviceInfo()
    simpleGatewayInfo.description = gatewayName 
    simpleGatewayInfo.deviceClass = platform.machine()
    simpleGatewayInfo.manufacturer = platform.system()
    simpleGatewayInfo.fwVersion = platform.version()
    simpleGatewayInfo.hwVersion = None
    simpleGatewayInfo.model = None
    simpleGatewayInfo.serialNumber = None

    options = {"org": organization, "type": gatewayType, "id": gatewayId, "auth-method": authMethod, "auth-token": authToken}

    try:
        #By default the client is an unmanaged client and on disconnecting it again becomes unmanaged
        #Thats why we need to make it a managed gateway
        client = ibmiotf.gateway.ManagedClient(options, logHandlers=None, deviceInfo=simpleGatewayInfo)
        client.commandCallback = commandProcessor
        client.connect()
        
        # manage() method sends request to DM server to make the device a managed device
        client.manage(3600, supportDeviceActions=True, supportFirmwareActions=True).wait()
        
    except ibmiotf.ConfigurationException as e:
        print(str(e))
        sys.exit()
    except ibmiotf.UnsupportedAuthenticationMethod as e:
        print(str(e))
        sys.exit()
    except ibmiotf.ConnectionException as e:
        print(str(e))
        sys.exit()

    
    # Initiate DM action to update the geo location of the device, but don't wait (async) for it to complete
    client.setLocation(longitude=85, latitude=85, accuracy=100)
    print("Location has been set")
    
    # Make a GET call to https://orgid.internetofthings.ibmcloud.com/api/v0002/device/types/{gateway type}/devices/{gateway id}/location to test
    
    
    # Initiate DM action to set error codes to 1, wait for it to be completed (sync) and then clear all error codes
    client.setErrorCode(1).wait(10)
    print("Error code setting returned back")
    time.sleep(interval)
    client.clearErrorCodes()
    
    client.disconnect()
    print("(Press Ctrl+C to disconnect)")
