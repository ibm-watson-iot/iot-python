(function(window){
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

	function generateUUID() {
		var d = new Date().getTime();
		var uuid = 'xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
			var r = (d + Math.random()*16)%16 | 0;
			d = Math.floor(d/16);
			return (c=='x' ? r : (r&0x7|0x8)).toString(16);
		});
		return uuid;
	}

	var clientId = "a:"+window.iot_org+":webui_p" + Math.floor(Math.random()*1000);
	var client = new Paho.MQTT.Client(window.iot_host, parseFloat(window.iot_port), clientId);

	var sensorData = [];

	client.onMessageArrived = function(message) {
		//console.log("[%s] Message Arrived", new Date());
		var msg = JSON.parse(message.payloadString)
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

	function onConnectSuccess(){
		console.log("Connected Successfully!");
		var topic = "iot-2/type/+/id/" + window.deviceId + "/evt/sensorData/fmt/json";
		$(".requiresConnect").removeClass("disconnected");
		$(".requiresDisconnect").addClass("disconnected");
		client.subscribe(topic);
	}

	function onConnectFailure(){
		console.log("Couldn't connect, retrying...");
		$(".requiresConnect").addClass("disconnected");
		$(".requiresDisconnect").removeClass("disconnected");
		client.connect({
			onSuccess: onConnectSuccess,
			onFailure: onConnectFailure,
			userName: window.iot_apiKey,
			password: window.iot_apiToken
		});
	}

	function connect(deviceId) {
		window.deviceId = deviceId;
		client.connect({
			onSuccess: onConnectSuccess,
			onFailure: onConnectFailure,
			userName: window.iot_apiKey,
			password: window.iot_apiToken,
		});
	}

	$("#connectForm").submit(function(e) {
		connect(this.elements["deviceId"].value);
		e.preventDefault();
		return false;
	});

	function Graph(domId, properties) {
		this.maxValues = 400;
		this.domId = domId;
		this.properties = properties;

		$("#graphs").append("" +
			"<div class='col-xl-4 col-md-6'>" +
			"<div class='panel panel-default requiresConnect disconnected'>" +
			"<div class='panel-body'>" +
			"    <h3 style='margin-top: 0; text-align: center'>" + properties.title + "</h3>" +
			"    <div id='"+domId+"' class='graphHolder'></div>" +
			"</div>" +
			"</div>" +
			"</div>"
		);

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
			console.log(i);
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
