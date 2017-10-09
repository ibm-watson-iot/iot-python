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

def define(host, api, deviceType, deviceId):
  ids = {}

  logger.info("# ---- add an event schema -------")
  infile = open("json/event1.json")
  schemaFileContents = ''.join([x.strip() for x in infile.readlines()])
  infile.close()
  ids["event1 schema"], result = api.createSchema("event1 schema", 'event1.json', schemaFileContents)

  logger.info("# ---- get the schema back -------")
  result = api.getSchema(ids["event1 schema"], draft=True)
  print(result)

  logger.info("# ---- add an event type -------")
  ids["k64feventtype"], result = api.createEventType("K64F event", ids["event1 schema"], "K64F event")

  logger.info("# ---- add a physical interface -------")
  ids["physicalinterface"], result = api.createPhysicalInterface("K64F", "The physical interface for K64F example")

  logger.info("# ---- add the event type to the physical interface -------")
  result = api.createEvent(ids["physicalinterface"], ids["k64feventtype"], "status")

  logger.info("# ---- add the physical interface to the device type")
  result = api.addPhysicalInterfaceToDeviceType(deviceType, ids["physicalinterface"])

  logger.info("# ---- add a logical interface schema -------")
  infile = open("json/loginterface1.json")
  schemaFile = ''.join([x.strip() for x in infile.readlines()])
  infile.close()
  ids["k64f log interface schema"], result = api.createSchema("k64floginterface", 'k64floginterface.json', schemaFile)
  print("Logical interface schema id", ids["k64f log interface schema"])

  logger.info("# ---- add a logical interface -------")
  try:
	  ids["k64f log interface"], result = \
       api.createLogicalInterface("K64F logical interface", ids["k64f log interface schema"])
  except Exception as exc:
    print(exc.response.json())
    raise
  """
  logger.info("# ---- add a rule to the logical interface -------")
  ruleUrl = 'https://%s/api/v0002%s/logicalinterfaces/%s/rules'

  expression = "$state.temp.isHigh"
  description = None
  print("ids", ids["k64f log interface"], type(ids["k64f log interface"]))
  req = ruleUrl % (host, "/draft", ids["k64f log interface"])
  print("url", req)
  body = {"condition" : expression}
  resp = requests.post(req, headers={"Content-Type":"application/json"},
							data=json.dumps(body), 	verify=False)
  """
  logger.info("# ---- associate logical interface with the device type -------")
  result = api.addLogicalInterfaceToDeviceType(deviceType, ids["k64f log interface"])

  logger.info("# ---- add mappings to the device type -------")
  infile = open("json/event1logint1mappings.json")
  mappings = json.loads(''.join([x.strip() for x in infile.readlines()]))
  infile.close()
  try:
    result = api.addMappingsToDeviceType(deviceType, ids["k64f log interface"], mappings,
             notificationStrategy="on-state-change")
  except Exception as exc:
    print(exc.response.json())
    raise

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
    params["domain"] = domain

  if "verify" in property_names:
    verify = properties.verify

  if "host" in property_names:
    params["host"] = properties.host

  import ibmiotf.api

  api = ibmiotf.api.ApiClient(params)
  if verify:
    api.verify = verify

  define(properties.host, api, properties.devicetype, properties.deviceid)

  logger.info("# ---- validate definitions -------")
  result = api.validateDeviceTypeConfiguration(properties.devicetype)
  print(result)

  logger.info("# ---- activate definitions -------")
  result = api.activateDeviceTypeConfiguration(properties.devicetype)
  print(result)
