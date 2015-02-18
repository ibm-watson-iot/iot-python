<!DOCTYPE HTML>
<html lang="en">
<head>
		<link href="/static/stylesheets/bootstrap.min.css" rel="stylesheet" media="screen">
		<link href="/static/stylesheets/bluemix.css" rel="stylesheet" media="screen">
		<title>IBM Internet of Things</title>
		<meta charset="utf-8">
</head>
<body class="iotDemo">
	<!-- Welcome Banner & Connect Panel -->
	<div class="white-section" id="name-entry-section">
		<div class="medium-large-font center-text">First...</div>
		<p class="medium-font center-text" id="first-steps">Give your smartphone a unique name and a 4-digit code.  We’ll generate a URL for you to open in your phone’s browser.</p>
		<div class="use-code-input-row center-text" id="connectPanel">
			<form id="goForm">
				<input type="text" id="username3" placeholder="Enter device name" required>
				<input type="password" id="pin3" placeholder="4-digit code" inputmode="numeric" maxlength="4" required>
				<button class="section-button black-button" type="submit">Go play!</button>
			</form>
		</div>
		<div id="goWarning">&nbsp;</div>
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
			<p class="medium-font center-text">This is made possible via MQTT messaging, the IoT Foundation, and this cool sample that's hosted on Bluemix! This is all done using secure connections.</p>
			<div class="alert alert-danger" role="alert" id="vibrationWarning">Excessive device vibration detected!</div>
		</div>
		<div class="row" id="visualisations">
			<ul class="nav nav-pills nav-justified">
			  <li class="active"><a href="#tab_a" data-toggle="tab">3D Model</a></li>
			  <li><a href="#tab_b" data-toggle="tab">Vibration</a></li>
			  <li><a href="#tab_c" data-toggle="tab">Motion</a></li>
			  <li><a href="#tab_d" data-toggle="tab">Orientation</a></li>
			</ul>				
			<div class="tab-content">
				<div class="tab-pane active" id="tab_a">
					<div class="panel panel-default">
						<div class="panel-body center-text">
							<p>Hello</p>
							<div id="cube"></div>
						</div>
					</div>
				</div>

				<div class="tab-pane" id="tab_b">
					<div class="panel panel-default">
						<div class="panel-body center-text">
							<div id="magData" class="graphHolder"></div>
						</div>
					</div>
				</div>
				<div class="tab-pane" id="tab_c">
					<div class="panel panel-default">
						<div class="panel-body center-text">
							<div id="accelData" class="graphHolder"></div>
						</div>
					</div>
				</div>
				<div class="tab-pane" id="tab_d">
					<div class="panel panel-default">
						<div class="panel-body center-text">
							<div id="gyroData" class="graphHolder"></div>
						</div>
					</div>
				</div>
			</div><!-- tab content -->
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
