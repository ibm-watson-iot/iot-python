# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

from collections import defaultdict
from requests_toolbelt.multipart.encoder import MultipartEncoder

from wiotp.sdk.api.common import IterableList
from wiotp.sdk.api.common import RestApiItemBase
from wiotp.sdk.api.common import RestApiDict
from wiotp.sdk.api.common import RestApiDictReadOnly
from wiotp.sdk.exceptions import ApiException

import json


# See docs @ https://orgid.internetofthings.ibmcloud.com/docs/v0002-beta/Schema-mgr-beta.html


class Schema(RestApiItemBase):
    def __init__(self, apiClient, **kwargs):
        super(Schema, self).__init__(apiClient, **kwargs)
        self.contentUrl = None

    # Note - data accessor functions for common data items are defined in RestApiItemBase

    @property
    def schemaType(self):
        return self["schemaType"]

    @property
    def schemaFileName(self):
        return self["schemaFileName"]

    @property
    def contentType(self):
        return self["contentType"]

    @property
    def content(self):
        # determine the REST URL to call
        if self.contentUrl == None:
            if self.version == "draft":
                self.contentUrl = "api/v0002/draft/schemas/%s/content" % (self.id)
            elif self.version == "active":
                self.contentUrl = "api/v0002/schemas/%s/content" % (self.id)
            else:
                raise Exception("Schema version is not recognised: (%s)" % (self.version))

        # call the Rest API
        r = self._apiClient.get((self.contentUrl))
        if r.status_code == 200:
            return r.json()
        else:
            raise Exception("Unexpected response from API (%s) = %s %s" % (self.contentUrl, r.status_code, r.text))

    @property
    def version(self):
        return self["version"]


class IterableSchemaList(IterableList):
    def __init__(self, apiClient, url, filters=None):
        # This API does not support sorting
        super(IterableSchemaList, self).__init__(apiClient, Schema, url, filters=filters)


class ActiveSchemas(RestApiDict):
    def __init__(self, apiClient):
        super(ActiveSchemas, self).__init__(apiClient, Schema, IterableSchemaList, "api/v0002/schemas")


class DraftSchemas(RestApiDict):
    def __init__(self, apiClient):
        super(DraftSchemas, self).__init__(apiClient, Schema, IterableSchemaList, "api/v0002/draft/schemas")

    def create(self, name, schemaFileName, schemaContents, description):

        """
        Create a schema for the org.
        Returns: schemaId (string), response (object).
        Throws APIException on failure
        """
        if not isinstance(schemaContents, str):
            schemaContents = json.dumps(schemaContents)

        fields = {
            "schemaFile": (schemaFileName, schemaContents, "application/json"),
            "schemaType": "json-schema",
            "name": name,
        }
        if description:
            fields["description"] = description

        multipart_data = MultipartEncoder(fields=fields)

        r = self._apiClient.postMultipart(self._baseUrl, multipart_data)
        if r.status_code == 201:
            return Schema(apiClient=self._apiClient, **r.json())
        else:
            raise ApiException(r)

    def updateContent(self, schemaId, schemaFileName, schemaContents):
        """
        Updates a schema for the org.
        Returns: True on success
        Throws APIException on failure
        """
        if not isinstance(schemaContents, str):
            schemaContents = json.dumps(schemaContents)

        fields = {"schemaFile": (schemaFileName, schemaContents, "application/json")}

        multipart_data = MultipartEncoder(fields=fields)

        r = self._apiClient.putMultipart("%s/%s/content" % (self._baseUrl, schemaId), multipart_data)
        if r.status_code == 204:
            return True
        else:
            raise ApiException(r)
