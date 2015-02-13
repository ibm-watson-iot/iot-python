from bottle import request, Bottle, abort, static_file, template, HTTPError, HTTPResponse
import time
import ibmiotf.application
import cloudant
import json
import uuid
import urllib
import os

app = Bottle()

if "VCAP_APPLICATION" in os.environ:
	# Bluemix VCAP lookups
	application = json.loads(os.getenv('VCAP_APPLICATION'))
	service = json.loads(os.getenv('VCAP_SERVICES'))

	uri = application["application_uris"][0]

	organization = service['iotf-service'][0]['credentials']['org']
	authKey = service['iotf-service'][0]['credentials']['apiKey']
	authToken = service['iotf-service'][0]['credentials']['apiToken']
	authMethod = "apikey"

	dbUsername = service['cloudantNoSQLDB'][0]['credentials']['username']
	dbPassword = service['cloudantNoSQLDB'][0]['credentials']['password']
else:
	# Set up properties for local testing
	# Note: ensure you blank these out before commiting/uploading the code
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
		raise HTTPError(400)
	
	data = request.json
	errors = []
	if "email" not in data:
		errors.append("email address not provided")
	if "pin" not in data:
		errors.append("pin  not provided")
	if len(errors) > 0:
		raise HTTPError(400, errors)
	
	doc = cloudantDb.document(urllib.quote(data["email"]))
	response = doc.get().result(10)
	if response.status_code == 200:
		print("User already registered: %s" % data["email"])
		raise HTTPError(409)

	else:
		print("Creating new registration for %s" % data["email"])
		# Create doc
		options = {"org": organization, "id": str(uuid.uuid4()), "auth-method": authMethod, "auth-key": authKey, "auth-token": authToken}
		client = ibmiotf.application.Client(options)
		device = client.api.registerDevice("zone-sample", uuid.uuid4().hex, {"registeredTo": data["email"]} )
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
			
	# Shouldn't get here, if we do an error has occured
	raise HTTPError(500)


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
		errors.append("pin  not provided")
	if len(errors) > 0:
		print "Invalid request to auth"
		raise HTTPError(400, errors)
	
	doc = cloudantDb.document(urllib.quote(data["email"]))
	response = doc.get().result(10)
	if response.status_code != 200:
		print("User not registered: %s" % data["email"])
		raise HTTPError(401)
		
	else:
		docBody = response.json()
		if int(docBody["pin"]) != int(data["pin"]):
			print("PIN does not match")
			raise HTTPError(401)
		else:
			return docBody['device']


@app.route('/device/<id>')
def device(id):
	return template('device', deviceId=id, uri=uri)


@app.route('/')
def applicationUi():
	return template('app', uri=uri)

	
@app.route('/websocket')
def handle_websocket():
	def myEventCallback(event):
		if wsock:
			wsock.send(json.dumps(event.data))

	wsock = request.environ.get('wsgi.websocket')
	print wsock
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
				print(deviceType)
				print(deviceId)
			
				options = {"org": organization, "id": str(uuid.uuid4()), "auth-method": authMethod, "auth-key": authKey, "auth-token": authToken}

				client = ibmiotf.application.Client(options)
				client.connect()
				client.deviceEventCallback = myEventCallback
				client.subscribeToDeviceEvents(deviceType, deviceId, "+")
		
	except WebSocketError as e:
		print "WebSocket Error: %s" % str(e)
	
	#Send the message back
	while True:
		try:
			message = wsock.receive()
			time.sleep(1)
			#wsock.send("Your message was: %r" % message)
		except WebSocketError:
			break
	
	print "Socket closed"
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
server.serve_forever()
