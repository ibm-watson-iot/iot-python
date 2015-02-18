<!DOCTYPE HTML>
<html lang="en">
<head>
	<link rel="stylesheet" href="/static/stylesheets/bluemix.css">
	<title>IBM Internet of Things</title>
	<meta charset="utf-8">
</head>
<body class="iotDemo">
	<section class="white-section section-base" id="name-entry-section">
		<div class="medium-large-font center-text">First...</div>
		<p class="medium-font center-text" id="first-steps">Give your smartphone a unique name and a 4-digit code.
We’ll generate a URL for you to open in your phone’s browser.</p>
		<div class="use-code-input-row" id="connectPanel">
			<form id="goForm">
				<input type="text" id="username3" placeholder="Enter device name" required>
				<input type="password" id="pin3" placeholder="4-digit code" inputmode="numeric" maxlength="4" required>
				<button id="name-entry-submit" class="section-button black-button" type="submit">Go play!</button>
			</form>
		</div>
		<div id="goWarning">&nbsp;</div>
	</section>
	<section class="white-section section-base" id="connectedPanel">
		<p class="medium-font center-text">Your custom URL:</p>
		<p class="medium-font center-text"><a id="myDeviceLink"></a></p>
		<div class="medium-large-font center-text" id="qrcode"></div>
		<img class="divider-line" src="/static/images/hr.png" />
		<div class="medium-large-font center-text">Watch the magic happen!</div>
		<p class="medium-font center-text">Enter your 4-digit code on your phone and then try moving your phone around.<br />
		See the model and graph below mirroring your movements?<br />
		This is made possible via MQTT messaging, the IoT Foundation, and this cool sample that's hosted on Bluemix! This is all done using secure connections.</p>
		<div id="vis-row" class="vis-row cf">
			<div id="cube"></div>
			<div id="visualisations">
				<ul id="vis-tabs">
					<li data-graph="magData">Vibration</li>
					<li data-graph="accelData">Motion</li>
					<li data-graph="gyroData">Orientation</li>
				</ul>
				<div id="magData" class="graphHolder"></div>
				<div id="accelData" class="graphHolder"></div>
				<div id="gyroData" class="graphHolder"></div>
			</div>
		</div>
	</section>



	<script type="text/javascript" src="/static/js/three.min.js"></script>
	<script type="text/javascript" src="/static/js/d3.v3.min.js"></script>
	<script type="text/javascript" src="/static/js/rAF.js"></script>
	<script type="text/javascript" src="/static/js/jquery.js"></script>
	<script type="text/javascript" src="/static/js/util.js"></script>
	<script type="text/javascript" src="/static/js/jquery.qrcode.min.js"></script>
	<script type="text/javascript" src="/static/js/cube.js"></script>
</body>
</html>
