var CLIENT_ID = '1046449573186-s5k9dtkn2obp6nojh7lruq8gp56cheu1.apps.googleusercontent.com';
var SCOPES = 'https://www.googleapis.com/auth/drive';

var pickerApiLoaded = false;
var oauthToken;

function onPickerApiLoad() {
  pickerApiLoaded = true;
}

var googleDocumentName = undefined;

/**
 * Called when the client library is loaded to start the auth flow.
 */
function handleClientLoad() {
  console.log("Loading google client libraries.");
  window.setTimeout(checkAuth, 1);
  gapi.load('picker', {'callback': onPickerApiLoad});
}

/**
 * Check if the current user has authorized the application.
 */
function checkAuth() {
  gapi.auth.authorize(
      {'client_id': CLIENT_ID, 'scope': SCOPES, 'immediate': true},
      handleAuthResult);
}

/**
 * Called when authorization server replies.
 *
 * @param {Object} authResult Authorization result.
 */
function handleAuthResult(authResult) {
  var authButton = document.getElementById('authorizeGDrive');
  var filePicker = document.getElementById('exploreGDrive');
  var saveGDrive = document.getElementById('saveGDrive');
  authButton.style.display = 'none';
  $('.authorizedMethods').css('display', 'none');
  if (authResult && !authResult.error) {
    // Access token has been successfully retrieved, requests can be sent to the API.
    $('.authorizedMethods').css('display', 'block');
    filePicker.onclick = createPicker;
    saveGDrive.onclick = function() {
      if (googleDocumentName !== undefined) {
        $('#gDriveDocName').val(googleDocumentName);
      }
      $('#saveGDriveDocButton').unbind("click");
      $('#saveGDriveDocButton').on('click', function() {
        var name = $('#gDriveDocName').val();
        console.log('Save document on Google Drive save button clicked. Name: ' + name);
        console.log('Loading iframe editorContent');
        editorIframe = document.getElementById('editorContent');
        editorIframe = (editorIframe.contentWindow) ? editorIframe.contentWindow : (editorIframe.contentDocument.document) ? editorIframe.contentDocument.document : editorIframe.contentDocument;
        editorDocument = editorIframe.document;
        editorBody = editorDocument.getElementById('editorBody');
        console.log('Iframe editorContent successfully loaded');
        saveDocumentOnGDrive(name, editorBody.innerHTML);
      });
      $('#saveGDriveWindowTrigger').trigger('click');
    }
  } else {
    // No access token could be retrieved, show the button to start the authorization flow.
    authButton.style.display = 'block';
    authButton.onclick = function() {
        gapi.auth.authorize(
            {'client_id': CLIENT_ID, 'scope': SCOPES, 'immediate': false},
            handleAuthResult);
    };
  }

  if (authResult && !authResult.error) {
    oauthToken = authResult.access_token;
  }
}

// Create and render a Picker object for searching images.
function createPicker() {
  if (pickerApiLoaded && oauthToken) {
    var view = new google.picker.View(google.picker.ViewId.DOCUMENTS);
    var picker = new google.picker.PickerBuilder()
        .enableFeature(google.picker.Feature.NAV_HIDDEN)
        .enableFeature(google.picker.Feature.MINE_ONLY)
        .setOAuthToken(oauthToken)
        .addView(view)
        .addView(new google.picker.DocsUploadView())
        .setCallback(pickerCallback)
        .build();
     picker.setVisible(true);
  }
}

