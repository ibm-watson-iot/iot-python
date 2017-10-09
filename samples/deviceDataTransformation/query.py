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
import time, ibmiotf.api

if __name__ == "__main__":
  domain = None
  verify = True
  from properties import orgid, key, token, devicetype, deviceid

  params = {"auth-key": key, "auth-token": token}

  try:
    from properties import domain
    params["domain"] = domain
  except:
    pass

  try:
    from properties import host
    params["host"] = host
  except:
    pass

  try:
    from properties import verify
  except:
    pass

  api = ibmiotf.api.ApiClient(params)
  api.verify = verify

  result = api.getSchema("event1schema", draft=False)
  sys.exit()

  result = api.getDeviceTypes()
  print(result)
  print([x for x in result["results"] if x['id'] == devicetype])

  result = api.getLogicalInterfaces()
  print("logical interfaces", str(result))
  """
  physinterfaceid, result = api.getPhysicalInterfaceOnDeviceType(devicetype)
  appinterfaceids, result = api.getMappingsOnDeviceType(devicetype)
  appinterfaceids, result = api.getLogicalInterfacesOnDeviceType(devicetype)
  """
