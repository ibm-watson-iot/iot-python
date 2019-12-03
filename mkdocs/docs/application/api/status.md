# Service Status

The `serviceStatus()` method provides a simple way to query the health of IBM Watston IoT Platform in your region.  The response is a Python dictionary that firstly, tells you the region your service instance is running in (e.g. `us`, `uk`, `de`), and below that will provide a simple `green`, `orange`, `red` overview of the health of the platform broken down by different capabilities:

- `dashboard` Availability of the dashboard
- `messaging` Availability of the core messaging service (for events, commands, device management protocol etc)
- `thirdParty` Availability of the third party connector service (for ARM)

The three status' represent:

- `green` No known issues currently
- `orange` Degraded performance, by service is available
- `red` Service outage, or performance significantly impacted as to be unusable


## Handling the ServiceStatus data

The `wiotp.sdk.api.status.ServiceStatusResult` class extends defaultdict allowing you to treat the reponse as a simple Python dictionary that contains the json response body of the API call made under the covers if you so choose, however it's designed to make it easy to interact with the API results by providing convenient properties representing the data available from the API:

- `region` The Watson IoT Platform region where your organization runs.
- `messaging` The status of core messaging services in your region.
- `dashboard` The availability of the web dashboard (UI) in your region.
- `thirdParty` The status of third party connector service (for ARM) in your region.

```python
import wiotp.sdk.application

options = wiotp.sdk.application.parseEnvVars()
appClient = wiotp.sdk.application.ApplicationClient(options)

status = appClient.serviceStatus()

# If you don't know what region you are in you can look it up from the status
region = status.region

print("Messaging is %s" % (status.messaging))
print("Dashboard is %s" % (status.dashboard))
```
