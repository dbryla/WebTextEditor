import datetime
import logging
from models import Document

logger = logging.getLogger('db_manager')

def insert_text(document, text, position):
	logger.info("Inserting '" + text + "' at position " + str(position) + " in " + document.name)
	document["text"] = document["text"][:position] + text + document["text"][position:]
	document["last_change"] = datetime.datetime.now()
	logger.info("After editing text: " + document["text"])
	document.save()
	logger.info("Document saved")

def remove_text(document, text, position):
	logger.info("Removing '" + text + "' at position " + str(position) + " in " + document.name)
	document["text"] = document["text"][:position] + document["text"][position + len(text):]
	document["last_change"] = datetime.datetime.now()
	logger.info("After removing text: " + document["text"])
	document.save()
	logger.info("Document saved")

def create_document(name, text, priv=False):
	logger.info("Creating document " + name + ' with text ' + text + ' in private mode: ' + str(priv))
	document = Document(name = name)
	document.last_change = datetime.datetime.now()
	document.text = text
	document.priv = priv
	document.save()
	logger.info("Document created with id: " + str(document.id))
	return document.id