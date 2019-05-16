# IBM Watson IoT Platform PSUtil Device Client

Device code for sending system utilization data to IBM Watson IoT Platform, powered by [giampaolo/psutil](https://github.com/giampaolo/psutil).

> psutil (process and system utilities) is a cross-platform library for retrieving information on running processes and system utilization (CPU, memory, disks, network, sensors) in Python.

The following data points are collected:
 * CPU utilization (%)
 * Memory utilization (%)
 * Outbound network utilization across all network interfaces (KB/s)
 * Inbound network utilization across all network interfaces (KB/s)


## Event Format

- `name` obtained using `platform.node()` from the [Python standard library](https://docs.python.org/3/library/platform.html), can be overriden using `-n` parameter
- `cpu` obtained from `psutil.cpu_percent()`
- `mem` obtained from `psutil.virtual_memory().percent`
- `network.up` calculated using `psutil.net_io_counters()`
- `network.down` calculated using `psutil.net_io_counters()`


## Docker

The easiest way to test out the sample is via the [wiotp/psutil](https://cloud.docker.com/u/wiotp/repository/docker/wiotp/psutil) Docker image provided and the `--quickstart` command line option.

```
$ docker run -d --name psutil wiotp/psutil --quickstart
psutil
$ docker logs -tf psutil
2019-05-07T11:09:19.672513500Z 2019-05-07 11:09:19,671   wiotp.sdk.device.client.DeviceClient  INFO    Connected successfully: d:quickstart:sample-iotpsutil:242ac110002
```

To connect as a registered device in your organization you must set the following environment variables: `WIOTP_IDENTITY_ORGID`, `WIOTP_IDENTITY_TYPEID`, `WIOTP_IDENTITY_DEVICEID`, and `WIOTP_AUTH_TOKEN` in the container's environment.

```
$ export WIOTP_IDENTITY_ORGID=myorgid
$ export WIOTP_IDENTITY_TYPEID=mytypeid
$ export WIOTP_IDENTITY_DEVICEID=mydeviceid
$ export WIOTP_AUTH_TOKEN=myauthtoken
$ docker run -d -e WIOTP_IDENTITY_ORGID -e WIOTP_IDENTITY_ORGID -e WIOTP_AUTH_TOKEN --name psutil wiotp/psutil
psutil
$ docker logs -tf psutil
2019-05-07T11:09:19.672513500Z 2019-05-07 11:09:19,671   wiotp.sdk.device.client.DeviceClient  INFO    Connected successfully: d:myorgid:mytypeid:mydeviceid
```


## Installation
Installation across all OS's is pretty much the same:

- Install any necessary system packages missing from the host (in order to [install psutil on Windows](https://github.com/giampaolo/psutil/blob/master/INSTALL.rst#windows) you'll need Visual Studio installed)
- Install the `wiotp-sdk` and `psutil` python modules using `pip`
- [Download](https://github.com/ibm-watson-iot/iot-python/archive/master.zip) the sample code from GitHub
- Run the sample

The example below shows the setup process on **Raspbian** (Raspberry Pi).

```
pi@raspberrypi ~ $ sudo apt-get update
pi@raspberrypi ~ $ sudo apt-get install python-dev python-pip
pi@raspberrypi ~ $ sudo pip install wiotp-sdk psutil
pi@raspberrypi ~ $ wget https://github.com/ibm-watson-iot/iot-python/archive/master.zip
pi@raspberrypi ~ $ unzip master.zip
pi@raspberrypi ~ $ cd iot-python-master/samples/psutil/src
pi@raspberrypi ~ $ python iotpsutil.py --quickstart
(Press Ctrl+C to disconnect)

```


## Support Application
A sample application is provided that allows commands to be sent to the device when used in registered mode only.

The application provides two functions:
 * Adjust the publish rate of the psutil device sample 
 * Print a debug message to the console on the device

```
python psutilApp.py -c application.yaml
Command List:
 1. Change target device
(Ctrl+C to disconnect)
None:None>1

 0. Manually enter type and ID
 1. 001:psutil
Choose Device >1

Command List:
 1. Change target device
 2. Set publish rate of psutil:001
 3. Send message to console of psutil:001
(Ctrl+C to disconnect)
psutil:001>2

Enter Interval (seconds) >10

Command List:
 1. Change target device
 2. Set publish rate of psutil:001
 3. Send message to console of psutil:001
(Ctrl+C to disconnect)
psutil:001>
```
