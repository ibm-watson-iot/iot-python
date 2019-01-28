# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

from collections import defaultdict
import json

class ServiceBindingCredentials(defaultdict):
    def __init__(self, **kwargs):
        dict.__init__(self, **kwargs)


class CloudantServiceBindingCredentials(ServiceBindingCredentials):
    def __init__(self, **kwargs):
        if not set(['host', 'port', 'username', 'password']).issubset(kwargs):
            raise Exception("host, port, username, & password are required parameters for a Cloudant Service Binding: %s" % (json.dumps(kwargs, sort_keys=True)))
        
        if ['url' not in kwargs]:
            kwargs['url'] = "https://%s:%s@%s:%s" % (kwargs['username'], kwargs['password'], kwargs['host'], kwargs['port'])

        ServiceBindingCredentials.__init__(self, **kwargs)

    @property
    def url(self):
        return self["url"]
    @property
    def host(self):
        return self["host"]
    @property
    def port(self):
        return self["port"]
    @property
    def username(self):
        return self["username"]
    @property
    def password(self):
        return self["password"]


class EventStreamsServiceBindingCredentials(ServiceBindingCredentials):
    def __init__(self, **kwargs):
        if not set(['host', 'port', 'username', 'password']).issubset(kwargs):
            raise Exception("host, port, username, & password are required parameters for a Cloudant Service Binding: %s" % (json.dumps(kwargs, sort_keys=True)))
        
        if ['url' not in kwargs]:
            kwargs['url'] = "https://%s:%s@%s:%s" % (kwargs['username'], kwargs['password'], kwargs['host'], kwargs['port'])

        ServiceBindingCredentials.__init__(self, **kwargs)

    @property
    def url(self):
        return self["url"]
    @property
    def host(self):
        return self["host"]
    @property
    def port(self):
        return self["port"]
    @property
    def username(self):
        return self["username"]
    @property
    def password(self):
        return self["password"]
