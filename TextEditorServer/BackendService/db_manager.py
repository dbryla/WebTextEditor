import time

def insert_text(document, text, position):
	document["text"] = document["text"][:position] + text + document["text"][position:]
	document["last_change"] = time.strftime("%Y-%m-%dT%X")
	document.save()

def remove_text(document, text, position):
	document["text"] = document["text"][:position] + document["text"][position + len(text):]
	document["last_change"] = time.strftime("%Y-%m-%dT%X")
	document.save()
