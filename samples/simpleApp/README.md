# Python Simple Application
Sample code for a very basic appliation which subscribes to both events and connectivity status from one or more devices connected to the IBM Internet of Things service.

## Using an application configuration file
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

## Using command line options
```
[me@localhost ~] python simpleApp.py -o $orgId -i myApplication -k $key -t $token
```

## Additional command line options
By default the application will attempt to subscribe to all events from all devices in the organization.  Three options exist to control the scope of the application:
 * Device Type
 * Device Id
 * Event

### Example 1: Subscribe to all events from all connected devices
```
[me@localhost ~] python simpleApp.py -o $orgId -i myApplication -k $key -t $token
```

### Example 2: Subscribe to all events from all connected devices of a specific type
```
[me@localhost ~] python simpleApp.py -o $orgId -i myApplication -k $key -t $token -T $deviceType
```

### Example 3: Subscribe to all events from a specific device
```
[me@localhost ~] python simpleApp.py -o $orgId -i myApplication -k $key -t $token -T $deviceType -I deviceId
```

### Example 4: Subscribe a specific event sent from any connected device
```
[me@localhost ~] python simpleApp.py -o $orgId -i myApplication -k $key -t $token -E $event
```
