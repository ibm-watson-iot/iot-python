# *****************************************************************************
# Copyright (c) 2018 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Initial Contribution:
#   Sanjay Prabhakar
# *****************************************************************************

from __future__ import print_function
import time, ibmiotf.api, sys, logging, importlib

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

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

  api = ibmiotf.api.ApiClient(params)
  api.verify = verify
  
  # get eventstreams type service for the org
  services = api.getServices()
  
  print("Services retrieved : %s" % services)
  
  # Get available historian connectors
  connectors = api.getHistorianConnectors()
  
  print("Available connectors : %s" % connectors)
  
  # ===================================
  # TODO ENTER A VALID CREDENTIALS
  # ===================================
  credentials = {}
  
  try:
    # Create a new eventstreams service  
    newService = api.addService("my_eventstreams_instance", "eventstreams", credentials, "some desc")
    print("New Service: %s" % newService)
    newServiceId=newService['id']
  
    # Create new Historian connector
    histConnector = api.addHistorianConnector("my_hist_conn", newServiceId, "UTC", "some desc", True)
    print("New Hist connector created: %s" % histConnector)  
    histConnectorId = histConnector['id']
  
    # Create a destination with  a proper configuration
    destination = api.addHistorianConnectorDestination(histConnectorId, "all_my_events", "eventstreams", {"partitions" : 2})
    print("New Destination created: %s" % destination)  
  
    # Create a forwarding rule with proper selector
    destinationName = destination['name']
    forwardingRule = api.addHistorianConnectorForwardingRule(histConnectorId, "my_rule_1", "some desc", destinationName, "event", {"deviceType" : "someType", "eventId": "tempevt"}, True)
    print("New Forwardign rule created: %s" % forwardingRule)  
  
    forwardingRuleId = forwardingRule['id']
    
    
    # Delete the forwarding rule
    api.deleteHistorianConnectorForwardingRuleId(histConnectorId, forwardingRuleId)
    print("Forwarding Rule deleted..")
  
    # Delete the Destination
    api.deleteHistorianConnectorDestination(histConnectorId, destinationName)
    print("Destination deleted..")
  
    # Delete the historian connector rule
    api.deleteHistorianConnector(histConnectorId)
    print("Historian connector deleted..")
    
    # Delete the service
    api.deleteService(newServiceId)
    print("Service deleted..")
  
  except Exception as exc:
    print("Exception: %s" % exc)
  
  
  
  

