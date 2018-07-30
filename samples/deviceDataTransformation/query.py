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

if __name__ == "__main__":

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

  api = ibmiotf.api.ApiClient(params)
  api.verify = verify

  #result = api.getLogicalInterfaces()
  #print("logical interfaces", str(result))
  #physinterfaceid, result = api.getPhysicalInterfaceOnDeviceType(devicetype)
  #appinterfaceids, result = api.getMappingsOnDeviceType(properties.devicetype)
  appinterfaceids, result = api.getLogicalInterfacesOnDeviceType(properties.devicetype)
  mappings = api.getMappingsOnDeviceTypeForLogicalInterface(properties.devicetype, "44af725c-d0a6-4855-91c2-23b626be193d")
  print(result)
  print("***", mappings)
