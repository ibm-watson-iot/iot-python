# Python Simple Device

Sample code for a very basic appliation which publishes events and subscribes to commands on the IBM Watson Internet of Things platform.

## Using an device configuration file
Create a file named device.cfg in the simpleDevice directory and insert the org, device type, device id and the authentication token:.

```
    identity:
      orgId: $InsertOrgID
      typeId: $InsertDeviceType
      deviceId: $InsertDeviceID
    auth:
      token: $InsertAuthenticationToken
```

```
[jon@localhost simpleDevice]$ python3 simpleDevice.py -c device.cfg
wiotp.sdk.device.client.DeviceClient  INFO    Connected successfully: d:<OrgID>:<DeviceType>:<DeviceID>
Confirmed event 0 received by WIoTP

2019-11-20 11:24:17,706   wiotp.sdk.device.client.DeviceClient  INFO    Disconnected from IBM Watson IoT Platform
2019-11-20 11:24:17,707   wiotp.sdk.device.client.DeviceClient  INFO    Closed connection to the IBM Watson IoT Platform

```
Or to send 100 messages, 1 every two seconds:
```
[me@localhost simpleDevice]$ python3 simpleDevice.py -c device.cfg -N 100 -D 2
```

###Using command line options
```
[me@localhost ~] python3 simpleDevice.py -o $orgId -T $deviceType -I $deviceid -t $token
```

## Additional command line options
By default the device will send one message and then disconnect. Two options can be used to send more messages (and stay connected longer)
   * -N : total number of messages (default 1)
   * -D : Delay in seconds between message (default 1)

####Example: Send 10 messages, one every 2 seconds
```
[me@localhost ~] python3 simpleDevice.py -o $orgId -T $deviceType -I $deviceid -t $token -N 10 -D 2
```
