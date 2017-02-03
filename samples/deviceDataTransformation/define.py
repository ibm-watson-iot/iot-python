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
  schemaFile = json.dumps({ "type" : "object", "properties" : { "d" :
    { "type" : "object", "properties" : {
        "myName": {"type": "string"},
        "accelX": {"type": "number"},
        "accelY": {"type": "number"},
        "accelZ": {"type": "number"},
        "temp": {"type": "number"},
        "potentiometer1": {"type": "number"},
        "potentiometer2": {"type": "number"},
        "joystick" : {"type": "string"},
    } } } })
        	
  ids["k64f event schema"], result = api.createSchema("k64F event schema", 'K64Event.json', schemaFile)
    
  logger.info("# ---- get the schema back -------")
  result = api.getSchema(ids["k64f event schema"])

  logger.info("# ---- add an event type -------")    
  ids["k64feventtype"], result = api.createEventType("K64F event", ids["k64f event schema"], "K64F event")
    
  logger.info("# ---- add a physical interface -------")  
  ids["physicalinterface"], result = api.createPhysicalInterface("K64F", "The physical interface for K64F example")
    
  logger.info("# ---- add the event type to the physical interface -------") 
  result = api.createEvent(ids["physicalinterface"], ids["k64feventtype"], "status")
    
  logger.info("# ---- add the physical interface to the device type")
  result = api.addPhysicalInterfaceToDeviceType(deviceType, ids["physicalinterface"])
    
  logger.info("# ---- add an application interface schema -------")    
  schemaFile = json.dumps(
      { "type" : "object",
        "properties" : {
          "eventCount" :{"type": "number", "default":-1},
          "realEventCount" :{"type": "number"},
          "accel": {"type": "object",
            "properties" : {
              "x": {"type": "number", "default": 0},
              "y": {"type": "number", "default": 0},
              "z": {"type": "number", "default": 0},
            },
            "required" : ["x", "y", "z"],
          },
          "temp": {"type": "object",
            "properties" : {
              "C": {"type": "number", "default": 0},
              "F": {"type": "number", "default": 0},
              "isLow": {"type": "boolean", "default": False},
              "isHigh": {"type": "boolean", "default": False},
              "lowest" : {"type": "number", "default": 100},
              "highest" : {"type": "number", "default": 0},
            },
            "required" : ["C", "F", "isLow", "isHigh", "lowest", "highest"],
          },
          "potentiometers": {"type": "object",
             "properties" : {
                "1": {"type": "number"},
                "2": {"type": "number"},
            },
          },
          "joystick": {"type": "string", "default": "NONE" },
        },
        "required" : ["eventCount", "accel", "joystick", "temp"],
      }
    )
  ids["k64f app interface schema"], result = api.createSchema("k64fappinterface", 'k64fappinterface.json', schemaFile)
  print("App interface schema id", ids["k64f app interface schema"])
    
  logger.info("# ---- add an application interface -------")
  try:
	  ids["k64f app interface"], result = \
       api.createApplicationInterface("K64F application interface", ids["k64f app interface schema"])
  except Exception as exc:
    print(exc.response.json())  
    
  logger.info("# ---- associate application interface with the device type -------")  
  result = api.addApplicationInterfaceToDeviceType(deviceType, ids["k64f app interface"], ids["k64f app interface schema"])
                 
  logger.info("# ---- add mappings to the device type -------")
  mappings = {
              # eventid -> { property -> eventid property expression }
              "status" :  { 
                "eventCount" : "($state.eventCount == -1) ? $event.d.count : ($state.eventCount+1)",
                "realEventCount" : "$event.d.count",
                "accel.x" : "$event.d.accelX",
                "accel.y" : "$event.d.accelY",
                "accel.z" : "$event.d.accelZ",
                "temp.C" : "$event.d.temp",  
                "temp.F" : "$event.d.temp * 1.8 + 32",
                "temp.isLow" : "$event.d.temp < $state.temp.lowest",
                "temp.isHigh" : "$event.d.temp > $state.temp.highest",
                "temp.lowest" : "($event.d.temp < $state.temp.lowest) ? $event.d.temp : $state.temp.lowest",
                "temp.highest" : "($event.d.temp > $state.temp.highest) ? $event.d.temp : $state.temp.highest",
                "potentiometers.1" : "$event.d.potentiometer1",
                "potentiometers.2" : "$event.d.potentiometer2",
                "joystick" : '($event.d.joystick == "LEFT") ? "RIGHT" : (($event.d.joystick == "RIGHT") ? "LEFT" : $event.d.joystick)'
               },
            }
  result = api.addMappingsToDeviceType(deviceType, ids["k64f app interface"], mappings)
    

if __name__ == "__main__":    

  from properties import orgid, key, token, devicetype, deviceid
    
  import ibmiotf.api
  
  api = ibmiotf.api.ApiClient({"auth-key": key, "auth-token": token})
  
  #define(api, devicetype, deviceid)
  
  logger.info("# ---- validate definitions -------") 
  result = api.validateDeviceType(devicetype)
  print(result)
    
  logger.info("# ---- deploy definitions -------") 
  result = api.deployDeviceType(devicetype)
  print(result)
