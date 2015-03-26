# -*- coding: UTF-8 -*-
from django.test import TestCase
from mongoengine import *
from models import Document as Doc
from mongoengine.django.shortcuts import get_document_or_404
from mongoengine.context_managers import switch_db
from django.http import Http404
from bson.errors import InvalidId

import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_ALIAS = 'testdb'
SAMPLE_TEXT = 'Użytkownik może wyświetlić i modyfikować dokument z jego zawartością.'

class TestEnv(TestCase):

	def testBaseDir(self):
		self.assertTrue(BASE_DIR.endswith('TextEditorServer'))
                                                      
class TestDB(TestCase):

	def setUp(self):
		register_connection(DB_ALIAS, 'test')

	def testGetDocumentOr404(self):
		documentName = 'TestDocument'
		with switch_db(Doc, DB_ALIAS) as Docx:
			Docx(name=documentName, text=SAMPLE_TEXT).save()
			self.assertTrue(get_document_or_404(Doc, name=documentName).name == documentName)
		with self.assertRaisesMessage(Http404, 'No Document matches the given query.'):
			get_document_or_404(Doc, name='not_exisitng')

	def testDocumentModel(self):
		with switch_db(Doc, DB_ALIAS) as Docx:
			with self.assertRaisesMessage(ValidationError, '(Document:None) (Field is required: [\'name\'])'):
				Docx(text=SAMPLE_TEXT).save()
			with self.assertRaisesMessage(ValidationError, '(Document:None) (StringField only accepts string values: [\'name\'])'):
				Docx(name=1).save()
			with self.assertRaisesMessage(InvalidId, '\'piec\' is not a valid ObjectId, it must be a 12-byte input of type \'str\' or a 24-character hex string'):
				Docx(id='piec', name='test').save()

	#test global document from story 1
	def testGlobalDocument(self):
		self.assertTrue(get_document_or_404(Doc, id='551347a1489f70f38ddb5126').name == 'global')

	def tearDown(self):
		with switch_db(Doc, DB_ALIAS) as Docx:
			Docx.drop_collection()

class TestDBManager(TestCase):

	def testInsertText(self):
		pass

	def testRemoveText(self):
		pass