#Bluemix Zone Demo
Sample application demonstrating how to send events to the cloud from a device and process them in an application.  The application demonstrates one approach to delegating access to sensor data in the IOT Foundation to users of a backend application utilising an IOT Foundation API key. 

See the demo application running live: http://iot-demo.mybluemix.net/

You can also see the demo application running in the IBM Bluemix Internet of Things solutions page https://console.ng.bluemix.net/solutions/iot


---


##Introduction
The application has two main pieces of function.


### The WSGI Application
The main application is a Python WSGI server which primarily exists to provide delegated authentication to real time device events.  The application requires a user to register a unique username and PIN.  Once authorized using the correct combination of username and PIN the application renders a number of realtime visualizations representing the movement of the device associated with that user.


### The Simulated Device
The second part of the application is a page designed to be run on a users phone that uses JavaScript to simulate device code running on the phone.  The device code presents the same username & PIN to the backend application for authentication, on a successful authentication the backend application will provide the device with the necessary credentials required to connect securely to the IOT Foundation.


---


##Bluemix Deployment
The sample is specifically designed to be deployed into Bluemix.  The application requires a binding to both an instance of the IOTF & Cloudant services.

###Get the sample source code
```
$ git clone https://github.com/ibm-messaging/iot-python.git
$ cd iot-python/samples/bluemixZoneDemo
```

###Create a new application
```bash
$ cf push <app_name> --no-start
```

###Create the required services
```bash
$ cf create-service iotf-service iotf-service-bronze iotdemo-iotf
$ cf create-service cloudantNoSQLDB Shared iotdemo-cloudant
```

### Bind the services to your application
```bash
$ cf bind-service <app_name> iotdemo-iotf
$ cf bind-service <app_name> iotdemo-cloudant
```

###Start the application
```
cf push <app_name>
```
###Launch your application

Open http://&lt;app_name&gt;.mybluemix.net/ in a browser


---


##Configuration
The demo supports multiple themes.  The Demo running in Bluemix uses a highly customised theme specifically designed for the IOT Bluemix Zone, but there are a number of simpler themes included in the sample code that provide a cleaner starting point for building your own application based on this sample.

One way to do this is to use the cf **set-env** command:
```
cf set-env <app_name> theme simple
```

To change the theme simply set a value for the "theme" environment variable to one of these options:
 - **default** - The original theme, provides the traditional interface associated with a modern web application, with discrete registration and login options for the application user.
 - **simple** - A simplified theme, which combines registration and login into a single "Go" action.  This will login a user if the username matches an existing user (and the PIN is correct), or register a new user if the username is new to the system.  This is the model that the demo running in the Bluemix IOT zone utilises.
 - **bluemix** - A highly customised theme designed to seemlessly integrate into the Bluemix IOT Zone.


---


##Local development
The sample can also be run outside of Bluemix, primarily this is an aid for local development prior to pushing the code into Bluemix.
```python
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
```
