#Python Command Line Interface (CLI) for IOT Foundation
A basic command line interface for interacting with your IoT Foundation organization.

## Example Usage

```
[me@localhost ~]$ python cli.py -c app-production.cfg device list
d:hld45t:test:001                       Registered 14 days ago by ibmer@uk.ibm.com
d:hld45t:generic:intel-galileo-1        Registered 208 days ago by ibmer@uk.ibm.com
d:hld45t:generic:mbed-k64f-1            Registered 209 days ago by a-hld45t-norczl3hzx
d:hld45t:generic:mbed-lpc1768-1         Registered 209 days ago by a-hld45t-norczl3hzx
d:hld45t:generic:psutil                 Registered 257 days ago by ibmer@uk.ibm.com
d:hld45t:generic:raspberry-pi-1         Registered 210 days ago by a-hld45t-norczl3hzx
d:hld45t:generic:sigar                  Registered 166 days ago by ibmer@uk.ibm.com
d:hld45t:generic:ti-bbst-1              Registered 210 days ago by a-hld45t-norczl3hzx
d:hld45t:generic2:intel-galileo-2       Registered 153 days ago by ibmer2@in.ibm.com
d:hld45t:generic2:mbed-k64f-2           Registered 153 days ago by ibmer2@in.ibm.com
d:hld45t:generic2:mbed-lpc1768-2        Registered 153 days ago by ibmer2@in.ibm.com
d:hld45t:generic2:raspberry-pi-2        Registered 153 days ago by ibmer2@in.ibm.com
d:hld45t:generic2:ti-cc3200-1           Registered 153 days ago by ibmer2@in.ibm.com
d:hld45t:sdfgh:dfghgfds                 Registered 12 days ago by ibmer@uk.ibm.com
```

## Supported Commands:

### device list
Prints a list of all registered devices

```
[me@localhost ~]$ python cli.py -c app-production.cfg device list
```


### device add TYPE ID
Registers a new device with an auto-generated authentication token

```
[me@localhost ~]$ python cli.py -c app-production.cfg device add myType myId
```


### device get TYPE ID
Prints the details of a specific registered device

```
[me@localhost ~]$ python cli.py -c app-production.cfg device get myType myId
```


### device remove TYPE ID
Revoke the registration of the specified device 

```
[me@localhost ~]$ python cli.py -c app-production.cfg device remove myType myId
```


### device update TYPE ID METADATA
Update the device registration record with the provided metadata

```
[me@localhost ~]$ python cli.py -c app-production.cfg device update myType myId '{"colour": "red"}'
```


### historian [TYPE [ID]]
Retrieve historical events.  If no options are supplied it will return the most recent 100 events across all devices.  If type is suppied the result set will be restricted to only devices of that type.  If both type and id are set then only events from a single device will be returned

```
[me@localhost ~]$ python cli.py -c app-production.cfg historian
```
