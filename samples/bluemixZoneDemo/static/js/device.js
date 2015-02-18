(function(window){
    var ax = 0, ay = 0, az = 0, oa = 0, ob = 0, og = 0;
	
	var client;
    var orgId;
	var clientId;
    var password;
    
	var topic = "iot-2/evt/sensorData/fmt/json";
    var isConnected = false;

    window.ondevicemotion = function(event) {
        ax = parseFloat((event.acceleration.x || 0));
        ay = parseFloat((event.acceleration.y || 0));
        az = parseFloat((event.acceleration.z || 0));

        document.getElementById("accx").innerHTML = ax.toFixed(2);
        document.getElementById("accy").innerHTML = ay.toFixed(2);
        document.getElementById("accz").innerHTML = az.toFixed(2);
    }

    window.ondeviceorientation = function(event){

        oa = (event.alpha || 0);
        ob = (event.beta || 0);
        og = (event.gamma || 0);

        if(event.webkitCompassHeading){
            oa = -event.webkitCompassHeading;
        }

        document.getElementById("alpha").innerHTML = oa.toFixed(2);
        document.getElementById("beta").innerHTML = ob.toFixed(2);
        document.getElementById("gamma").innerHTML = og.toFixed(2);
    }

    function publish() {
    	// We only attempt to publish if we're actually connected, saving CPU and battery
		if (isConnected) {
	    	var payload = {
	            "d": {
					"ax": ax.toFixed(2),
					"ay": ay.toFixed(2),
					"az": az.toFixed(2),
					"oa": oa.toFixed(2),
					"ob": ob.toFixed(2),
					"og": og.toFixed(2)
				}
	        };
	        var message = new Paho.MQTT.Message(JSON.stringify(payload));
	        message.destinationName = topic;
	       	try {
			     client.send(message);
			     console.log("[%s] Published", new Date().getTime());
			}
			catch (err) {
				// This occurs if we've actually lost our connection. We should therefore attempt to reconnect. 
				// We wait for a second before doing this, so that chronic issues with the network do not lead
				// to rapid connect attempts and hence drain the battery/use unnecessary network bandwidth.
				// Alternatively, we could use Paho's onConnectionLost mechanism.
				isConnected = false;
				document.getElementById("connection").innerHTML = "Disconnected";
				setTimeout(connectDevice(client), 1000);		
			}
		}
    }

    function onConnectSuccess(){
    	// The device connected successfully
        console.log("Connected Successfully!");
        isConnected = true;
        document.getElementById("connection").innerHTML = "Connected";
    }

    function onConnectFailure(){
    	// The device failed to connect. Let's try again in one second.
        console.log("Could not connect to IoT Foundation! Trying again in one second.");
        setTimeout(connectDevice(client), 1000);	
    }
    
    function connectDevice(client){
		document.getElementById("connection").innerHTML = "Connecting...";	
    	console.log("Connecting device to IoT Foundation...");
		client.connect({
			onSuccess: onConnectSuccess,
			onFailure: onConnectFailure,
			userName: "use-token-auth",
			password: password
		});
    }
    
    function getDeviceCredentials() {
		var data = {"email": window.deviceId, "pin": document.getElementById('pin').value};
		$.ajax({
			url: "/auth",
			type: "POST",
			data: JSON.stringify(data),
			contentType: "application/json; charset=utf-8",
			dataType: "json",
			success: function(response){
				orgId = response.orgid;
				clientId = response.clientid;
				password = response.authtoken;
				
				client = new Paho.MQTT.Client(orgId+".messaging.internetofthings.ibmcloud.com", 1883, clientId);

				console.log("Attempting connect");

				connectDevice(client);

				/*
				 * Now start the publish cycle to publish 10 times a second. This offers smooth animations 
				 * in the demo, but in most cases a publish rate of 10 msg/sec will be far in excess of any 
				 * real world needs.
				 */
				setInterval(publish, 100);
			},
			error: function(xhr, status, error) {
				alert("Failed to authenticate! " + error);
			}
		});
    }
	
	$("#connectButton").click(getDeviceCredentials);

    var deviceId = window.deviceId;
	document.getElementById("connection").innerHTML = "Disconnected";
	
}(window));
