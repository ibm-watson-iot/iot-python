#Python Command Line Interface (CLI) for Watson IoT

A basic command line interface for interacting with your Watson IoT organization.

## Example Usage

```
[me@localhost ~]$ python cli.py -c app.cfg device list 12
  1 LCT003:00-17-80-01-10-35-5a-13-0b                           Registered 12 days ago by a-hld45t-b6v5f3uf92
  2 LCT003:00-17-80-01-10-35-1b-69-0b                           Registered 12 days ago by a-hld45t-b6v5f3uf92
  3 LCT003:00-17-80-01-10-35-35-00-0b                           Registered 12 days ago by a-hld45t-b6v5f3uf92
  4 MyPiGateway:000000008cf12aff                                Registered 81 days ago by ibmer@uk.ibm.com
  5 hursley-devices:psbob                                       Registered 143 days ago by ibmer@uk.ibm.com
  6 hursley-devices:raspberry-pi-1                              Registered 424 days ago by a-hld45t-nreszl3hzx
  7 hursley-devices:ti-bbst-1                                   Registered 424 days ago by a-hld45t-nreszl3hzx
  9 smartthings:978f19aa-b455-4e27-bd02-cf70d2b3d2eb            Registered 3 days ago by a-hld45t-nreszl3hzx
  9 smartthings:cb21adee-11a9-4217-8f61-427ae4622294            Registered 3 days ago by a-hld45t-nreszl3hzx
 10 smartthings:d070392e-4307-4307-a3d8-be7a2fd612d9            Registered 3 days ago by a-hld45t-nreszl3hzx
 11 smartthings:eefc5e14-5d57-419c-afe0-1b5d23ec420b            Registered 3 days ago by a-hld45t-nreszl3hzx
 12 smartthings:f45909dc-8747-4781-a26b-51ab1b234ae1            Registered 3 days ago by a-hld45t-nreszl3hzx
```

## Supported Commands:

### device list MAX_RESULTS
Prints a list of all (up to ``MAX_RESULTS``) registered devices

```
[me@localhost ~]$ python cli.py -c app-production.cfg device list 12
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
