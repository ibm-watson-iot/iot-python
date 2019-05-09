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
        #for li in self.appClient.statemanagement.draftLogicalInterfaces:
        #    for dt in self.appClient.statemanagement.draftDeviceTypes.find({"logicalInterfaceId":li.id}):
        #        print("Device type instance: %s" % (dt))
        #        if (dt.id in (TestDeviceTypes.testDeviceTypeName, TestDeviceTypes.updatedDeviceTypeName)):
        #            print("Deleting old test device type instance: %s" % (dt))
        #            del self.appClient.statemanagement.draftDeviceTypes[dt.id]
           
        # delete any left over device types
        for dt in self.appClient.statemanagement.activeDeviceTypes:
            #ßprint("Device type instance: %s" % (dt))
            if (dt.id in (TestDeviceTypes.testDeviceTypeName, TestDeviceTypes.updatedDeviceTypeName)):
                print("Deleting old test device type instance: %s" % (dt))
                del self.appClient.statemanagement.activeDeviceTypes[dt.id]
                               
         # delete any left over logical interfaces
        for li in self.appClient.statemanagement.draftLogicalInterfaces:
            if li.name == TestDeviceTypes.testLogicalInterfaceName:
                print("Deleting old test LI: %s" % (li))
                del self.appClient.statemanagement.draftLogicalInterfaces[li.id]
                
 
        # delete any left over physical interfaces, event type and schema
        for pi in self.appClient.statemanagement.draftPhysicalInterfaces:
            if pi.name == TestDeviceTypes.testPhysicalInterfaceName:
                print("Deleting old test PI: %s" % (pi))
                del self.appClient.statemanagement.draftPhysicalInterfaces[pi.id]
            
        for et in self.appClient.statemanagement.draftEventTypes:
            if et.name == TestDeviceTypes.testEventTypeName:
                print("Deleting old test event type: %s" % (et))
                del self.appClient.statemanagement.draftEventTypes[et.id]
                
        for s in self.appClient.statemanagement.draftSchemas:
            if s.name in (TestDeviceTypes.testEventSchemaName, TestDeviceTypes.testLiSchemaName):
                print("Deleting old test schema instance: %s" % (s))
                del self.appClient.statemanagement.draftSchemas[s.id]    
               
        # TBD this was all debugv stuff        
        #for DT in self.appClient.statemanagement.activeDeviceTypes:
        #    print ("Active Device Type: %s" % DT)

        #for li in self.appClient.statemanagement.draftLogicalInterfaces:
        #    #print ("Logical Interface: %s" % li.id)
        #    for DT in self.appClient.statemanagement.draftDeviceTypes.find({"logicalInterfaceId":li.id}):
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
        for a in self.appClient.statemanagement.draftSchemas.find({"name": name}):
            if (a.name == name):
                return True
        return False
    
    def doesEventTypeNameExist (self, name):
        for et in self.appClient.statemanagement.draftEventTypes.find({"name": name}):
            if (et.name == name):
                return True
        return False
    
    def doesPINameExist (self, name):
        for pi in self.appClient.statemanagement.draftPhysicalInterfaces.find({"name": name}):
            if (pi.name == name):
                return True
        return False
        
    def doesLINameExist (self, name):
        for li in self.appClient.statemanagement.draftLogicalInterfaces.find({"name": name}):
            if (li.name == name):
                return True
        return False
    
    def doesDTNameExist (self, name):
        for dt in self.appClient.statemanagement.activeDeviceTypes.find({"id": name}):
            if (dt.id == name):
                return True
        return False
    
    def createSchema(self, name, schemaFileName, schemaContents, description):
        jsonSchemaContents = json.dumps(schemaContents)
        createdSchema = self.appClient.statemanagement.draftSchemas.create(
            name, schemaFileName, jsonSchemaContents, description)        
        return createdSchema
    
    def createEventType(self, name, description, schemaId):
        createdEventType = self.appClient.statemanagement.draftEventTypes.create(
            {"name": name, "description": description, "schemaId": schemaId})
        return createdEventType

    def createPI(self, name, description):
        createdPI = self.appClient.statemanagement.draftPhysicalInterfaces.create(
            {"name": name, "description": description})        
        return createdPI
    
    def createLI(self, name, description, schemaId):
        createdLI = self.appClient.statemanagement.draftLogicalInterfaces.create(
            {"name": name, "description": description, "schemaId": schemaId})        
        return createdLI
    
    def createAndCheckDT(self, name, description, deviceInfo = None, metadata = None, edgeConfiguration = None, classId = "Device"):
        payload = {'id' : name, 'description' : description, 'deviceInfo' : deviceInfo, 'metadata': metadata,'classId': classId, 'edgeConfiguration': edgeConfiguration}

        createdDT = self.appClient.statemanagement.activeDeviceTypes.create(payload)
        self.checkDT(createdDT, name, description, deviceInfo, metadata, edgeConfiguration, classId)

        # now actively refetch the DT to check it is stored
        fetchedDT = self.appClient.statemanagement.activeDeviceTypes.__getitem__(createdDT.id)
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
           

    def notestDeviceTypeCRUD(self):
        
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
        updatedDT = self.appClient.statemanagement.activeDeviceTypes.update(
            createdDT.id, {'description': "Test Device Type updated description"})
        self.checkDT(updatedDT, test_dt_name, "Test Device Type updated description")

        # Delete the DT
        del self.appClient.statemanagement.activeDeviceTypes[createdDT.id]
        # It should be gone
        assert self.doesDTNameExist(test_dt_name)==False

    def notestDeviceTypePICRUD(self):
        
        test_dt_name = TestDeviceTypes.testDeviceTypeName
        assert self.doesDTNameExist(test_dt_name)==False
        
        # Create a Device Type
        createdDT = self.createAndCheckDT(
            test_dt_name, 
            "Test Device Type description")
        
        # Check the PI
        try:
            PI = createdDT.physicalInterface
            print("A newly created Device Type sholdn't have an associated Physical Interface. We have: %s" % PI)
            assert False
        except:
             assert True # TBD check the exception
       
        createdDT.physicalInterface = TestDeviceTypes.createdPI
        
        assert createdDT.physicalInterface == TestDeviceTypes.createdPI
    
        
        print ("Created Device Type")
        # Can we search for it
        assert self.doesDTNameExist(test_dt_name)==True

        # Update the DT 
        updatedDT = self.appClient.statemanagement.activeDeviceTypes.update(
            createdDT.id, {'description': "Test Device Type updated description"})
        self.checkDT(updatedDT, test_dt_name, "Test Device Type updated description")

        # Delete the DT
        del self.appClient.statemanagement.activeDeviceTypes[createdDT.id]
        # It should be gone
        assert self.doesDTNameExist(test_dt_name)==False


    def notestDeviceTypeLICRUD(self):
        
        test_dt_name = TestDeviceTypes.testDeviceTypeName
        assert self.doesDTNameExist(test_dt_name)==False
        
        # Create a Device Type
        createdDT = self.createAndCheckDT(
            test_dt_name, 
            "Test Device Type description")
        
        # Check the LI
        for li in createdDT.logicalInterfaces:
            print("A newly created Device Type sholdn't have an associated Logical Interface, we have %s" % li)
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
            print("This Device Type sholdn't have an associated Logical Interface, we have %s" % li)
            assert False==True
           
        
        # Delete the DT
        del self.appClient.statemanagement.activeDeviceTypes[createdDT.id]
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
            print("A newly created Device Type sholdn't have an associated Mappings, we have %s" % m)
            assert False==True

        createdDT.mappings.create({
            "logicalInterfaceId": TestDeviceTypes.createdLI.id,
            "notificationStrategy": "on-state-change",
            "propertyMappings": {
                "event1234": {
                  "temperature": "$event.temp",
                  "eventCount": "$state.eventCount + 1"
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
        for li in createdDT.logicalInterfaces:
            print("This Device Type sholdn't have an associated Logical Interface, we have %s" % li)
            assert False==True        
           
        
        # Delete the DT
        del self.appClient.statemanagement.activeDeviceTypes[createdDT.id]
        # It should be gone
        assert self.doesDTNameExist(test_dt_name)==False

    def notestDeviceTypeActivation(self, something):
        test_schema_name = TestDeviceTypes.testSchemaName
        assert self.doesSchemaNameExist(test_schema_name)==False
        testLIName = TestDeviceTypes.testDeviceTypeName
        assert self.doesLINameExist(testLIName)==False
        
        # Create a schema
        createdSchema = self.createSchema(
            test_schema_name, 
            "liSchema.json", 
            TestDeviceTypes.testLISchema, 
            "Test schema description",
            )

        # Create a Logical Interface
        createdLI = self.createAndCheckLI(
            testLIName, 
            "Test Logical Interface description",
            createdSchema.id)
                
       # Can we search for it
        assert self.doesLINameExist(testLIName)==True

        # Validate and Activate the LI
        createdLI.validate()
        
        # Activating the Li should fail as it is not yet associated with a Device or Thong Type.
        try:
            createdLI.activate()
            # Hmm, the activate should raise an exception
            assert False;
        except:
            assert True; # The expected exception was raised 
        
        # Delete the LI
        del self.appClient.statemanagement.draftDeviceTypes[createdLI.id]
        # It should be gone
        assert self.doesLINameExist(testLIName)==False

        # Delete the schema
        del self.appClient.statemanagement.draftSchemas[createdSchema.id]
        # It should be gone
        assert self.doesSchemaNameExist(test_schema_name)==False    
        
        
    def testDeletePreReqs(self):
        del self.appClient.statemanagement.draftPhysicalInterfaces[TestDeviceTypes.createdPI.id]
        assert self.doesPINameExist(TestDeviceTypes.testPhysicalInterfaceName)==False

        del self.appClient.statemanagement.draftEventTypes[TestDeviceTypes.createdEventType.id]
        assert self.doesEventTypeNameExist(TestDeviceTypes.testEventTypeName)==False

        del self.appClient.statemanagement.draftSchemas[TestDeviceTypes.createdEventSchema.id]
        assert self.doesSchemaNameExist(TestDeviceTypes.testEventSchemaName)==False     
        
        # Delete the LI
        del self.appClient.statemanagement.draftLogicalInterfaces[TestDeviceTypes.createdLI.id]
        assert self.doesLINameExist(TestDeviceTypes.testLogicalInterfaceName)==False

        # Delete the schema
        del self.appClient.statemanagement.draftSchemas[TestDeviceTypes.createdLISchema.id]
        assert self.doesSchemaNameExist(TestDeviceTypes.testLiSchemaName)==False    
        