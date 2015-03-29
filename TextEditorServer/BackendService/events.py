from django_socketio import events
from mongoengine.django.shortcuts import get_document_or_404
from db_manager import *
from models import Document

INSERT = 'i'
REMOVE = 'r'
ID = '551347a1489f70f38ddb5126'


@events.on_subscribe(channel="^document-")
def connect(request, socket, context, channel):
	document = get_document_or_404(Document, id=ID)
	message = {}
	message["text"] = document["text"]
	message["action"] = "doc"
	socket.send(message)

@events.on_message(channel="^document-")
def message(request, socket, context, message):
	document = get_document_or_404(Document, id= ID)
	operation = message["op"]
	if operation["type"] == INSERT:
		insert_text(document, operation["text"], operation["pos"])
	elif operation["type"] == REMOVE:
		remove_text(document, operation["text"], operation["pos"])

	message["action"] = "msg"
	print 'dupa';
	print message;
	print 'dupa';
	socket.broadcast_channel(message)


