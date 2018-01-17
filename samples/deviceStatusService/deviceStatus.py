# *****************************************************************************
# Copyright (c) 2018 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html 
#
# *****************************************************************************

import getopt
import json
import logging
import os
import signal
import sys
import time

from flask import Flask

try:
    import ibmiotf.application
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
    import ibmiotf.application

logger = logging.getLogger('wiotp.deviceconnstate')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

TABLE_ROW_TEMPLATE = "%-33s%-30s%s"
NEVER_CONNECTED_ACTION  = "Never Connected"

# The dict where the device connection state is stored deviceId -> status payload message
# No locking necessary 
deviceConnStateMap = {}

def usage():
    print(
        "deviceStatus: Basic Flask application to report device connection status." + "\n" +
        "\n" +
        "Options: " + "\n" +
        "  -h, --help          Display help information" + "\n" + 
        "  -o, --organization  Connect to the specified organization" + "\n" + 
        "  -i, --id            Application identifier" + "\n" + 
        "  -k, --key           API key used to connect" + "\n" + 
        "  -t, --token         Authentication token for the API key specified" + "\n" + 
        "  -c, --config        Load application configuration file (ignore -o, -i, -k, -t options)" + "\n" 
    )

#####################################################################################
# IoTP Functions
#####################################################################################
        
def statusCallback(status):
    if status.action == "Disconnect":
        summaryText = "%s %s (%s)" % (status.action, status.clientAddr, status.reason)
    else:
        summaryText = "%s %s" % (status.action, status.clientAddr)
    
    logger.debug(TABLE_ROW_TEMPLATE % (status.time.isoformat(), status.device, summaryText))
    if status.closeCode == 288 and not status.retained:
        # "Action":"Disconnect", "CloseCode":288,"Reason":"The client ID was reused."
        # These status messages are ignored because it is possible this application
        # will receive the disconnect status message after the connect status message,
        # which would led to the wrong status in the map.
        # (Both a connect and disconnect happen when a client ID is reused)
        # BUT if the message is retained, it reflects the true client state (edge case),
        # and we don't ignore the message.
        logger.debug("Ignoring client ID reused")
        return
    
    if status.clientId in deviceConnStateMap:
        if deviceConnStateMap[status.clientId].time > status.time:
            # With scalable applications (A;...) it is possible that an older status message
            # arrives after a newer one.
            logger.debug("Ignoring older status message; %s <= %s" % (deviceConnStateMap[status.clientId].time, status.time))
            return

    deviceConnStateMap[status.clientId] = status
            

def interruptHandler(signal, frame):
    client.disconnect()
    sys.exit(0)
    
#####################################################################################
# Flask Endpoints
#####################################################################################
app = Flask(__name__)

@app.route('/<type>/<id>', methods=['GET'])
def getDeviceStatus(type, id):
    clientId = "d:%s:%s:%s" % (client.organization, type, id)
    if clientId in deviceConnStateMap:
        status = deviceConnStateMap[clientId]
        return json.dumps(status.payload)
    else:
        neverConnectedStatus = {"ClientID": clientId, "Action": NEVER_CONNECTED_ACTION}
        return json.dumps(neverConnectedStatus)
    

#####################################################################################
# MAIN
#####################################################################################
if __name__ == "__main__":
    
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:o:i:k:t:c:p:", ["help", "org=", "id=", "key=", "token=", "config=", "port"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(2)
        
    organization = None
    appId = None
    authMethod = None
    authKey = None
    authToken = None
    configFilePath = None
    port = 5000
    
    for o, a in opts:
        if o in ("-o", "--organization"):
            organization = a
        elif o in ("-i", "--id"):
            appId = a
        elif o in ("-k", "--key"):
            authMethod = "apikey"
            authKey = a
        elif o in ("-t", "--token"):
            authToken = a
        elif o in ("-c", "--cfg"):
            configFilePath = a
        elif o in ("-p", "--port"):
            port = int(a)
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        else:
            assert False, "unhandled option" + o
    
    client = None
    if configFilePath is not None:
        options = ibmiotf.application.ParseConfigFile(configFilePath)
    else:
        options = {"org": organization, "id": appId, "auth-method": authMethod, "auth-key": authKey, "auth-token": authToken}
    try:
        client = ibmiotf.application.Client(options, logHandlers = ch)
        signal.signal(signal.SIGINT, interruptHandler)
        client.connect()
        client.deviceStatusCallback = statusCallback
        client.subscribeToDeviceStatus()
    except ibmiotf.ConfigurationException as e:
        print(str(e))
        sys.exit()
    except ibmiotf.UnsupportedAuthenticationMethod as e:
        print(str(e))
        sys.exit()
    except ibmiotf.ConnectionException as e:
        print(str(e))
        sys.exit()

    
    app.logger.addHandler(ch)
    app.run(host='0.0.0.0', port=port)
