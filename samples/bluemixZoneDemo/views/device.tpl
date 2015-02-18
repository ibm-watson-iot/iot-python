<!DOCTYPE html>
<html>
<head>
  <title>Internet of Things Cloud Mobile Demo</title>
  <link rel='stylesheet' href='/static/stylesheets/device.css'/>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
</head>
<body>
	<script type="text/javascript">
		window.deviceId = "{{deviceId}}";
	</script>
	
	<div class="outer-main">
		<img class="watermark" src="/static/images/bg.svg" />
		<div class="trail left"></div>
		<div class="trail right"></div>
		<img class="plane left" src="/static/images/plane.svg" />
		<img class="plane right r180" src="/static/images/plane.svg" />
		<div id="main" class="main">
			<h1>Your device ID:</h1>
			<h2><span id="deviceId">{{deviceId}}</span></h2>
			<h3><span id="instructions">Loading...</span></h3>
			<input id="pin" type="password" placeholder="Code" inputmode="numeric" maxlength="4"/>
			<button id="connectButton">Connect</button>
			<br>
			<p style="padding-top:10px">
    			<img id="connectionImage" src="/static/images/disconnected.svg" class="iot-connected-image" style="vertical-align:middle">
    			<span id="connection">Disconnected</span>
			</p>​
			<h3>So what exactly is happening here?</h3>
			<p>Using MQTT messaging, the accelerometer data from your phone is being sent to the IoT Foundation.</p>
			<p>A Bluemix app is using this data to mirror your movements &mdash; go on, try moving your phone.</p>
			<h3>Still not convinced?</h3>
			<p>Look at the web app and see what happens when you shake your phone harder!</p>
			<h3>Watch that raw data go!</h3>
		</div>
		<div class="main">
			<table class="data-table">
				<tr class="table-title">
					<th colspan="3">Movement</th>
				</tr>
				<tr class="data-title">
					<th>Alpha</th>
					<th>Beta</th>
					<th>Gamma</th>
				</tr>
				<tr>
					<td id="alpha"></td>
					<td id="beta"></td>
					<td id="gamma"></td>
				</tr>
			</table>
			<table class="data-table">
				<tr class="table-title">
					<th colspan="3">Acceleration</th>
				</tr>
				<tr class="data-title">
					<th>X</th>
					<th>Y</th>
					<th>Z</th>
				</tr>
				<tr>
					<td id="accx">X</td>
					<td id="accy">Y</td>
					<td id="accz">Z</td>
				</tr>
			</table>
		</div>
		<div class="iot-footer-pad"></div>
	</div>
	<!-- Please do not change the order of these links as some depend on each other -->
	<script type="text/javascript" src="/static/js/jquery.js"></script>
	<script type="text/javascript" src="/static/js/mqttws31.js"></script>
	<script type="text/javascript" src="/static/js/util.js"></script>
	<script type="text/javascript" src="/static/js/device.js"></script>
</body>
</html>