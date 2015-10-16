import ibmiotf.application
import sys

try:
	appOptions = {"org": "quickstart", "id": "a:quickstart:myapp02", "auth-key": None, "auth-token": None}
	appCli = ibmiotf.application.Client(appOptions)

except Exception as e:
	print("Caught exception", e)
	sys.exit()

myData = { 'hello' : 'world', 'x' : 23}
	
try:
	success = appCli.publishEventOverHTTP("iotsample-arduino", "00aabbccde02", "greeting", myData)
	print ("Post Operation HTTP response = ", success)

except Exception as e:
	print(e)
	sys.exit()
	
