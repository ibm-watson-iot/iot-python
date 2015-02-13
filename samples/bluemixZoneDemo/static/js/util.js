(function(window){

	function generateUUID() {
		var d = new Date().getTime();
		var uuid = 'xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
			var r = (d + Math.random()*16)%16 | 0;
			d = Math.floor(d/16);
			return (c=='x' ? r : (r&0x7|0x8)).toString(16);
		});

		return uuid;
	}

	window.timscube = window.timscube || {};
	window.timscube.generateUUID = generateUUID;
	
}(window))