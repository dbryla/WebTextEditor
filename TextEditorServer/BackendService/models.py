from django.db import models
import mongoengine

class Document(mongoengine.Document):
	id = mongoengine.fields.ObjectIdField(db_field='_id')
	name = mongoengine.fields.StringField(required=True)
	last_change = mongoengine.fields.DateTimeField()
	text = mongoengine.fields.StringField()
