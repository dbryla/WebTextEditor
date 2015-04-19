$(document).ready( function() {

	showWaitPage = function() {
		$('#showWaitPageTrigger').trigger('click');
	}

	hideWaitPage = function() {
		$('#closeWaitPageTrigger').trigger('click');
	}

	showWaitPage();

	var editorIframe;
	var editorDocument;
	var editorBody;
	var socket;
	var documentId;


	function insertAtCaret(areaId,text) {
		var txtarea = editorBody;
		var img = editorDocument.createElement('img');
		img.src = '../img/emotikon.jpeg';
		txtarea.appendChild(img);
		return false;
	}

	function fillCell(table, targetRow, targetCell, fillContents) {
		var tableObj = document.getElementById(table);
		var selectedRow = tableObj.rows[targetRow-1];

		var selectedCell = selectedRow.cells[targetCell-1];
		selectedCell.innerHTML = fillContents;
	}

	prepareDocument = function(unsubscribeDocumentId, subscribeDocumentId) {
		console.log('Unsubscribing from ' + unsubscribeDocumentId);
		socket.unsubscribe(unsubscribeDocumentId);
		console.log('Subscribing for ' + subscribeDocumentId);
		socket.subscribe(subscribeDocumentId);
		documentId = subscribeDocumentId;
	}

	selectDocument = function(element) {
		selectedDocumentId = $(element).closest('tr').attr('id');
		prepareDocument(documentId, selectedDocumentId);
		$('#fileListModal').trigger('reveal:close');
	}

	
	changeBackgroundColor = function(tableRow, highLight) {
		if (highLight) {
		  tableRow.style.backgroundColor = '#dcfac9';
		}
		else {
		  tableRow.style.backgroundColor = 'white';
		}
	}

	saveDocument = function(documentName, documentBody, action) {
		console.log(documentName + ' ' + documentBody);
		var saveMessage = { action : action, text : documentBody, name: documentName };
		socket.send(saveMessage);
		$('#closeFileNameTrigger').trigger('click');
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
		div.innerHTML = 'Here you can put your text :)';
		editorBody = editorDocument.getElementById('editorBody');
		editorBody.innerHTML = '<p></br></p>';
		console.log('Iframe editorContent successfully loaded');
		var bodyBeforeOperation;

		socket = new io.Socket();
		documentId = '551347a1489f70f38ddb5126';
		socket.connect('http://127.0.0.1');
		//subscribe
		socket.on('connect', function() {
			console.log('Subscribing for global document');
			socket.subscribe(documentId);
			console.log('Subscribed for global document');
		});

		socket.on('message', function(data) {
			console.log('Recieved message');
			//recieved full document from server
			if (data.action === 'doc') {
				console.log('Action = doc, current content: ' + editorBody.innerHTML);
				hideWaitPage();
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
			} else if (data.action === 'list') {
				console.log('Recieved documents list: ' + data.files.length);
				$('#documentList').find('tr').remove();
				$.each(data.files, function() {
					console.log(this);
					var documentRow = $('<tr>', {
						id: this.id,
						onmouseover: 'changeBackgroundColor(this, true);', 
						onmouseout: 'changeBackgroundColor(this, false);', 
						onclick: 'selectDocument(this);return false;'
					});
					documentRow.append($('<td>').append(this.name));
					$('#documentList').append(documentRow);
				});
			} else if (data.action === 'save' || data.action === 'new') {
				console.log(data);
				prepareDocument(documentId, data.id);
			}
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
				var text = bodyBeforeOperation.substring(index, index + changeLength + 1);
				if (changeLength < 1) {
					bodyBeforeOperation = editorBody.innerHTML;
					return;
				} else if (changeLength > 1 && text !== '</p>') {		    		
					message = {id : documentId, action: "msg", op : { type :"r", text : text, pos : index}};
					console.log('Sending remove message: ' + text + ' on pos: ' + index);
					socket.send(message);
				}
				message = {id : documentId, action: "msg", op : { type :"i", text : key, pos : index}};
				console.log('Sending insert message: ' + key + ' on pos: ' + index);
				socket.send(message);
			} else if (key === 'Enter') {
				console.log('enter');
				if (changeLength > '</p><p><br>'.length) {
					var text = bodyBeforeOperation.substring(index, index + changeLength + 1);
					message = {id : documentId, action: "msg", op : { type :"r", text : text, pos : index}};
					console.log('Sending remove message: ' + text + ' on pos: ' + index);
					socket.send(message);
				}
				message = {id : documentId, action: "msg", op : { type :"i", text : '</p><p>', pos : index}};
				console.log('Sending insert message: ' + key + ' on pos: ' + index);
				socket.send(message);
			} else if (key === 'Backspace') {
				if (editorBody.innerHTML === '' || editorBody.innerHTML === '<br>' ) {
					editorBody.innerHTML = '<p></br></p>';
				} else {
					console.log('backspace');
					var text = bodyBeforeOperation.substring(index, index + changeLength);
					message = {id : documentId, action: "msg", op : { type :"r", text : text, pos : index}};
					console.log('Sending remove message: ' + text + ' on pos: ' + index);
					socket.send(message);
				}
			} else if (key === 'Delete') {
				console.log('delete');
				var text = bodyBeforeOperation.substring(index, index + changeLength);
				message = {id : documentId, action: "msg", op : { type :"r", text : text, pos : index}};
				console.log('Sending remove message: ' + text + ' on pos: ' + index);
				socket.send(message);
			}
			bodyBeforeOperation = editorBody.innerHTML;
		});

		$('#documentListButton').on('click', function() {
			console.log('Filling documents list into table');
			message = {action : 'list'};
			socket.send(message);
		});



	});

	$('#newDocument').on('click', function() {
		$('#saveDocumentButton').unbind("click");
		$('#saveDocumentButton').on('click', function() {
			var name = $('#documentName').val();
			console.log('New document save button clicked. Name: ' + name);
			saveDocument(name, '<p><br></p>', 'new');
		});
	});

	$('#saveDocument').on('click', function() {
		$('#saveDocumentButton').unbind("click");
		$('#saveDocumentButton').on('click', function() {
			var name = $('#documentName').val();
			console.log('Save document save button clicked. Name: ' + name);
			saveDocument(name, editorBody.innerHTML, 'save');
		});
	});

});
