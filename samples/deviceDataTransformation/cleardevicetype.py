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

import requests, json, time, sys, importlib, ibmiotf.api, logging

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("Property file name needed")
    sys.exit()

  property_file_name = sys.argv[1]

  logger.info("Getting properties from %s" % property_file_name)
  properties = importlib.import_module(property_file_name)
  property_names = dir(properties)

  verify = None
  params = {"auth-key": properties.key, "auth-token": properties.token}
  if "domain" in property_names:
    params["domain"] = properties.domain

  if "verify" in property_names:
    verify = properties.verify

  if "host" in property_names:
    params["host"] = properties.host

  print(params)
  api = ibmiotf.api.ApiClient(params)
  api.verify = verify

  # make sure device type is deactivated
  try:
    api.deactivateDeviceTypeConfiguration(properties.devicetype)
    #time.sleep(5)
  except Exception as exc:
    print("Deactivate exception", exc.response.json())
    if exc.response.status_code != 409:
      sys.exit()

  # get mappings
  try:
    result = api.getMappingsOnDeviceType(properties.devicetype, draft=True)
  except:
    result = []

  count = 0; ids = []
  for mapping in result:
    logicalInterfaceId = mapping["logicalInterfaceId"]
    # delete the mappings for this device type
    result = api.deleteMappingsFromDeviceType(properties.devicetype, logicalInterfaceId)
    count += 1; ids.append(logicalInterfaceId)
  print("Mappings deleted:", count, ids)

  try:
    result = api.getMappingsOnDeviceType(properties.devicetype, draft=True)
    print("There shouldn't be any mappings now")
  except:
    pass

  # list application interfaces for the device type
  schemaIds = []
  try:
    ids, result = api.getLogicalInterfacesOnDeviceType(properties.devicetype, draft=True)
    print("Logical interfaces found:", ids)
    schemaIds = [li["schemaId"] for li in result]
    print("Schemas found:", schemaIds)
  except:
    ids = result = []

  # disassociate and delete the logical interfaces from the device type
  count = 0
  for logicalInterfaceId in ids:
    result = api.removeLogicalInterfaceFromDeviceType(properties.devicetype, logicalInterfaceId)
    result = api.deleteLogicalInterface(logicalInterfaceId)
    count += 1
  print("Logical interfaces disassociated and deleted:", count, ids)

  # delete the logical interface schemas
  count = 0
  for schemaId in schemaIds:
    result = api.deleteSchema(schemaId)
    count += 1
  print("Logical interface schemas deleted:", count, schemaIds)

  physicalInterfaceId = None
  try:
    physicalInterfaceId, result = api.getPhysicalInterfaceOnDeviceType(properties.devicetype, draft=True)
  except Exception as exc:
    print(exc)
  if physicalInterfaceId:
    print("Physical interface id", physicalInterfaceId)
    result = api.removePhysicalInterfaceFromDeviceType(properties.devicetype)

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
