# Python Simple Application

Sample code for a very basic appliation which subscribes to both events and connectivity status from one or more devices connected to the IBM Internet of Things service.

## QuickStart Usage
Ssimply provide the device ID of your QuickStart connected device: 
```
[me@localhost ~]$ python simpleApp.py -I 112233445566
(Press Ctrl+C to disconnect)
=============================================================================
Timestamp                        Device                        Event
=============================================================================
2014-07-07T12:04:32.296000+00:00 sample-iotpsutil:112233445566 psutil: {"mem": 73.2, "network_up": 0.75, "cpu": 0.2, "name": "W520", "network_down": 0.44}
2014-07-07T07:03:55.202000-04:00 sample-iotpsutil:112233445566 Connect 1.2.3.4
2014-07-07T12:04:33.300000+00:00 sample-iotpsutil:112233445566 psutil: {"mem": 73.2, "network_up": 0.42, "cpu": 5.4, "name": "W520", "network_down": 1.08}
2014-07-07T12:04:34.304000+00:00 sample-iotpsutil:112233445566 psutil: {"mem": 73.2, "network_up": 0.27, "cpu": 0.0, "name": "W520", "network_down": 0.29}
2014-07-07T12:04:35.308000+00:00 sample-iotpsutil:112233445566 psutil: {"mem": 73.2, "network_up": 0.27, "cpu": 1.9, "name": "W520", "network_down": 0.29}
2014-07-07T12:04:36.312000+00:00 sample-iotpsutil:112233445566 psutil: {"mem": 73.2, "network_up": 0.27, "cpu": 0.4, "name": "W520", "network_down": 0.35}
2014-07-07T12:04:37.317000+00:00 sample-iotpsutil:112233445566 psutil: {"mem": 73.2, "network_up": 0.27, "cpu": 0.4, "name": "W520", "network_down": 0.29}
2014-07-07T12:04:38.321000+00:00 sample-iotpsutil:112233445566 psutil: {"mem": 73.2, "network_up": 0.27, "cpu": 0.2, "name": "W520", "network_down": 0.59}
2014-07-07T07:04:37.550000-04:00 sample-iotpsutil:112233445566 Disconnect 195.212.29.68 (The connection has completed normally.)
2014-07-07T07:11:47.779000-04:00 sample-iotpsutil:112233445566 Connect 1.2.3.4
2014-07-07T12:11:49.732000+00:00 sample-iotpsutil:112233445566 psutil: {"mem": 75.4, "network_up": 0.12, "cpu": 0.2, "name": "W520", "network_down": 0.0}
2014-07-07T12:11:50.736000+00:00 sample-iotpsutil:112233445566 psutil: {"mem": 75.4, "network_up": 0.38, "cpu": 1.5, "name": "W520", "network_down": 0.58}
2014-07-07T12:11:51.740000+00:00 sample-iotpsutil:112233445566 psutil: {"mem": 75.4, "network_up": 0.38, "cpu": 5.4, "name": "W520", "network_down": 0.63}
2014-07-07T12:11:52.745000+00:00 sample-iotpsutil:112233445566 psutil: {"mem": 75.4, "network_up": 0.27, "cpu": 3.9, "name": "W520", "network_down": 0.29}
2014-07-07T07:11:52.186000-04:00 sample-iotpsutil:112233445566 Disconnect 1.2.3.4 (The connection has completed normally.)
```

## Registered Organization Usage
Once you have access to an API Key for an organization in the Internet of Things Cloud additional the application can be used to display events from multiple devices: 

### Using an application configuration file
Create a file named application.cfg in the simpleApp directory and insert the credentials for your API key as well as an ID that is unique to your application instance. 
```
[application]
org=$orgId
id=myApplication
auth-method=apikey
auth-key=$key
auth-token=$token
```

```
[me@localhost ~] python simpleApp.py -c application.cfg
(Press Ctrl+C to disconnect)
=============================================================================
Timestamp                        Device                        Event
=============================================================================
2014-07-07T07:16:44.826000-04:00 psutil:001                    Connect 1.2.3.4
2014-07-07T12:16:53.813000+00:00 psutil:001                    psutil: {"mem": 75.1, "network_up": 0.89, "cpu": 2.0, "name": "W520", "network_down": 1.1}
2014-07-07T12:16:54.817000+00:00 psutil:001                    psutil: {"mem": 75.1, "network_up": 0.27, "cpu": 0.2, "name": "W520", "network_down": 0.29}
2014-07-07T12:16:55.821000+00:00 psutil:001                    psutil: {"mem": 75.0, "network_up": 0.27, "cpu": 1.8, "name": "W520", "network_down": 0.29}
```

### Using command line options
```
[me@localhost ~] python simpleApp.py -o $orgId -i myApplication -k $key -t $token
```

### Additional command line options
By default the application will attempt to subscribe to all events from all devices in the organization.  Three options exist to control the scope of the application:
 * Device Type
 * Device Id
 * Event

#### Example 1: Subscribe to all events from all connected devices
```
[me@localhost ~] python simpleApp.py -o $orgId -i myApplication -k $key -t $token
```

#### Example 2: Subscribe to all events from all connected devices of a specific type
```
[me@localhost ~] python simpleApp.py -o $orgId -i myApplication -k $key -t $token -T $deviceType
```

#### Example 3: Subscribe to all events from a specific device
```
[me@localhost ~] python simpleApp.py -o $orgId -i myApplication -k $key -t $token -T $deviceType -I deviceId
```

#### Example 4: Subscribe a specific event sent from any connected device
```
[me@localhost ~] python simpleApp.py -o $orgId -i myApplication -k $key -t $token -E $event
```
