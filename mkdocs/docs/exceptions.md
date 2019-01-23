# Exceptions

Exception classes in the SDK are common across the three packages (application, device, gateway). Below is a summary of the custom exception classes that are used in this SDK.  All classes extend the base `Exception` class, in the majority of cases you should be able to develop code without needing to worry about these classes, however their presence allows for more sophisticated error handling in more complex programs.

## ConnectionException

`wiotp.sdk.ConnectionException` is a generic Connection exception.  More details about the exception are available in the `reason` property of the thrown exception.

Raised By:

- Applications: **Yes**
- Devices: **Yes**
- Gateways: **Yes**

## UnsupportedAuthenticationMethod

`wiotp.sdk.UnsupportedAuthenticationMethod` is a specific type of `wiotp.sdk.ConnectionException`, thrown when the authentication method specified is not supported.  More details about the exception are available in the `reason` property of the thrown exception.

Raised By:

- Applications: **Yes**
- Devices: **Yes**
- Gateways: **Yes**


## ConfigurationException

`wiotp.sdk.ConfigurationException` is thrown when the configuration passed into an application, device, or gateway client is missing required properties, or has one or more invalid values defined.  More details about the exception are available in the `reason` property of the thrown exception.

Raised By:

- Applications: **Yes**
- Devices: **Yes**
- Gateways: **Yes**

## InvalidEventException

`wiotp.sdk.InvalidEventException` is thrown when an `Event` object can not be constructed by a `MessageCodec`.  More details about the exception are available in the `reason` property of the thrown exception.

Raised By:

- Applications: **Yes**
- Devices: **Yes**
- Gateways: **Yes**

## MissingMessageDecoderException

`wiotp.sdk.MissingMessageDecoderException` is thrown when there is no message decoder defined for the message format being processed.  The specific format that cuased the problem can be found from the `format` property of the thrown exception.

Raised By:

- Applications: **Yes**
- Devices: **Yes**
- Gateways: **Yes**

## MissingMessageEncoderException

`wiotp.sdk.MissingMessageEncoderException` is thrown when there is no message encoder defined for the message format being processed.  The specific format that cuased the problem can be found from the `format` property of the thrown exception.

Raised By:

- Applications: **Yes**
- Devices: **Yes**
- Gateways: **Yes**

## ApiException

`wiotp.sdk.ApiException` is thrown when any API call unexpectedly fails. The thrown exception has a number of properties available to aid in debug:

- `response` Full details of the underlying API call that failed. This will be an instance of `requests.Response`.
- `body` The reponse body, if a reponse body was returned.  Otherwise `None`.
- `message` The specific error message (in English) returned by IBM Watson IoT Platform.  e.g. `CUDRS0007E: The request was not valid. Review the constraint violations provided.`
- `exception` The Exception code and properties for the error message, allowing clients to support error translation.
- `id` The exception ID of the error (if available), e.g. `CUDRS0007E`
- `violations` If the error is due to a malformed request, this will contain the list of reasons why the request was rejected.

Raised By:

- Applications: **Yes**
- Devices: **No**
- Gateways: **No**
