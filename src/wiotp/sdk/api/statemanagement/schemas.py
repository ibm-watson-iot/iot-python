# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

from collections import defaultdict
import iso8601

from wiotp.sdk.api.common import IterableList
from wiotp.sdk.api.common import  RestApiDict

# See docs @ https://orgid.internetofthings.ibmcloud.com/docs/v0002-beta/Schema-mgr-beta.html


class Schema(defaultdict):
    def __init__(self, apiClient, **kwargs):
        self._apiClient = apiClient
        dict.__init__(self, **kwargs)

    @property
    def id(self):
        return self["id"]
    
    @property
    def name(self):
        return self["name"]

    @property
    def description(self):
        return self["description"]

    @property
    def SchemaType(self):
        return self["type"]

    @property
    def enabled(self):
        return self["enabled"]
    
    @property
    def configuration(self):
        return self["configuration"]
    
    @property
    def created(self):
        return iso8601.parse_date(self["created"])

    @property
    def createdBy(self):
        return self["createdBy"]

    @property
    def updated(self):
        return iso8601.parse_date(self["updated"])

    @property
    def updatedBy(self):
        return self["updatedBy"]

class IterableSchemaList(IterableList):
    def __init__(self, apiClient, filters=None):
        # This API does not support sorting
        super(IterableSchemaList, self).__init__(
            apiClient, Schema, "api/v0002/schemas", sort=None, filters=filters, passApiClient=True
        )


class Schemas(RestApiDict):

    def __init__(self, apiClient):
        super(Schemas, self).__init__(
            apiClient, Schema, IterableSchemaList, "api/v0002/schemas"
        )
        