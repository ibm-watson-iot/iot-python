# IBM Watson IoT Platform Device Factory Sample

This sample demonstrates the principles of device registration and deployment.


## Device Registration

`deviceRegistrator.py` represents the necessary integration with IBM Watson IoT Platform at the earliest phase of manufacturing physical devices that will connect to the platform.  For each device that rolls off the assembly line a device registration request must be processed by Watson IoT to retrieve the necessary configuration for the devices.  For efficiency these requests are processed in batches.

For example, to register 1000 devices of typeId `iotpsutil` using the registration date as the batchId (e.g. `190523`) and a simple incrementing count to complete a unique identifier for each device in the batch:

```
$ export WIOTP_API_KEY=mykey
$ export WIOTP_API_TOKEN=mytoken
$ python deviceRegistrator.py --batchId 190523 --numberOfDevices 1000 --typeId iotpsutil --classId Device
```


## Device Deployment & Recall

`deviceDeployer.py` represents the stage post-manufacture where your devices are paired with the previously created configuration from the device registration process.  The device configuration holds everything required to identify each device uniquely.  We utilise Helm and Kubernetes as the framework for deploying the virtual devices, but the principles hold just as true if we were producing physical devices.  The python script does not perform any actions itself, instead it generates a script file containing the necessary helm commands to both create and delete virtual devices using the configuration files created during device registration.  

### Supported Virtual Device Images

These Helm charts are designed to take the standard WIoTP device configuration file and inject it into the docker container as a set of environment variables treating it as a Helm values file, you can easily write your own Helm charts and Docker images that do the same thing too:

- `--helmChart wiotp/psutil` PSUtil Device Client (Python) [wiotp/psutil](https://hub.docker.com/r/wiotp/psutil)
- `--helmChart wiotp/oshi` OSHI Device Client (Java) [wiotp/oshi](https://hub.docker.com/r/wiotp/oshi)


To generate the scripts to manage 1000 virtual devices into a Kubernetes cluster using batch `190523` of the `iotpsutil` devices using the `wiotp/psutil` helm chart (also found in this repository):

```
$ export WIOTP_API_KEY=mykey
$ export WIOTP_API_TOKEN=mytoken
$ python deviceDeployer.py --batchId 190523 --numberOfDevices 100 --typeId iotpsutil --classId Device --helmChart wiotp/psutil
```

### Configuration

Assuming you are going to use the official IBM Watson IoT Platform helm charts for your virtual devices you will want to add our Helm chart repository before you proceed:

```
$ helm repo add wiotp https://ibm-watson-iot.github.io/helm/charts/
```

### Device Deployment

The generated deployment script will look something like the following:

```
helm upgrade iotpsutil-190523-0001 wiotp/psutil -i  --values ./localDeviceRegistry/device/iotpsutil/190523/190523-0001.yaml
helm upgrade iotpsutil-190523-0002 wiotp/psutil -i  --values ./localDeviceRegistry/device/iotpsutil/190523/190523-0002.yaml
helm upgrade iotpsutil-190523-0003 wiotp/psutil -i  --values ./localDeviceRegistry/device/iotpsutil/190523/190523-0003.yaml
helm upgrade iotpsutil-190523-0004 wiotp/psutil -i  --values ./localDeviceRegistry/device/iotpsutil/190523/190523-0004.yaml
...
```

Note: this step can take some time to work through large batch sizes, it took approximately 1 hour to deploy a batch of 1000 virtual devices using the `psutil` helm chart

<p align="center">
  <img alt="1000 Virtual Devices Configured and Connected in 1 hour" src="https://raw.githubusercontent.com/ibm-watson-iot/iot-python/master/samples/deviceFactory/docs/resources/pods.png">
</p>

```
$ bash bin/deploy-device-iotpsutil-190523.bat

...
helm upgrade iotpsutil-190523-1000 wiotp/psutil -i  --values ./localDeviceRegistry/device/iotpsutil/190523/190523-1000.yaml
Release "iotpsutil-190523-1000" does not exist. Installing it now.
NAME:   iotpsutil-190523-1000
LAST DEPLOYED: Wed May 22 22:40:53 2019
NAMESPACE: default
STATUS: DEPLOYED

RESOURCES:
==> v1/Deployment
NAME                          READY  UP-TO-DATE  AVAILABLE  AGE
iotpsutil-190523-1000-psutil  0/1    1           0          0s

==> v1/Pod(related)
NAME                                           READY  STATUS   RESTARTS  AGE
iotpsutil-190523-1000-psutil-6fb5cc5566-7ln5s  0/1    Pending  0         0s

```



### Device Recall

The generated recall script will look something like the following:

```
helm delete --purge iotpsutil-190523-0001
helm delete --purge iotpsutil-190523-0002
helm delete --purge iotpsutil-190523-0003
helm delete --purge iotpsutil-190523-0004
...
```

```
$ bash bin/recall-device-iotpsutil-190523.bat
```
