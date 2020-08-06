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
        if not set(["host", "port", "username", "password"]).issubset(kwargs):
            raise Exception(
                "host, port, username, & password are required parameters for a Cloudant Service Binding: %s"
                % (json.dumps(kwargs, sort_keys=True))
            )

        if ["url" not in kwargs]:
            kwargs["url"] = "https://%s:%s@%s:%s" % (
                kwargs["username"],
                kwargs["password"],
                kwargs["host"],
                kwargs["port"],
            )

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
        if not set(["api_key", "kafka_admin_url", "kafka_brokers_sasl", "user", "password"]).issubset(kwargs):
            raise Exception(
                "api_key, kafka_admin_url, host, port, username, & password are required parameters for a EventStreams Service Binding: %s"
                % (json.dumps(kwargs, sort_keys=True))
            )

        ServiceBindingCredentials.__init__(self, **kwargs)

    @property
    def api_key(self):
        return self["api_key"]

    @property
    def kafka_admin_url(self):
        return self["kafka_admin_url"]

    @property
    def kafka_brokers_sasl(self):
        return self["kafka_brokers_sasl"]

    @property
    def user(self):
        return self["user"]

    @property
    def password(self):
        return self["password"]


class DB2ServiceBindingCredentials(ServiceBindingCredentials):
    def __init__(self, **kwargs):
        if not set(["username", "password", "db", "ssljdbcurl"]).issubset(kwargs):
            raise Exception(
                "username, password, db and ssljdbcurl are required parameters for a DB2 Service Binding: %s"
                % (json.dumps(kwargs, sort_keys=True))
            )

        ServiceBindingCredentials.__init__(self, **kwargs)

    @property
    def username(self):
        return self["username"]

    @property
    def password(self):
        return self["password"]

    @property
    def db(self):
        return self["db"]

    @property
    def ssljdbcurl(self):
        return self["ssljdbcurl"]


class PostgresServiceBindingCredentials(ServiceBindingCredentials):
    def __init__(self, **kwargs):
        if not set(["hostname", "port", "username", "password", "certificate", "database"]).issubset(kwargs):
            raise Exception(
                "hostname, port, username, password, certificate and database are required parameters for a PostgreSQL Service Binding: %s"
                % (json.dumps(kwargs, sort_keys=True))
            )

        self["connection"] = {
            "postgres": {
                "authentication": {"username": kwargs["username"], "password": kwargs["password"]},
                "certificate": {"certificate_base64": kwargs["certificate"]},
                "database": kwargs["database"],
                "hosts": [{"hostname": kwargs["hostname"], "port": kwargs["port"]}],
            }
        }

    @property
    def connection(self):
        return self["connection"]