function loadContent(content, googleName) {
  $('#closeWaitPageTrigger').trigger('click');
  if (content == null) {
    alert('Problem while loading document occured.');
    $('#showFileListTrigger').trigger('click');
    return;
  }
  if (googleName !== undefined) {
    googleDocumentName = googleName;
  }
  console.log('Loading iframe editorContent');
  editorIframe = document.getElementById('editorContent');
  editorIframe = (editorIframe.contentWindow) ? editorIframe.contentWindow : (editorIframe.contentDocument.document) ? editorIframe.contentDocument.document : editorIframe.contentDocument;
  editorDocument = editorIframe.document;
  editorBody = editorDocument.getElementById('editorBody');
  console.log('Iframe editorContent successfully loaded');
  editorBody.innerHTML = '<p>' + content + '</p>';
  $('#documentNameHeader').text(googleName);
  var r = confirm("Do you want to save loaded document?");
   if (r == true) {
    $('#documentName').val(googleName);
    $('#saveDocumentButton').unbind("click");
    $('#saveDocumentButton').on('click', function() {
      var name = $('#documentName').val();
      var privateFlag = $('#privateFlag').is(":checked");
      console.log('Save document save button clicked. Name: ' + name + ', is private: ' + privateFlag);
      saveDocument(name, editorBody.innerHTML, privateFlag);
    });
    $('#showFileNameModalTrigger').trigger('click');
  } else {
    alert("All your changes will be lost after application close.");
    offline();
  } 
}

// A simple callback implementation.
function pickerCallback(data) {
  if (data.action == google.picker.Action.PICKED) {
    $('#fileListModal').trigger('reveal:close'); 
    $('#showWaitPageTrigger').trigger('click');
    gapi.client.load('drive', 'v2', function() {
      var request = gapi.client.drive.files.get({
        'fileId': data.docs[0].id
      });
      request.execute(function(resp) {
        name = data.docs[0].name;
        downloadFile(resp, loadContent);
        console.log('The user selected: ' + name);
      });
    });
  }
}

/**
 * Download a file's content.
 *
 * @param {File} file Drive File instance.
 * @param {Function} callback Function to call when the request is complete.
 */
function downloadFile(file, callback) {
  if (file.downloadUrl) {
    var accessToken = gapi.auth.getToken().access_token;
    var xhr = new XMLHttpRequest();
    //xhr.open('GET', file.downloadUrl);
    xhr.open('GET', 'https://www.googleapis.com/drive/v2/files/' + file.id + '?alt=media')
    xhr.setRequestHeader('Authorization', 'Bearer ' + accessToken);
    xhr.onload = function() {
      callback(xhr.responseText, file.title);
    };
    xhr.onerror = function() {
      callback(null, null);
    };
    xhr.send();

  } else {
    callback(null);
  }
}

function saveDocumentOnGDrive(name, content) {
  gapi.client.load('drive', 'v2', function() {
    console.log('Saving document on Google Drive with name: ' + name);
    file = new File([content], name, {'type': 'text/plain'});
    insertFile(file);        
  });
}

/**
  * Insert new file.
  *
  * @param {File} fileData File object to read data from.
  * @param {Function} callback Function to call when the request is complete.
  */
function insertFile(fileData, callback) {
  const boundary = '-------314159265358979323846';
  const delimiter = "\r\n--" + boundary + "\r\n";
  const close_delim = "\r\n--" + boundary + "--";

  var reader = new FileReader();
  reader.readAsBinaryString(fileData);
  reader.onload = function(e) {
    var contentType = fileData.type || 'application/octet-stream';
    var metadata = {
      'title': fileData.name,
      'mimeType': contentType
    };

    var base64Data = btoa(reader.result);
    var multipartRequestBody =
        delimiter +
        'Content-Type: application/json\r\n\r\n' +
        JSON.stringify(metadata) +
        delimiter +
        'Content-Type: ' + contentType + '\r\n' +
        'Content-Transfer-Encoding: base64\r\n' +
        '\r\n' +
        base64Data +
        close_delim;

    var request = gapi.client.request({
        'path': '/upload/drive/v2/files',
        'method': 'POST',
        'params': {'uploadType': 'multipart'},
        'headers': {
          'Content-Type': 'multipart/mixed; boundary="' + boundary + '"'
        },
        'body': multipartRequestBody});
    if (!callback) {
      callback = function(file) {
        console.log(file);
        $('#closeFileNameTrigger').trigger('click');
        $('#documentNameHeader').text(fileData.name);
      };
    }
    request.execute(callback);
  }
}