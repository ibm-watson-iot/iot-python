<!DOCTYPE HTML>
<html lang="en">
<head>
		<link href="/static/stylesheets/bootstrap.min.css" rel="stylesheet" media="screen">
		<link href="/static/stylesheets/style.css" rel="stylesheet" media="screen">
		<title>IBM Internet of Things</title>
		<meta charset="utf-8">
</head>
<body>
	<div class="row">
		<div class="container">
			<div class="panel panel-default">
				<div class="panel-heading">
					<h3 class="panel-title">Welcome to the IoT Foundation Demo Application</h3>
				</div>
				<div class="panel-body" >
					<div id="connectPanel">
						<div class="panel panel-default">
							<div class="panel-body">
								<p>Enter a unique <b>username</b> and <b>PIN</b> and click Go.</p>
								<form id="goForm" class="form-inline">
									<div class="form-group">
										<label class="sr-only" for="username3">Username</label>
										<input type="text" class="form-control" id="username3" placeholder="Enter username" />
									</div>
									<div class="form-group">
										<label class="sr-only" for="pin3">PIN</label>
										<input type="password" class="form-control" id="pin3" placeholder="Enter PIN" />
									</div>
									<button type="submit" class="btn btn-primary">Go</button>
								</form>
								<p>Andouille bresaola pork ham hock kevin hamburger pig swine frankfurter pancetta sirloin. Tenderloin prosciutto pork loin frankfurter venison capicola spare ribs meatball ham hock cow brisket jowl kielbasa fatback. Cow ball tip meatball, doner pig salami landjaeger brisket shankle pastrami chuck turkey swine picanha. Ham shank bresaola shankle shoulder ribeye pancetta alcatra tenderloin frankfurter, hamburger jowl flank prosciutto. Frankfurter pastrami shoulder swine pork loin spare ribs.</p>

								<div class="alert alert-danger" role="alert" id="goWarning">&nbsp;</div>
							</div>
						</div>
					</div>
					<div id="connectedPanel">
						<p>Hi, <span id="myUsername">My Username</span>!</p>
						<p>Open the following page in your phone's browser and enter your PIN to turn your phone into your personal IOT connected device: <a id="myDeviceLink" href="#">My Device</a></p>
						<div class="medium-large-font center-text" id="qrcode"></div>
						<div>
							<button id="signoutButton" type="button" class="btn btn-default">Switch User</button>
						</div>
						<div class="alert alert-danger" role="alert" id="vibrationWarning">Wow! We've detected some serious shaking!</div>
						<br />
						<ul class="nav nav-pills">
						  <li class="active"><a href="#tab_a" data-toggle="tab">Visualization</a></li>
						  <li><a href="#tab_b" data-toggle="tab">Vibration</a></li>
						  <li><a href="#tab_c" data-toggle="tab">Motion</a></li>
						  <li><a href="#tab_d" data-toggle="tab">Orientation</a></li>
						  <li><a href="#tab_e" data-toggle="tab">How it Works</a></li>
						</ul>				
						<div class="tab-content">
							<div class="tab-pane active" id="tab_a">
								<div class="panel panel-default">
									<div class="panel-body">
										<h4>Visualization</h4>
										<p>Corned beef pork loin flank fatback meatloaf, short loin turducken ham strip steak. Tenderloin chuck tri-tip meatloaf capicola filet mignon drumstick andouille ball tip picanha sirloin bresaola doner flank pork. Drumstick ribeye flank tongue shankle kevin. Sausage filet mignon shoulder andouille beef ribs strip steak. Tail tenderloin tongue, fatback swine shankle corned beef spare ribs pork loin chuck ham hock sausage cupim. Pig pancetta ground round shank alcatra strip steak rump short ribs shankle ham hock pork belly kevin porchetta spare ribs pork chop. Cow short loin ball tip bresaola, pancetta beef drumstick.</p>
										<div id="cube"></div>
									</div>
								</div>
							</div>
							<div class="tab-pane" id="tab_b">
								<div class="panel panel-default">
									<div class="panel-body">
										<h4>Vibration</h4>
										<p>Short loin meatball shankle, filet mignon chicken drumstick tenderloin salami landjaeger ground round doner. Chicken pig frankfurter, jowl kielbasa leberkas pork chop t-bone. Sirloin chicken cow, picanha salami landjaeger capicola jowl swine tenderloin andouille. Jowl salami sirloin t-bone shankle. Short ribs ball tip shank leberkas, biltong tail turducken chicken alcatra andouille ham strip steak meatloaf. Pastrami leberkas bresaola turkey rump pork belly cupim ham hock meatloaf pork chop.</p>
										<div id="magData" class="graphHolder"></div>
									</div>
								</div>
							</div>
							<div class="tab-pane" id="tab_c">
								<div class="panel panel-default">
									<div class="panel-body">
										<h4>Motion</h4>
										<p>Pancetta sausage fatback shoulder chicken turducken biltong. Porchetta shankle drumstick, andouille chicken ham cow ham hock short loin. Leberkas short loin alcatra, flank turducken hamburger t-bone shoulder beef pork chop tongue turkey. Jerky sausage turkey corned beef, t-bone pork belly short loin picanha tri-tip hamburger meatloaf pork loin spare ribs ribeye cupim. Pork ham hock meatball turkey kielbasa.</p>
										<div id="accelData" class="graphHolder"></div>
									</div>
								</div>
							</div>
							<div class="tab-pane" id="tab_d">
								<div class="panel panel-default">
									<div class="panel-body">
										<h4>Orientation</h4>
										<p>Tongue short loin chicken brisket rump capicola pork loin ground round swine alcatra pig pastrami kevin hamburger. Jerky sausage turducken chuck. Pork chop leberkas ham cupim biltong bresaola. Filet mignon spare ribs beef ground round turducken doner.</p>
										<div id="gyroData" class="graphHolder"></div>
									</div>
								</div>
							</div>
							<div class="tab-pane" id="tab_e">
								<div class="panel panel-default">
									<div class="panel-body">
										<h4>How it works</h4>
										<p>Your phone is running JavaScript code that turns it into a connected <b>device</b> publishing sensor data directly to the Internet of Things Foundation (IOTF) via MQTT.  This website is a 
										connected <b>application</b> built in the <a href="http://wsgi.readthedocs.org/en/latest/" target="_new">WSGI framework</a> that utilises the <a href="https://github.com/ibm-messaging/iot-python" target="_new">IOTF Python client library</a> to subscribe to, and visualize, the sensor data being published by your phone in real time.</p>
										<p>The application demonstrates one approach to controlling access to sensor data from specific devices to users of an application.  When you clicked "Register" the application created a user record
										in a <a href="https://cloudant.com/" target="_new">Cloudant</a> database, invoked the IOTF <a href="http://docs.internetofthings.ibmcloud.com/en/latest/api/device_management.html" target="_new">Device Management API</a> to register a device.  When you entered your PIN on your phone an API call was made to this application to verify that the PIN you 
										entered matched the one held on record, before returning the credentials your phone required to uniquely identify itself as a specific device.</p>
										<p>You can view the entire source code for this application and the device code running on your phone in <a href="https://github.com/ibm-messaging/iot-python/tree/master/samples/bluemixZoneDemo" target="_new">GitHub</a></p>
										<p>Want to deploy your own copy of this application in Bluemix?</p>
										<ol>
											<li>Create a new application in Bluemix</li>
											<li>Bind an instance of the Cloudant service to your application</li>
											<li>Bind an instance of the Internet of Things Foundation service to your application</li>
											<li>git clone https://github.com/ibm-messaging/iot-python.git</li>
											<li>cd iot-python/samples/bluemixZoneDemo</li>
											<li>cf push <b>application-name</b> -m 32M -b https://github.com/cloudfoundry/cf-buildpack-python.git -c "python server.py"</li>
											<li>Open http://<b>application-name</b>.mybluemix.net/ in a browser</li>
										</ol>
									</div>
								</div>
							</div>
						</div><!-- tab content -->
					</div>
				</div>
			</div>
		</div>
	</div>
	
	<script type="text/javascript" src="/static/js/three.min.js"></script>
	<script type="text/javascript" src="/static/js/d3.v3.min.js"></script>
	<script type="text/javascript" src="/static/js/rAF.js"></script>
	<script type="text/javascript" src="/static/js/jquery.js"></script>
	<script type="text/javascript" src="/static/js/bootstrap.min.js"></script>
	<script type="text/javascript" src="/static/js/util.js"></script>
	<script type="text/javascript" src="/static/js/jquery.qrcode.min.js"></script>
	<script type="text/javascript" src="/static/js/cube.js"></script>
</body>
</html>
