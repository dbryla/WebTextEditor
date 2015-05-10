$(document).ready( function() {

	Offline.options = {checks: {xhr: {url: '/login'}}};

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
	var documentId = undefined;
	var selection = '';
	var offlineMode = false;
	var noDocumentReplace = false;

	Offline.on('down', function () {
        console.log('Going offline!');
        console.log(socket);
        $('#localSave').show();
        offline();
        noDocumentReplace = true;
    });

    Offline.on('up', function () {
        console.log('Going back online!!');
        console.log(socket);
        $('#localSave').hide();
        offlineMode = false;
        socket.connect('http://127.0.0.1');
        //socket.subscribe('id-' + documentId);
    });


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

	offline = function() {
		console.log('Unsubscribing from ' + documentId);
		socket.unsubscribe('id-' + documentId);
		offlineMode = true;
	}

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

	saveDocument = function(documentName, documentBody, privateFlag) {
		console.log(documentName + ' ' + documentBody);
		var saveMessage = { action : 'save', text : documentBody, name: documentName, priv : privateFlag };
		socket.send(saveMessage);
		$('#closeFileNameTrigger').trigger('click');
		$('#documentNameHeader').text(documentName);
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
		editorBody = editorDocument.getElementById('editorBody');
		console.log('Iframe editorContent successfully loaded');
		var bodyBeforeOperation;

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

		socket.on('message', function(data) {
			console.log('Recieved message');
			console.log(data);
			//recieved full document from server
			if (data.action === 'doc') {
				if (noDocumentReplace === false) {
					if (data.override_warning === 'true') {
						alert('Someone changed content while being in offline mode. Your changes will be overriden.');
					}
					console.log('Action = doc, current content: ' + editorBody.innerHTML);
					editorBody.innerHTML = data.text;
					bodyBeforeOperation = data.text;
					console.log('Replaced content with: ' + data.text);
				} else {
					console.log('Action = doc, after reconnection');
					var message = {id : documentId, action : 'doc', text : editorBody.innerHTML};
					socket.send(message);
					console.log('Sending whole document: ' + message.text);
					noDocumentReplace = true;
				}
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
			} else if (data.action === 'save') {
				console.log(data);
				prepareDocument(documentId, data.id);
			}
		});

		var selection;

		$(editorBody).on('mouseup', function() {
			selection = rangy.getSelection(editorIframe).toHtml();
			console.log('Selected text: ' + selection);			
		});

		sendRemoveText = function(doc, text, position) {
			message = {id : doc, action: "msg", op : { type :"r", text : text, pos : position}};
			console.log('Sending remove message: ' + text + ' on pos: ' + position);
			socket.send(message);
		}

		sendInsertText = function(doc, text, position) {
			message = {id : doc, action: "msg", op : { type :"i", text : text, pos : position}};
			console.log('Sending insert message: ' + text + ' on pos: ' + position);
			socket.send(message);
		}
		
		setAlignment = function(direction) {
			var text = rangy.getSelection(editorIframe);
			var parentStart = text.anchorNode.parentNode;
			var parentEnd = text.focusNode.parentNode;
			var flag = false;
			var isStartStart;
			$(parentStart).siblings().andSelf().each(function() {
				if (flag == false && this === parentStart) {
					flag = true;
					isStartStart = true;
				}
				
				if (flag == false && this === parentEnd) {
					flag = true;
					isStartStart = false;
				}
				
				if (flag) {
					this.style.textAlign = direction;
				}
				
				if (this === parentEnd && isStartStart == true) {
					return false;
				}
				
				if (this === parentStart && isStartStart == false) {
					return false;
				}
			});
		}
		
		formatText = function(tag) {
			var text = rangy.getSelection(editorIframe);
			var start = text.anchorOffset;
			var end = text.focusOffset;
			var startInTag = false;
			var endInTag = false;
			
			if (text.anchorNode == text.focusNode) {
				if (start == end) {
					return;
				} else 
				if (start > end) {
					var cosiek = start;
					start = end;
					end = cosiek;
				}
			}
			
			var parentANode;
			if (text.anchorNode.localName == null) {
				parentANode = text.anchorNode.parentNode;
			} else {
				parentANode = text.anchorNode;
			}
			var startFirst = true;
			
			$(parentANode).siblings().andSelf().each(function() {
				if (this === text.anchorNode) {
					return false;
				}
				if (this === text.focusNode) {
					startFirst = false;
					return false;
				}
			});
			
			if (!startFirst) {
				var tmpNode = text.anchorNode;
				text.anchorNode = text.focusNode;
				text.focusNode = tmpNode;
				var tmp = start;
				start = end;
				end = tmp;
			}
			
			var parentNode = text.focusNode.parentNode;
			if (checkChildes(parentNode, tag)) {
				startInTag = true;
			}
			parentNode = text.focusNode.parentNode;
			
			if (checkChildes(parentNode, tag)) {
				endInTag = true;
			}
			
			if (startInTag) {
				rangy.getSelection(editorIframe).anchorNode.nodeValue = [text.anchorNode.textContent.slice(0, start), '</' + tag + '>', text.anchorNode.textContent.slice(start)].join('');
			} else {
				rangy.getSelection(editorIframe).anchorNode.nodeValue = [text.anchorNode.textContent.slice(0, start), '<' + tag + '>', text.anchorNode.textContent.slice(start)].join('');
			}
			
			if (endInTag) {
				if (text.anchorNode === text.focusNode) {
					rangy.getSelection(editorIframe).focusNode.nodeValue = [text.focusNode.textContent.slice(0, end + 4), '<' + tag + '>', text.focusNode.textContent.slice(end + 4)].join('');
				} else {
					rangy.getSelection(editorIframe).focusNode.nodeValue = [text.focusNode.textContent.slice(0, end), '<' + tag + '>', text.focusNode.textContent.slice(end)].join('');	
				}
			} else {
				if (text.anchorNode === text.focusNode) {
					rangy.getSelection(editorIframe).focusNode.nodeValue = [text.focusNode.textContent.slice(0, end + 3), '</' + tag + '>', text.focusNode.textContent.slice(end + 3)].join('');
				} else {
					rangy.getSelection(editorIframe).focusNode.nodeValue = [text.focusNode.textContent.slice(0, end), '</' + tag + '>', text.focusNode.textContent.slice(end)].join('');	
				}
			}
			
			replaceTags(tag);
		}
		
		checkChildes = function(parentNode, tag) {
			if (parentNode.localName == tag) {
				return true;
			}
			return false;
		}
		
		replaceTags = function(tag) {
			var text = editorBody.innerHTML;
			var regexStart = new RegExp('<' + tag + '>', 'g');
			var regexEnd = new RegExp('</' + tag + '>', 'g');
			var regexAll = new RegExp('(<' + tag + '>|</' + tag + '>)', 'g');
			var startIndex = text.indexOf('&lt;' + tag + '&gt;');
			var endIndex = text.indexOf('&lt;/' + tag + '&gt;');
			if (startIndex == -1) {
				startIndex = text.indexOf('&lt;/' + tag + '&gt;', endIndex + 1);
			}
			if (endIndex == -1) {
				endIndex = text.indexOf('&lt;' + tag + '&gt;', startIndex + 1);
			}
			if (startIndex > endIndex) {
				var tmp = startIndex;
				startIndex = endIndex;
				endIndex = tmp;
			}
			var selectedText = text.substring(startIndex, endIndex + 10);
			var newSelectedText = selectedText;
			newSelectedText = newSelectedText.replace(regexAll, function($1) {
				 return $1 === '<' + tag + '>' ? '</' + tag + '>'  : '<' + tag + '>';
			});
			newSelectedText = newSelectedText.replace('&lt;' + tag + '&gt;', '<' + tag + '>');
			newSelectedText = newSelectedText.replace('&lt;/' + tag + '&gt;', '</' + tag + '>');
			editorBody.innerHTML = editorBody.innerHTML.replace(selectedText, newSelectedText);
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
					//TODO: fix selection ending with the end of line
					//TODO: fix selection of single line
					//TODO: fix selection starting with start of line <- big problem since <p> after selecton dissapear
					var text = bodyBeforeOperation.substring(index, index + changeLength + 7);
					sendRemoveText(documentId, text, index);
					sendInsertText(documentId, '</p><p>', index);
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
					//TODO: fix selection starting with start of line
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
		$('#saveDocumentButton').on('click', function() {
			var name = $('#documentName').val();
			var privateFlag = $('#privateFlag').is(":checked");
			console.log('New document save button clicked. Name: ' + name + ' is private: ' + privateFlag);
			saveDocument(name, '<p><br></p>', privateFlag);
		});
	});

	$('#saveDocument').on('click', function() {
		$('#saveDocumentButton').unbind("click");
		$('#saveDocumentButton').on('click', function() {
			var name = $('#documentName').val();
			var privateFlag = $('#privateFlag').is(":checked");
			console.log('Save document save button clicked. Name: ' + name + ', is private: ' + privateFlag);
			saveDocument(name, editorBody.innerHTML, privateFlag);
		});
	});

	$('#boldText').on('click', function() {
		formatText('b');
	});
	
	$('#italicText').on('click', function() {
		formatText('i');
	});
	
	$('#underlineText').on('click', function() {
		formatText('u');
	});
	
	$('#alignLeft').on('click', function() {
		setAlignment('left');
	});
	
	$('#alignCenter').on('click', function() {
		setAlignment('center');
	});
	
	$('#alignJustify').on('click', function() {
		setAlignment('justify');
	});
	
	$('#alignRight').on('click', function() {
		setAlignment('right');
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


});
