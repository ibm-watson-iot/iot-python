import getopt
import time
import threading
import sys
import psutil
import platform
import json
import signal
import paho.mqtt.client as paho
from uuid import getnode as get_mac


class ClientThread(threading.Thread):

	def __init__(self, deviceId, deviceName, stopEvent, verbose=False):
		super(ClientThread, self).__init__()
		self.brokerAddress = "messaging.quickstart.internetofthings.ibmcloud.com"
		self.brokerPort = 1883
		self.keepAlive = 60
		self.deviceId = deviceId
		self.deviceName = deviceName
		self.verbose = verbose
		self.stopEvent = stopEvent
		
		self.messages = 0
		self.topic = 'iot-1/d/'+self.deviceId+'/evt/py-psutil-quickstart/json'

		self.client = paho.Client("quickstart:"+deviceId, clean_session=True)
		
		#attach MQTT callbacks
		if self.verbose:
			self.client.on_log = self.on_log
		self.client.on_connect = self.on_connect
		self.client.on_publish = self.on_publish
		self.client.on_disconnect = self.on_disconnect


	def run(self):
		self.client.connect(self.brokerAddress, port=self.brokerPort, keepalive=self.keepAlive)
		self.client.loop_start()
		
		if self.verbose:
			print "Publishing to " + self.topic

		start = time.time() * 1000
		
		# Take initial reading
		psutil.cpu_percent(percpu=False)
		
		while(not self.stopEvent.is_set()):
			ioBefore = psutil.net_io_counters()
			time.sleep(1)
			ioAfter = psutil.net_io_counters();
			
			data = { 
				'name' : self.deviceName,
				'cpu' : psutil.cpu_percent(percpu=False),
				'mem' : psutil.virtual_memory().percent,
				'network_up': "%.2f" % ((ioAfter.bytes_sent - ioBefore.bytes_sent)/float(1024)), 
				'network_down':  "%.2f" % ((ioAfter.bytes_recv - ioBefore.bytes_recv)/float(1024)) 
			}
			if self.verbose:
				print "Datapoint = " + json.dumps(data)
			
			payload = { 'd' : data }
			self.client.publish(self.topic, payload=json.dumps(payload), qos=0, retain=False)
				
		self.client.disconnect()
		self.client.loop_stop()
		
		elapsed = ((time.time() * 1000) - start)
		msgPerSecond = self.messages/(elapsed/1000)
		print "Messages published:"+ str(self.messages) + ", life:" + "%.0f" % (elapsed/1000) + "s, msg/s:" + "%.2f" % msgPerSecond
	
	
	def on_log(self, mqttc, obj, level, string):
		print string
	
	'''
	This is called after the client has received a CONNACK message from the broker in response to calling connect(). 
	The parameter rc is an integer giving the return code:
	0: Success
	1: Refused - unacceptable protocol version
	2: Refused - identifier rejected
	3: Refused - server unavailable
	4: Refused - bad user name or password (MQTT v3.1 broker only)
	5: Refused - not authorised (MQTT v3.1 broker only)
	'''
	def on_connect(self, mosq, obj, rc):
		if rc == 0:
			print "Connected successfully - Your device ID is %s" % self.deviceId
			print " * http://quickstart.internetofthings.ibmcloud.com/?deviceId=%s"  % (self.deviceId)
			print "Visit the QuickStart portal to see this device's data visualized in real time and learn more about the IBM Internet of Things Cloud"
			print ""
			print "(Press Ctrl+C to disconnect)"
		else:
			print "Connection failed: RC=" + str(rc)

	'''
	This is called when the client disconnects from the broker. The rc parameter indicates the status of the disconnection. 
	When 0 the disconnection was the result of disconnect() being called, when 1 the disconnection was unexpected.
	'''
	def on_disconnect(self, mosq, obj, rc):
		if rc == 1:
			print "Unexpected disconnect"
		
	'''
	This is called when a message from the client has been successfully sent to the broker. 
	The mid parameter gives the message id of the successfully published message.
	'''
	def on_publish(self, mosq, obj, mid):
		if self.verbose:
			print "Message " + str(mid) + " published"
		self.messages = self.messages + 1



def interruptHandler(signal, frame):
	print "Closing connection to the IBM Internet of Things Cloud service"
	deviceStopEvent.set()
	sys.exit(0)

def usage():
	print(
		"IOT-PSUTIL: Publish basic system utilization statistics to the IBM Internet of Things Cloud service." + "\n" +
		"\n" +
		"Datapoints sent:" + "\n" +
		"  name          The name of this device.  Defaults to hostname ('%s')" % platform.node() + "\n" +
		"  cpu           Current CPU utilization (%)" + "\n" +
		"  mem           Current memory utilization (%)" + "\n" +
		"  network_up    Current outbound network utilization across all network interfaces (KB/s)" + "\n" +
		"  network_down  Current inbound network utilization across all network interfaces (KB/s)" + "\n" + 
		"\n" + 
		"Options: " + "\n" +
		"  -h, --help       Display help information" + "\n" + 
		"  -n, --name       Override the default device name" + "\n" + 
		"  -v, --verbose    Be more verbose"
	)

if __name__ == "__main__":
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hn:v", ["help", "name=", "verbose"])
	except getopt.GetoptError as err:
		print str(err)
		usage()
		sys.exit(2)

	verbose = False
	deviceId = str(hex(int(get_mac())))[2:-1]
	deviceName = platform.node()
	
	for o, a in opts:
		if o in ("-v", "--verbose"):
			verbose = True
		elif o in ("-n", "--name"):
			deviceName = a
		elif o in ("-h", "--help"):
			usage()
			sys.exit()
		else:
			assert False, "unhandled option" + o

	signal.signal(signal.SIGINT, interruptHandler)
	deviceStopEvent = threading.Event()
	
	device = ClientThread(deviceId, deviceName, deviceStopEvent, verbose=verbose)
	device.start()
	
	while True:
		time.sleep(1)
