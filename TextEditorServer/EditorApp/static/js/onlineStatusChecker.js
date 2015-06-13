/**
 *	Functions responsible for detecting changes in connection to the server and providing mechanism of reconnection to the document
 *	a user was connected before losing connection.
 */
$(document).ready( function() {
	Offline.options = {checks: {xhr: {url: '/login'}}};

	Offline.on('down', function () {
        console.log('Going offline!');
        console.log(socket);
        alert('You are going into offline mode. Your changes to the document will be propagated once you go online!');
        offline();
        noDocumentReplace = true;
    });

    Offline.on('up', function () {
        console.log('Going back online!!');
        console.log(socket);
        alert('You are going back online. Your changes will now be propagated to other users!');
        offlineMode = false;
        socket.connect('http://127.0.0.1');
		if (documentId === undefined) {
			socket.subscribe('list');
		} else {
			socket.subscribe('id-' + documentId);
		}
    });

    online = function() {
		offlineMode = false;
		console.log(documentId);
		if (documentId === undefined) {
			socket.subscribe('list');
		} else {
			socket.subscribe('id-' + documentId);
		}
	}

	/**
	 *	Function imitating offline mode - called only when google drive document is loaded to prevent from sending messages
	 *	to socket with data about document changes until the document is saved and online function is called.
	 */
	offline = function() {
		console.log(documentId);
		console.log('Unsubscribing from ' + documentId);
		socket.unsubscribe('id-' + documentId);
		documentId = undefined;
		offlineMode = true;
	}
});