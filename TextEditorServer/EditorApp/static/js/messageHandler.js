/**
 *	Handlers for messages recieved from server.
 */
$(document).ready( function() {

	$('iframe#editorContent').load(function() {

		var re = /\<span class=\"rangySelectionBoundary.*?\<\/span\>/g;

		socket.on('message', function(data) {
			console.log('Recieved message');
			console.log(data);
			// recieved full document from server
			if (data.action === 'doc') {
				console.log('No document replace: ' + noDocumentReplace);
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
			// recieved operation on text from another user
			} else if (data.action === 'msg') {
				operation = data.op;
				text = operation.text;
				pos = operation.pos;
				var savedSel = rangy.saveSelection(editorIframe);
				var match;
				while ((match = re.exec(editorBody.innerHTML)) !== null) {
					if (pos > match.index) {
						console.log("Moving pos from " + pos + " to " + pos + match[0].length);
						pos += match[0].length;
					}
				}
				var savedSelActiveElement = document.activeElement;
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
				console.log('Restoring selection!');
				rangy.restoreSelection(savedSel, true);
				window.setTimeout(function() {
                    if (savedSelActiveElement && typeof savedSelActiveElement.focus != "undefined") {
                        savedSelActiveElement.focus();
                    }
                }, 1);
				bodyBeforeOperation = editorBody.innerHTML;
			// recieved list of available documents
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
			// callback after document is saved in database
			} else if (data.action === 'save') {
				console.log(data);
				prepareDocument(documentId, data.id);
			} 
		});
	});

});