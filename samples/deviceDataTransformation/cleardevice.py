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


from __future__ import print_function
import requests, json, time


if __name__ == "__main__":    
  from properties import orgid, key, token, devicetype, deviceid
  
  import ibmiotf.api
  
  api = ibmiotf.api.ApiClient({"auth-key": key, "auth-token": token})
  
  # get mappings
  result = api.getMappingsOnDeviceType(devicetype)
  
  count = 0; ids = []
  for mapping in result:
    applicationInterfaceId = mapping["applicationInterfaceId"]
    # delete the mappings for this device type
    result = api.deleteMappingsFromDeviceType(devicetype, applicationInterfaceId)
    count += 1; ids.append(applicationInterfaceId)
  print("Mappings deleted:", count, ids)
  
  # list application interfaces for the device type
  schemaIds = []
  ids, result = api.getApplicationInterfacesOnDeviceType(devicetype)
  print("Application interfaces found:", ids)
  print("Schemas found:", schemaIds)
  
  # disassociate and delete the application interfaces from the device type
  count = 0
  for applicationInterfaceId in ids:
    result = api.removeApplicationInterfaceFromDeviceType(devicetype, applicationInterfaceId)
    result = api.deleteApplicationInterface(applicationInterfaceId)
    count += 1
  print("Application interfaces disassociated and deleted:", count, ids)
  
  # delete the application interface schemas
  count = 0
  for schemaId in schemaIds:
    result = deleteSchema(applicationInterfaceId)
    count += 1
  print("Application interface schemas deleted:", count, schemaIds)
   
  result = api.getDeviceType(devicetype)
  if "physicalInterfaceId" in result.keys():
    physicalInterfaceId = result["physicalInterfaceId"]  # get the physical interface id
    print("Physical interface id", physicalInterfaceId)
    result = api.removePhysicalInterfaceFromDeviceType(devicetype)

  	# list event types on the physical interface
    result = api.getEvents(physicalInterfaceId)
    eventIds = [res["eventId"] for res in result]
    eventTypeIds = [res["eventTypeId"] for res in result]
    print(eventIds, eventTypeIds)
    
    for eventId in eventIds:
     	result = api.deleteEvent(physicalInterfaceId, eventId) # remove event mapping from device type
  	
  	result = api.eletePhysicalInterface(physicalInterfaceId)
  	print("Physical interface deleted")
  	
    # delete event types and schemas
    count = 0; schemaIds = []
    for eventTypeId in eventTypeIds:
      schemaId = api.getEventType(eventTypeId)["schemaId"]
      result = api.deleteEventType(eventTypeId)
      result = api.deleteSchema(schemaId)
      count += 2; schemaIds.append(schemaId)
    print("Event types and event type schemas deleted:", count, schemaIds)
	  
		
  
    

