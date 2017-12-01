#Python Simple Device

Sample code for a very basic appliation which publishes events and subscribes to commands on the  IBM Internet of Things service.

## QuickStart Usage
Simply run to send an event to the platform:
```
[me@localhost simpleDevice]$ python simpleDevice.py 
2017-12-01 10:06:19,102   ibmiotf.device.Client      INFO    Connected successfully: d:quickstart:simpleDev:ab1fdbb3-73eb-49c9-80c9-1443740580fd
Confirmed event 0 received by IoTF

2017-12-01 10:06:20,146   ibmiotf.device.Client      INFO    Disconnected from the IBM Watson IoT Platform
2017-12-01 10:06:20,147   ibmiotf.device.Client      INFO    Closed connection to the IBM Watson IoT Platform

```

## Registered Organization Usage
Once you have access to an auth token for a device in an organization in the Internet of Things Cloud additional the device can be used to send events to that organization: 

###Using an device configuration file
Create a file named device.cfg in the simpleDevice directory and insert the org, device type, device id and the authentication token:. 
```
[device]
org=$org
type=$type
id=$id
auth-method=token
auth-token=$token
clean-session=true

```

```
[jon@localhost simpleDevice]$ python simpleDevice.py -c device.cfg 
2017-12-01 10:23:36,796   ibmiotf.device.Client      INFO    Connected successfully: d:<org>:<type>:<deviceid>
Confirmed event 0 received by IoTF

2017-12-01 10:23:37,822   ibmiotf.device.Client      INFO    Disconnected from the IBM Watson IoT Platform
2017-12-01 10:23:37,823   ibmiotf.device.Client      INFO    Closed connection to the IBM Watson IoT Platform

```
Or to send 100 messages, 1 every two seconds:
```
[me@localhost simpleDevice]$ python simpleDevice.py -c device.cfg -N 100 -D 2
```

###Using command line options
```
[me@localhost ~] python simpleDevice.py -o $orgId -T $deviceType -I $deviceid -t $token
```

### Additional command line options
By default the device will send one message and then disconnect. Two options can be used to send more messages (and stay connected longer)
   * -N : total number of messages (default 1)
   * -D : Delay in seconds between message (default 1)

####Example: Send 10 messages, one every 2 seconds
```
[me@localhost ~] python simpleDevice.py -o $orgId -T $deviceType -I $deviceid -t $token -N 10 -D 2
```
