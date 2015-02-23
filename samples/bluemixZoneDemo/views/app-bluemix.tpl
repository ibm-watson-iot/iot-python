<!DOCTYPE HTML>
<html lang="en">
<head>
		<link href="/static/stylesheets/bootstrap.min.css" rel="stylesheet" media="screen">
		<link href="/static/stylesheets/bluemix.css" rel="stylesheet" media="screen">
		<title>IBM Internet of Things</title>
		<meta charset="utf-8">
</head>
<body class="iotDemo">
	<!-- divs to help us track resizing -->
	<div class="device-xs visible-xs"></div>
	<div class="device-sm visible-sm"></div>
	<div class="device-md visible-md"></div>
	<div class="device-lg visible-lg"></div>
	<!-- Welcome Banner & Connect Panel -->
	<div class="white-section" id="name-entry-section">
		<div class="medium-large-font center-text">First...</div>
		<p class="medium-font center-text" id="first-steps">Give your smartphone a unique name and a 4-digit code.  We’ll generate a URL for you to open in your phone’s browser.</p>
		<div class="use-code-input-row center-text" id="connectPanel">
			<form id="goForm">
				<input type="text" id="username3" placeholder="DEVICE NAME" required>
				<input type="password" id="pin3" placeholder="4-DIGIT CODE" inputmode="numeric" maxlength="4" required>
				<button class="section-button black-button" type="submit">Go play!</button>
			</form>
		</div>
		<div class="alert" id="goWarning"><span>&nbsp;</span></div>
	</div>


	
	<div id="connectedPanel">
		<div class="white-section">
			<p class="medium-font center-text">Your custom URL:</p>
			<p class="medium-font center-text"><a id="myDeviceLink"></a></p>
			<div class="medium-large-font center-text" id="qrcode"></div>
			<div class="medium-large-font center-text">
				<img class="divider-line" src="/static/images/hr.png" />
			</div>
			<p class="medium-large-font center-text">Watch the magic happen!</p>
			<p class="medium-font center-text">Enter your 4-digit code on your phone and then try moving your phone around.<br />
			<p class="medium-font center-text">See the model and graph below mirroring your movements?</p>
			<p class="medium-font center-text">This is made possible via MQTT messaging, the IoT Foundation, and this cool sample that's hosted on Bluemix!</p>
		</div>
		<div class="alert" id="vibrationWarning"><span>Wow! We've detected some serious shaking!</span></div>
		<div class="container" id="visualisations">
    		<div class="row">
      			<div class="col-md-6 col-sm-12 col-lg-3 center-text">
					<p class="medium-font-bold style="font-weight:bold">Your device</p>
					<div id="cube"></div>
				</div>
				<div class="col-md-6 col-sm-12 col-lg-3 center-text">
					<p class="medium-font-bold style="font-weight:bold">Vibration</p>
					<div id="magData" class="graphHolder"></div>
				</div>
				<div class="col-md-6 col-sm-12 col-lg-3 center-text">
					<p class="medium-font-bold style="font-weight:bold">Motion</p>
					<div id="accelData" class="graphHolder"></div>
				</div>
				<div class="col-md-6 col-sm-12 col-lg-3 center-text">
					<p class="medium-font-bold style="font-weight:bold">Orientation</p>
					<div id="gyroData" class="graphHolder"></div>
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
