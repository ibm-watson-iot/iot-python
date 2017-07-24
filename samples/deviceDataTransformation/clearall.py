# *****************************************************************************
# Copyright (c) 2017 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Initial Contribution:
#   Ian Craggs
# *****************************************************************************

"""

Clear all the relevant definitions we can find


"""

from __future__ import print_function
import requests, json, time


def clearPhysicalInterface(physicalInterfaceId):
  print("Physical interface id", physicalInterfaceId)

  for devicetype in devicetypes:
    succeeded = True
    try:
      result = api.removePhysicalInterfaceFromDeviceType(devicetype)
    except:
      succeeded = False
    if succeeded:
      print("Physical interface removed from devicetype", devicetype)

  # list event types on the physical interface
  result = api.getEvents(physicalInterfaceId, draft=True)
  eventIds = [res["eventId"] for res in result]
  eventTypeIds = [res["eventTypeId"] for res in result]
  print(eventIds, eventTypeIds)

  for eventId in eventIds:
   	result = api.deleteEvent(physicalInterfaceId, eventId) # remove event mapping from device type

  result = api.deletePhysicalInterface(physicalInterfaceId)
  print("Physical interface deleted")

  # delete event types and schemas
  count = 0; schemaIds = []
  for eventTypeId in eventTypeIds:
    schemaId = api.getEventType(eventTypeId, draft=True)["schemaId"]
    result = api.deleteEventType(eventTypeId)
    result = api.deleteSchema(schemaId)
    count += 2; schemaIds.append(schemaId)
  print("Event types and event type schemas deleted:", count, schemaIds)

if __name__ == "__main__":
  from properties import orgid, key, token, devicetype, deviceid

  try:
    from properties import domain
  except:
    pass

  try:
    from properties import verify
  except:
    pass

  params = {"auth-key": key, "auth-token": token}
  if domain:
    params["domain"] = domain

  import ibmiotf.api
  api = ibmiotf.api.ApiClient(params)

  # find all the device types
  #devicetypes = [x["id"] for x in api.getDeviceTypes(draft=True)["results"]]
  devicetypes = ['dt0']
  print("Device types", devicetypes)

  # find all application interfaces
  appintids, result = api.getLogicalInterfaces(draft=True)
  if len(appintids) > 0:
    print("Application interface ids", appintids)

  # try and delete the application interfaces
  for appintid in appintids:
    try:
      result = api.deleteLogicalInterface(appintid)
    except Exception as exc:
      print(exc)
      #if it fails, remove the app interface from the device type
      for devicetype in devicetypes:
        succeeded = True
        try:
    	    result = api.removeLogicalInterfaceFromDeviceType(devicetype, appintid)
        except Exception as exc:
          succeeded = False
        if succeeded:
    	    print("app interface removed from device type", devicetype)
      try:
	      result = api.deleteLogicalInterface(appintid)
      except Exception as exc:
        print(exc)

  # find all physical interfaces
  physintids, result = api.getPhysicalInterfaces(draft=True)
  if len(physintids) > 0:
    print("Physical interface ids", physintids)
  for physintid in physintids:
    resp = clearPhysicalInterface(physintid)

  # get all mappings for the device types
  for devicetype in devicetypes:
    try:
      resp = api.getMappingsOnDeviceType(devicetype, draft=True)
    except Exception as exc:
      print(exc.response.json())
    for a in resp:
      print("deleting mappings for devicetype", devicetype, "application interface", a["logicalInterfaceId"])
      resp = api.deleteMappingsFromDeviceType(devicetype, a["logicalInterfaceId"])

  # list and delete event types
  eventTypeIds, result = api.getEventTypes(draft=True)
  for eventTypeId in eventTypeIds:
   	result = api.deleteEventType(eventTypeId) # remove event mapping from device type

  # list and delete schemas
  ids, resp = api.getSchemas(draft=True)
  for schemaId in ids:
    try:
      resp = api.deleteSchema(schemaId)
    except Exception as exc:
      print(exc.response.json())
