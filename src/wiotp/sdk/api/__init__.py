# *****************************************************************************
# Copyright (c) 2015, 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************
from wiotp.sdk.api.common import ApiClient
from wiotp.sdk.api.registry import Registry
from wiotp.sdk.api.usage import Usage
from wiotp.sdk.api.status import ServiceStatus
from wiotp.sdk.api.dsc import DSC
from wiotp.sdk.api.lec import LEC
from wiotp.sdk.api.mgmt import Mgmt
from wiotp.sdk.api.services import ServiceBindings
from wiotp.sdk.api.actions import Actions
from wiotp.sdk.api.state import StateMgr

# This method returns the organization
# def getOrganizationDetails(self):
#    """
#    Get details about an organization
#    It does not need any parameter to be passed
#    In case of failure it throws APIException
#    """
#    if self.__options['org'] is None:
#        raise ibmiotf.ConfigurationException("Missing required property: org")
#    else:
#        url = ApiClient.organizationUrl % (self.host)
#    r = requests.get(url, auth=self.credentials, verify=self.verify)
#    status = r.status_code
#    if status == 200:
#        self.logger.debug("Organization retrieved")
#        return r.json()
#    elif status == 401:
#        raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
#    elif status == 403:
#        raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
#    elif status == 404:
#        raise ibmiotf.APIException(404, "The organization does not exist", None)
#    elif status == 500:
#        raise ibmiotf.APIException(500, "Unexpected error", None)
#    else:
#        raise ibmiotf.APIException(None, "Unexpected error", None)
