var editorIframe;
var document2;
var document2body;

function onEditorLoad() {
	editorIframe = document.getElementById('editorContent');
	editorIframe = (editorIframe.contentWindow) ? editorIframe.contentWindow : (editorIframe.contentDocument.document) ? editorIframe.contentDocument.document : editorIframe.contentDocument;

	document2 = editorIframe.document;
	var div = document2.createElement('p');
	div.innerHTML = 'Here you can put your text :)'
	document2body = document2.getElementById('editorBody');
	//document2body.appendChild(div);
	document2body.innerHTML = '<p></br></p>';
}

function onKeyHandler(event) {
	var keyCode = event.keyCode;
		
	switch(keyCode) {
		case (8) : {
			
			if ( parent.document2body.innerHTML === '<p><br></p>' ) {
				event.preventDefault();
			}
		}
	}

	if (parent.document2body.innerHTML === '' || parent.document2body.innerHTML === '<br>' ) {
		parent.document2body.innerHTML = '<p></br></p>';
	}
}