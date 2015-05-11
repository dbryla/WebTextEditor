from django_socketio import events
from mongoengine.django.shortcuts import get_document_or_404, get_list_or_404
from db_manager import *
from models import Document
import logging
import datetime

logger = logging.getLogger('events')

INSERT = 'i'
REMOVE = 'r'

@events.on_subscribe(channel="list")
def connect(request, socket, context, channel):
	logger.info("Subscribed to channel: " + channel
		+" with session id: " + str(socket.socket.session.session_id))
	message = {}
	message["action"] = "list"
	handle_list(message, request)
	socket.send(message)

@events.on_subscribe(channel="^id-")
def connect(request, socket, context, channel):
	logger.info("Subscribed to channel: " + channel 
		+ " with session id: " + str(socket.socket.session.session_id))
	document = get_document_or_404(Document, id = channel[3:])
	if document["text"] != None:
		logger.info("Document content: " + document["text"])
	message = {}
	message["text"] = document["text"]
	message["action"] = "doc"
	socket.send(message)


def handle_msg(operation, document_id):
	document = get_document_or_404(Document, id = document_id)
	if operation["type"] == INSERT:
		insert_text(document, operation["text"], operation["pos"])
	elif operation["type"] == REMOVE:
		remove_text(document, operation["text"], operation["pos"])

def get_user_permissions(request):
	user_permissions = []
	if not request.user.is_anonymous():
		for permission in request.user.user_permissions:
			user_permissions.append(permission._DBRef__id)
	return user_permissions

def handle_list(message, request):
	documents_list = get_list_or_404(Document)
	message["files"] = []
	user_permissions = get_user_permissions(request)
	for document in documents_list:
		if document['priv'] != True or document.id in user_permissions:
			element = {}
			element["id"] = str(document["id"])
			element["name"] = document["name"]
			message["files"].append(element)

def handle_create_document(message, request):
	id = create_document(request, message['name'], message["text"], message['priv'])
	message["id"] = str(id)

@events.on_message(channel="^")
def message(request, socket, context, message):
	logger.info("Received message: " + str(message))
	if message["action"] == "msg":
		handle_msg(message["op"], message["id"])
		socket.broadcast_channel(message)
	elif message["action"] == "list":
		handle_list(message, request)
		socket.send(message)
	elif message["action"] == "save":
		handle_create_document(message, request)
		message["text"] = ""
		socket.send(message)
	elif message["action"] == "doc":
		document = get_document_or_404(Document, id = message["id"])
		update_document(document, message["text"])
		if message["override_warning"] is None:
			message["override_warning"] = "true"
		socket.broadcast_channel(message)
		

@events.on_connect
def socket_connect(request, socket, context):
	logger.info("Connection established to socket with session id: " + str(socket.socket.session.session_id))

@events.on_unsubscribe(channel="^")
def unsubscribe(request, socket, context, channel):
	logger.info("Unsubscribe from channel " + channel + " with session id: " + str(socket.socket.session.session_id))

@events.on_error
def error(request, socket, context, exception):
	logger.error("Error from socket with session id: " + str(socket.socket.session.session_id) 
		+ " exception: " + exception)

@events.on_disconnect
def disconnect(request, socket, context):
	logger.info("Disconnected from socket with session id: " + str(socket.socket.session.session_id))

@events.on_finish
def finish(request, socket, context):
	logger.info("Finished with session id: " + str(socket.socket.session.session_id))
