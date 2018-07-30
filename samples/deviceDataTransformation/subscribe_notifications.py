from __future__ import print_function
import time, ibmiotf.api, paho.mqtt.client as mqtt, json, random
import sys, importlib, logging, ssl

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))
  # Subscribing in on_connect() means that if we lose the connection and
  # reconnect then subscriptions will be renewed.
  for topic in topics:
    client.subscribe(topic)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
  print(msg.topic+" "+str(msg.payload))
  return True


if __name__ == "__main__":
  if len(sys.argv) < 2:
      print("Property file name needed")
      sys.exit()

  property_file_name = sys.argv[1]

  logger.info("Getting properties from %s" % property_file_name)
  properties = importlib.import_module(property_file_name)
  property_names = dir(properties)

  verify = None
  params = {"auth-key": properties.key, "auth-token": properties.token}
  if "domain" in property_names:
    params["domain"] = properties.domain

  if "verify" in property_names:
    verify = properties.verify

  if "host" in property_names:
    params["host"] = properties.host

  clientid = "a:%s:subscribe_notifications" % properties.orgid
  port = 8883
  if "host" in property_names:
    hostname = properties.host.split(":")[0]
  else:
    hostname = "%s.messaging.internetofthings.ibmcloud.com" % properties.orgid
  username = properties.key
  password = properties.token

  client = mqtt.Client(client_id=clientid, clean_session=True)
  client.username_pw_set(username, password)
  client.on_connect = on_connect
  client.on_message = on_message
  client.enable_logger()
  caFile = "messaging3.pem"
  client.tls_set(ca_certs=caFile, certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)

  global topics
  topics = ["iot-2/type/%s/id/%s/intf/%s/evt/state" % (properties.devicetype, properties.deviceid, "+"),
            "iot-2/type/%s/id/%s/err/data" % (properties.devicetype, properties.deviceid)]
  client.connect(hostname, port=port, keepalive=60)

  # Blocking call that processes network traffic, dispatches callbacks and
  # handles reconnecting.
  # Other loop*() functions are available that give a threaded interface and a
  # manual interface.
  client.loop_forever()

  client.disconnect()
