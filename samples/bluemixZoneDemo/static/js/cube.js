(function(window){
	// Work out what size window we are in when we start - we need to know this if embedded in an iFrame
	var cachedSize = getWindowScheme();
	
	function Client() {
		var ws; // web socket to the sample application
		var expectDisconnect = false; // allows the client to handle expected and unexpected disconnects from the iotzone application
		var excessiveVibrationDetected = false; // allows the client to track excessive vibration from the phone
		
		/*
		 * Toggle whether the client should expect a disconnect from the web socket server: used to control 
		 * whether an automatic reconnect occurs
		 */
		this.setExpectDisconnect = function(bool) {
			expectDisconnect = bool;
		}
		
		/*
		 * Toggle the excessiveVibrationDetected flag
		 */
		this.setExcessiveVibrationDetected = function(bool) {
			excessiveVibrationDetected = bool;
		}
		
		/*
		 * Open a web socket connection to the iotzone server
		 */
		this.connect = function(data) {
			console.log("Connecting to live data feed for user " + data.email);
			/*
			 * wss establishes a secure websocket
			 * ws establishes an insecure websocket (required for use when accessing the sample via https
			 */
			ws = new WebSocket("wss://" + window.location.host + "/websocket");
			ws.onopen = function() {
				var message = JSON.stringify(data);
				ws.send(message);
				$("#status-message").text("Connected as " + data.email)
				// Update the graphs so even if we're not receiving data, we at least have empty charts to show
				updateGraphs();
			};
			ws.onclose = function() {
				// Reconnect in a second's time, to avoid hammering the server in the event of a chronic issue
				if (!expectDisconnect) {
					console.log("Web socket connection dropped. Reconnecting in one second...");
					// We'll connect in a second's time, to avoid hammering the server in the event of a chronic issue
					setTimeout(function() {
						cli.connect(data)}, 1000);
				} else {
					console.log("Web socket connection closed successfully");
				}
			};
			ws.onmessage = function (evt) {
				var msg = JSON.parse(evt.data)
				var values = {
					time: (new Date()).getTime(),
					accelX: parseFloat(msg.ax),
					accelY: parseFloat(msg.ay),
					accelZ: parseFloat(msg.az),
					rotA: parseFloat(msg.oa),
					rotB: parseFloat(msg.ob),
					rotG: parseFloat(msg.og)
				};
				
				/*
				 * Calculate if the phone we're monitoring is vibrating excessively. You could easily extend this sample by subscribing to events
				 * from *all* phones simultaneously, and therefore alert if any phone is vibrating excessively.
				 */
				values["accelMag"] = Math.sqrt(values.accelX * values.accelX + values.accelY * values.accelY + values.accelZ * values.accelZ);
				if (values["accelMag"] >= 20 && (!excessiveVibrationDetected)) {
					vibrateWarning();
				}
									
				// Update the 3D image and graphs
				sensorData.push(values);
				render(values.rotB, values.rotG, values.rotA);
				updateGraphs();
			};
			$('#connectPanel').hide()
			$('#myUsername').text(username);
			var url = 'http://' + window.location.host + '/device/' + username;
			$('#myDeviceLink').text(url);
			$('#myDeviceLink').attr('href', url);
			$('#connectedPanel').show()
			
			$('#connectedPanel').css('opacity', 0).slideDown({
				duration: 'slow',
				progress: function() {
					updateParentIFrame();
				}
			}).animate(
				{ opacity: 1 },
				{ queue: false, duration: 'slow' }
			);
		}

		this.disconnect = function() {
			ws.send("close");
			ws.close();
			console.log("Disconnected from live data feed");
			$('#connectPanel').show()
			$('#connectedPanel').hide()
			updateParentIFrame()
		}
	}
	
	/*
	 * Allows us to report page dimensions to a parent iframe
	 * This is used in the bluemix theme, but is a no-op in all others
	 */
	function updateParentIFrame() {
		if (isInIframe) {
			// TODO: Address this workaround to extend iFrame manually when bootstrap responsively renders the visualisation.
			// Shortly we will deliver a more robust way of handling resizing in an iFrame.
			var bootstrapExtraSize = 0;
			if (getWindowScheme()=="xs") {bootstrapExtraSize = 980};
			if (getWindowScheme()=="sm") {bootstrapExtraSize = 980};
			if (getWindowScheme()=="md") {bootstrapExtraSize = 330};
			var bodyHeight = document.body.clientHeight + bootstrapExtraSize;
			if (bodyHeight != cachedHeight) {
				updateGraphs(); // Ensures that graphs are drawn to correct size
				console.log("Posting message to parent of iframe to resize to height " + bodyHeight);
				window.parent.postMessage(bodyHeight, "*");
				cachedHeight = bodyHeight;
			}
		}
	}
	
	$(document).ready(function() {
		$('#goForm').css("visibility", "visible");
		$('#registerForm').css("visibility", "visible");
		$('#connectForm').css("visibility", "visible");
		$('#signoutButton').css("visibility", "visible");
		updateParentIFrame();

		// If in iframe, post resize messages to parent
		if (isInIframe) {
			$(window).resize(function() {
				updateParentIFrame();
			});
		}
		
		$("#goForm").submit(function(e) {
			$("#goWarning").css("visibility", "hidden");
			var requestData = {"email": this.elements["username3"].value, "pin": this.elements["pin3"].value};
			username = this.elements["username3"].value;
			// Try to authenticate
			$.ajax({
				url: "/auth",
				type: "POST",
				data: JSON.stringify(requestData),
				dataType: "json",
				contentType: "application/json; charset=utf-8",
				success: function(response){
					cli.connect(requestData);
					updateQrCode();
				},
				error: function(xhr, status, error) {
					if (xhr.status==403) {
						// Username existed, but incorrect code
						console.log("User exists, but incorrect PIN");
						$("#goWarning").css("visibility", "visible");
						$("#goWarning").html("<span>Incorrect code provided for existing smartphone '"+username+"'</span>");
					} 
					else if (xhr.status==404) {
						// Username doesn't exist, so let's auto register
						console.log("User "+username+"does not exist, so autoregistering");
						$.ajax({
							url: "/register",
							type: "POST",
							data: JSON.stringify(requestData),
							contentType: "application/json; charset=utf-8",
							success: function(response){
								cli.connect(requestData);
							},
							error: function(xhr, status, error) {
								$("#goWarning").css("visibility", "visible");
								$("#goWarning").html("<span>Failed to register! " + xhr.responseText + "</span>");
							}
						});
					}
					else {
						// An unexpected error
						$("#goWarning").css("visibility", "visible");
						$("#goWarning").html("<span>Error authenticating: '+error</span>");
					}
				}
			});
			return false;
		});

		$("#registerForm").submit(function(e) {
			$("#registerWarning").css("visibility", "hidden");
			var requestData = {"email": this.elements["username1"].value, "pin": this.elements["pin1"].value};
			username = this.elements["username1"].value;
			$.ajax({
				url: "/register",
				type: "POST",
				data: JSON.stringify(requestData),
				contentType: "application/json; charset=utf-8",
				success: function(response){
					cli.connect(requestData);
					updateQrCode();
				},
				error: function(xhr, status, error) {
					$("#registerWarning").css("visibility", "visible");
					if (error == "Conflict") {
						$("#registerWarning").html("<strong>Username '" + username + "' is already taken!</strong>  Please choose another.");
					}
					else {
						$("#registerWarning").html("<strong>Failed to register username!</strong>  " + error);
					}
				}
			});
			return false;
		});

		$("#connectForm").submit(function(e) {
			$("#connectWarning").css("visibility", "hidden");
			var requestData = {"email": this.elements["username2"].value, "pin": this.elements["pin2"].value};
			username = this.elements["username2"].value;
			$.ajax({
				url: "/auth",
				type: "POST",
				data: JSON.stringify(requestData),
				dataType: "json",
				contentType: "application/json; charset=utf-8",
				success: function(response){
					cli.setExpectDisconnect(false);
					cli.connect(requestData);
					updateQrCode();
				},
				error: function(xhr, status, error) {
					$("#connectWarning").css("visibility", "visible");
					$("#connectWarning").html("<strong>Failed to connect!</strong>  Invalid combination of username and PIN");
				}
			});
			return false;
		});

		$("#signoutButton").click(
			function(){
				/*
				 * We have been deliberately requested to close the web socket connection, so let's tell the client
				 * so it knows not to reconnect automatically.
				 */		
				cli.setExpectDisconnect(true); // We expect the web socket connection to close
				cli.disconnect();
			}
		);
	});
	
	function updateQrCode() {
		// Remove any existing QR code and build a new QR code for the currently selected device
		$('#qrcode').empty();
		$('#qrcode').qrcode({
			text: 'http://' + window.location.host + '/device/' + username,
			width: 128,
			height: 128,
			foreground : "#1d3649",
			background : "#ffffff"
		});
	}
	
	function vibrateWarning() {
		/*
		 * Excessive vibration has been detected from the incoming events! Show an alert and switch off the excessive vibration detector while
		 * the alert is being shown
		 */
		cli.setExcessiveVibrationDetected(true);
		$("#vibrationWarning").css("visibility", "visible");
		setTimeout(function() {
			$("#vibrationWarning").css("visibility", "hidden");
			// Reset the excessive vibration detector
			cli.setExcessiveVibrationDetected(false);
		}, 2000);
	}
	
	// Allows the page to be embedded in an iframe and report resize events to the parent
	var cachedHeight = undefined;
	var isInIframe = (window.location != window.parent.location) ? true : false;
	// If embedded in an iFrame, we want to ensure that any responsive resizing by Bluemix is reflected in the parent iFrame. We only do this if we 
	// can detect a specific change in rendering.
	$(window).resize(function () {
		var newSize = getWindowScheme();
		if (newSize!=cachedSize) {
			cachedSize = newSize;
			updateParentIFrame();
		}
	});
	
	var cli = new Client();
	var username;
	
	var container;

	var camera, scene, renderer;

	var cube;

	var targetRotation = 0;
	var targetRotationOnMouseDown = 0;

	var mouseX = 0;
	var mouseXOnMouseDown = 0;

	var width = 270;
	var height = 270;

	init();
	render(0, 0, 0);
	
	function getWindowScheme() {
		if ($('.device-xs').is(':visible')) {return "xs";}
		if ($('.device-sm').is(':visible')) {return "sm";}
		if ($('.device-md').is(':visible')) {return "md";}
		// Assume large
		else {return "lg";}
	}

	function init() {

		renderer = new THREE.WebGLRenderer();
		renderer.setSize(width, height);
		$("#cube").append(renderer.domElement);

		// camera
		camera = new THREE.PerspectiveCamera(65, width / height, 1, 1000);
		camera.position.z = 500;

		// scene
		scene = new THREE.Scene();
		        
		// cube
		cube = new THREE.Mesh(new THREE.CubeGeometry(200, 400, 75), new THREE.MeshLambertMaterial({
			color: 'rgb(2,104,144)' 
		}));
		
		cube.overdraw = true;
		cube.rotation.x = Math.PI * 0.1;
		scene.add(cube);

		var ambientLight = new THREE.AmbientLight(0x111111);
		scene.add(ambientLight);

		// directional lighting
		var directionalLight = new THREE.DirectionalLight(0xffffff);
		directionalLight.position.set(1, 1, 1).normalize();
		scene.add(directionalLight);
	}

	function changeColor(color){
		cube.material.color.setStyle(color);
		render(0, 0, 0);
	}

	function animate() {
		requestAnimationFrame( animate );
		render();
	}

	function render(_x, _y, _z) {
		cube.rotation.x = (_x-90) * Math.PI/180; // beta
		cube.rotation.y = _y * Math.PI/180; // gamma
		cube.rotation.z = (_z-90) * Math.PI/180; // alpha
		renderer.render( scene, camera );
	}

	var sensorData = [];

	function Graph(domId, properties) {
		this.maxValues = 400;
		this.domId = domId;
		this.properties = properties;
	}

	Graph.prototype.update = function() {
		var valuesSet = [];
		var availableData = sensorData;
		var dataLength = availableData.length;

		for (var j in this.properties.stats) {
			var statField = this.properties.stats[j].field;
			var values = [];
			for (var i = 0; i < dataLength; i++) {
				var val = {
					x: availableData[i].time,
					y: availableData[i][statField]
				};
				values.push(val);
			}
			if (dataLength < this.maxValues) {
				for (var i = 0; i < this.maxValues - dataLength; i++) { 
					var val = { x: 0, y: 0 };
					values.splice(0,0,val); 
				}
			}
			if (dataLength > this.maxValues) {
				values.splice(0, dataLength - this.maxValues);
			}

			for (var i = 0; i < values.length; i++) {
				if (values[i].x == 0) {
					values[i].x = new Date((new Date()).getTime() - (values.length - i) * 100);
				}
			}
			valuesSet.push(values);
		}

		var minval = this.properties.minValue;
		var maxval = this.properties.maxValue;

		var margin = {
			top: 30, 
			right: 20, 
			bottom: 30, 
			left: 40
		};
		var width = $("#"+this.domId).parent().width() - margin.left - margin.right;
		var height = 300 - margin.top - margin.bottom;

		
		// Set the ranges
		var x = d3.time.scale().range([0, width]);
		var y = d3.scale.linear().range([height, 0]);

		
		// Define the axes
		var xAxis = d3.svg.axis().scale(x)
			.orient("bottom").ticks(5).tickFormat("").outerTickSize(0);

		var yAxis = d3.svg.axis().scale(y)
			.orient("left").ticks(5);

		// Define the line
		var line = new d3.svg.line()
			.x(function(d) { return x(d.x); })
			.y(function(d) { return y(d.y); });

		// Adds the svg canvas
		$("#"+this.domId).html("");
		var svg = d3.select("#"+this.domId)
			.append("svg")
				.attr("width", width + margin.left + margin.right)
				.attr("height", height + margin.top + margin.bottom)
			.append("g")
				.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

		// Scale the range of the data
		x.domain(d3.extent(valuesSet[0], function(d) { return d.x; }));
		y.domain([minval, maxval]);

		// Add the paths.
		var classes = ["primaryline", "secondaryline", "tertiaryline"];
		for (var i = 0; i < valuesSet.length; i++) {
			svg.append("path")
				.attr("class", classes[i])
				.attr("d", line(valuesSet[i]));
		}

		// Add the X Axis
		svg.append("g")
			.attr("class", "x axis")
			.attr("transform", "translate(0," + height + ")")
			.call(xAxis);

		// Add the Y Axis
		svg.append("g")
			.attr("class", "y axis")
			.call(yAxis);

		var colors = ["#1d3649", "#41d6c3", "#5596e6"];
		
		// Add a key to the graph
		for (var i = 0 ; i < valuesSet.length; i++) {
			svg.append("svg:rect")
					.attr("x", width - 120)
					.attr("y", 0 + i * 22)
					.attr("stroke", colors[i])
					.attr("height", 2)
					.attr("width", 40);
			svg.append("svg:text")
					.attr("x", width - 70)
					.attr("y", 5 + i * 22)
					.text(this.properties.stats[i].name);
		}
	}

	function updateGraphs() {
		for (var i in graphs) { 
			graphs[i].update(); 
		}
	}

	var graphs = []; 

	graphs.push(new Graph("magData", {
		title: "Vibration", 
		stats: [
			{ field: "accelMag", name: "Vibration" }
		],
		minValue: 0,
		maxValue: 70 
	}));
	
	graphs.push(new Graph("accelData", {
		title: "Device Motion", 
		stats: [
			{ field: "accelX", name: "Accel X" },
			{ field: "accelY", name: "Accel Y" },
			{ field: "accelZ", name: "Accel Z" }
		],
		minValue: -30,
		maxValue: 30 
	}));

	graphs.push(new Graph("gyroData", {
		title: "Device Orientation", 
		stats: [
			{ field: "rotA", name: "Alpha" },
			{ field: "rotB", name: "Beta" },
			{ field: "rotG", name: "Gamma" }
		],
		minValue: -500,
		maxValue: 500 
	}));

}(window));
