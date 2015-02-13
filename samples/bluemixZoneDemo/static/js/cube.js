(function(window){
	function Client() {
		var ws;

		this.connect = function(data) {
			console.log("Connecting to live data feed for user " + data.email);
			ws = new WebSocket("ws://" + window.location.host + "/websocket");
			ws.onopen = function() {
				var message = JSON.stringify(data);
				ws.send(message);
				$("#status-message").text("Connected as " + data.email)
			};
			ws.onmessage = function (evt) {
				console.log("Event data received: " + evt.data);
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
				values["accelMag"] = Math.sqrt(values.accelX * values.accelX + values.accelY * values.accelY + values.accelZ * values.accelZ);
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
		}

		this.disconnect = function() {
			ws.send("close");
			ws.close();
			console.log("Disconnected from live data feed")
			$('#connectPanel').show()
			$('#connectedPanel').hide()
		}
	}

	// Start with the necessary tabs hidden
	$('#connectedPanel').hide()

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
				cli.connect(requestData);
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
			cli.disconnect();
		}
	);
	
	
	var cli = new Client();
	var username;
	
	var container;

	var camera, scene, renderer;

	var cube;

	var targetRotation = 0;
	var targetRotationOnMouseDown = 0;

	var mouseX = 0;
	var mouseXOnMouseDown = 0;

	var width = 300;
	var height = 300;

	init();
	render(0, 0, 0);

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
		
		this.update();
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

		//////////////////////////
		
		var minval = this.properties.minValue;
		var maxval = this.properties.maxValue;

		/*
		if (this.properties.scalable) {
			for (var i in valuesSet) { 
				for (var j in valuesSet[i]) {
					if (valuesSet[i][j].y < minval) { minval = valuesSet[i][j].y; } 
					if (valuesSet[i][j].y > maxval) { maxval = valuesSet[i][j].y; } 
				}
			}
		}
		*/

		var margin = {
			top: 30, 
			right: 20, 
			bottom: 30, 
			left: 40
		};
		var width = $("#"+this.domId).parent().width() - margin.left - margin.right;
		var height = 300 - margin.top - margin.bottom;

		// Parse the date / time
		var parseDate = d3.time.format("%d-%b-%y").parse;

		// Set the ranges
		var x = d3.time.scale().range([0, width]);
		var y = d3.scale.linear().range([height, 0]);

		// Define the axes
		var xAxis = d3.svg.axis().scale(x)
			.orient("bottom").ticks(5);

		var yAxis = d3.svg.axis().scale(y)
			.orient("left").ticks(5);


		// Define the line
		var line = new d3.svg.line()
			.x(function(d) { return x(d.x); })
			.y(function(d) { return y(d.y); });
		/*
		for (var i in this.properties.stats) {
			var props = this.properties;
			lines.push(new d3.svg.line()
				.x(function(d) { return x(d.x); })
				.y(function(d) { 
					(function(idx) { 
						console.log(props, idx);
						console.log(y(d[props.stats[idx].field]));
						return function() { 
							return y(d[props.stats[idx].field]); 
						} 
					})(i) 
				}));
		}
		*/

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
		var classes = ["redline", "blueline", "greenline"];
		for (var i = 0; i < valuesSet.length; i++) {
			//console.log(i);
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

		var colors = ["darkred", "darkblue", "green"];
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
		// TODO: update all graphs
		for (var i in graphs) { graphs[i].update(); }
	}

	var graphs = []; 

	graphs.push(new Graph("magData", {
		title: "Vibration", 
		stats: [
			{ field: "accelMag", name: "Vibration" }
		],
		minValue: 0,
		maxValue: 50 
	}));
	
	graphs.push(new Graph("accelData", {
		title: "Device Motion", 
		stats: [
			{ field: "accelX", name: "Accel X" },
			{ field: "accelY", name: "Accel Y" },
			{ field: "accelZ", name: "Accel Z" }
		],
		minValue: -15,
		maxValue: 15 
		//scalable: true
	}));

	graphs.push(new Graph("gyroData", {
		title: "Device Orientation", 
		stats: [
			{ field: "rotA", name: "Alpha" },
			{ field: "rotB", name: "Beta" },
			{ field: "rotG", name: "Gamma" }
		],
		minValue: -400,
		maxValue: 400 
	}));


}(window));
