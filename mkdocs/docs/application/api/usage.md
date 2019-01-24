# Usage & Metering

The `usage.dataTransfer(start, end, detail)` method allows you to retrieve data regarding the volume of data transfer to Watson IoT Platfrom in your organization.


## Viewing Summary Data

By setting `detail=False` (or omitting the parameter entirely) the response will provide a month by month breakdown of your data transfer:

```python
import wiotp.sdk.application

options = wiotp.sdk.application.parseEnvVars()
appClient = wiotp.sdk.application.ApplicationClient(options)

dataTransfer = appClient.usage.dataTransfer(datetime.today() - timedelta(days=10), datetime.today())

print("Time period = %s to %s" % (dataTransfer.start.isoformat(), dataTransfer.end.isoformat()))
print("- Average usage = %s" % (dataTransfer.average))
print("- Total usage = %s" % (dataTransfer.total))
```


## Getting Detailed Breakdown of Data Transfer

In setting `detail=True` the response will additionally provide a day by day breakdown of data transfer.

```python
import wiotp.sdk.application

options = wiotp.sdk.application.parseEnvVars()
appClient = wiotp.sdk.application.ApplicationClient(options)

dataTransfer = appClient.usage.dataTransfer(datetime.today() - timedelta(days=10), datetime.today(), True)

print("Time period = %s to %s" % (dataTransfer.start.isoformat(), dataTransfer.end.isoformat()))
print("- Average usage = %s bytes" % (dataTransfer.average))
print("- Total usage = %s bytes" % (dataTransfer.total))

for day in dataTransfer.days:
    print(" * Usage on %s = %s bytes" % (day.date.isoformat(), day.total) )

```


## Handling DataTransferSummary and DayDataTransfer data

The `wiotp.sdk.api.usage.DataTransferSummary` and `wiotp.sdk.api.usage.DayDataTransfer` classes provide an easy way to work with the data that is returned by the usage API.  `wiotp.sdk.api.usage.DataTransferSummary` is the top level container and provides the following properties:

- `start` The start date for the summary report (`datetime.date`)
- `end` The end date for the summary report (`datetime.date`)
- `average` The average usage across the summary period
- `total` The total usage across the summary period
- `days` If `detail=True` then this will be a list of `DayDataTransfer` objects

The `wiotp.sdk.api.usage.DayDataTransfer` allows you to work with the day by day breakdown of data usage, exposing the following properties:

- `date` The day that usage is being reported for (`datetime.date`)
- `total` The total usage on this day
