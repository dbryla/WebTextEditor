from django_socketio import events
from mongoengine.django.shortcuts import get_document_or_404
from db_manager import *
from models import Document
import logging

logger = logging.getLogger('events')

INSERT = 'i'
REMOVE = 'r'
ID = '551347a1489f70f38ddb5126'


@events.on_subscribe(channel="^document-")
def connect(request, socket, context, channel):
	logger.info("Connected to channel: " + str(channel))
	document = get_document_or_404(Document, id=ID)
	logger.info("Document content: " + document["text"])
	message = {}
	message["text"] = document["text"]
	message["action"] = "doc"
	socket.send(message)

@events.on_message(channel="^document-")
def message(request, socket, context, message):
	logger.info("Received message: " + str(message))
	document = get_document_or_404(Document, id= ID)
	operation = message["op"]
	if operation["type"] == INSERT:
		insert_text(document, operation["text"], operation["pos"])
	elif operation["type"] == REMOVE:
		remove_text(document, operation["text"], operation["pos"])

	message["action"] = "msg"
	socket.broadcast_channel(message)

@events.on_connect
def socket_connect(request, socket, context):
	logger.info("Connection established to socket")

@events.on_unsubscribe
def unsubscribe(request, socket, context, channel):
	logger.info("Unsubscribe from channel " + channel)

@events.on_error
def error(request, socket, context, exception):
	logger.error("Error from socket: " + exception)

@events.on_disconnect
def disconnect(request, socket, context):
	logger.info("Disconnected")

@events.on_finish
def finish(request, socket, context):
	logger.info("Finished")
