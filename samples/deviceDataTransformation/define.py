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
import logging, json, requests, sys, importlib
from requests_toolbelt.multipart.encoder import MultipartEncoder

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

ids = {}

def define(api, properties):

  logger.info("# ---- add an event schema -------")
  infile = open(properties.eventSchemaFileName)
  schemaFileContents = ''.join([x.strip() for x in infile.readlines()])
  infile.close()
  ids["Event schema"], result = api.createSchema("Event schema",
                  properties.eventSchemaFileName, schemaFileContents)

  logger.info("# ---- get the schema back -------")
  result = api.getSchema(ids["Event schema"], draft=True)
  print(result)

  logger.info("# ---- add an event type -------")
  ids["Event type"], result = api.createEventType("Event type name", ids["Event schema"], "Event type description")

  logger.info("# ---- add a physical interface -------")
  ids["Physical interface"], result = api.createPhysicalInterface("PhysicalInterfaceName", "The physical interface description")

  logger.info("# ---- add the event type to the physical interface -------")
  result = api.createEvent(ids["Physical interface"], ids["Event type"], properties.eventName)

  logger.info("# ---- add the physical interface to the device type")
  result = api.addPhysicalInterfaceToDeviceType(properties.devicetype, ids["Physical interface"])

  logger.info("# ---- add a logical interface schema -------")
  infile = open(properties.logicalInterfaceSchemaFileName)
  schemaFile = ''.join([x.strip() for x in infile.readlines()])
  infile.close()
  ids["Logical interface schema"], result = api.createSchema("LogicalInterfaceName",
                           properties.logicalInterfaceSchemaFileName, schemaFile)
  print("Logical interface schema id", ids["Logical interface schema"])

  logger.info("# ---- add a logical interface -------")
  try:
	  ids["Logical interface"], result = \
       api.createLogicalInterface("Logical interface", ids["Logical interface schema"])
  except Exception as exc:
    print(exc.response.json())
    raise

  logger.info("# ---- associate logical interface with the device type -------")
  result = api.addLogicalInterfaceToDeviceType(properties.devicetype, ids["Logical interface"])

  logger.info("# ---- add mappings to the device type -------")
  infile = open(properties.mappingsFileName)
  mappings = json.loads(''.join([x.strip() for x in infile.readlines()]))
  infile.close()
  try:
    result = api.addMappingsToDeviceType(properties.devicetype, ids["Logical interface"], mappings,
             notificationStrategy="on-state-change")
  except Exception as exc:
    print(exc.response.json())
    raise

def defineThings(api, properties):
    
  logger.info("# ---- add thing type schema -------")
  
  thingTypeSchemaContents = json.load(open(properties.thingTypeSchemaFileName))
  
  thingTypeSchemaContents['properties']['temperatureSensor']['$logicalInterfaceRef'] = ids["Logical interface"]
  
  print(str(thingTypeSchemaContents))
  
  ids["thingTypeSchemaId"], result = api.createSchema("room Sensor Schema", properties.thingTypeSchemaFileName, json.dumps(thingTypeSchemaContents))

  logger.info("# ---- add thing LI schema -------")
  thingLogicalInterfaceSchemaContents = json.load(open(properties.thingLogicalInterfaceSchema))
  ids["thingLISchemaId"], result = api.createSchema("temp thing LI Schema", properties.thingLogicalInterfaceSchema, json.dumps(thingLogicalInterfaceSchemaContents))

  logger.info("# ---- create thing type -------")
  api.addDraftThingType(properties.thingType, properties.thingId, None, ids["thingTypeSchemaId"])

  logger.info("# Create logical interface to associate with thing type")
  ids["thingLogicalInterfaceID"], result = api.createLogicalInterface("temp Thing LI", ids["thingLISchemaId"])

  logger.info("# Associate thing logical interface to thing type")
  result = api.addLogicalInterfaceToThingType(properties.thingType, ids["thingLogicalInterfaceID"])
  print(result)
  
  thingMapping = json.load(open(properties.thingMapping))
  print(ids["thingLogicalInterfaceID"])
  print(json.dumps(thingMapping))

  logger.info("# Create mapping for thing type and LI")
  api.addMappingsToThingType(properties.thingType, ids["thingLogicalInterfaceID"], thingMapping, notificationStrategy="on-state-change")

def createThing(api, properties):
  
  logger.info("# --- create thing -----")
  
  aggregateObject = json.load(open(properties.thingAggregateFileName))
  
  aggregateObject["temperatureSensor"]["id"] = properties.deviceid
  aggregateObject["temperatureSensor"]["typeId"] = properties.devicetype
  
  thing = api.registerThing(properties.thingType, properties.thingId, properties.thingId, None, aggregateObject)
  
  logger.info("Created thing [%s]" % thing)

def getThing(api, properties):
  
  logger.info("# --- Get thing -----")

  thing = api.getThing(properties.thingType, properties.thingId)
  
  logger.info("Get thing [%s]" % thing)

def getThingsForType(api, properties):
  
  logger.info("# --- Get things for type -----")

  thing = api.getThingsForType(properties.thingType)
  
  logger.info("Get things for type [%s]" % thing)

def getThingsState(api, properties):
  
  logger.info("# --- Get things state for Logical Interface -----")

  thing = api.getThingStateForLogicalInterface(properties.thingType, properties.thingId,ids["thingLogicalInterfaceID"])
  
  logger.info("Get things state for Logical Interface  [%s]" % thing)


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

  import ibmiotf.api

  api = ibmiotf.api.ApiClient(params)
  if verify:
    api.verify = verify
  
  define(api, properties)

  logger.info("# ---- validate definitions -------")
  result = api.validateDeviceTypeConfiguration(properties.devicetype)
  print(result)

  logger.info("# ---- activate definitions -------")
  result = api.activateDeviceTypeConfiguration(properties.devicetype)
  print(result)
  
  defineThings(api, properties)
  
  logger.info("# ---- validate things definitions -------")
  result = api.validateThingTypeConfiguration(properties.thingType)
  print(result)

  logger.info("# ---- activate things definitions -------")
  result = api.activateThingTypeConfiguration(properties.thingType)
  print(result)
  
  createThing(api, properties)
  getThing(api, properties)
  getThingsForType(api, properties)
  getThingsState(api, properties)
