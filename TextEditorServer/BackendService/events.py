from django_socketio import events
from mongoengine.django.shortcuts import get_document_or_404
from db_manager import *

INSERT = 'i'
REMOVE = 'r'

@events.on_message(channel="^document-")
def message(request, socket, context, message):
	#for now it should be hardcoded for id='551347a1489f70f38ddb5126' or name='global'
	document = get_document_or_404(Document, id=message["id"])
	operation = message["op"]
	if operation["type"] == INSERT:
		insert_text(document, operation["text"], operation["pos"])
	elif operation["type"] == REMOVE:
		remove_text(document, operation["text"], operation["pos"])

	socket.broadcast_channel(message)

