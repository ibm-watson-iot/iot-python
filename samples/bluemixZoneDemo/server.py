from bottle import request, Bottle, abort, static_file, template, HTTPError, HTTPResponse
import time
import ibmiotf.application
import cloudant
import json
import uuid
import urllib
import os
import bottle
from bottle import HTTPResponse

app = Bottle()


# If running in Bluemix, the VCAP environment variables will be available, and hence we can look up the bound Cloudant and IoT Foundation
# services that are required by this application.
if "VCAP_APPLICATION" in os.environ:
	application = json.loads(os.getenv('VCAP_APPLICATION'))
	service = json.loads(os.getenv('VCAP_SERVICES'))

	uri = application["application_uris"][0]
	
	# Check we have an IoT Foundation service bound
	if "iotf-service" not in service:
		print(" IoT Foundation service has not been bound!")
		raise Exception("IoT Foundation service has not been bound!")

	# Check we have a cloudantNoSQLDB service bound	
	if "cloudantNoSQLDB" not in service:
		print(" CloudantNoSQLDB service has not been bound!")
		raise Exception("cloudantNoSQLDB service has not been bound!")

	organization = service['iotf-service'][0]['credentials']['org']
	authKey = service['iotf-service'][0]['credentials']['apiKey']
	authToken = service['iotf-service'][0]['credentials']['apiToken']
	authMethod = "apikey"

	dbUsername = service['cloudantNoSQLDB'][0]['credentials']['username']
	dbPassword = service['cloudantNoSQLDB'][0]['credentials']['password']
else:
	# Not running in Bluemix, so you need to set up your own properties for local testing.
	# Ensure you blank these out before committing/uploading the code
	uri = "localhost"

	organization = ""
	authKey = ""
	authToken = ""
	authMethod = "apikey"
	dbUsername = ""
	dbPassword = ""

dbName = "iotfzonesample"
port = int(os.getenv('VCAP_APP_PORT', 80))
host = str(os.getenv('VCAP_APP_HOST', "0.0.0.0"))

# =============================================================================
# Choose application theme
# =============================================================================
theme = os.getenv('theme', "bluemix")
print("Using theme '%s'" % theme)

# =============================================================================
# Configure global properties
# =============================================================================
cloudantAccount = cloudant.Account(dbUsername, async=True)
future = cloudantAccount.login(dbUsername, dbPassword)
login = future.result(10)
assert login.status_code == 200

cloudantDb = cloudantAccount.database(dbName)
# Allow up to 10 seconds
response = cloudantDb.get().result(10)
if response.status_code == 200:
	print(" * Database '%s' already exists (200)" % (dbName))
elif response.status_code == 404:
	print(" * Database '%s' does not exist (404), creating..." % (dbName))
	response = cloudantDb.put().result(10)
	if response.status_code != 201:
		print(" * Error creating database '%s' (%s)" % (dbName, response.status_code))
else:
	print(" * Unexpected status code (%s) when checking for existence of database '%s'" % (status, dbName))
	raise Exception("Unexpected status code (%s) when checking for existence of database '%s'" % (status, dbName))

# =============================================================================
# Define application routes
# =============================================================================
@app.route('/register', method='POST')
def register():
	if request.json is None:
		return bottle.HTTPResponse(status=400, body="Invalid request");
	
	data = request.json
	if "email" not in data:
		return bottle.HTTPResponse(status=400, body="Credentials not provided");
	if "pin" not in data:
		return bottle.HTTPResponse(status=400, body="4-digit code not provided");
	if ' ' in data["email"]:
		return bottle.HTTPResponse(status=400, body="Spaces are not allowed");
	
	doc = cloudantDb.document(urllib.quote(data["email"]))
	response = doc.get().result(10)
	if response.status_code == 200:
		print("User already registered: %s" % data["email"])
		return bottle.HTTPResponse(status=409, body="User already registered");

	else:
		print("Creating new registration for %s" % data["email"])
		# Create doc
		options = {"org": organization, "id": str(uuid.uuid4()), "auth-method": authMethod, "auth-key": authKey, "auth-token": authToken}
		registrationClient = ibmiotf.application.Client(options)
		device = registrationClient.api.registerDevice("zone-sample", uuid.uuid4().hex, {"registeredTo": data["email"]} )
		response = doc.put(params={
			'id': data["email"],
			'pin': data["pin"],
			'device': {
				'type': device['type'], 
				'id': device['id'], 
				'authtoken': device['password'],
				'clientid': device['uuid'],
				'orgid': organization
			}
		}).result(10)
		if response.status_code == 201:
			return HTTPResponse(status=201)
			
	# Shouldn't get here, if we do an error has occurred
	return bottle.HTTPResponse(status=500, body="Apologies - an internal error occurred :(");


