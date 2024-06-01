# MQTT Primer

MQTT is the primary protocol that devices and applications use to communicate with IBM Watson IoT Platform. MQTT is a publish and subscribe messaging transport protocol that is designed for the efficient exchange of real-time data between sensor and mobile devices.  MQTT support is available over TCP/IP and websockets, in your configuration file specify `options.mqtt.transport=tcp` or `options.mqtt.transport=websockets`


## Retained Messages
Watson IoT Platform provides limited support for the retained messages feature of MQTT messaging. If the retained message flag is set to true in an MQTT message that is sent from a device, gateway, or application to Watson IoT Platform, the message is handled as an unretained message.


## Quality of Service
The MQTT protocol provides three qualities of service for delivering messages between clients and servers: "at most once", "at least once", and "exactly once". While you can send events and commands by using any quality of service level, you must carefully consider what the right service level is for your needs. Quality of service level '2' is not always a better option than level '0'.

### At most once (QoS0)
The "at most once" quality of service level (QoS0) is the fastest mode of transfer and is sometimes called "fire and forget". The message is delivered at most once, or it might not be delivered at all. Delivery across the network is not acknowledged, and the message is not stored. The message might be lost if the client is disconnected, or if the server fails.

The MQTT protocol does not require servers to forward publications at quality of service level '0' to a client. If the client is disconnected at the time the server receives the publication, the publication might be discarded, depending on the server implementation.

!!! tip
    When sending real-time data on an interval, use quality of service level 0. If a single message goes missing, it does not really matter because another message that contains newer data will be sent shortly afterward. 
    
    In this scenario, the extra cost of using a higher quality of service does not result in any tangible benefit.

### At least once (QoS1)
With quality of service level 1 (QoS1), the message is always delivered at least once. If a failure occurs before an acknowledgment is received by the sender, a message can be delivered multiple times. The message must be stored locally at the sender until the sender receives confirmation that the message was published by the receiver. The message is stored in case the message must be sent again.

### Exactly once (QoS2)
The "exactly once" quality of service level 2 (QoS2) is the safest, but slowest mode of transfer. The message is always delivered exactly once and must also be stored locally at the sender, until the sender receives confirmation that the message was published by the receiver. The message is stored in case the message must be sent again. With quality of service level 2, a more sophisticated handshaking and acknowledgment sequence is used than for level 1 to ensure that messages are not duplicated.

!!! tip
    When sending commands, if you want confirmation that only the specified command will be actioned, and that it will be actioned once only, use the quality of service level 2. 
    
    This is an example of when the additional overheads of level 2 can be advantageous over other levels.


## Subscription Buffers and Clean Session
Each subscription from either a device or application is allocated a buffer of 5000 messages. The buffer allows for any application or device to fall behind the live data it is processing, and to also build up a backlog of up to 5000 pending messages for each subscription it has made. When the buffer is full, the oldest messages are discarded when a new message is received.

Use the MQTT clean session option to access the subscription buffer. When clean session is set to false, the subscriber receives messages from the buffer. When clean session is set to true, the buffer is reset.

!!! warning
    The subscription buffer limit applies regardless of the quality of service setting that is used. It is possible that a message that is sent at level 1 or 2 might not be delivered to an application that is unable to keep up with the messages rate for the subscription that it has made.


## Message Payload Limitations
IBM Watson IoT Platform supports sending and receiving messages in any format. MQTT is data-agnostic so it's possible to send images, text in any encoding, encrypted data, or raw data in binary format.

The maximum payload size on Watson IoT Platform is **131072** bytes. 

!!! warning    
    Messages with a payload that is greater than the limit are rejected. The connecting client is also disconnected, and a message appears in the diagnostic logs, as outlined in the following device message example:  `Closed connection from x.x.x.x. The message size is too large for this endpoint.`


## MQTT Keep Alive
The MQTT keep alive interval, which is measured in seconds, defines the maximum time that can pass without communication between the client and broker. 

The MQTT client must ensure that, in the absence of any other communication with the broker, a `PINGREQ` packet is sent. The keep alive interval allows both the client and the broker to detect that the network failed, resulting in a broken connection, without needing to wait for the TCP/IP timeout period to be reached.

!!! warning
    If your application utilizes a shared subscription, the keep alive interval value can be set only to between 1 and 3600 seconds. 
    
    If a value of 0 or a value that is greater than 3600 is requested, Watson IoT Platform sets the keep alive interval to 3600 seconds.