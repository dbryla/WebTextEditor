$(document).ready( function() {

	String.prototype.insert = function (index, string) {
		if (index > 0) {
			return this.substring(0, index) + string + this.substring(index, this.length);
		}
		else {
			return string + this;
		}
	};

	var socket = new io.Socket();
	var documentId = '551347a1489f70f38ddb5126';
	socket.connect();
	socket.on('connect', function() {
		socket.subscribe('document-global');
	});
	socket.on('message', function(data) {
		if (data.action === 'doc') {
			$('.webDocument').html(data.text);
		} else if (data.action === 'msg') {
			operation = data.op;
			text = operation.text;
			pos = operation.pos;
			currentContent = $('.webDocument').html();
			if (operation.type === 'i') {
				console.log(currentContent);
				currentContent = currentContent.insert(pos, text);
				console.log(currentContent);
				$('.webDocument').html(currentContent);
				console.log($('.webDocument').html());
			} else if (operation.type === 'r') {
				length = text.length
				$('.webDocument').html(currentContent.substring(0, pos) + currentContent.substring(pos + length, currentContent.length));
			}
		}
	});

	$('.webDocument').keypress(function(e) {
		var letter, selectedText;
	    var selection = window.getSelection();
	    var range = Math.abs(selection.anchorOffset - selection.focusOffset);
	    var selectionStart = Math.min(selection.anchorOffset, selection.focusOffset);
	    var text = $('.webDocument').html();
	    if (range !== 0) {
	    	selectedText = text.substring(selectionStart, selectionStart + range);
	    } else {
	    	selectedText = text[selectionStart - 1];
	    }
	    var message;
	    if (e.keyCode == 0 || e.keyCode == 13) {//char or new line
	    	letter = String.fromCharCode(e.which);
	    	if (range !== 0) {
		    	message = {id : documentId, op : { type :"r", text : selectedText, pos : selectionStart}};
		    	socket.send(message);
		    }
		    message = {id : documentId, op : { type :"i", text : letter, pos : selectionStart}};
		    socket.send(message);
	    } else if (e.keyCode == 8) {//backspace
	    	if (range !== 0) {
		    	message = {id : documentId, op : { type :"r", text : selectedText, pos : selectionStart}};
		    } else {
		    	message = {id : documentId, op : { type :"r", text : text[selectionStart - 1], pos : selectionStart - 1}};
		    }
		    socket.send(message);
	    } else if (e.keyCode == 46) {//delete
	    	if (range !== 0) {
		    	message = {id : documentId, op : { type :"r", text : selectedText, pos : selectionStart}};
		    } else {
		    	message = {id : documentId, op : { type :"r", text : text[selectionStart], pos : selectionStart}};
		    }
		    socket.send(message);
	    }
	});
});
