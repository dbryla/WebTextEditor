/**
 *	Functions responsible for performing text formatting and propagating those changes in document to other users via socket.
 */
$(document).ready( function() {

	$('iframe#editorContent').load(function() {

		/**
		 *	Creates list at cursor position 
		 */
		
		createList = function() {
			var text = rangy.getSelection(editorIframe);
			var textNode = text.focusNode;
			var offset = text.focusOffset;
			if (textNode.textContent === "") {
				text.focusNode.textContent = '<ul><li> </li></ul>';
			} else {
				text.focusNode.textContent = [text.focusNode.textContent.slice(0, offset), '<ul><li> </li></ul>', text.focusNode.textContent.slice(offset)].join('');
			}
			replaceTags('ul');
			replaceTags('li');
		}
		
		
		/**
		 *	Surrounds text (selected by user) with tags (<tag>text</tag>) 
		 */
		
		formatText = function(tag) {
			var text = rangy.getSelection(editorIframe);
			var start = text.anchorOffset;
			var end = text.focusOffset;
			var startInTag = false;
			var endInTag = false;
			var bodyBeforeTagging = editorBody.innerHTML;
			console.log('Before tagging: ' + bodyBeforeTagging);

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
			
			var parentNode = text.anchorNode.parentNode;
			if (checkChildes(parentNode, tag)) {
				startInTag = true;
			}

			parentNode = text.focusNode.parentNode;
			
			if (checkChildes(parentNode, tag)) {
				endInTag = true;
			}
			
			if (startInTag) {
				rangy.getSelection(editorIframe).anchorNode.textContent = [text.anchorNode.textContent.slice(0, start), '</' + tag + '>', text.anchorNode.textContent.slice(start)].join('');
			} else {
				rangy.getSelection(editorIframe).anchorNode.textContent = [text.anchorNode.textContent.slice(0, start), '<' + tag + '>', text.anchorNode.textContent.slice(start)].join('');
			}
			
			if (endInTag) {
				if (text.anchorNode === text.focusNode) {
					rangy.getSelection(editorIframe).focusNode.textContent = [text.focusNode.textContent.slice(0, end + 4), '<' + tag + '>', text.focusNode.textContent.slice(end + 4)].join('');
				} else {
					rangy.getSelection(editorIframe).focusNode.textContent = [text.focusNode.textContent.slice(0, end), '<' + tag + '>', text.focusNode.textContent.slice(end)].join('');	
				}
			} else {
				if (text.anchorNode === text.focusNode) {
					rangy.getSelection(editorIframe).focusNode.textContent = [text.focusNode.textContent.slice(0, end + 3), '</' + tag + '>', text.focusNode.textContent.slice(end + 3)].join('');
				} else {
					rangy.getSelection(editorIframe).focusNode.textContent = [text.focusNode.textContent.slice(0, end), '</' + tag + '>', text.focusNode.textContent.slice(end)].join('');	
				}
			}
			replaceTags(tag);
			var flag = -1;
			while (flag == 1) {
				flag = clearEmptyTags(tag);
			}
			
			var bodyAfterTagging = editorBody.innerHTML;
			console.log('After tagging: ' + bodyAfterTagging);
			propagateChanges(bodyBeforeTagging, bodyAfterTagging, tag);
			bodyBeforeOperation = bodyAfterTagging;
		}

		propagateChanges = function(bodyBefore, bodyAfter, tag) {
			//temporary solution
			var message = {id : documentId, action : 'doc', text : editorBody.innerHTML, override_warning : 'false'};
			socket.send(message);
		}
		
		/**
		 *	Removes empty tags from HTML content of document (e.g. <b></b>) which happens when user formats selected text and then unformats it.
		 */
		clearEmptyTags = function(tag) {
			console.log('Removing empty tags: ' + tag + 'from: ' + editorBody.innerHTML);
			var regex = new RegExp('<' + tag + '><\/' + tag + '>', 'g');
			editorBody.innerHTML = editorBody.innerHTML.replace(regex, '');
			console.log('After removing: ' + editorBody.innerHTML);
		}
		
		checkChildren = function(parentNode, tag) {
			if (parentNode.localName == tag) {
				return true;
			}
			return false;
		}

		/**
		 *	Replaces escaped tags (e.g. &lt;b&gt;) with proper HTML tag values (e.g. <b>)
		 */
		replaceTags = function(tag) {
			console.log('Replacing Tags');
			var text = editorBody.innerHTML;
			var toReplaceOpeningTag = '&lt;' + tag + '&gt;';
			var toReplaceClosingTag = '&lt;/' + tag + '&gt;';
			var openingTag = '<' + tag + '>';
			var closingTag = '</' + tag + '>';
			var regexStart = new RegExp(openingTag, 'g');
			var regexEnd = new RegExp(closingTag, 'g');
			var regexAll = new RegExp('(<' + tag + '>|</' + tag + '>)', 'g');
			var startIndex = text.indexOf(toReplaceOpeningTag);
			var endIndex = text.indexOf(toReplaceClosingTag);
			if (startIndex == -1) {
				startIndex = text.indexOf(toReplaceClosingTag, endIndex + 1);
				toReplaceOpeningTag = toReplaceClosingTag;
				openingTag = closingTag;
			}
			if (endIndex == -1) {
				endIndex = text.indexOf(toReplaceOpeningTag, startIndex + 1);
				toReplaceClosingTag = toReplaceOpeningTag;
				closingTag = openingTag;
			}
			if (startIndex > endIndex) {
				var tmp = startIndex;
				startIndex = endIndex;
				endIndex = tmp;
			}
			var offset = 9 + tag.length;
			var selectedText = text.substring(startIndex, endIndex + offset);
			var newSelectedText = selectedText;
			newSelectedText = newSelectedText.replace(regexAll, function($1) {
			     return $1 === '<' + tag + '>' ? '</' + tag + '>' : '<' + tag + '>';
			});
			newSelectedText = newSelectedText.replace(toReplaceOpeningTag, openingTag);
			newSelectedText = newSelectedText.replace(toReplaceClosingTag, closingTag);
			
			editorBody.innerHTML = editorBody.innerHTML.replace(selectedText, newSelectedText);
		}

		/**
		 *	Adds proper class to <p> elements (selected by user) that affects text alignment.
		 */
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
			propagateChanges();
		}
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
	
	$('#alignRight').on('click', function() {
		setAlignment('right');
	});
	
	$('#list').on('click', function() {
		createList();
	});

});