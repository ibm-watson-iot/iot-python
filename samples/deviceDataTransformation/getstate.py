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
  
  api = ibmiotf.api.ApiClient(params)
  api.verify = verify
    
  appinterfaceids, result = api.getApplicationInterfacesOnDeviceType(devicetype)
  print("Application interface ids", appinterfaceids)
  
  while True:
    for applicationInterfaceId in appinterfaceids:
      print("Getting state for application interface id", applicationInterfaceId)
      try:
        result = api.getDeviceStateForApplicationInterface(devicetype, deviceid, applicationInterfaceId)
        print(result)
      except Exception as exc:
        print(exc.response, exc.response.json())
      time.sleep(1)
