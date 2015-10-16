import ibmiotf.device
import sys

try:
	deviceOptions = {"org": "uguhsp", "type": "iotsample-arduino", "id": "00aabbccde03", "auth-method": "token", "auth-token": "MASKED PASSWORD"}

	deviceCli = ibmiotf.device.Client(deviceOptions)

except Exception as e:
	print("Caught exception")
	sys.exit()

myData = { 'hello' : 'world', 'x' : 23}
try:
	success = deviceCli.publishEventOverHTTP("greeting", myData)
	print ("Post Operation HTTP response = ", success)

except Exception as e:
	print(e)
	sys.exit()
	
