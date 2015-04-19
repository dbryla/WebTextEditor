from django_socketio import events
from mongoengine.django.shortcuts import get_document_or_404, get_list_or_404
from db_manager import *
from models import Document
import logging
import datetime

logger = logging.getLogger('events')

INSERT = 'i'
REMOVE = 'r'

@events.on_subscribe(channel="^")
def connect(request, socket, context, channel):
	logger.info("Connected to channel: " + channel)
	document = get_document_or_404(Document, id = channel)
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

def handle_list(message):
	documents_list = get_list_or_404(Document)
	message["files"] = []
	for document in documents_list:
		element = {}
		element["id"] = str(document["id"])
		element["name"] = document["name"]
		message["files"].append(element)

def handle_create_document(message, text):
	document = Document(name = message["name"])
	document.last_change = datetime.datetime.now()
	document.text = text
	document.save()
	message["id"] = str(document.id)

@events.on_message(channel="^")
def message(request, socket, context, message):
	logger.info("Received message: " + str(message))
	if message["action"] == "msg":
		handle_msg(message["op"], message["id"])
		socket.broadcast_channel(message)
	elif message["action"] == "list":
		handle_list(message)
		socket.send(message)
	elif message["action"] == "new":
		handle_create_document(message, "<p></p>")
		socket.send(message)
	elif message["action"] == "save":
		handle_create_document(message, message["text"])
		message["text"] = ""
		socket.send(message)
		

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
