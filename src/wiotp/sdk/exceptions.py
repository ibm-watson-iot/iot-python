# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************


class ConnectionException(Exception):
    """
    Generic Connection exception
    
    # Attributes
    reason (string): The reason why the connection exception occured
    """

    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return self.reason


class ConfigurationException(Exception):
    """
    Specific Connection exception where the configuration is invalid
    
    # Attributes
    reason (string): The reason why the configuration is invalid
    """

    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return self.reason


class UnsupportedAuthenticationMethod(ConnectionException):
    """
    Specific Connection exception where the authentication method specified is not supported
    
    # Attributes
    method (string): The authentication method that is unsupported
    """

    def __init__(self, method):
        self.method = method

    def __str__(self):
        return "Unsupported authentication method: %s" % self.method


class InvalidEventException(Exception):
    """
    Specific exception where an Event object can not be constructed
    
    # Attributes
    reason (string): The reason why the event could not be constructed
    """

    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return "Invalid Event: %s" % self.reason


class MissingMessageDecoderException(Exception):
    """
    Specific exception where there is no message decoder defined for the message format being processed
    
    # Attributes
    format (string): The message format for which no encoder could be found
    """

    def __init__(self, format):
        self.format = format

    def __str__(self):
        return "No message decoder defined for message format: %s" % self.format


class MissingMessageEncoderException(Exception):
    """
    Specific exception where there is no message encoder defined for the message format being processed
    
    # Attributes
    format (string): The message format for which no encoder could be found
    """

    def __init__(self, format):
        self.format = format

    def __str__(self):
        return "No message encoder defined for message format: %s" % self.format


class ApiException(Exception):
    """
    Exception raised when any API call fails unexpectedly
    
    # Attributes
    response (requests.Response): See: http://docs.python-requests.org/en/master/api/#requests.Response
    """

    def __init__(self, response):
        self.response = response

        # {
        #   "violations":[
        #     {
        #       "message":"CUDRS0012E: The severity field has a value that is too high. Specify a value equal to or less than 2.",
        #       "exception":{"id":"CUDRS0012E","properties":["severity","2"]}
        #     }
        #   ],
        #   "message":"CUDRS0007E: The request was not valid. Review the constraint violations provided.",
        #   "exception":{"id":"CUDRS0007E","properties":[]}
        # }

        try:
            self.body = self.response.json()
            self.message = self.body.get("message", None)
            self.exception = self.body.get("exception", None)
        except ValueError:
            self.body = None
            self.message = None
            self.exception = None

    @property
    def id(self):
        if self.exception is not None:
            return self.exception.get("id", None)

    @property
    def violations(self):
        violations = self.body.get("violations", None)
        if violations is None:
            return None
        else:
            returnArray = []
            for violation in violations:
                returnArray.append(violation.get("message", None))
            return returnArray

    def __str__(self):
        if self.message:
            return self.message
        else:
            return "Unexpected return code from API: %s (%s) - %s\n%s" % (
                self.response.status_code,
                self.response.reason,
                self.response.url,
                self.response.text,
            )

    def __repr__(self):
        return self.response.__repr__()
