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
import time, ibmiotf.api, sys, logging, importlib, mmod

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def filterSchemaId(draft, schemaId):
  if not linkedtodevicetypes:
    return
  if draft and schemaId in draftSchemaIds:
    draftSchemaIds.remove(schemaId)
  if not draft and schemaId in activeSchemaIds:
    activeSchemaIds.remove(schemaId)

def filterEventTypes(draft, eventtypeid):
  if not linkedtodevicetypes:
    return
  if draft and eventtypeid in draftEventTypes:
    draftEventTypes.remove(eventtypeid)
  if not draft and eventtypeid in activeEventTypes:
    activeEventTypes.remove(eventtypeid)

def filterPhysicalInterface(draft, physinterfaceid):
  if not linkedtodevicetypes:
    return
  if draft and physinterfaceid in draftPhysicalInterfaces:
    draftPhysicalInterfaces.remove(physinterfaceid)
  if not draft and physinterfaceid in activePhysicalInterfaces:
    activePhysicalInterfaces.remove(physinterfaceid)

def filterLogicalInterface(draft, loginterfaceid):
  if not linkedtodevicetypes:
    return
  if draft and loginterfaceid in draftLogicalInterfaces:
    draftLogicalInterfaces.remove(loginterfaceid)
  if not draft and loginterfaceid in activeLogicalInterfaces:
    activeLogicalInterfaces.remove(loginterfaceid)

def getEvent(api, mm, eventtypeid, draft=False):
  eventtype = api.getEventType(eventtypeid, draft=draft)
  mm.insert("schema:"+eventtype["schemaId"])
  filterSchemaId(draft, eventtype["schemaId"])
  filterEventTypes(draft, eventtypeid)

def getPhysicalInterface(api, mm, devicetype, draft=False, physinterfaceid=None):
  if physinterfaceid == None:
    try:
      physinterfaceid, result = api.getPhysicalInterfaceOnDeviceType(devicetype["id"], draft=draft)
    except:
      pass
  if physinterfaceid:
    filterPhysicalInterface(draft, physinterfaceid)
    mm.push()
    mm.insert("Physical interface: "+physinterfaceid)
    results = api.getEvents(physinterfaceid, draft=draft)
    for result in results:
      mm.push()
      eventtypeid = result["eventTypeId"]
      mm.insert(str(result))
      getEvent(api, mm, eventtypeid, draft=draft)
      mm.pop()
    mm.pop()

def getLogicalInterfaces(api, mm, devicetype, draft=False, loginterfaceid=None):
  result = None
  if loginterfaceid != None:
    loginterfaceids = [loginterfaceid]
  else:
    loginterfaceids = None
    try:
      loginterfaceids, result = api.getLogicalInterfacesOnDeviceType(devicetype["id"], draft=draft)
    except Exception as e:
      print("getLogicalInterfacesOnDeviceType", e.response.text)
  if loginterfaceids:
    count = 0
    for loginterfaceid in loginterfaceids:
      mm.push() # start
      filterLogicalInterface(draft, loginterfaceid)
      mm.insert("Logical interface: "+loginterfaceid)
      if result == None:
        result = api.getLogicalInterface(loginterfaceid, draft=draft)
        schemaId = result["schemaId"]
      else:
        schemaId = result[count]["schemaId"]
      mm.insert("Schema: "+schemaId)
      filterSchemaId(draft, schemaId)
      try:
        mappings = api.getMappingsOnDeviceTypeForLogicalInterface(devicetype["id"], loginterfaceid, draft=draft)
        mm.gotoParent()
        mm.insert("Mappings: "+str(mappings["propertyMappings"])[0:24])
      except Exception as e:
        print(e)
      count += 1
      mm.pop() # start

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

  #print(params)
  api = ibmiotf.api.ApiClient(params)
  api.verify = verify

  mm = mmod.MindMaps(properties.orgid)
  mm.enhance("colour", "red")
  mm.enhance("bold")

  global linkedtodevicetypes
  linkedtodevicetypes = True

  global draftSchemaIds, activeSchemaIds
  draftSchemaIds = api.getSchemas(draft=True)[0]
  activeSchemaIds = api.getSchemas()[0]

  global draftEventTypes, activeEventTypes
  draftEventTypes = api.getEventTypes(draft=True)[0]
  activeEventTypes = api.getEventTypes()[0]

  global draftPhysicalInterfaces, activePhysicalInterfaces
  draftPhysicalInterfaces = api.getPhysicalInterfaces(draft=True)[0]
  activePhysicalInterfaces = api.getPhysicalInterfaces()[0]

  global draftLogicalInterfaces, activeLogicalInterfaces
  draftLogicalInterfaces = api.getLogicalInterfaces(draft=True)[0]
  activeLogicalInterfaces = api.getLogicalInterfaces()[0]

  result = api.getDeviceTypes()
  for devicetype in result["results"]:
    logger.info("Processing device type %s" % (devicetype["id"],))
    mm.insert('/' + "Device type: "+devicetype["id"])
    mm.push() # device type
    mm.insert("active")
    mm.push() # active
    getPhysicalInterface(api, mm, devicetype)
    mm.pop() # active
    getLogicalInterfaces(api, mm, devicetype)
    mm.pop(); mm.push() # device type
    mm.insert("draft")
    mm.push() # draft
    getPhysicalInterface(api, mm, devicetype, draft=True)
    mm.pop() # draft
    getLogicalInterfaces(api, mm, devicetype, draft=True)
    mm.pop() # device type

    # Devices
    devices = api.getDevicesForType(devicetype["id"])["results"]
    for device in devices:
      mm.insert("Device: "+device["deviceId"])
      mm.gotoParent()

  linkedtodevicetypes = False

  # Now delete any resources not associated with a device type

  for physicalInterfaceId in draftPhysicalInterfaces:
    api.deletePhysicalInterface(physicalInterfaceId)

  for eventTypeId in draftEventTypes:
    api.deleteEventType(eventTypeId)

  for logicalInterfaceId in draftLogicalInterfaces:
    api.deleteLogicalInterface(logicalInterfaceId)

  for schemaId in draftSchemaIds:
    api.deleteSchema(schemaId)
