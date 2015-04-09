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

	String.prototype.insert = function (index, string) {
		if (index > 0) {
			return this.substring(0, index) + string + this.substring(index, this.length);
		}
		else {
			return string + this;
		}
	};

	String.prototype.indexOfFirstDifference = function(s, caseInsensitive){
      var l = this.length, i=-1;
      while(++i<l){
        if (!s[i]) {return i}
        var diff = caseInsensitive 
                   ? this[i].toUpperCase() !== s[i].toUpperCase() 
                   : this[i] !== s[i];
        if ( diff ) {  return i; }
      }
      return s.length>l ? l : null;
	};


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
		var bodyBeforeOperation;

		socket = new io.Socket();
		var documentId = '551347a1489f70f38ddb5126';
		socket.connect();
		//subscribe
		socket.on('connect', function() {
			console.log('Subscribing for global document');
			socket.subscribe('document-global');
			console.log('Subscribed for global document');
		});

		socket.on('message', function(data) {
			console.log('Recieved message');
			//recieved full document from server
			if (data.action === 'doc') {
				console.log('Action = doc, current content: ' + editorBody.innerHTML);
				editorBody.innerHTML = data.text;
				bodyBeforeOperation = data.text;
				console.log('Replaced content with: ' + data.text);
			} else if (data.action === 'msg') { //recieved operation from another user
				operation = data.op;
				text = operation.text;
				pos = operation.pos;
				currentContent = editorBody.innerHTML;
				console.log('Recieved message: ' + data);
				if (operation.type === 'i') {
					console.log('Inserting: ' + text + ' on pos: ' + pos);
					currentContent = currentContent.insert(pos, text);
					editorBody.innerHTML = currentContent;
					console.log('Inserted.. new content: ' + editorBody.innerHTML);
					//$('.webDocument').html(currentContent);
					//console.log($('.webDocument').html());
				} else if (operation.type === 'r') {
					console.log('Removing: ' + text + ' from pos: ' + pos);
					length = text.length
					editorBody.innerHTML = currentContent.substring(0, pos) + currentContent.substring(pos + length, currentContent.length);
					console.log('Removed.. new content: ' + editorBody.innerHTML);			
				}
			}
		});
		selectedText = 0;

		$(editorDocument).keypress(function(event) {
			selectedText = editorDocument.getSelection();
			console.log('selectionRange = ' + selectedText);
		});

		$(editorDocument).on('keyup', function(event) {
			console.log('Old body: ' + bodyBeforeOperation);
			console.log('Current body: ' + editorBody.innerHTML);
		    console.log('Pressed key in frame: ' + event.key);
		    console.log(event);
		    console.log('Selected text: ' + editorIframe.getSelection());
		    var key = event.key;
	    	var index = bodyBeforeOperation.indexOfFirstDifference(editorBody.innerHTML);
	    	var changeLength = Math.abs(bodyBeforeOperation.length - editorBody.innerHTML.length)
		    if (key.length == 1) {
		    	if (changeLength < 1) {
   				    bodyBeforeOperation = editorBody.innerHTML;
   				    return;
		    	} else if (changeLength > 1) {
		    		var text = bodyBeforeOperation.substring(index, index + changeLength + 1);
		    		message = {id : documentId, op : { type :"r", text : text, pos : index}};
		    		console.log('Sending remove message: ' + text + ' on pos: ' + index);
		    		socket.send(message);
		    	}
		    	message = {id : documentId, op : { type :"i", text : key, pos : index}};
		    	console.log('Sending insert message: ' + key + ' on pos: ' + index);
		    	socket.send(message);
		    } else if (key === 'Enter') {
		    	console.log('enter');
		    	if (changeLength > '</p><p>'.length) {
		    		var text = bodyBeforeOperation.substring(index, index + changeLength + 1);
		    		message = {id : documentId, op : { type :"r", text : text, pos : index}};
		    		console.log('Sending remove message: ' + text + ' on pos: ' + index);
		    		socket.send(message);
		    	}
		    	message = {id : documentId, op : { type :"i", text : '</p><p>', pos : index}};
		    	console.log('Sending insert message: ' + key + ' on pos: ' + index);
		    	socket.send(message);
		    } else if (key === 'Backspace') {
		    	console.log('backspace');
		    	var text = bodyBeforeOperation.substring(index, index + changeLength);
		    	message = {id : documentId, op : { type :"r", text : text, pos : index}};
		    	console.log('Sending remove message: ' + text + ' on pos: ' + index);
		    	socket.send(message);
		    } else if (key === 'Delete') {
		    	console.log('delete');
		    	var text = bodyBeforeOperation.substring(index, index + changeLength);
		    	message = {id : documentId, op : { type :"r", text : text, pos : index}};
		    	console.log('Sending remove message: ' + text + ' on pos: ' + index);
		    	socket.send(message);
		    }
		    bodyBeforeOperation = editorBody.innerHTML;
		});
	});



});
