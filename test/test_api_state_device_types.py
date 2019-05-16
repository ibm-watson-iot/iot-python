# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************
# 
import uuid
from datetime import datetime
import testUtils
import time
import pytest
from wiotp.sdk.exceptions import ApiException
import string
import json

class TestDeviceTypes(testUtils.AbstractTest):
    
    # Physical Interface Stuff
    testEventSchemaName = "python-api-test-dt-pi_schema"    
    testEventSchema =  {
        '$schema' : 'http://json-schema.org/draft-04/schema#',
        'type' : 'object',
        'title' : 'Sensor Event Schema',
        'properties' : {
            'temperature' : {
                'description' : 'temperature in degrees Celsius',
                'type' : 'number',
                'minimum' : -237.15,
                'default' : 0.0
            },
            'humidity' : {
                'description' : 'relative humidty (%)',
                'type' : 'number',
                'minimum' : 0.0,
                'default' : 0.0
            },
            'publishTimestamp' : {
                'description' : 'publishTimestamp',
                'type' : 'number',
                'minimum' : 0.0,
                'default' : 0.0
            }
        },
        'required' : ['temperature', 'humidity', 'publishTimestamp']
    } 
    testEventTypeName = "python-api-test-dt-pi_eventType"
    testEventId = "python-api-test-dt-pi_eventId"
    testPhysicalInterfaceName = "python-api-test-dt-pi"
        
    # Logical Interface Stuff
    testLiSchemaName = "python-api-test-dt-li-schema"    
    testLISchema =  {
        "$schema" : "http://json-schema.org/draft-04/schema#",
        "type" : "object",
        "title" : "Environment Sensor Schema",
        "properties" : {
            "temperature" : {
                "description" : "temperature in degrees Celsius",
                "type" : "number",
                "minimum" : -237.15,
                "default" : 0.0
            },
            "humidity" : {
                "description" : "relative humidity (%)",
                "type" : "number",
                "minimum" : 0.0,
                "default" : 0.0
            },
            "publishTimestamp" : {
                "description" : "publishTimestamp",
                "type" : "number",
                "minimum" : 0.0,
                "default" : 0.0
            }
        },
        "required" : ["temperature", "humidity", "publishTimestamp"]
    } 
    testLogicalInterfaceName = "python-api-test-dt-li"

    testDeviceTypeName = "python-api-test-DeviceType"
    updatedDeviceTypeName = "python-api-test-DeviceType-updated"
        
    # =========================================================================
    # Set up services
    # =========================================================================
    def testCleanup(self):
        # delete any left over device types
        #for li in self.appClient.state.draft.logicalInterfaces:
        #    for dt in self.appClient.state.draft.deviceTypes.find({"logicalInterfaceId":li.id}):
        #        print("Device type instance: %s" % (dt))
        #        if (dt.id in (TestDeviceTypes.testDeviceTypeName, TestDeviceTypes.updatedDeviceTypeName)):
        #            print("Deleting old test device type instance: %s" % (dt))
        #            del self.appClient.state.draft.deviceTypes[dt.id]
           
        # delete any left over device types
        for dt in self.appClient.state.active.deviceTypes:
            #print("Device type instance: %s" % (dt))
            if (dt.id in (TestDeviceTypes.testDeviceTypeName, TestDeviceTypes.updatedDeviceTypeName)):
                print("Deleting old test device type instance: %s" % (dt))
                del self.appClient.state.active.deviceTypes[dt.id]
                               
         # delete any left over logical interfaces
        for li in self.appClient.state.draft.logicalInterfaces:
            if li.name == TestDeviceTypes.testLogicalInterfaceName:
                print("Deleting old test LI: %s" % (li))
                del self.appClient.state.draft.logicalInterfaces[li.id]
                
 
        # delete any left over physical interfaces, event type and schema
        for pi in self.appClient.state.draft.physicalInterfaces:
            if pi.name == TestDeviceTypes.testPhysicalInterfaceName:
                print("Deleting old test PI: %s" % (pi))
                del self.appClient.state.draft.physicalInterfaces[pi.id]
            
        for et in self.appClient.state.draft.eventTypes:
            if et.name == TestDeviceTypes.testEventTypeName:
                print("Deleting old test event type: %s" % (et))
                del self.appClient.state.draft.eventTypes[et.id]
                
        for s in self.appClient.state.draft.schemas:
            if s.name in (TestDeviceTypes.testEventSchemaName, TestDeviceTypes.testLiSchemaName):
                print("Deleting old test schema instance: %s" % (s))
                del self.appClient.state.draft.schemas[s.id]    
               
        # TBD this was all debugv stuff        
        #for DT in self.appClient.state.active.deviceTypes:
        #    print ("Active Device Type: %s" % DT)

        #for li in self.appClient.state.draft.logicalInterfaces:
        #    #print ("Logical Interface: %s" % li.id)
        #    for DT in self.appClient.state.draft.deviceTypes.find({"logicalInterfaceId":li.id}):
        #        print ("LI: %s, Draft Device Type: %s" % (li.id, DT))
        #        newPI = DT.physicalInterface
        #        print ("DT physicalInterface: %s" % DT.physicalInterface)
        #        for subLi in DT.logicalInterfaces:
        #            print ("LI: %s" % (subLi.id))                           
        #        for map in DT.mappings:
        #            print ("Mapping: %s" % (map))                           
        #return 
        
    def checkDT (self, DeviceType, name, description, deviceInfo = None, metadata = None, edgeConfiguration = None, classId = "Device"):
        assert DeviceType.id == name
        assert DeviceType.description == description
        
        # TBD more needed here
        
    def doesSchemaNameExist (self, name):
        for a in self.appClient.state.draft.schemas.find({"name": name}):
            if (a.name == name):
                return True
        return False
    
    def doesEventTypeNameExist (self, name):
        for et in self.appClient.state.draft.eventTypes.find({"name": name}):
            if (et.name == name):
                return True
        return False
    
    def doesPINameExist (self, name):
        for pi in self.appClient.state.draft.physicalInterfaces.find({"name": name}):
            if (pi.name == name):
                return True
        return False
        
    def doesLINameExist (self, name):
        for li in self.appClient.state.draft.logicalInterfaces.find({"name": name}):
            if (li.name == name):
                return True
        return False
    
    def doesDTNameExist (self, name):
        for dt in self.appClient.state.active.deviceTypes.find({"id": name}):
            if (dt.id == name):
                return True
        return False
    
    def doesActiveSchemaNameExist (self, name):
        for a in self.appClient.state.active.schemas.find({"name": name}):
            if (a.name == name):
                return True
        return False
    
    def doesActiveEventTypeNameExist (self, name):
        for et in self.appClient.state.active.eventTypes.find({"name": name}):
            if (et.name == name):
                return True
        return False
    
    def doesActivePINameExist (self, name):
        for pi in self.appClient.state.active.physicalInterfaces.find({"name": name}):
            if (pi.name == name):
                return True
        return False
        
    def doesActiveLINameExist (self, name):
        for li in self.appClient.state.active.logicalInterfaces.find({"name": name}):
            if (li.name == name):
                return True
        return False
    
    def doesActiveDTNameExist (self, name):
        for dt in self.appClient.state.active.deviceTypes.find({"id": name}):
            if (dt.id == name):
                return True
        return False
    
    def createSchema(self, name, schemaFileName, schemaContents, description):
        jsonSchemaContents = json.dumps(schemaContents)
        createdSchema = self.appClient.state.draft.schemas.create(
            name, schemaFileName, jsonSchemaContents, description)        
        return createdSchema
    
    def createEventType(self, name, description, schemaId):
        createdEventType = self.appClient.state.draft.eventTypes.create(
            {"name": name, "description": description, "schemaId": schemaId})
        return createdEventType

    def createPI(self, name, description):
        createdPI = self.appClient.state.draft.physicalInterfaces.create(
            {"name": name, "description": description})        
        return createdPI
    
    def comparePIs(self, PI1, PI2):
        assert PI1.id == PI2.id
        assert PI1.name == PI2.name
        assert PI1.description == PI2.description
        assert PI1.version == PI2.version
        assert PI1.events == PI2.events
    
    def createLI(self, name, description, schemaId):
        createdLI = self.appClient.state.draft.logicalInterfaces.create(
            {"name": name, "description": description, "schemaId": schemaId})        
        return createdLI
    
    def createAndCheckDT(self, name, description, deviceInfo = None, metadata = None, edgeConfiguration = None, classId = "Device"):
        payload = {'id' : name, 'description' : description, 'deviceInfo' : deviceInfo, 'metadata': metadata,'classId': classId, 'edgeConfiguration': edgeConfiguration}

        createdDT = self.appClient.state.active.deviceTypes.create(payload)
        self.checkDT(createdDT, name, description, deviceInfo, metadata, edgeConfiguration, classId)

        # now actively refetch the DT to check it is stored
        fetchedDT = self.appClient.state.active.deviceTypes.__getitem__(createdDT.id)
        assert createdDT == fetchedDT
        
        return createdDT

    def testCreatePreReqs(self):
        # LI
        test_schema_name = TestDeviceTypes.testLiSchemaName
        assert self.doesSchemaNameExist(test_schema_name)==False
        testLIName = TestDeviceTypes.testLogicalInterfaceName
        assert self.doesLINameExist(testLIName)==False
        
        # Create a schema
        TestDeviceTypes.createdLISchema = self.createSchema(
            test_schema_name, 
            "liSchema.json", 
            TestDeviceTypes.testLISchema, 
            "Test schema description",
            )

        # Create a Logical Interface
        TestDeviceTypes.createdLI = self.createLI(
            testLIName, 
            "Test Logical Interface description",
            TestDeviceTypes.createdLISchema.id)      
        
        # PI
        test_schema_name = TestDeviceTypes.testEventSchemaName
        assert self.doesSchemaNameExist(test_schema_name)==False
        test_eventType_name = TestDeviceTypes.testEventTypeName
        assert self.doesEventTypeNameExist(test_eventType_name)==False
        testPIName = TestDeviceTypes.testPhysicalInterfaceName
        assert self.doesPINameExist(testPIName)==False
        
        # Create a schema
        TestDeviceTypes.createdEventSchema = self.createSchema(
            test_schema_name, 
            "eventSchema.json", 
            TestDeviceTypes.testEventSchema, 
            "Test schema description")
        
        # Create an eventType
        TestDeviceTypes.createdEventType = self.createEventType(
            test_eventType_name, 
            "Test event type description",
            TestDeviceTypes.createdEventSchema.id)

        # Create a Physical Interface
        TestDeviceTypes.createdPI = self.createPI(
            testPIName, 
            "Test Physical Interface description")      
        
        # Associate event with PI
        TestDeviceTypes.createdPI.events.create({"eventId": TestDeviceTypes.testEventId, "eventTypeId": TestDeviceTypes.createdEventType.id})
           

    def testDeviceTypeCRUD(self):
        
        test_dt_name = TestDeviceTypes.testDeviceTypeName
        assert self.doesDTNameExist(test_dt_name)==False
        
        # Create a Device Type
        createdDT = self.createAndCheckDT(
            test_dt_name, 
            "Test Device Type description")
                
        print ("Created Device Type")
        # Can we search for it
        assert self.doesDTNameExist(test_dt_name)==True

        # Update the DT 
        updatedDT = self.appClient.state.active.deviceTypes.update(
            createdDT.id, {'description': "Test Device Type updated description"})
        self.checkDT(updatedDT, test_dt_name, "Test Device Type updated description")

        # Delete the DT
        del self.appClient.state.active.deviceTypes[createdDT.id]
        # It should be gone
        assert self.doesDTNameExist(test_dt_name)==False

    
    def testDeviceTypePICRUD(self):
        
        test_dt_name = TestDeviceTypes.testDeviceTypeName
        assert self.doesDTNameExist(test_dt_name)==False
        
        # Create a Device Type
        createdDT = self.createAndCheckDT(
            test_dt_name, 
            "Test Device Type description")
        
        # Check the PI
        try:
            PI = createdDT.physicalInterface
            print("A newly created Device Type shouldn't have an associated Physical Interface. We have: %s" % PI)
            assert False==True
        except:
             assert True # TBD check the exception
       
        createdDT.physicalInterface = TestDeviceTypes.createdPI
        
        self.comparePIs(createdDT.physicalInterface,TestDeviceTypes.createdPI)    
        
        print ("Created PI")

        # Update the PI 
        createdDT.physicalInterface = TestDeviceTypes.createdPI

        # Delete the PI
        del createdDT.physicalInterface
        
        try:
            PI = createdDT.physicalInterface
            print("We deleted the PI, so there shouldn't be an associated Physical Interface. We have: %s" % PI)
            assert False==True
        except:
             assert True # TBD check the exception

        
        # Delete the DT
        del self.appClient.state.active.deviceTypes[createdDT.id]
        # It should be gone
        assert self.doesDTNameExist(test_dt_name)==False


    def testDeviceTypeLICRUD(self):
        
        test_dt_name = TestDeviceTypes.testDeviceTypeName
        assert self.doesDTNameExist(test_dt_name)==False
        
        # Create a Device Type
        createdDT = self.createAndCheckDT(
            test_dt_name, 
            "Test Device Type description")
        assert self.doesDTNameExist(test_dt_name)==True
        
        # Check the LI
        for li in createdDT.logicalInterfaces:
            print("A newly created Device Type shouldn't have an associated Logical Interface, we have %s" % li)
            assert False==True

        createdDT.logicalInterfaces.create(TestDeviceTypes.createdLI) 
       
        associatedLICount = 0
        for li in createdDT.logicalInterfaces:
            associatedLICount = associatedLICount + 1
            assert li == TestDeviceTypes.createdLI
        assert associatedLICount == 1
        
        # delete the associated LI
        for li in createdDT.logicalInterfaces:
            del createdDT.logicalInterfaces[li.id]
            
        # Check the LI
        for li in createdDT.logicalInterfaces:
            print("This Device Type shouldn't have an associated Logical Interface, we have %s" % li)
            assert False==True
           
        
        # Delete the DT
        del self.appClient.state.active.deviceTypes[createdDT.id]
        # It should be gone
        assert self.doesDTNameExist(test_dt_name)==False

    def testDeviceTypeEventMappingCRUD(self):
        
        test_dt_name = TestDeviceTypes.testDeviceTypeName
        assert self.doesDTNameExist(test_dt_name)==False
        
        # Create a Device Type
        createdDT = self.createAndCheckDT(
            test_dt_name, 
            "Test Device Type description")
        
        createdDT.logicalInterfaces.create(TestDeviceTypes.createdLI) 
        
        # Check there are no Mappings
        for m in createdDT.mappings:
            print("A newly created Device Type shouldn't have an associated Mappings, we have %s" % m)
            assert False==True

        createdDT.mappings.create({
            "logicalInterfaceId": TestDeviceTypes.createdLI.id,
            "notificationStrategy": "on-state-change",
            "propertyMappings": {
                TestDeviceTypes.testEventId: {
                    "temperature" : "$event.temperature",
                    "humidity" : "$event.humidity",
                    "publishTimestamp" : "$event.publishTimestamp"
                }
            }}) 
       
        associatedMapCount = 0
        for m in createdDT.mappings:
            associatedMapCount = associatedMapCount + 1
            # TBD assert li == TestDeviceTypes.createdLI
        assert associatedMapCount == 1
        
        # delete the associated Mappings
        for m in createdDT.mappings:
            del createdDT.mappings[m.logicalInterfaceId]
            
        # Check the Mappings have gone
        for m in createdDT.mappings:
            print("The Device Type shouldn't have any associated Mappings, we have %s" % m)
            assert False==True
        
        # Delete the DT
        del self.appClient.state.active.deviceTypes[createdDT.id]
        # It should be gone
        assert self.doesDTNameExist(test_dt_name)==False

    def testDeviceTypeActivation(self):

        test_dt_name = TestDeviceTypes.testDeviceTypeName
        assert self.doesDTNameExist(test_dt_name)==False
        
        # Create a Device Type
        createdDT = self.createAndCheckDT(
            test_dt_name, 
            "Test Device Type description")
        
        # Associate PI
        createdDT.physicalInterface = TestDeviceTypes.createdPI
        
        # Associate the LI
        createdDT.logicalInterfaces.create(TestDeviceTypes.createdLI) 
       
       # Mappings
        createdDT.mappings.create({
            "logicalInterfaceId": TestDeviceTypes.createdLI.id,
            "notificationStrategy": "on-state-change",
            "propertyMappings": {
                TestDeviceTypes.testEventId: {
                    "temperature" : "$event.temperature",
                    "humidity" : "$event.humidity",
                    "publishTimestamp" : "$event.publishTimestamp"
                }
            }}) 
       
        # Validate and Activate the LI
        createdDT.validate()
        
        createdDT.activate()

        # Wait for active resources
        
        # Check all the active resources, we mayhave to wait for this to complete
        for attempt in range(6):
            if (self.doesActiveSchemaNameExist(TestDeviceTypes.testEventSchemaName) and
               self.doesActiveSchemaNameExist(TestDeviceTypes.testLiSchemaName) and
               self.doesActiveEventTypeNameExist(TestDeviceTypes.testEventTypeName) and
               self.doesActivePINameExist(TestDeviceTypes.testPhysicalInterfaceName) and
               self.doesActiveLINameExist(TestDeviceTypes.testLogicalInterfaceName) and
               self.doesActiveDTNameExist(TestDeviceTypes.testDeviceTypeName)):
                print ("Device Type resources are all activated, attempt %s" % attempt)
                break
            print ("Device Type resources not yet activated, attempt %s" % attempt)
            print ("Active? Event Schema: %s, LI Schema: %s, Event Type: %s, Physical Interface: %s, Logical Interface: %s, Devive Type: %s" %
                      (self.doesActiveSchemaNameExist(TestDeviceTypes.testEventSchemaName),
                       self.doesActiveSchemaNameExist(TestDeviceTypes.testLiSchemaName),
                       self.doesActiveEventTypeNameExist(TestDeviceTypes.testEventTypeName),
                       self.doesActivePINameExist(TestDeviceTypes.testPhysicalInterfaceName),
                       self.doesActiveLINameExist(TestDeviceTypes.testLogicalInterfaceName),
                       self.doesActiveDTNameExist(TestDeviceTypes.testDeviceTypeName)))
            time.sleep(10)

        
        # Now we should be able to activate the LI:
        TestDeviceTypes.createdLI.validate()
        TestDeviceTypes.createdLI.activate()
       
        createdDT.deactivate()
        
        # Check all the active resources are removed, we may have to wait for this to complete
        for attempt in range(6):
            if not (self.doesActiveSchemaNameExist(TestDeviceTypes.testEventSchemaName) or
               self.doesActiveSchemaNameExist(TestDeviceTypes.testLiSchemaName) or
               self.doesActiveEventTypeNameExist(TestDeviceTypes.testEventTypeName) or
               self.doesActivePINameExist(TestDeviceTypes.testPhysicalInterfaceName) or
               self.doesActiveLINameExist(TestDeviceTypes.testLogicalInterfaceName)):
                print ("Device Type resources are all de-activated, attempt %s" % attempt)
                break
            print ("Device Type resources not yet de-activated, attempt %s" % attempt)
            print ("Active? Event Schema: %s, LI Schema: %s, Event Type: %s, Physical Interface: %s, Logical Interface: %s" %
                      (self.doesActiveSchemaNameExist(TestDeviceTypes.testEventSchemaName),
                       self.doesActiveSchemaNameExist(TestDeviceTypes.testLiSchemaName),
                       self.doesActiveEventTypeNameExist(TestDeviceTypes.testEventTypeName),
                       self.doesActivePINameExist(TestDeviceTypes.testPhysicalInterfaceName),
                       self.doesActiveLINameExist(TestDeviceTypes.testLogicalInterfaceName)))
            time.sleep(10)
                
         # Delete the DT
        del self.appClient.state.active.deviceTypes[createdDT.id]
        # It should be gone
        assert self.doesDTNameExist(test_dt_name)==False       

        
    def testDeletePreReqs(self):
        del self.appClient.state.draft.physicalInterfaces[TestDeviceTypes.createdPI.id]
        assert self.doesPINameExist(TestDeviceTypes.testPhysicalInterfaceName)==False

        del self.appClient.state.draft.eventTypes[TestDeviceTypes.createdEventType.id]
        assert self.doesEventTypeNameExist(TestDeviceTypes.testEventTypeName)==False

        del self.appClient.state.draft.schemas[TestDeviceTypes.createdEventSchema.id]
        assert self.doesSchemaNameExist(TestDeviceTypes.testEventSchemaName)==False     
        
        # Delete the LI
        del self.appClient.state.draft.logicalInterfaces[TestDeviceTypes.createdLI.id]
        assert self.doesLINameExist(TestDeviceTypes.testLogicalInterfaceName)==False

        # Delete the schema
        del self.appClient.state.draft.schemas[TestDeviceTypes.createdLISchema.id]
        assert self.doesSchemaNameExist(TestDeviceTypes.testLiSchemaName)==False    
        