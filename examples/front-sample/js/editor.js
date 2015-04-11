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

		}
		default : {
			if (parent.document2body.innerHTML === '<br>') {
				parent.document2body.innerHTML = '<p></p>';
			}
		}
	}
}

function insertAtCaret(areaId,text) {
    var txtarea = document2body;
    var img = document2.createElement('img');
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

function selectDocument(e) {
	var currentRow = $(e).closest('tr');
	var selectedFileName = currentRow.get(0).cells.item(0).getAttribute('value');
	if (selectedFileName != null) {
		document.getElementById('fileName').value = selectedFileName;
	}
	$('#fileListModal').trigger('reveal:close');

}