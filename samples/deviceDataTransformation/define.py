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
import logging, json, requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def define(api, deviceType, deviceId):
  ids = {}

  logger.info("# ---- add an event schema -------")
  infile = open("event1.json")
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

  logger.info("# ---- add an application interface schema -------")
  infile = open("appinterface1.json")
  schemaFile = ''.join([x.strip() for x in infile.readlines()])
  infile.close()
  ids["k64f app interface schema"], result = api.createSchema("k64fappinterface", 'k64fappinterface.json', schemaFile)
  print("App interface schema id", ids["k64f app interface schema"])

  logger.info("# ---- add a logical interface -------")
  try:
	  ids["k64f app interface"], result = \
       api.createLogicalInterface("K64F logical interface", ids["k64f app interface schema"])
  except Exception as exc:
    print(exc.response.json())

  logger.info("# ---- associate application interface with the device type -------")
  result = api.addLogicalInterfaceToDeviceType(deviceType, ids["k64f app interface"])

  logger.info("# ---- add mappings to the device type -------")
  infile = open("event1appint1mappings.json")
  mappings = json.loads(''.join([x.strip() for x in infile.readlines()]))
  infile.close()
  try:
    result = api.addMappingsToDeviceType(deviceType, ids["k64f app interface"], mappings,
             notificationStrategy="on-state-change")
  except Exception as exc:
    print(exc.response.json())

if __name__ == "__main__":

  from properties import orgid, key, token, devicetype, deviceid, verify

  domain = verify = None

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
  if verify:
    api.verify = verify

  define(api, devicetype, deviceid)

  logger.info("# ---- validate definitions -------")
  result = api.validateDeviceTypeConfiguration(devicetype)
  print(result)

  logger.info("# ---- activate definitions -------")
  result = api.activateDeviceTypeConfiguration(devicetype)
  print(result)
