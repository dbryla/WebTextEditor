var CLIENT_ID = '1046449573186-s5k9dtkn2obp6nojh7lruq8gp56cheu1.apps.googleusercontent.com';
var SCOPES = 'https://www.googleapis.com/auth/drive';

var pickerApiLoaded = false;
var oauthToken;

function onPickerApiLoad() {
  pickerApiLoaded = true;
}
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
  authButton.style.display = 'none';
  filePicker.style.display = 'none';
  if (authResult && !authResult.error) {
    // Access token has been successfully retrieved, requests can be sent to the API.
    filePicker.style.display = 'block';
    filePicker.onclick = createPicker;
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

// A simple callback implementation.
function pickerCallback(data) {
  if (data.action == google.picker.Action.PICKED) {
    name = data.docs[0].name;
    console.log('The user selected: ' + name);
  }
}