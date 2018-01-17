# Python Device Status Service

Sample code for a simple service to answer requests for current device connection status via REST API.  The program connects to IoTP and subscribes to device
status topic `iot-2/type/+/id/+/mon`.  It will incur data transfer   
It uses the retained messages on this topic to populate an in-memory map of device ID to status and then continues to process live status messages to maintain the map.  The
map is used by a Flask endpoint to answer requests for current device connection status.

### Using an application configuration file
Create a file named application.cfg in the simpleApp directory and insert the credentials for your API key as well as an ID that is unique to your application instance. 
```
[application]
org=$orgId
id=myServiceStatusApp
auth-method=apikey
auth-key=$key
auth-token=$token
```

```
python deviceStatus.py -c ~/application.cfg -p 5000
2018-01-02 17:03:09,116 - ibmiotf.application.Client - INFO - Connected successfully: a:7gnple:myServiceStatusApp
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
2018-01-02 17:03:09,269 - wiotp.devicestatus - DEBUG - 2017-11-23T17:03:15.672000+00:00 type2:ps2                     Disconnect 195.212.29.65 (None)
2018-01-02 17:03:09,269 - wiotp.devicestatus - DEBUG - 2017-11-24T15:00:27.457000+00:00 pstype:psbob                  Disconnect 81.101.46.216 (None)
2018-01-02 17:03:09,270 - wiotp.devicestatus - DEBUG - 2018-01-02T17:02:15.890000+00:00 type1:ps1                     Connect 195.212.29.65
```

### Using command line options
```
python deviceStatus.py -o $orgId -i myApplication -k $key -t $token -p 5000
```

### Using the service once it is running
```
curl localhost:5000/type1/ps1
```

Response is JSON and will come in 3 flavours, always with `ClientID` and `Action` fields:

#### Device is Connected
```{"ClientAddr": "195.212.29.65", "Protocol": "mqtt3", "Secure": false, "Durable": false, "ClientID": "d:7gnple:type1:ps1", "Time": "2018-01-02T16:51:10.558Z", "Action": "Connect", "Port": 1883}```

#### Device is Disconnected
```{"WriteMsg": 0, "ClientAddr": "195.212.29.65", "Protocol": "mqtt3", "Secure": false, "CloseCode": 91, "ClientID": "d:7gnple:type1:ps1", "ReadMsg": 0, "Reason": "Connection closed by client", "ReadBytes": 127, "ConnectTime": "2018-01-02T16:51:10.557Z", "Time": "2018-01-02T16:52:14.296Z", "Action": "Disconnect", "WriteBytes": 9, "Port": 1883}```

#### Device Never Connected
```{"Action": "Never Connected", "ClientID": "d:7gnple:type1:ps11"}```

In addition to actually having never connected, a device may be reported as never connected if it disconnected (or connected) more than 45 days ago 
because this is when messages expire (unless this app still has a map populated with the expired status message).

### Possible Enhancements
1. The default subscription buffer for a normal application is 5000.  For a scalable application it is 50,000.  Messages on the mon topic are retained,
so if there are more than 5000 retained messages (more than 5000 devices) the initial map population will be incomplete because not all the retained 
messages can be received.  Use scalable subscriber to get a bigger buffer.  Optionally also use cleanSession `false` and or partion the topic space to 
further divide up work and avoid filling the subscription buffer on startup.
2. Persist the map used to answer the connection status somewhere (file/DB/XtremeScale) and use that to rebuild the in memory map on startup.  Because messages
expire after 45 days, a daily merge of the current map into the persistence would be sufficient rather than writing every connect/disconnect event. 
3. The in memory map should be able to store many devices and cope with frequent connects and disconnects but eventually it may need to be scaled.  Mulitple instances
of a scalable application would be needed.  Status messages would need to be persisted somewhere where it can be queried. 
