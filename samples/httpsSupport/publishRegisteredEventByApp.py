import ibmiotf.application
import sys

try:
	appOptions = {"org": "uguhsp", "id": "a:uguhsp:myapp88", "auth-key": "a-uguhsp-ywwgvqzatf", "auth-token": "MASKED PASSWORD"}
	appCli = ibmiotf.application.Client(appOptions)

except Exception as e:
	print("Caught exception", e)
	sys.exit()

myData = { 'hello' : 'world', 'x' : 23}
	
try:
	success = appCli.publishEventOverHTTP("iotsample-arduino", "00aabbccde03", "greeting", myData)
	print ("Post Operation HTTP response = ", success)

except Exception as e:
	print(e)
	sys.exit()
	
