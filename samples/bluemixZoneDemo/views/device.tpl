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
		<!--
			For some reason this watermark sits IN FRONT of the rest of the page, which makes it impossible to interact with the page.
			Whoever pretties this up can fix it, or remove it!
			<img class="watermark" src="/static/images/bg.svg" />
		-->
		<div class="trail left"></div>
		<div class="trail right"></div>
		<img class="plane left" src="/static/images/plane.svg" />
		<img class="plane right r180" src="/static/images/plane.svg" />
		<div class="iot-footer-container">
			<img class="iot-footer" src="/static/images/iot-footer.svg" />
		</div>
		<div class="main">
			<h1>Your device ID:</h1>
			<h2><span id="deviceId">{{deviceId}}</span></h2>
			<input id="pin" type="password" />
			<button id="connectButton">Connect</button>
			<h3>So what exactly is happening here?</h3>
			<p>Using MQTT messaging, the accelerometer data from your phone is being sent to the IoT Foundation.</p>
			<p>A Bluemix app is using this data to mirror your movements &mdash; go on, try moving your phone.</p>
			<h3>Still not convinced?</h3>
			<p>The application will flag a warning if your phone moves too fast. Start shaking!</p>
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
			<table class="data-table">
				<tr class="table-title">
					<th colspan="1">Device status</th>
				</tr>
				<tr class="data-title">
					<th>Connection</th>
				</tr>
				<tr>
					<td id="connection">N/A</td>
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