    # Information management URLs

    # Draft Device type URLs
    draftDeviceTypeUrl = 'https://%s/api/v0002/draft/device/types/%s'

    # Schema URLs
    allSchemasUrl = "https://%s/api/v0002%s/schemas"
    oneSchemaUrl  = "https://%s/api/v0002%s/schemas/%s"
    oneSchemaContentUrl  = "https://%s/api/v0002%s/schemas/%s/content"

    # Event type URLs
    allEventTypesUrl = "https://%s/api/v0002%s/event/types"
    oneEventTypeUrl  = "https://%s/api/v0002%s/event/types/%s"

    # Physical Interface URLs
    allPhysicalInterfacesUrl = "https://%s/api/v0002%s/physicalinterfaces"
    onePhysicalInterfaceUrl  = "https://%s/api/v0002%s/physicalinterfaces/%s"
    oneDeviceTypePhysicalInterfaceUrl = 'https://%s/api/v0002%s/device/types/%s/physicalinterface'

    # Event URLs
    allEventsUrl = "https://%s/api/v0002%s/physicalinterfaces/%s/events"
    oneEventUrl  = "https://%s/api/v0002%s/physicalinterfaces/%s/events/%s"

    # Logical Interface URLs
    allLogicalInterfacesUrl = "https://%s/api/v0002%s/logicalinterfaces"
    oneLogicalInterfaceUrl  = "https://%s/api/v0002%s/logicalinterfaces/%s"
    allDeviceTypeLogicalInterfacesUrl = "https://%s/api/v0002%s/device/types/%s/logicalinterfaces"
    oneDeviceTypeLogicalInterfaceUrl = "https://%s/api/v0002/draft/device/types/%s/logicalinterfaces/%s"

    # Rules
    allRulesForLogicalInterfaceUrl = "https://%s/api/v0002%s/logicalinterfaces/%s/rules"
    oneRuleForLogicalInterfaceUrl  = "https://%s/api/v0002%s/logicalinterfaces/%s/rules/%s"

    # Mappings
    allDeviceTypeMappingsUrl = "https://%s/api/v0002%s/device/types/%s/mappings"
    oneDeviceTypeMappingUrl = "https://%s/api/v0002%s/device/types/%s/mappings/%s"

    # Device state
    deviceStateUrl = "https://%s/api/v0002/device/types/%s/devices/%s/state/%s"
    
    # Thing Types URLs
    thingTypesUrl   = "https://%s/api/v0002/thing/types"
    thingTypeUrl    = "https://%s/api/v0002/thing/types/%s"
    
    # Thing URLs
    thingsUrl   = "https://%s/api/v0002/thing/types/%s/things"
    thingUrl    = "https://%s/api/v0002/thing/types/%s/things/%s"
    
    # Draft Thing type URLs
    draftThingTypesUrl  = 'https://%s/api/v0002/draft/thing/types'
    draftThingTypeUrl   = 'https://%s/api/v0002/draft/thing/types/%s'
    
    # Thing types logical interface URLs
    allThingTypeLogicalInterfacesUrl = "https://%s/api/v0002%s/thing/types/%s/logicalinterfaces"
    oneThingTypeLogicalInterfaceUrl = "https://%s/api/v0002/draft/thing/types/%s/logicalinterfaces/%s"
    
    # Thing Mappings
    allThingTypeMappingsUrl = "https://%s/api/v0002%s/thing/types/%s/mappings"
    oneThingTypeMappingUrl = "https://%s/api/v0002%s/thing/types/%s/mappings/%s"
    
    # Thing state
    thingStateUrl = "https://%s/api/v0002/thing/types/%s/things/%s/state/%s"
    
    """
    Thing API methods
     - register a new thing
     - get a single thing
     - get all thing instances for a type
     - remove thing
     - update thing
    """
    
    def registerThing(self, thingTypeId, thingId, name = None, description = None, aggregatedObjects = None, metadata=None):
        """
        Registers a new thing.
        It accepts thingTypeId (string), thingId (string), name (string), description (string), aggregatedObjects (JSON) and metadata (JSON) as parameters
        In case of failure it throws APIException
        """
        thingsUrl = ApiClient.thingsUrl % (self.host, thingTypeId)
        payload = {'thingId' : thingId, 'name' : name, 'description' : description, 'aggregatedObjects' : aggregatedObjects, 'metadata': metadata}

        r = requests.post(thingsUrl, auth=self.credentials, data=json.dumps(payload), headers = {'content-type': 'application/json'}, verify=self.verify)
        status = r.status_code
        if status == 201:
            self.logger.debug("Thing Instance Created")
            return r.json()
        elif status == 400:
            raise ibmiotf.APIException(400, "Invalid request (No body, invalid JSON, unexpected key, bad value)", r.json())
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the API key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "The thing type with specified id does not exist", None)
        elif status == 409:
            raise ibmiotf.APIException(409, "A thing instance with the specified id already exists", r.json())
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)
        
    def getThing(self, thingTypeId, thingId):
        """
        Gets thing details.
        It accepts thingTypeId (string), thingId (string)
        In case of failure it throws APIException
        """
        thingUrl = ApiClient.thingUrl % (self.host, thingTypeId, thingId)

        r = requests.get(thingUrl, auth=self.credentials, verify=self.verify)
        status = r.status_code

        if status == 200:
            self.logger.debug("Thing instance was successfully retrieved")
            return r.json()
        elif status == 304:
            raise ibmiotf.APIException(304, "The state of the thing has not been modified (response to a conditional GET).", None)
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "A thing type with the specified id, or a thing with the specified id, does not exist.", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def getThingsForType(self, thingTypeId, parameters = None):
        """
        Gets details for multiple things of a type
        It accepts thingTypeId (string) and parameters
        In case of failure it throws APIException
        """
        thingsUrl = ApiClient.thingsUrl % (self.host, thingTypeId)

        r = requests.get(thingsUrl, auth=self.credentials, params = parameters, verify=self.verify)
        status = r.status_code
        if status == 200:
            self.logger.debug("List of things was successfully retrieved")
            return r.json()
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "The thing type does not exist", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def removeThing(self, thingTypeId, thingId):
        """
        Delete an existing thing.
        It accepts thingTypeId (string) and thingId (string) as parameters
        In case of failure it throws APIException
        """
        thingUrl = ApiClient.thingUrl % (self.host, thingTypeId, thingId)

        r = requests.delete(thingUrl, auth=self.credentials, verify=self.verify)
        status = r.status_code
        if status == 204:
            self.logger.debug("Thing was successfully removed")
            return True
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "A thing type or thing instance with the specified id does not exist.", None)
        elif status == 409:
            raise ibmiotf.APIException(409, "The thing instance is aggregated into another thing instance.", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def updateThing(self, thingTypeId, thingId, name, description, aggregatedObjects, metadata = None):
        """
        Updates a thing.
        It accepts thingTypeId (string), thingId (string), name (string), description (string), aggregatedObjects(JSON), metadata (JSON) as parameters
        In case of failure it throws APIException
        """
        thingUrl = ApiClient.thingUrl % (self.host, thingTypeId, thingId)

        payload = {'name' : name, 'description' : description, 'aggregatedObjects' : aggregatedObjects, 'metadata': metadata}
        r = requests.put(thingUrl, auth=self.credentials, data=json.dumps(payload), headers = {'content-type': 'application/json'}, verify=self.verify)

        status = r.status_code
        if status == 200:
            self.logger.debug("The thing with the specified id was successfully updated.")
            return r.json()
        elif status == 400:
            raise ibmiotf.APIException(400, "Invalid request (No body, invalid JSON, unexpected key, bad value)", None)
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "A thing type with the specified id, or a thing with the specified id, does not exist.", None)
        elif status == 412:
            raise ibmiotf.APIException(412, "The state of the thing has been modified since the client retrieved its representation (response to a conditional PUT).", r.json())
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)
        
    
    
    """
    Thing Types API methods
     - Add thing type
     - Get thing types
     - Get thing type
     - update thing type
     - remove thing type
    """
    
    def addDraftThingType(self, thingTypeId, name = None, description = None, schemaId = None, metadata = None):
        """
        Creates a thing type.
        It accepts thingTypeId (string), name (string), description (string), schemaId(string) and metadata(dict) as parameter
        In case of failure it throws APIException
        """
        draftThingTypesUrl = ApiClient.draftThingTypesUrl % (self.host)
        payload = {'id' : thingTypeId, 'name' : name, 'description' : description, 'schemaId' : schemaId, 'metadata': metadata}

        r = requests.post(draftThingTypesUrl, auth=self.credentials, data=json.dumps(payload), headers = {'content-type': 'application/json'}, verify=self.verify)
        status = r.status_code
        if status == 201:
            self.logger.debug("The draft thing Type is created")
            return r.json()
        elif status == 400:
            raise ibmiotf.APIException(400, "Invalid request (No body, invalid JSON, unexpected key, bad value)", r.json())
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 409:
            raise ibmiotf.APIException(409, "The draft thing type already exists", r.json())
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)
        
    def updateDraftThingType(self, thingTypeId, name, description, schemaId, metadata = None):
        """
        Updates a thing type.
        It accepts thingTypeId (string), name (string), description (string), schemaId (string) and metadata(JSON) as the parameters
        In case of failure it throws APIException
        """
        draftThingTypeUrl = ApiClient.draftThingTypeUrl % (self.host, thingTypeId)
        draftThingTypeUpdate = {'name' : name, 'description' : description, 'schemaId' : schemaId, 'metadata' : metadata}
        r = requests.put(draftThingTypeUrl, auth=self.credentials, data=json.dumps(draftThingTypeUpdate), headers = {'content-type': 'application/json'}, verify=self.verify)
        status = r.status_code
        if status == 200:
            self.logger.debug("Thing type was successfully modified")
            return r.json()
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "The Thing type does not exist", None)
        elif status == 409:
            raise ibmiotf.APIException(409, "The update could not be completed due to a conflict", r.json())
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)
    
    def getDraftThingTypes(self, parameters = None):
        """
        Retrieves all existing draft thing types.
        It accepts accepts an optional query parameters (Dictionary)
        In case of failure it throws APIException
        """
        draftThingTypesUrl = ApiClient.draftThingTypesUrl % (self.host)
        r = requests.get(draftThingTypesUrl, auth=self.credentials, params = parameters, verify=self.verify)
        status = r.status_code
        if status == 200:
            self.logger.debug("Draft thing types successfully retrieved")
            self.logger.debug(json.dumps(r.json()))
            return r.json()
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)
    
    def getDraftThingType(self, thingTypeId, parameters = None):
        """
        Retrieves all existing draft thing types.
        It accepts accepts an optional query parameters (Dictionary)
        In case of failure it throws APIException
        """
        draftThingTypeUrl = ApiClient.draftThingTypeUrl % (self.host, thingTypeId)
        r = requests.get(draftThingTypeUrl, auth=self.credentials, params = parameters, verify=self.verify)
        status = r.status_code
        if status == 200:
            self.logger.debug("Draft thing type successfully retrieved")
            self.logger.debug(json.dumps(r.json()))
            return r.json()
        elif status == 304:
            raise ibmiotf.APIException(304, "The state of the thing type has not been modified (response to a conditional GET).", None)
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "A draft thing type with the specified id does not exist.", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)
            
    def deleteDraftThingType(self, thingTypeId):
        """
        Deletes a Thing type.
        It accepts thingTypeId (string) as the parameter
        In case of failure it throws APIException
        """
        draftThingTypeUrl = ApiClient.draftThingTypeUrl % (self.host, thingTypeId)

        r = requests.delete(draftThingTypeUrl, auth=self.credentials, verify=self.verify)
        status = r.status_code
        if status == 204:
            self.logger.debug("Device type was successfully deleted")
            return True
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "A thing type with the specified id does not exist.", None)
        elif status == 409:
            raise ibmiotf.APIException(409, "The draft thing type with the specified id is currently being referenced by another object.", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)
        
    def getActiveThingTypes(self, parameters = None):
        """
        Retrieves all existing active thing types.
        It accepts accepts an optional query parameters (Dictionary)
        In case of failure it throws APIException
        """
        thingTypesUrl = ApiClient.thingTypesUrl % (self.host)
        r = requests.get(thingTypesUrl, auth=self.credentials, params = parameters, verify=self.verify)
        status = r.status_code
        if status == 200:
            self.logger.debug("Active thing types successfully retrieved")
            self.logger.debug(json.dumps(r.json()))
            return r.json()
        elif status == 400:
            raise ibmiotf.APIException(400, "Invalid request (invalid or missing query parameter, invalid query parameter value)", None)
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)
        
    def getActiveThingType(self, thingTypeId, parameters = None):
        """
        Retrieves all existing Active thing types.
        It accepts accepts an optional query parameters (Dictionary)
        In case of failure it throws APIException
        """
        thingTypeUrl = ApiClient.thingTypeUrl % (self.host, thingTypeId)
        r = requests.get(thingTypeUrl, auth=self.credentials, params = parameters, verify=self.verify)
        status = r.status_code
        if status == 200:
            self.logger.debug("Acvtive thing type successfully retrieved")
            self.logger.debug(json.dumps(r.json()))
            return r.json()
        elif status == 304:
            raise ibmiotf.APIException(304, "The state of the thing type has not been modified (response to a conditional GET).", None)
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "A active thing type with the specified id does not exist.", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)


    """
    ===========================================================================
    Information Management Schema APIs
    ===========================================================================
    """

    def getSchemas(self, draft=False, name=None, schemaType=None):
        """
        Get all schemas for the org.  In case of failure it throws APIException
        """
        if draft:
            req = ApiClient.allSchemasUrl % (self.host, "/draft")
        else:
            req = ApiClient.allSchemasUrl % (self.host, "")

        if name or schemaType:
            req += "?"
            if name:
                req += "name="+name
            if schemaType:
                if name:
                    req += "&"
                req += "schemaType="+schemaType

        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("All schemas retrieved")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting all schemas", resp)
        return [x["id"] for x in resp.json()["results"]], resp.json()

    def getSchema(self, schemaId, draft=False):
        """
        Get a single schema.  Throws APIException on failure
        """
        if draft:
            req = ApiClient.oneSchemaUrl % (self.host, "/draft", schemaId)
        else:
            req = ApiClient.oneSchemaUrl % (self.host, "", schemaId)

        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("One schema retrieved")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error in get a schema", resp)
        return resp.json()

    def createSchema(self, schemaName, schemaFileName, schemaContents, description=None):
        """
        Create a schema for the org.
        Returns: schemaId (string), response (object).
        Throws APIException on failure
        """
        req = ApiClient.allSchemasUrl % (self.host, "/draft")
        fields={
        'schemaFile': (schemaFileName, schemaContents, 'application/json'),
            'schemaType': 'json-schema',
            'name': schemaName,
        }
        if description:
            fields["description"] = description

        multipart_data = MultipartEncoder(fields=fields)
        resp = requests.post(req, auth=self.credentials, data=multipart_data,
                            headers={'Content-Type': multipart_data.content_type}, verify=self.verify)
        if resp.status_code == 201:
            self.logger.debug("Schema created")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error creating a schema", resp)
        return resp.json()["id"], resp.json()

    def deleteSchema(self, schemaId):
        """
        Delete a schema.  Parameter: schemaId (string). Throws APIException on failure.
        """
        req = ApiClient.oneSchemaUrl % (self.host, "/draft", schemaId)
        resp = requests.delete(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 204:
            self.logger.debug("Schema deleted")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error deleting schema", resp)
        return resp

    def updateSchema(self, schemaId, schemaDefinition):
        """
        Update a schema. Throws APIException on failure.
        """
        req = ApiClient.oneSchemaUrl % (self.host, "/draft", schemaId)
        body = {"schemaDefinition": schemaDefinition}
        resp = requests.put(req, auth=self.credentials, headers={"Content-Type":"application/json"},
                           data=json.dumps(body),  verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("Schema updated")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error updating schema", resp)
        return resp.json()

    def getSchemaContent(self, schemaId, draft=False):
        """
        Get the content for a schema.  Parameters: schemaId (string), draft (boolean). Throws APIException on failure.
        """
        if draft:
            req = ApiClient.oneSchemaContentUrl % (self.host, "/draft", schemaId)
        else:
            req = ApiClient.oneSchemaContentUrl % (self.host, "", schemaId)
        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("Schema content retrieved")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting schema content", resp)
        return resp.json()

    def updateSchemaContent(self, schemaId, schemaFile):
        """
        Updates the content for a schema.  Parameters: schemaId (string). Throws APIException on failure.
        """
        req = ApiClient.oneSchemaContentUrl % (self.host, "/draft", schemaId)
        body = {"schemaFile": schemaFile}
        resp = requests.put(req, auth=self.credentials, headers={"Content-Type":"application/json"},
                           data=json.dumps(body),  verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("Schema content updated")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error updating schema content", resp)
        return resp.json()

    """
    ===========================================================================
    Information Management event type APIs
    ===========================================================================
    """

    def getEventTypes(self, draft=False, name=None, schemaId=None):
        """
        Get all event types for an org.  Throws APIException on failure.
        """
        if draft:
            req = ApiClient.allEventTypesUrl % (self.host, "/draft")
        else:
            req = ApiClient.allEventTypesUrl % (self.host, "")

        if name or schemaId:
            req += "?"
            if name:
                req += "name="+name
            if schemaId:
                if name:
                    req += "&"
                req += "schemaId="+schemaId

        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("All event types retrieved")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting all event types", resp)
        return [x["id"] for x in resp.json()["results"]], resp.json()

    def createEventType(self, name, schemaId, description=None):
        """
        Creates an event type.
        Parameters: name (string), schemaId (string), description (string, optional).
        Returns: event type id (string), response (object).
        Throws APIException on failure.
        """
        req = ApiClient.allEventTypesUrl % (self.host, "/draft")
        body = {"name" : name, "schemaId" : schemaId}
        if description:
            body["description"] = description
        resp = requests.post(req, auth=self.credentials, headers={"Content-Type":"application/json"},
                            data=json.dumps(body),  verify=self.verify)
        if resp.status_code == 201:
            self.logger.debug("event type created")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error creating event type", resp)
        return resp.json()["id"], resp.json()

    def updateEventType(self, eventTypeId, name, schemaId, description=None):
        """
        Updates an event type.
        Parameters: eventTypeId (string), name (string), schemaId (string), description (string, optional).
        Throws APIException on failure.
        """
        req = ApiClient.oneEventTypesUrl % (self.host, "/draft", eventTypeId)
        body = {"name" : name, "schemaId" : schemaId}
        if description:
            body["description"] = description
        resp = requests.put(req, auth=self.credentials, headers={"Content-Type":"application/json"},
                            data=json.dumps(body),  verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("event type updated")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error updating event type", resp)
        return resp.json()

    def deleteEventType(self, eventTypeId):
        """
        Deletes an event type.  Parameters: eventTypeId (string). Throws APIException on failure.
        """
        req = ApiClient.oneEventTypeUrl % (self.host, "/draft", eventTypeId)
        resp = requests.delete(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 204:
            self.logger.debug("event type deleted")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error deleting an event type", resp)
        return resp

    def getEventType(self, eventTypeId, draft=False):
        """
        Gets an event type.  Parameters: eventTypeId (string), draft (boolean).  Throws APIException on failure.
        """
        if draft:
            req = ApiClient.oneEventTypeUrl % (self.host, "/draft", eventTypeId)
        else:
            req = ApiClient.oneEventTypeUrl % (self.host, "", eventTypeId)
        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("event type retrieved")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting an event type", resp)
        return resp.json()

    """
    ===========================================================================
    Information Management Physical Interface APIs
    ===========================================================================
    """

    def getPhysicalInterfaces(self, draft=False, name=None):
        """
        Get all physical interfaces for an org.
        Parameters: draft (boolean).
        Throws APIException on failure.
        """
        if draft:
            req = ApiClient.allPhysicalInterfacesUrl % (self.host, "/draft")
        else:
            req = ApiClient.allPhysicalInterfacesUrl % (self.host, "")

        if name:
            req += "?name="+name

        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("All physical interfaces retrieved")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting all physical interfaces", resp)
        return [x["id"] for x in resp.json()["results"]], resp.json()

    def createPhysicalInterface(self, name, description=None):
        """
        Create a physical interface.
        Parameters:
          - name (string)
          - description (string, optional)
        Returns: physical interface id, response.
        Throws APIException on failure.
        """
        req = ApiClient.allPhysicalInterfacesUrl % (self.host, "/draft")
        body = {"name" : name}
        if description:
            body["description"] = description
        resp = requests.post(req, auth=self.credentials, headers={"Content-Type":"application/json"},
                            data=json.dumps(body),  verify=self.verify)
        if resp.status_code == 201:
            self.logger.debug("physical interface created")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error creating physical interface", resp)
        return resp.json()["id"], resp.json()

    def updatePhysicalInterface(self, physicalInterfaceId, name, schemaId, description=None):
        """
        Update a physical interface.
        Parameters:
          - physicalInterfaceId (string)
          - name (string)
          - schemaId (string)
          - description (string, optional)
        Throws APIException on failure.
        """
        req = ApiClient.onePhysicalInterfacesUrl % (self.host, "/draft", physicalInterfaceId)
        body = {"name" : name, "schemaId" : schemaId}
        if description:
            body["description"] = description
        resp = requests.put(req, auth=self.credentials, headers={"Content-Type":"application/json"},
                            data=json.dumps(body),  verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("physical interface updated")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error updating physical interface", resp)
        return resp.json()

    def deletePhysicalInterface(self, physicalInterfaceId):
        """
        Delete a physical interface.
        Parameters: physicalInterfaceId (string).
        Throws APIException on failure.
        """
        req = ApiClient.onePhysicalInterfaceUrl % (self.host, "/draft", physicalInterfaceId)
        resp = requests.delete(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 204:
            self.logger.debug("physical interface deleted")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error deleting a physical interface", resp)
        return resp

    def getPhysicalInterface(self, physicalInterfaceId, draft=False):
        """
        Get a physical interface.
        Parameters:
          - physicalInterfaceId (string)
          - draft (boolean)
        Throws APIException on failure.
        """
        if draft:
            req = ApiClient.onePhysicalInterfaceUrl % (self.host, "/draft", physicalInterfaceId)
        else:
            req = ApiClient.onePhysicalInterfaceUrl % (self.host, "", physicalInterfaceId)

        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("physical interface retrieved")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting a physical interface", resp)
        return resp.json()


    """
    ===========================================================================
    Information Management Event Mapping APIs
    ===========================================================================
    """

    def getEvents(self, physicalInterfaceId, draft=False):
        """
        Get the event mappings for a physical interface.
        Parameters:
          - physicalInterfaceId (string)
          - draft (boolean)
        Throws APIException on failure.
        """
        if draft:
            req = ApiClient.allEventsUrl % (self.host, "/draft", physicalInterfaceId)
        else:
            req = ApiClient.allEventsUrl % (self.host, "", physicalInterfaceId)

        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("All event mappings retrieved")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting event mappings", resp)
        return resp.json()

    def createEvent(self, physicalInterfaceId, eventTypeId, eventId):
        """
        Create an event mapping for a physical interface.
        Parameters:
          physicalInterfaceId (string) - value returned by the platform when creating the physical interface
          eventTypeId (string) - value returned by the platform when creating the event type
          eventId (string) - matches the event id used by the device in the MQTT topic
        Throws APIException on failure.
        """
        req = ApiClient.allEventsUrl % (self.host, "/draft", physicalInterfaceId)
        body = {"eventId" : eventId, "eventTypeId" : eventTypeId}
        resp = requests.post(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=json.dumps(body),
                       verify=self.verify)
        if resp.status_code == 201:
            self.logger.debug("Event mapping created")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error creating event mapping", resp)
        return resp.json()

    def deleteEvent(self, physicalInterfaceId, eventId):
        """
        Delete an event mapping from a physical interface.
        Parameters: physicalInterfaceId (string), eventId (string).
        Throws APIException on failure.
        """
        req = ApiClient.oneEventUrl % (self.host, "/draft", physicalInterfaceId, eventId)
        resp = requests.delete(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 204:
            self.logger.debug("Event mapping deleted")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error deleting event mapping", resp)
        return resp


    """
    ===========================================================================
    Information Management Logical Interface APIs
    ===========================================================================
    """

    def getLogicalInterfaces(self, draft=False, name=None, schemaId=None):
        """
        Get all logical interfaces for an org.
        Parameters: draft (boolean).
        Returns:
            - list of ids
            - response object
        Throws APIException on failure.
        """
        if draft:
            req = ApiClient.allLogicalInterfacesUrl % (self.host, "/draft")
        else:
            req = ApiClient.allLogicalInterfacesUrl % (self.host, "")

        if name or schemaId:
            req += "?"
            if name:
                req += "name="+name
            if schemaId:
                if name:
                    req += "&"
                req += "schemaId="+schemaId

        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("All logical interfaces retrieved")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting all logical interfaces", resp)
        return [x["id"] for x in resp.json()["results"]], resp.json()

    def createLogicalInterface(self, name, schemaId, description=None, alias=None):
        """
        Creates a logical interface..
        Parameters: name (string), schemaId (string), description (string, optional), alias (string, optional).
        Returns: logical interface id (string), response (object).
        Throws APIException on failure.
        """
        req = ApiClient.allLogicalInterfacesUrl % (self.host, "/draft")
        body = {"name" : name, "schemaId" : schemaId}
        if description:
          body["description"] = description
        if alias:
          body["alias"] = alias
        resp = requests.post(req, auth=self.credentials, headers={"Content-Type":"application/json"},
                            data=json.dumps(body), verify=self.verify)
        if resp.status_code == 201:
            self.logger.debug("Logical interface created")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error creating logical interface", resp)
        return resp.json()["id"], resp.json()

    def updateLogicalInterface(self, logicalInterfaceId, name, schemaId, description=None):
        """
        Updates a logical interface.
        Parameters: logicalInterfaceId (string), name (string), schemaId (string), description (string, optional).
        Throws APIException on failure.
        """
        req = ApiClient.oneLogicalInterfaceUrl % (self.host, "/draft", logicalInterfaceId)
        body = {"name" : name, "schemaId" : schemaId, "id" : logicalInterfaceId}
        if description:
            body["description"] = description
        resp = requests.put(req, auth=self.credentials, headers={"Content-Type":"application/json"},
                            data=json.dumps(body),  verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("Logical interface updated")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error updating logical interface", resp)
        return resp.json()

    def deleteLogicalInterface(self, logicalInterfaceId):
        """
        Deletes a logical interface.
        Parameters: logicalInterfaceId (string).
        Throws APIException on failure.
        """
        req = ApiClient.oneLogicalInterfaceUrl % (self.host, "/draft", logicalInterfaceId)
        resp = requests.delete(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 204:
            self.logger.debug("logical interface deleted")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error deleting a logical interface", resp)
        return resp

    def getLogicalInterface(self, logicalInterfaceId, draft=False):
        """
        Gets a logical interface.
        Parameters:
          - logicalInterfaceId (string)
          - draft (boolean)
        Throws APIException on failure.
        """
        if draft:
            req = ApiClient.oneLogicalInterfaceUrl % (self.host, "/draft", logicalInterfaceId)
        else:
            req = ApiClient.oneLogicalInterfaceUrl % (self.host, "", logicalInterfaceId)
        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("logical interface retrieved")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting a logical interface", resp)
        return resp.json()

    def getRulesForLogicalInterface(self, logicalInterfaceId, draft=False):
        """
        Gets rules for a logical interface.
        Parameters:
          - logicalInterfaceId (string)
          - draft (boolean)
        Throws APIException on failure.
        """
        if draft:
            req = ApiClient.allRulesForLogicalInterfaceUrl % (self.host, "/draft", logicalInterfaceId)
        else:
            req = ApiClient.allRulesForLogicalInterfaceUrl % (self.host, "", logicalInterfaceId)
        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("logical interface rules retrieved")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting logical interface rules", resp)
        return resp.json()

    def getRuleForLogicalInterface(self, logicalInterfaceId, ruleId, draft=False):
        """
        Gets a rule for a logical interface.
        Parameters:
          - logicalInterfaceId (string)
          - ruleId (string)
          - draft (boolean)
        Throws APIException on failure.
        """
        if draft:
            req = ApiClient.oneRuleForLogicalInterfaceUrl % (self.host, "/draft", logicalInterfaceId, ruleId)
        else:
            req = ApiClient.oneRuleForLogicalInterfaceUrl % (self.host, "", logicalInterfaceId, ruleId)
        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("logical interface rule retrieved")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting logical interface rule", resp)
        return resp.json()

    def addRuleToLogicalInterface(self, logicalInterfaceId, name, condition, description=None, alias=None):
        """
        Adds a rule to a logical interface.
        Parameters: 
          - logicalInterfaceId (string)
          - name (string)
          - condition (string)
          - (description (string, optional)
        Returns: rule id (string), response (object).
        Throws APIException on failure.
        """
        req = ApiClient.allRulesForLogicalInterfaceUrl % (self.host, "/draft", logicalInterfaceId)
        body = {"name" : name, "condition" : condition}
        if description:
          body["description"] = description
        resp = requests.post(req, auth=self.credentials, headers={"Content-Type":"application/json"},
                            data=json.dumps(body), verify=self.verify)
        if resp.status_code == 201:
            self.logger.debug("Logical interface rule created")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error creating logical interface rule", resp)
        return resp.json()["id"], resp.json()

    def updateRuleOnLogicalInterface(self, logicalInterfaceId, ruleId, name, condition, description=None):
        """
        Updates a rule on a logical interface..
        Parameters: 
          - logicalInterfaceId (string),
          - ruleId (string)
          - name (string)
          - condition (string)
          - description (string, optional)
        Returns: response (object).
        Throws APIException on failure.
        """
        req = ApiClient.oneRuleForLogicalInterfaceUrl % (self.host, "/draft", logicalInterfaceId, ruleId)
        body = {"logicalInterfaceId" : logicalInterfaceId, "id" : ruleId, "name" : name, "condition" : condition}
        if description:
          body["description"] = description
        resp = requests.put(req, auth=self.credentials, headers={"Content-Type":"application/json"},
                            data=json.dumps(body), verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("Logical interface rule updated")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error updating logical interface rule", resp)
        return resp.json()

    def deleteRuleOnLogicalInterface(self, logicalInterfaceId, ruleId):
        """
        Deletes a rule from a logical interface
        Parameters: 
          - logicalInterfaceId (string),
          - ruleId (string)
        Returns: response (object)
        Throws APIException on failure
        """
        req = ApiClient.oneRuleForLogicalInterfaceUrl % (self.host, "/draft", logicalInterfaceId, ruleId)
        resp = requests.delete(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 204:
            self.logger.debug("Logical interface rule deleted")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error deleting logical interface rule", resp)
        return resp


    """
    ===========================================================================
    Information Management Device Type APIs
    ===========================================================================
    """

    def addPhysicalInterfaceToDeviceType(self, typeId, physicalInterfaceId):
        """
        Adds a physical interface to a device type.
        Parameters:
            - typeId (string) - the device type
            - physicalInterfaceId (string) - the id returned by the platform on creation of the physical interface
        Throws APIException on failure.
        """
        req = ApiClient.oneDeviceTypePhysicalInterfaceUrl % (self.host, "/draft", typeId)
        body = {"id" : physicalInterfaceId}
        resp = requests.post(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=json.dumps(body),
                       verify=self.verify)
        if resp.status_code == 201:
            self.logger.debug("Physical interface added to a device type")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error adding physical interface to a device type", resp)
        return resp.json()

    def getPhysicalInterfaceOnDeviceType(self, typeId, draft=False):
        """
        Gets the physical interface associated with a device type.
        Parameters:
            - typeId (string) - the device type
            - draft (boolean)
        Throws APIException on failure.
        """
        if draft:
            req = ApiClient.oneDeviceTypePhysicalInterfaceUrl % (self.host, "/draft", typeId)
        else:
            req = ApiClient.oneDeviceTypePhysicalInterfaceUrl % (self.host, "", typeId)
        resp = requests.get(req, auth=self.credentials, headers={"Content-Type":"application/json"},
                       verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("Physical interface retrieved from a device type")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting physical interface on a device type", resp)
        return resp.json()["id"], resp.json()

    def removePhysicalInterfaceFromDeviceType(self, typeId):
        """
        Removes the physical interface from a device type.  Only one can be associated with a device type,
          so the physical interface id is not necessary as a parameter.
        Parameters:
                    - typeId (string) - the device type
        Throws APIException on failure.
        """
        req = ApiClient.oneDeviceTypePhysicalInterfaceUrl % (self.host, "/draft", typeId)
        body = {}
        resp = requests.delete(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=json.dumps(body),
           verify=self.verify)
        if resp.status_code == 204:
            self.logger.debug("Physical interface removed")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error removing a physical interface from a device type", resp)
        return resp

    def getLogicalInterfacesOnDeviceType(self, typeId, draft=False):
        """
        Get all logical interfaces for a device type.
        Parameters:
          - typeId (string)
          - draft (boolean)
        Returns:
            - list of logical interface ids
            - HTTP response object
        Throws APIException on failure.
        """
        if draft:
            req = ApiClient.allDeviceTypeLogicalInterfacesUrl % (self.host, "/draft", typeId)
        else:
            req = ApiClient.allDeviceTypeLogicalInterfacesUrl % (self.host, "", typeId)
        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("All device type logical interfaces retrieved")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting all device type logical interfaces", resp)
        return [appintf["id"] for appintf in resp.json()], resp.json()

    def addLogicalInterfaceToDeviceType(self, typeId, logicalInterfaceId):
        """
        Adds a logical interface to a device type.
        Parameters:
            - typeId (string) - the device type
            - logicalInterfaceId (string) - the id returned by the platform on creation of the logical interface
            - description (string) - optional (not used)
        Throws APIException on failure.
        """
        req = ApiClient.allDeviceTypeLogicalInterfacesUrl % (self.host, "/draft", typeId)
        body = {"id" : logicalInterfaceId}
#       body = {"name" : "required but not used!!!", "id" : logicalInterfaceId, "schemaId" : schemaId}
#       if description:
#           body["description"] = description
        resp = requests.post(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=json.dumps(body),
                        verify=self.verify)
        if resp.status_code == 201:
            self.logger.debug("Logical interface added to a device type")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error adding logical interface to a device type", resp)
        return resp.json()

    def removeLogicalInterfaceFromDeviceType(self, typeId, logicalInterfaceId):
        """
        Removes a logical interface from a device type.
        Parameters:
            - typeId (string) - the device type
            - logicalInterfaceId (string) - the id returned by the platform on creation of the logical interface
        Throws APIException on failure.
        """
        req = ApiClient.oneDeviceTypeLogicalInterfaceUrl % (self.host, typeId, logicalInterfaceId)
        resp = requests.delete(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 204:
            self.logger.debug("Logical interface removed from a device type")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error removing logical interface from a device type", resp)
        return resp

    def getMappingsOnDeviceType(self, typeId, draft=False):
        """
        Get all the mappings for a device type.
        Parameters:
            - typeId (string) - the device type
            - draft (boolean) - draft or active
        Throws APIException on failure.
        """
        if draft:
            req = ApiClient.allDeviceTypeMappingsUrl % (self.host, "/draft", typeId)
        else:
            req = ApiClient.allDeviceTypeMappingsUrl % (self.host, "", typeId)

        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("All device type mappings retrieved")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting all device type mappings", resp)
        return resp.json()

    def addMappingsToDeviceType(self, typeId, logicalInterfaceId, mappingsObject, notificationStrategy = "never"):
        """
        Add mappings for a device type.
        Parameters:
            - typeId (string) - the device type
            - logicalinterface (string) - the id of the application interface these mappings are for
            - notificationStrategy (string) - the notification strategy to use for these mappings
            - mappingsObject (Python dictionary corresponding to JSON object) example:

            { # eventid -> { property -> eventid property expression }
         "status" :  {
                "eventCount" : "($state.eventCount == -1) ? $event.d.count : ($state.eventCount+1)",
           }
        }

        Throws APIException on failure.
        """
        req = ApiClient.allDeviceTypeMappingsUrl % (self.host, "/draft", typeId)
        try:
            mappings = json.dumps({
                "logicalInterfaceId" : logicalInterfaceId,
                "notificationStrategy" : notificationStrategy,
                "propertyMappings" : mappingsObject
            })
        except Exception as exc:
            raise ibmiotf.APIException(-1, "Exception formatting mappings object to JSON", exc)
        resp = requests.post(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=mappings,
               verify=self.verify)
        if resp.status_code == 201:
            self.logger.debug("Device type mappings created for logical interface")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error creating device type mappings for logical interface", resp)
        return resp.json()

    def deleteMappingsFromDeviceType(self, typeId, logicalInterfaceId):
        """
        Deletes mappings for an application interface from a device type.
        Parameters:
            - typeId (string) - the device type
          - logicalInterfaceId (string) - the platform returned id of the application interface
        Throws APIException on failure.
        """
        req = ApiClient.oneDeviceTypeMappingUrl % (self.host, "/draft", typeId, logicalInterfaceId)
        resp = requests.delete(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 204:
            self.logger.debug("Mappings deleted from the device type")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error deleting mappings for a logical interface from a device type", resp)
        return resp

    def getMappingsOnDeviceTypeForLogicalInterface(self, typeId, logicalInterfaceId, draft=False):
        """
        Gets the mappings for a logical interface from a device type.
        Parameters:
            - typeId (string) - the device type
            - logicalInterfaceId (string) - the platform returned id of the logical interface
        Throws APIException on failure.
        """
        if draft:
            req = ApiClient.oneDeviceTypeMappingUrl % (self.host, "/draft", typeId, logicalInterfaceId)
        else:
            req = ApiClient.oneDeviceTypeMappingUrl % (self.host, "", typeId, logicalInterfaceId)

        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("Mappings retrieved from the device type")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting mappings for a logical interface from a device type", resp)
        return resp.json()

    def updateMappingsOnDeviceType(self, typeId, logicalInterfaceId, mappingsObject, notificationStrategy = "never"):
        """
        Add mappings for a device type.
        Parameters:
            - typeId (string) - the device type
            - logicalInterfaceId (string) - the id of the application interface these mappings are for
            - notificationStrategy (string) - the notification strategy to use for these mappings
            - mappingsObject (Python dictionary corresponding to JSON object) example:

            { # eventid -> { property -> eventid property expression }
         "status" :  {
                "eventCount" : "($state.eventCount == -1) ? $event.d.count : ($state.eventCount+1)",
           }
      }

        Throws APIException on failure.
        """
        req = ApiClient.oneDeviceTypeMappingUrl % (self.host, "/draft", typeId, logicalInterfaceId)
        try:
            mappings = json.dumps({
                "logicalInterfaceId" : logicalInterfaceId,
                "notificationStrategy" : notificationStrategy,
                "propertyMappings" : mappingsObject
            })
        except Exception as exc:
            raise ibmiotf.APIException(-1, "Exception formatting mappings object to JSON", exc)
        resp = requests.put(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=mappings,
               verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("Device type mappings updated for logical interface")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error updating device type mappings for logical interface", resp)
        return resp.json()

    """
    ===========================================================================
    Information Management Device APIs
    ===========================================================================
    # """

    def validateDeviceTypeConfiguration(self, typeId):
        """
        Validate the device type configuration.
        Parameters:
            - typeId (string) - the platform device type
        Throws APIException on failure.
        """
        req = ApiClient.draftDeviceTypeUrl % (self.host, typeId)
        body = {"operation" : "validate-configuration"}
        resp = requests.patch(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=json.dumps(body),
               verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("Validation for device type configuration succeeded")
        else:
            raise ibmiotf.APIException(resp.status_code, "Validation for device type configuration failed", resp)
        return resp.json()

    def activateDeviceTypeConfiguration(self, typeId):
        """
        Activate the device type configuration.
        Parameters:
            - typeId (string) - the platform device type
        Throws APIException on failure.
        """
        req = ApiClient.draftDeviceTypeUrl % (self.host, typeId)
        body = {"operation" : "activate-configuration"}
        resp = requests.patch(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=json.dumps(body),
               verify=self.verify)
        if (resp.status_code == 202):
            self.logger.debug("Activation for device type configuration succeeded")
        else:
            raise ibmiotf.APIException(resp.status_code, "Activation for device type configuration failed", resp)
        return resp.json()

    def deactivateDeviceTypeConfiguration(self, typeId):
        """
        Deactivate the device type configuration.
        Parameters:
            - typeId (string) - the platform device type
        Throws APIException on failure.
        """
        req = ApiClient.deviceTypeUrl % (self.host, typeId)
        body = {"operation" : "deactivate-configuration"}
        resp = requests.patch(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=json.dumps(body),
               verify=self.verify)
        if resp.status_code == 202:
            self.logger.debug("Deactivation for device type configuration succeeded")
        else:
            raise ibmiotf.APIException(resp.status_code, "Deactivation for device type configuration failed", resp)
        return resp.json()

    def validateLogicalInterfaceConfiguration(self, logicalInterfaceId):
        """
        Validate the logical interface configuration.
        Parameters:
            - logicalInterfaceId (string)
        Throws APIException on failure.
        """
        req = ApiClient.oneLogicalInterfaceUrl % (self.host, "/draft", logicalInterfaceId)
        body = {"operation" : "validate-configuration"}
        resp = requests.patch(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=json.dumps(body),
               verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("Validation for logical interface configuration succeeded")
        else:
            raise ibmiotf.APIException(resp.status_code, "Validation for logical interface configuration failed", resp)
        return resp.json()

    def activateLogicalInterfaceConfiguration(self, logicalInterfaceId):
        """
        Activate the logical interface configuration.
        Parameters:
            - logicalInterfaceId (string)
        Throws APIException on failure.
        """
        req = ApiClient.oneLogicalInterfaceUrl % (self.host, "/draft", logicalInterfaceId)
        body = {"operation" : "activate-configuration"}
        resp = requests.patch(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=json.dumps(body),
               verify=self.verify)
        if (resp.status_code == 202):
            self.logger.debug("Activation for logical interface configuration succeeded")
        else:
            raise ibmiotf.APIException(resp.status_code, "Activation for logical interface configuration failed", resp)
        return resp.json()

    def deactivateLogicalInterfaceConfiguration(self, logicalInterfaceId):
        """
        Deactivate the logical interface configuration.
        Parameters:
            - logicalInterfaceId (string)
        Throws APIException on failure.
        """
        req = ApiClient.oneLogicalInterfaceUrl % (self.host, "/draft", logicalInterfaceId)
        body = {"operation" : "deactivate-configuration"}
        resp = requests.patch(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=json.dumps(body),
               verify=self.verify)
        if resp.status_code == 202:
            self.logger.debug("Deactivate for logical interface configuration succeeded")
        else:
            raise ibmiotf.APIException(resp.status_code, "Deactivate for logical interface configuration failed", resp)
        return resp.json()

    def getDeviceStateForLogicalInterface(self, typeId, deviceId, logicalInterfaceId):
        """
        Gets the state for a logical interface for a device.
        Parameters:
            - typeId (string) - the platform device type
            - deviceId (string) - the platform device id
            - logicalInterfaceId (string) - the platform returned id of the logical interface
        Throws APIException on failure.
        """
        req = ApiClient.deviceStateUrl % (self.host, typeId, deviceId, logicalInterfaceId)
        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("State retrieved from the device type for a logical interface")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting state for a logical interface from a device type", resp)
        return resp.json()
    
    """
    ===========================================================================
    Information Management Things APIs
    ===========================================================================
    """
    
    def validateThingTypeConfiguration(self, thingTypeId):
        """
        Validate the thing type configuration.
        Parameters:
            - thingTypeId (string) - the platform thing type
        Throws APIException on failure.
        """
        req = ApiClient.draftThingTypeUrl % (self.host, thingTypeId)
        body = {"operation" : "validate-configuration"}
        resp = requests.patch(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=json.dumps(body),
               verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("Validation for thing type configuration succeeded")
        else:
            raise ibmiotf.APIException(resp.status_code, "Validation for thing type configuration failed", resp)
        return resp.json()

    def activateThingTypeConfiguration(self, thingTypeId):
        """
        Activate the thing type configuration.
        Parameters:
            - thingTypeId (string) - the platform thing type
        Throws APIException on failure.
        """
        req = ApiClient.draftThingTypeUrl % (self.host, thingTypeId)
        body = {"operation" : "activate-configuration"}
        resp = requests.patch(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=json.dumps(body),
               verify=self.verify)
        if (resp.status_code == 202):
            self.logger.debug("Activation for thing type configuration succeeded")
        else:
            raise ibmiotf.APIException(resp.status_code, "Activation for thing type configuration failed", resp)
        return resp.json()

    def deactivateDeviceTypeConfiguration(self, thingTypeId):
        """
        Deactivate the thing type configuration.
        Parameters:
            - thingTypeId (string) - the platform thing type
        Throws APIException on failure.
        """
        req = ApiClient.thingTypeUrl % (self.host, thingTypeId)
        body = {"operation" : "deactivate-configuration"}
        resp = requests.patch(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=json.dumps(body),
               verify=self.verify)
        if resp.status_code == 202:
            self.logger.debug("Deactivation for thing type configuration succeeded")
        else:
            raise ibmiotf.APIException(resp.status_code, "Deactivation for thing type configuration failed", resp)
        return resp.json()
    
    def getThingStateForLogicalInterface(self, thingTypeId, thingId, logicalInterfaceId):
        """
        Gets the state for a logical interface for a thing.
        Parameters:
            - thingTypeId (string) - the platform thing type
            - thingId (string) - the platform thing id
            - logicalInterfaceId (string) - the platform returned id of the logical interface
        Throws APIException on failure.
        """
        req = ApiClient.thingStateUrl % (self.host, thingTypeId, thingId, logicalInterfaceId)
        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("State retrieved from the thing type for a logical interface")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting state for a logical interface from a thing type", resp)
        return resp.json()

    def resetThingStateForLogicalInterface(self, thingTypeId, thingId , logicalInterfaceId):
        """
        Perform an operation against the thing state for a logical interface
        Parameters:
           - thingTypeId (string)
           - thingId (string)
           - logicalInterfaceId (string)
        Throws APIException on failure.
        """
        req = ApiClient.thingStateUrl % (self.host, "", thingTypeId,thingId , logicalInterfaceId)
        body = {"operation" : "reset-state"}
        resp = requests.patch(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=json.dumps(body),
               verify=self.verify)
        if (resp.status_code == 200):
            self.logger.debug("Reset ThingState For LogicalInterface succeeded")
        else:
            raise ibmiotf.APIException(resp.status_code, " HTTP error on reset ThingState For LogicalInterface ", resp)
        return resp.json()


    """
    ===========================================================================
    Information Management Things type APIs
    ===========================================================================
    """
    
    def getLogicalInterfacesOnThingType(self, thingTypeId, draft=False):
        """
        Get all logical interfaces for a thing type.
        Parameters:
          - thingTypeId (string)
          - draft (boolean)
        Returns:
            - list of logical interface ids
            - HTTP response object
        Throws APIException on failure.
        """
        if draft:
            req = ApiClient.allThingTypeLogicalInterfacesUrl % (self.host, "/draft", thingTypeId)
        else:
            req = ApiClient.allThingTypeLogicalInterfacesUrl % (self.host, "", thingTypeId)
        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("All thing type logical interfaces retrieved")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting all thing type logical interfaces", resp)
        return [appintf["id"] for appintf in resp.json()], resp.json()

    def addLogicalInterfaceToThingType(self, thingTypeId, logicalInterfaceId, schemaId = None, name = None):
        """
        Adds a logical interface to a thing type.
        Parameters:
            - thingTypeId (string) - the thing type
            - logicalInterfaceId (string) - the id returned by the platform on creation of the logical interface
        Throws APIException on failure.
        """
        req = ApiClient.allThingTypeLogicalInterfacesUrl % (self.host, "/draft", thingTypeId)
        body = {"id" : logicalInterfaceId}
#        body = {"name" : name, "id" : logicalInterfaceId, "schemaId" : schemaId}
#       if description:
#           body["description"] = description
        resp = requests.post(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=json.dumps(body),
                        verify=self.verify)
        if resp.status_code == 201:
            self.logger.debug("The draft logical interface was successfully associated with the thing type.")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error adding logical interface to a thing type", resp)
        return resp.json()

    def removeLogicalInterfaceFromThingType(self, thingTypeId, logicalInterfaceId):
        """
        Removes a logical interface from a thing type.
        Parameters:
            - thingTypeId (string) - the thing type
            - logicalInterfaceId (string) - the id returned by the platform on creation of the logical interface
        Throws APIException on failure.
        """
        req = ApiClient.oneThingTypeLogicalInterfaceUrl % (self.host, thingTypeId, logicalInterfaceId)
        resp = requests.delete(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 204:
            self.logger.debug("Logical interface removed from a thing type")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error removing logical interface from a thing type", resp)
        return resp
    
    def getMappingsOnThingType(self, thingTypeId, draft=False):
        """
        Get all the mappings for a thing type.
        Parameters:
            - thingTypeId (string) - the thing type
            - draft (boolean) - draft or active
        Throws APIException on failure.
        """
        if draft:
            req = ApiClient.allThingTypeMappingsUrl % (self.host, "/draft", thingTypeId)
        else:
            req = ApiClient.allThingTypeMappingsUrl % (self.host, "", thingTypeId)

        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("All thing type mappings retrieved")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting all thing type mappings", resp)
        return resp.json()

    def addMappingsToThingType(self, thingTypeId, logicalInterfaceId, mappingsObject, notificationStrategy = "never"):
        """
        Add mappings for a thing type.
        Parameters:
            - thingTypeId (string) - the thing type
            - logicalinterface (string) - the id of the application interface these mappings are for
            - notificationStrategy (string) - the notification strategy to use for these mappings
            - mappingsObject (Python dictionary corresponding to JSON object) example:

            { # eventid -> { property -> eventid property expression }
         "status" :  {
                "eventCount" : "($state.eventCount == -1) ? $event.d.count : ($state.eventCount+1)",
           }
        }

        Throws APIException on failure.
        """
        req = ApiClient.allThingTypeMappingsUrl % (self.host, "/draft", thingTypeId)
        try:
            mappings = json.dumps({
                "logicalInterfaceId" : logicalInterfaceId,
                "notificationStrategy" : notificationStrategy,
                "propertyMappings" : mappingsObject
            })
        except Exception as exc:
            raise ibmiotf.APIException(-1, "Exception formatting mappings object to JSON", exc)
        resp = requests.post(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=mappings,
               verify=self.verify)
        if resp.status_code == 201:
            self.logger.debug("Thing type mappings created for logical interface")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error creating Thing type mappings for logical interface", resp)
        return resp.json()

    def deleteMappingsFromThingType(self, thingTypeId, logicalInterfaceId):
        """
        Deletes mappings for an application interface from a thing type.
        Parameters:
            - thingTypeId (string) - the thing type
            - logicalInterfaceId (string) - the platform returned id of the application interface
        Throws APIException on failure.
        """
        req = ApiClient.oneThingTypeMappingUrl % (self.host, "/draft", thingTypeId, logicalInterfaceId)
        resp = requests.delete(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 204:
            self.logger.debug("Mappings deleted from the thing type")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error deleting mappings for a logical interface from a thing type", resp)
        return resp

    def getMappingsOnThingTypeForLogicalInterface(self, thingTypeId, logicalInterfaceId, draft=False):
        """
        Gets the mappings for a logical interface from a thing type.
        Parameters:
            - thingTypeId (string) - the thing type
            - logicalInterfaceId (string) - the platform returned id of the logical interface
        Throws APIException on failure.
        """
        if draft:
            req = ApiClient.oneThingTypeMappingUrl % (self.host, "/draft", thingTypeId, logicalInterfaceId)
        else:
            req = ApiClient.oneThingTypeMappingUrl % (self.host, "", thingTypeId, logicalInterfaceId)

        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("Mappings retrieved from the thing type")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting mappings for a logical interface from a thing type", resp)
        return resp.json()

    def updateMappingsOnDeviceType(self, thingTypeId, logicalInterfaceId, mappingsObject, notificationStrategy = "never"):
        """
        Add mappings for a thing type.
        Parameters:
            - thingTypeId (string) - the thing type
            - logicalInterfaceId (string) - the id of the application interface these mappings are for
            - notificationStrategy (string) - the notification strategy to use for these mappings
            - mappingsObject (Python dictionary corresponding to JSON object) example:

            { # eventid -> { property -> eventid property expression }
         "status" :  {
                "eventCount" : "($state.eventCount == -1) ? $event.d.count : ($state.eventCount+1)",
           }
      }

        Throws APIException on failure.
        """
        req = ApiClient.oneThingTypeMappingUrl % (self.host, "/draft", thingTypeId, logicalInterfaceId)
        try:
            mappings = json.dumps({
                "logicalInterfaceId" : logicalInterfaceId,
                "notificationStrategy" : notificationStrategy,
                "propertyMappings" : mappingsObject
            })
        except Exception as exc:
            raise ibmiotf.APIException(-1, "Exception formatting mappings object to JSON", exc)
        resp = requests.put(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=mappings,
               verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("Thing type mappings updated for logical interface")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error updating thing type mappings for logical interface", resp)
        return resp.json()
        
        
