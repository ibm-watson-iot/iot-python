# IBM Watson IoT Platform PSUtil Device Client

Device code for sending system utilization data to IBM Watson IoT Platform, powered by [giampaolo/psutil](https://github.com/giampaolo/psutil).

> psutil (process and system utilities) is a cross-platform library for retrieving information on running processes and system utilization (CPU, memory, disks, network, sensors) in Python.

The following data points are collected:
 * CPU utilization (%)
 * Memory utilization (%)
 * Outbound network utilization across all network interfaces (KB/s)
 * Inbound network utilization across all network interfaces (KB/s)
 * Disk write rate (KB/s)
 * Disk read rate (KB/s)

A tutorial guiding you through the process of setting up this sample on a Raspberry Pi is published on [IBM Developer developerWorks Recipes](https://developer.ibm.com/recipes/tutorials/raspberry-pi-4/)

## Event Format

- `name` obtained using `platform.node()` from the [Python standard library](https://docs.python.org/3/library/platform.html), can be overriden using `-n` parameter
- `cpu` obtained from `psutil.cpu_percent()`
- `mem` obtained from `psutil.virtual_memory().percent`
- `network.up` calculated using `psutil.net_io_counters()`
- `network.down` calculated using `psutil.net_io_counters()`
- `disk.write` calculated using `psutil.disk_io_counters()`
- `disk.read` calculated using `psutil.disk_io_counters()`

## Before you Begin

Register a device with IBM Watson IoT Platform.  

For information on how to register devices, see the [Connecting Devices](https://www.ibm.com/support/knowledgecenter/SSQP8H/iot/platform/iotplatform_task.html) topic in the IBM Watson IoT Platform documentation.  

At the end of the registration process, make a note of the following parameters: 
   - Organization ID
   - Type ID
   - Device ID
   - Authentication Token  

## Docker

The easiest way to test out the sample is via the [wiotp/psutil](https://cloud.docker.com/u/wiotp/repository/docker/wiotp/psutil) Docker image provided and the `--quickstart` command line option.

The resource requirements for this container are tiny, if you use the accompanying helm chart it is by default confiugured with a request of 2m CPU + 18Mi memory, and  limits set to 4m cpu + 24Mi memory.

```
$ docker run -d --name psutil wiotp/psutil --quickstart
psutil
$ docker logs -tf psutil
2019-05-07T11:09:19.672513500Z 2019-05-07 11:09:19,671   wiotp.sdk.device.client.DeviceClient  INFO    Connected successfully: d:quickstart:sample-iotpsutil:242ac110002
```

To connect as a registered device in your organization you must set the following environment variables in the container's environment. These variables correspond to the device parameters for your registered device: 
- `WIOTP_IDENTITY_ORGID`
- `WIOTP_IDENTITY_TYPEID`
- `WIOTP_IDENTITY_DEVICEID`
- `WIOTP_AUTH_TOKEN`.

The following example shows how to set the environment variables:

```
$ export WIOTP_IDENTITY_ORGID=myorgid
$ export WIOTP_IDENTITY_TYPEID=mytypeid
$ export WIOTP_IDENTITY_DEVICEID=mydeviceid
$ export WIOTP_AUTH_TOKEN=myauthtoken
$ docker run -d -e WIOTP_IDENTITY_ORGID -e WIOTP_IDENTITY_TYPEID -e WIOTP_IDENTITY_DEVICEID -e WIOTP_AUTH_TOKEN --name psutil wiotp/psutil
psutil
$ docker logs -tf psutil
2019-05-07T11:09:19.672513500Z 2019-05-07 11:09:19,671   wiotp.sdk.device.client.DeviceClient  INFO    Connected successfully: d:myorgid:mytypeid:mydeviceid
```

## Kubernetes & Helm

A [helm chart](https://github.com/ibm-watson-iot/iot-python/tree/master/samples/psutil/helm/psutil) is available if that is your preferred way to Docker.  The chart accepts the standard format device configuration file as a Helm values file:

```
$ helm repo add wiotp https://ibm-watson-iot.github.io/helm/charts/
$ helm install psutil-mydevice wiotp/psutil --values path/to/mydevice.yaml
```

If you provide no additional values the chart will deploy in a configuration supporting Quickstart by default:

```
$ helm repo add wiotp https://ibm-watson-iot.github.io/helm/charts/
$ helm install psutil-quickstart wiotp/psutil
```

The pod consumes very little resource during operation, you can easily max out the default 110 pod/node limit with a cheap 2cpu/4gb worker if you are looking to deploy this chart at scale.


## Local Installation
Installation across all OS's is pretty much the same:

- Install any necessary system packages missing from the host (in order to [install psutil on Windows](https://github.com/giampaolo/psutil/blob/master/INSTALL.rst#windows) you'll need Visual Studio installed)
- Install the `wiotp-sdk` and `psutil` python modules using `pip`
- [Download](https://github.com/ibm-watson-iot/iot-python/archive/master.zip) the sample code from GitHub
- Run the sample

The following example shows the setup process on **Raspbian** (Raspberry Pi).

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

Note: Set the same environment variables detailed in the Docker section of this README (above) and ommit the `--quickstart` argument to connect your Raspberry Pi to IBM Watson IoT Platform as a registered device.


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