@app.route('/auth', method='POST')
def auth():
	if request.json is None:
		print "Invalid request to auth"
		raise HTTPError(400)
	
	data = request.json
	errors = []
	if "email" not in data:
		errors.append("email address not provided")
	if "pin" not in data:
		errors.append("pin not provided")
	if len(errors) > 0:
		print "Invalid request to auth"
		raise HTTPError(400, errors)
	
	doc = cloudantDb.document(urllib.quote(data["email"]))
	response = doc.get().result(10)
	if response.status_code != 200:
		print("User not registered: %s" % data["email"])
		return bottle.HTTPResponse(status=404, body="'"+data["email"]+"' does not exist");
		
	else:
		docBody = response.json()
		try:
			if int(docBody["pin"]) != int(data["pin"]):
				print("PIN does not match")
				return bottle.HTTPResponse(status=403, body="Incorrect code for '"+data["email"]+"'");
			else:
				return docBody['device']
		except ValueError:
			print("PIN has an unexpected value: "+data["pin"])
			return bottle.HTTPResponse(status=403, body="Incorrect code for '"+data["email"]+"'");

@app.route('/device/<id>')
def device(id):
	return template('device', deviceId=id, uri=uri)


@app.route('/')
def applicationUi():
	return template('app-' + theme, uri=uri)

	
@app.route('/websocket')
def handle_websocket():
	def myEventCallback(event):
		if wsock:
			wsock.send(json.dumps(event.data))

	wsock = request.environ.get('wsgi.websocket')
	if not wsock:
		abort(400, 'Expected WebSocket request.')

	try:
		message = wsock.receive()
		data = json.loads(message)
		pin = int(data["pin"])
	
		doc = cloudantDb.document(urllib.quote(data["email"]))
		response = doc.get().result(10)
		if response.status_code != 200:
			print("User not registered: %s" % data["email"])
			wsock.close()
		else:
			document = response.json()
			print document
			
			if str(pin) != str(document["pin"]):
				print "PIN does not match"
				wsock.close()
			else:
				deviceId = str(document['device']["id"])
				deviceType = str(document['device']["type"])
				options = {"org": organization, "id": str(uuid.uuid4()), "auth-method": authMethod, "auth-key": authKey, "auth-token": authToken}
				try :
					client = ibmiotf.application.Client(options)
					# In this sample, we don't want logs from the client.
					if (len(client.logger.handlers) > 0):
  						handler = client.logger.handlers[0]
  						#client.logger.removeHandler(handler)
  						#handler.close() 
					client.connect()
					client.deviceEventCallback = myEventCallback
					client.subscribeToDeviceEvents(deviceType, deviceId, "+")
				except ibmiotf.ConnectionException as e: 
					# We've been unable to do the initial connect. In this case, we'll terminate the socket to trigger the client to try again.
					print ("Connect attempt failed: "+str(e))
					wsock.close()
	except WebSocketError as e:
		print "WebSocket Error: %s" % str(e)	
	#Send the message back
	while True:
		try:
			message = wsock.receive()
			time.sleep(1)
			#wsock.send("Your message was: %r" % message)
		except WebSocketError:
			# This can occur if the browser has navigated away from the page, so the best action to take is to stop.
			break	
	# Always ensure we disconnect. Since we are using QoS0 and cleanSession=true, we don't need to worry about cleaning up old subscriptions as we go: the IoT Foundation
	# will handle this automatically.
	client.disconnect()
	


@app.route('/static/<path:path>')
def service_static(path):
	return static_file(path, root='static')


# =============================================================================
# Start
# =============================================================================
from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketError
from geventwebsocket.handler import WebSocketHandler


server = WSGIServer((host, port), app, handler_class=WebSocketHandler)
print(" * Starting web socket server")
server.serve_forever()
