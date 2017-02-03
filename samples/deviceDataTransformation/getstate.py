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
	from properties import orgid, key, token, devicetype, deviceid
  
	api = ibmiotf.api.ApiClient({"auth-key": key, "auth-token": token})
    
	appinterfaceids, result = api.getApplicationInterfacesOnDeviceType(devicetype)
	print("Application interface ids", appinterfaceids)
  
	while True:
		for applicationInterfaceId in appinterfaceids:
			print("Getting state for application interface id", applicationInterfaceId)
			result = api.getDeviceStateForApplicationInterface(devicetype, deviceid, applicationInterfaceId)
			print(result)
		time.sleep(1)
