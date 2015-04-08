$(document).ready( function() {

	var editorIframe;
	var editorDocument;
	var editorBody;
	var socket;

	function onKeyHandler(event) {
		var keyCode = event.keyCode;
		switch(keyCode) {
			case (8) : {

			}
			default : {
				if (parent.editorBody.innerHTML === '<br>') {
					parent.editorBody.innerHTML = '<p></p>';
				}
			}
		}
	}

	function insertAtCaret(areaId,text) {
	    var txtarea = editorBody;
	    var img = editorDocument.createElement('img');
	    img.src = '../img/emotikon.jpeg';
	    txtarea.appendChild(img);
	    return false;
	}

	function handleKey(keyCode, body) {
		switch(keyCode) {
			case (8) : {
				if (body.innerHTML ===  "<p><br/></p>") {
					return false;
				} else {
					return true;
				}
			}
		}
	}

	$('iframe#editorContent').load(function() {
		console.log('Loading iframe editorContent');
		editorIframe = document.getElementById('editorContent');
		editorIframe = (editorIframe.contentWindow) ? editorIframe.contentWindow : (editorIframe.contentDocument.document) ? editorIframe.contentDocument.document : editorIframe.contentDocument;

		editorDocument = editorIframe.document;
		var div = editorDocument.createElement('p');
		div.innerHTML = 'Here you can put your text :)'
		editorBody = editorDocument.getElementById('editorBody');
		editorBody.innerHTML = '<p></br></p>';
		console.log('Iframe editorContent successfully loaded');

		socket = new io.Socket();
		var documentId = '551347a1489f70f38ddb5126';
		socket.connect();
		socket.on('connect', function() {
			console.log('Subscribing for global document');
			socket.subscribe('document-global');
			console.log('Subscribed for global document');
		});
		socket.on('message', function(data) {
			console.log('Recieved message');
			if (data.action === 'doc') {
				console.log('Action = doc, current content: ' + editorBody.innerHTML);
				editorBody.innerHTML = data.text;
				console.log('Replaced content with: ' + data.text);
			}
		});
	});



});
