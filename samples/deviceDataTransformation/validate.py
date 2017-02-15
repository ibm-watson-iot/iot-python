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

if __name__ == "__main__":    
  import ibmiotf.api
    
  from properties import orgid as orgId, key, token, devicetype, deviceid
  
  apiClient = ibmiotf.api.ApiClient({"auth-key": key, "auth-token": token})

  result = apiClient.validateDeviceType(devicetype)
  print(result)
  
