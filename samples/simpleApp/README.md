#Python Simple Application

Sample code for a very basic appliation which subscribes to both events and connectivity status from one or more devices connected to the IBM Internet of Things service.

## QuickStart Usage
Ssimply provide the device ID of your QuickStart connected device: 
```
[me@localhost ~]$ python simpleApp.py -I 112233445566
Status of device [sample-iotpsutil:112233445566] changed to {"ClientAddr": "86.178.101.88", "Protocol": "mqtt-tcp", "ClientID": "d:quickstart:sample-iotpsutil:cc52af80cf38", "ConnectTime": "2014-07-05T15:57:39.280-04:00", "Time": "2014-07-05T15:57:39.283-04:00", "Action": "Connect", "Port": 1883}
json event 'psutil' received from device [sample-iotpsutil:112233445566]: {"mem": 67.1, "network_up": 0.99, "cpu": 3.3, "name": "My Laptop", "network_down": 0.86}
json event 'psutil' received from device [sample-iotpsutil:112233445566]: {"mem": 67.1, "network_up": 0.63, "cpu": 1.2, "name": "My Laptop", "network_down": 0.58}
json event 'psutil' received from device [sample-iotpsutil:112233445566]: {"mem": 67.2, "network_up": 0.65, "cpu": 1.2, "name": "My Laptop", "network_down": 0.47}
json event 'psutil' received from device [sample-iotpsutil:112233445566]: {"mem": 67.2, "network_up": 1.15, "cpu": 13.1, "name": "My Laptop", "network_down": 0.63}
json event 'psutil' received from device [sample-iotpsutil:112233445566]: {"mem": 67.2, "network_up": 0.65, "cpu": 4.2, "name": "My Laptop", "network_down": 0.64}
json event 'psutil' received from device [sample-iotpsutil:112233445566]: {"mem": 67.2, "network_up": 0.51, "cpu": 1.0, "name": "My Laptop", "network_down": 0.47}
```

## Registered Organization Usage
Once you have access to an API Key for an organization in the Internet of Things Cloud additional the application can be used to display events from multiple devices: 

###Using an application configuration file
Create a file named application.cfg in the simpleApp directory and insert the credentials for your API key as well as an ID that is unique to your application instance. 
```
org=$orgId
id=myApplication
auth-method=apikey
auth-key=$key
auth-token=$token
```

```
[me@localhost ~]C:\Users\David\Documents\GitHub\iot-python\samples\simpleApp>python simpleApp.py -c application.cfg
Status of device [psutil:001] changed to {"ClientAddr": "1.2.3.4", "Protocol": "mqtt-tcp", "ClientID": "d:aaaaa:psutil:001", "User": "use-token-auth", "Time": "2014-07-05T16:09:26.161-04:00", "Action": "Connect", "ConnectTime": "2014-07-05T16:09:26.161-04:00", "Port": 1883}
json event 'psutil' received from device [psutil:001]: {"mem": 67.2, "network_up": 1.32, "cpu": 1.7, "name": "My Laptop", "network_down": 0.38}
json event 'psutil' received from device [psutil:001]: {"mem": 67.1, "network_up": 0.73, "cpu": 2.2, "name": "My Laptop", "network_down": 1.05}
json event 'psutil' received from device [psutil:001]: {"mem": 67.1, "network_up": 0.51, "cpu": 1.3, "name": "My Laptop", "network_down": 0.47}
```

###Using command line options
```
[me@localhost ~]C:\Users\David\Documents\GitHub\iot-python\samples\simpleApp>python simpleApp.py -o $orgId -i myApplication -k $key -t $token
Status of device [psutil:001] changed to {"ClientAddr": "1.2.3.4", "Protocol": "mqtt-tcp", "ClientID": "d:aaaaa:psutil:001", "User": "use-token-auth", "Time": "2014-07-05T16:09:26.161-04:00", "Action": "Connect", "ConnectTime": "2014-07-05T16:09:26.161-04:00", "Port": 1883}
json event 'psutil' received from device [psutil:001]: {"mem": 67.2, "network_up": 1.32, "cpu": 1.7, "name": "My Laptop", "network_down": 0.38}
json event 'psutil' received from device [psutil:001]: {"mem": 67.1, "network_up": 0.73, "cpu": 2.2, "name": "My Laptop", "network_down": 1.05}
json event 'psutil' received from device [psutil:001]: {"mem": 67.1, "network_up": 0.51, "cpu": 1.3, "name": "My Laptop", "network_down": 0.47}
```

### Additional Options
By default the application will attempt to subscribe to all events from all devices in the organization.  Three options exist to control the scope of the application:
 * Device Type
 * Device Id
 * Event

####Example 1: Subscribe to all events from all connected devices
```
[me@localhost ~]C:\Users\David\Documents\GitHub\iot-python\samples\simpleApp>python simpleApp.py -o $orgId -i myApplication -k $key -t $token
```

####Example 2: Subscribe to all events from all connected devices of a specific type
```
[me@localhost ~]C:\Users\David\Documents\GitHub\iot-python\samples\simpleApp>python simpleApp.py -o $orgId -i myApplication -k $key -t $token -T $deviceType
```

####Example 3: Subscribe to all events from a specific device
```
[me@localhost ~]C:\Users\David\Documents\GitHub\iot-python\samples\simpleApp>python simpleApp.py -o $orgId -i myApplication -k $key -t $token -T $deviceType -I deviceId
```

####Example 4: Subscribe a specific event sent from any connected device
```
[me@localhost ~]C:\Users\David\Documents\GitHub\iot-python\samples\simpleApp>python simpleApp.py -o $orgId -i myApplication -k $key -t $token -E $event
```
