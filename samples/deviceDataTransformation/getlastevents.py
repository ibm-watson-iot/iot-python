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
import time, ibmiotf.api, json, base64

if __name__ == "__main__":    
  from properties import orgid, key, token, devicetype, deviceid
  
  api = ibmiotf.api.ApiClient({"auth-key": key, "auth-token": token})
  
  while True:
    try:
      result = api.getLastEvents(devicetype, deviceid)
      for event in result:
        if event["format"] == "json":
          event["payload"] = base64.decodestring(event["payload"])
      print(result)
    except Exception as exc:
      print(exc)
    time.sleep(1)
