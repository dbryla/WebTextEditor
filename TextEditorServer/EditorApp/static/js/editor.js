$(document).ready( function() {
	/**
	 *	Displays "Please wait" modal.
	 */
	showWaitPage = function() {
		$('#showWaitPageTrigger').trigger('click');
	}

	/**
	 *	Hides "Please wait" modal.
	 */
	hideWaitPage = function() {
		$('#closeWaitPageTrigger').trigger('click');
	}

	showWaitPage();

	//var editorDocument;
	var selection = '';


	/**
	 *	Updates table's [targetRow][TargetCell] element with fillContents.
	 */
	function fillCell(table, targetRow, targetCell, fillContents) {
		var tableObj = document.getElementById(table);
		var selectedRow = tableObj.rows[targetRow-1];

		var selectedCell = selectedRow.cells[targetCell-1];
		selectedCell.innerHTML = fillContents;
	}


	/**
	 *	Prepares for opened/saved document - this includes unsubscribing from old channel and subscribing to new one.
	 */
	prepareDocument = function(unsubscribeDocumentId, subscribeDocumentId) {
		if (unsubscribeDocumentId !== undefined) {
			console.log('Unsubscribing from ' + unsubscribeDocumentId);
			socket.unsubscribe('id-' + unsubscribeDocumentId);
		} else {
			console.log('Unsubscribing from list');
			socket.unsubscribe('list');
		}
		console.log('Subscribing for ' + subscribeDocumentId);
		socket.subscribe('id-' + subscribeDocumentId);
		documentId = subscribeDocumentId;
	}

	/**
	 *	Handler for selecting document from list.
	 */
	selectDocument = function(element) {
		selectedDocumentId = $(element).closest('tr').attr('id');
		prepareDocument(documentId, selectedDocumentId);
		$('#documentNameHeader').text($(element).children('td').text());
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


	/**
	 *	Prepares and sends message to socket with information about saving document.
	 */
	saveDocument = function(documentName, documentBody, privateFlag) {
		console.log(documentName + ' ' + documentBody);
		var saveMessage = { action : 'save', text : documentBody, name: documentName, priv : privateFlag };
		socket.send(saveMessage);
		$('#closeFileNameTrigger').trigger('click');
		$('#documentNameHeader').text(documentName);
	}
	
	$('iframe#editorContent').load(function() {
		console.log('Loading iframe editorContent');
		editorIframe = document.getElementById('editorContent');
		editorIframe = (editorIframe.contentWindow) ? editorIframe.contentWindow : (editorIframe.contentDocument.document) ? editorIframe.contentDocument.document : editorIframe.contentDocument;

		editorDocument = editorIframe.document;
		editorBody = editorDocument.getElementById('editorBody');
		console.log('Iframe editorContent successfully loaded');

		socket = new io.Socket();
		socket.connect('http://127.0.0.1');
		
		hideWaitPage();
		$('#showFileListTrigger').trigger('click');
		//subscribe
		socket.on('connect', function() {
			if (documentId === undefined) {
				console.log('Subscribing for document list');
				socket.subscribe('list');
				console.log('Subscribed for document list');
			} else {
				console.log('Reconnecting... ' + documentId);
				socket.subscribe('id-' + documentId);
			}
		});

		var selection;

		$(editorBody).on('mouseup', function() {
			selection = rangy.getSelection(editorIframe).toHtml();
			console.log('Selected text: ' + selection);			
		});

		$(editorIframe).on('mouseup', function() {
			selection = rangy.getSelection(editorIframe).toHtml();
			console.log('Selected text: ' + selection);			
		});


		/**
		 *	Prepares and sends message on socket with information about text to be removed from document on specified position.
		 */
		sendRemoveText = function(doc, text, position) {
			message = {id : doc, action: "msg", op : { type :"r", text : text, pos : position}};
			console.log('Sending remove message: ' + text + ' on pos: ' + position);
			socket.send(message);
		}

		/**
		 *	Prepares and sends message on socket with information about text to be inserted into document on specified position.
		 */
		sendInsertText = function(doc, text, position) {
			message = {id : doc, action: "msg", op : { type :"i", text : text, pos : position}};
			console.log('Sending insert message: ' + text + ' on pos: ' + position);
			socket.send(message);
		}
				
		insertAtCaret = function(imgName, path) {
			console.log('Inserting image ' + path + imgName);
			var bodyBeforeTagging = editorBody.innerHTML;
			console.log('Before inserting: ' + bodyBeforeTagging);
			var text = rangy.getSelection(editorIframe);
			var start = text.anchorOffset;
			var s = '<img src=' + path + imgName + '></img>';
			if (text.anchorNode.nodeValue == null) {
				text.anchorNode.textContent = s;
			} else {
				text.anchorNode.nodeValue = text.anchorNode.nodeValue.slice(0,start) + s + text.anchorNode.nodeValue.slice(start);
			}
			replaceImgTag();
			var bodyAfterTagging = editorBody.innerHTML;
			console.log('After tagging: ' + bodyAfterTagging);
			propagateChanges(bodyBeforeTagging, bodyAfterTagging, 'img');
			bodyBeforeOperation = bodyAfterTagging;
		    	return false;
		}
		
		replaceImgTag = function() {
			var text = editorBody.innerHTML;
			text = text.replace('&lt;img', '<img');
			text = text.replace('&lt;/img&gt;', '</img>');
			text = text.replace('&gt;', '>');
			editorBody.innerHTML = text;
		}
		
		$(editorDocument).on('keyup', function(event) {
			if (bodyBeforeOperation == null) {
				bodyBeforeOperation = "";
			}
			console.log('Old body: ' + bodyBeforeOperation);
			console.log('Current body: ' + editorBody.innerHTML);
			console.log('Pressed key in frame: ' + event.key);
			console.log(event);
			console.log('Selected text: ');
			console.log(selection);
			var key = event.key;
			var index = bodyBeforeOperation.indexOfFirstDifference(editorBody.innerHTML);
			var changeLength = Math.abs(bodyBeforeOperation.length - editorBody.innerHTML.length);
			console.log('Change length: ' + changeLength);
			if (key.length == 1) {
				var text = bodyBeforeOperation.substring(index, index + changeLength + 1);
				//TODO: fix when selected just one character
				//TODO: fix when typing in character same as selection start
				if (changeLength < 1) {
					//no changes
					bodyBeforeOperation = editorBody.innerHTML;
					return;
				} else if (selection.length > 1) {
					//remove selection and add new text		    		
					sendRemoveText(documentId, text, index);
					var text = editorBody.innerHTML.substring(index, index + changeLength);
					sendInsertText(documentId, key, index);
				} else {
					//simple add text
					var text = editorBody.innerHTML.substring(index, index + changeLength);
					sendInsertText(documentId, text, index);
				}
			} else if (key === 'Enter') {
				console.log('enter');
				if (selection.length > 1) {
					//replaces selection with new line
					//TODO: fix selection of single line
					//TODO: fix selection starting with start of line and ending just before space <- big problem since <p> after selecton dissapear
					//var text = bodyBeforeOperation.substring(index, index + changeLength + 7);
					//console.log(text);
					bodyBeforeOperation = bodyBeforeOperation.substring(0, index) + bodyBeforeOperation.substring(index + selection.length);
					changeLength = Math.abs(bodyBeforeOperation.length - editorBody.innerHTML.length);
					console.log(bodyBeforeOperation);
					console.log(editorBody.innerHTML);
					console.log(changeLength);
					sendRemoveText(documentId, selection, index);
					index = bodyBeforeOperation.indexOfFirstDifference(editorBody.innerHTML);
					if (changeLength === 11) {
						sendInsertText(documentId, '<br></p><p>', index);
					} else if (changeLength === 7) {
						sendInsertText(documentId, '</p><p>', index);
					} else if (changeLength === 15) {
						sendInsertText(documentId, '<br></p><p><br>', index - 1);
					}
				} else {
					//simple new line add
					var text = editorBody.innerHTML.substring(index, index + changeLength);
					sendInsertText(documentId, text, index);
				}
			} else if (key === 'Backspace') {
				console.log('backspace');
				if (editorBody.innerHTML === '' || editorBody.innerHTML === '<br>' ) {
					//prevents from removing <p> on empty document
					editorBody.innerHTML = '<p></br></p>';
				} else {
					console.log('backspace');
					if (selection.length === 0 && changeLength === 3) {
						//when backspacing character after space iframe adds <br>
						var text = bodyBeforeOperation.substring(index, index + 1);
						sendRemoveText(documentId, text, index);
						sendInsertText(documentId, '<br>', index);
					} else {
						//simple remove
						var text = bodyBeforeOperation.substring(index, index + changeLength);
						sendRemoveText(documentId, text, index);
					}
				}
			} else if (key === 'Delete') {
				console.log('delete');
				console.log(text);
				console.log(selection.length);
				console.log(changeLength);
				if (selection.length === 0) {
					if (changeLength === 4) {
						//when deleting character before space iframe changes space into &nbsp;
						var text = bodyBeforeOperation.substring(index, index + 2);
						sendRemoveText(documentId, text, index);
						sendInsertText(documentId, '&nbsp;', index);
					} else if (changeLength === 3) {
						//when deleting character before new line iframe adds <br>
						var text = bodyBeforeOperation.substring(index, index + 1);
						sendRemoveText(documentId, text, index);
						sendInsertText(documentId, '<br>', index);
					} else {
						//simple remove of character
						var text = bodyBeforeOperation.substring(index, index + changeLength);
						sendRemoveText(documentId, text, index);
					}
				} else {
					//simple remove of whole selection
					var text = bodyBeforeOperation.substring(index, index + changeLength);
					sendRemoveText(documentId, text, index);
				}
			}
			bodyBeforeOperation = editorBody.innerHTML;
			selection = '';
		});

		$('#documentListButton').on('click', function() {
			console.log('Filling documents list into table');
			message = {action : 'list'};
			socket.send(message);
		});

	});

	$('#newDocument').on('click', function () {
		$('#saveDocumentButton').unbind("click");
		editorBody.innerHTML = '<p><br></p>';
		$('#saveDocumentButton').on('click', function() {
			if (offlineMode == true) {
				online();
			}
			var name = $('#documentName').val();
			var privateFlag = $('#privateFlag').is(":checked");
			console.log('New document save button clicked. Name: ' + name + ' is private: ' + privateFlag);
			saveDocument(name, '<p><br></p>', privateFlag);
		});
	});

	$('#saveDocument').on('click', function() {
		$('#saveDocumentButton').unbind("click");
		$('#saveDocumentButton').on('click', function() {
			if (offlineMode == true) {
				online();
			}
			var name = $('#documentName').val();
			var privateFlag = $('#privateFlag').is(":checked");
			console.log('Save document save button clicked. Name: ' + name + ', is private: ' + privateFlag);
			saveDocument(name, editorBody.innerHTML, privateFlag);
		});
	});

	swapWindows = function() {
		$('#fileNameModalAtStart').trigger('reveal:close');
		$('#fileListModal').reveal({
     		animation: 'fadeAndPop',
     		closeonbackgroundclick: false,
		});
	}

	newDocAtStart = function() {
		if (documentId === undefined) {
			$('#fileListModal').trigger('reveal:close'); 
			$('#showFileNameModalAtStartTrigger').trigger('click');
			$('#saveDocumentButtonAtStart').unbind("click");
			$('#saveDocumentButtonAtStart').on('click', function() {
				var name = $('#documentNameAtStart').val();
				var privateFlag = $('#privateFlagAtStart').is(":checked");
				console.log('New document save button clicked. Name: ' + name + ' is private: ' + privateFlag);
				saveDocument(name, '<p><br></p>', privateFlag);
			});
		} else {
			$('#fileListModal').trigger('reveal:close'); 
			$('#showFileNameModalTrigger').trigger('click');
			$('#saveDocumentButton').unbind("click");
			$('#saveDocumentButton').on('click', function() {
				var name = $('#documentName').val();
				var privateFlag = $('#privateFlag').is(":checked");
				console.log('New document save button clicked. Name: ' + name + ' is private: ' + privateFlag);
				saveDocument(name, '<p><br></p>', privateFlag);
			});
		}
	}

	$('#localSave').on('click', function() {
		console.log(editorBody.innerHTML);
	});

	$('#export').on('click', function() {
		var name  = $('#documentNameHeader').text() + '.pdf' 
		var url = "/download/?documentId=" + documentId;
		console.log('Exporting ' + name);
		var link = document.createElement('a');
 		document.body.appendChild(link);
 		link.href = url;
 		link.download = name;
 		link.click();
	});

	$('#linkSubmitButton').on('click', function() {
		var link = $('#linkInputValue').val();
		insertAtCaret(link, '');
		$('#linkInputValue').val('');
		$('#linkUploadModalTrigger').trigger('click');
	});

	insertImage = function(path) {
		var fileName = document.getElementById("id_docfile").files[0].name;
		console.log("Inserting image " + fileName);
		insertAtCaret(fileName, path);
	}
});