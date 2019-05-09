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
    
    testSchemaName = "python-api-test-li-schema"
    
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
    
    testDeviceTypeName = "python-api-test-DeviceType"
    updatedDeviceTypeName = "python-api-test-DeviceType-updated"
        
    # =========================================================================
    # Set up services
    # =========================================================================
    def testCleanup(self):
        #for DT in self.appClient.statemanagement.activeDeviceTypes:
        #    print ("Active Device Type: %s" % DT)

        for li in self.appClient.statemanagement.draftLogicalInterfaces:
            #print ("Logical Interface: %s" % li.id)
            for DT in self.appClient.statemanagement.draftDeviceTypes.find({"logicalInterfaceId":li.id}):
                print ("LI: %s, Draft Device Type: %s" % (li.id, DT))
                print ("DT physicalInterface: %s" % DT.physicalInterface)
                for subLi in DT.logicalInterfaces:
                    print ("LI: %s" % (subLi))                           
        return
    
        for li in self.appClient.statemanagement.draftLogicalInterfaces:
            if li.name in (TestDeviceTypes.testDeviceTypeName, TestDeviceTypes.updatedDeviceTypeName):
                # print("Deleting old test schema instance: %s" % (a))
                del self.appClient.statemanagement.draftLogicalInterfaces[li.id]
            
        for s in self.appClient.statemanagement.draftSchemas:
            if s.name == TestDeviceTypes.testSchemaName:
                del self.appClient.statemanagement.draftSchemas[s.id]      
        
    def checkDT (self, DeviceType, name, description, schemaId):
        assert DeviceType.name == name
        assert DeviceType.description == description
        assert DeviceType.schemaId == schemaId
        

        assert isinstance(DeviceType.created, datetime)
        assert isinstance(DeviceType.createdBy, str)
        assert isinstance(DeviceType.updated, datetime)        
        assert isinstance(DeviceType.updatedBy, str)            
        
    def doesSchemaNameExist (self, name):
        for a in self.appClient.statemanagement.draftSchemas.find({"name": name}):
            if (a.name == name):
                return True
        return False
    
    def doesDTNameExist (self, name):
        for li in self.appClient.statemanagement.draftDeviceTypes.find({"name": name}):
            if (li.name == name):
                return True
        return False
    
    def createSchema(self, name, schemaFileName, schemaContents, description):
        jsonSchemaContents = json.dumps(schemaContents)
        createdSchema = self.appClient.statemanagement.draftSchemas.create(
            name, schemaFileName, jsonSchemaContents, description)        
        return createdSchema
    
    def createAndCheckDT(self, name, description, schemaId):
        createdDT = self.appClient.statemanagement.draftDeviceTypes.create(
            {"name": name, "description": description, "schemaId": schemaId})
        self.checkDT(createdDT, name, description, schemaId)

        # now actively refetch the DT to check it is stored
        fetchedDT = self.appClient.statemanagement.draftDeviceTypes.__getitem__(createdDT.id)
        assert createdDT == fetchedDT
        
        return createdDT

    def notestDeviceTypeCRUD(self, something):
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

        # Update the LI
        updated_li_name = TestDeviceTypes.updatedDeviceTypeName
        updatedLI = self.appClient.statemanagement.draftDeviceTypes.update(
            createdLI.id, {'id': createdLI.id, 'name': updated_li_name, 'description': "Test LI updated description", "schemaId": createdSchema.id})
        self.checkLI(updatedLI, updated_li_name, "Test LI updated description", createdSchema.id)

        # Delete the LI
        del self.appClient.statemanagement.draftDeviceTypes[createdLI.id]
        # It should be gone
        assert self.doesLINameExist(testLIName)==False

        # Delete the schema
        del self.appClient.statemanagement.draftSchemas[createdSchema.id]
        # It should be gone
        assert self.doesSchemaNameExist(test_schema_name)==False
    
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
        