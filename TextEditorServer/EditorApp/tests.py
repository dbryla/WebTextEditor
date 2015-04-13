# -*- coding: UTF-8 -*-
from django.test import TestCase
from mongoengine import *
from models import Document as Doc
from mongoengine.django.shortcuts import get_document_or_404
from mongoengine.context_managers import switch_db
from django.http import Http404
from bson.errors import InvalidId
from db_manager import *
from events import *
import datetime
import os
from selenium import selenium
from selenium import webdriver
import unittest, time

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_ALIAS = 'testdb'
SAMPLE_TEXT = u'Użytkownik może wyświetlić i modyfikować dokument z jego zawartością.'
DOC_NAME = 'TestDocument'

class TestEnv(TestCase):

	def testBaseDir(self):
		self.assertTrue(BASE_DIR.endswith('TextEditorServer'))

class TestDB(TestCase):

	def setUp(self):
		register_connection(DB_ALIAS, 'test')

	def testGetDocumentOr404(self):
		with switch_db(Doc, DB_ALIAS) as Docx:
			Docx(name=DOC_NAME, text=SAMPLE_TEXT).save()
			self.assertTrue(get_document_or_404(Doc, name=DOC_NAME).name == DOC_NAME)
		with self.assertRaisesMessage(Http404, 'No Document matches the given query.'):
			get_document_or_404(Doc, name='not_exisitng')

	def testDocumentModel(self):
		with switch_db(Doc, DB_ALIAS) as Docx:
			with self.assertRaisesMessage(ValidationError, '(Document:None) (Field is required: [\'name\'])'):
				Docx(text=SAMPLE_TEXT).save()
			with self.assertRaisesMessage(ValidationError, '(Document:None) (StringField only accepts string values: [\'name\'])'):
				Docx(name=1).save()
			with self.assertRaisesMessage(InvalidId, '\'piec\' is not a valid ObjectId, it must be a 12-byte input of type \'str\' or a 24-character hex string'):
				Docx(id='piec', name='DOC_NAME').save()

	#test global document from story 1
	def testGlobalDocument(self):
		self.assertTrue(get_document_or_404(Doc, id='551347a1489f70f38ddb5126').name == 'global')

	def tearDown(self):
		with switch_db(Doc, DB_ALIAS) as Docx:
			Docx.drop_collection()

class TestDBManager(TestCase):

	def setUp(self):
		register_connection(DB_ALIAS, 'test')

	def testInsertText(self):
		with switch_db(Doc, DB_ALIAS) as Docx:
			doc = Docx(name=DOC_NAME, last_change=datetime.datetime.now(), text=SAMPLE_TEXT).save()
			creation_date = doc.last_change
			insert_text(doc, 'A', 3)
			doc = Docx.objects(name=DOC_NAME)[0]
			self.assertTrue(creation_date < doc.last_change)
			self.assertTrue(doc.text[3] == 'A')
			Docx.drop_collection()
			doc = Docx(name=DOC_NAME, text="").save()
			insert_text(doc, 'k', 0)
			insert_text(doc, 'o', 0)
			self.assertTrue(Docx.objects(name=DOC_NAME)[0].text == 'ok')

	def testRemoveText(self):
		with switch_db(Doc, DB_ALIAS) as Docx:
			doc = Docx(name=DOC_NAME, last_change=datetime.datetime.now(), text=SAMPLE_TEXT).save()
			creation_date = doc.last_change
			remove_text(doc, 'Uzytkownik', 0)
			doc = Docx.objects(name=DOC_NAME)[0]
			self.assertTrue(creation_date < doc.last_change)
			self.assertTrue(doc.text[0] == ' ')
			Docx.drop_collection()
			doc = Docx(name=DOC_NAME, text="ok").save()
			remove_text(doc, 'o', 0)
			remove_text(doc, 'k', 0)
			self.assertTrue(Docx.objects(name=DOC_NAME)[0].text == '')

	def testPolishCharacters(self):
		with switch_db(Doc, DB_ALIAS) as Docx:
			doc = Docx(name=DOC_NAME, last_change=datetime.datetime.now(), text=SAMPLE_TEXT).save()
			creation_date = doc.last_change
			remove_text(doc, u'Użytkownik', 0)
			doc = Docx.objects(name=DOC_NAME)[0]
			self.assertTrue(doc.text[0] == ' ')

	def tearDown(self):
		with switch_db(Doc, DB_ALIAS) as Docx:
			Docx.drop_collection()

class TestEvents(TestCase):

	def setUp(self):
		register_connection(DB_ALIAS, 'test')

	def testHandleMsg(self):
		with switch_db(Doc, DB_ALIAS) as Docx:
			doc = Docx(name=DOC_NAME, last_change=datetime.datetime.now(), text=SAMPLE_TEXT).save()
			handle_msg({'type' : 'i', 'pos' : 0, 'text': 'ala'}, doc['id'])
			doc = Docx.objects(name=DOC_NAME)[0]
			self.assertTrue(doc.text[:3] == 'ala')
			Docx.drop_collection()
			doc = Docx(name=DOC_NAME, last_change=datetime.datetime.now(), text=SAMPLE_TEXT).save()
			handle_msg({'type' : 'r', 'pos' : 0, 'text': u'Użytkownik'}, doc['id'])
			doc = Docx.objects(name=DOC_NAME)[0]
			print doc.text[0]
			self.assertTrue(doc.text[0] == ' ')
		with self.assertRaisesMessage(Http404, 'No Document matches the given query.'):
			handle_msg({}, 'not_exisitng')

	def testHandleList(self):
		message = {}
		handle_list(message)
		self.assertTrue(len(message['files']), 0)
		with switch_db(Doc, DB_ALIAS) as Docx:
			doc = Docx(name=DOC_NAME, last_change=datetime.datetime.now(), text=SAMPLE_TEXT).save()
			handle_list(message)
			self.assertTrue(len(message['files']), 1)
			doc = Docx(name=DOC_NAME + '1', last_change=datetime.datetime.now(), text=SAMPLE_TEXT).save()
			self.assertTrue(len(message['files']), 2)

	def tearDown(self):
		with switch_db(Doc, DB_ALIAS) as Docx:
			Docx.drop_collection()

class TestEditorContent(unittest.TestCase):

	def setUp(self):
		self.driver = webdriver.Firefox()
		self.driver.implicitly_wait(30)
		self.base_url = "http://localhost:8000/"
		self.verificationErrors = []
		self.accept_next_alert = True

	def testRead(self):
		driver = self.driver
		driver.get(self.base_url)
		driver.switch_to_frame("editorContent")
		time.sleep(5)
		content = driver.find_element_by_css_selector("#editorBody")
		try: self.assertEqual("Lorem ipsum.", content.text)
		except AssertionError as e: self.verificationErrors.append(str(e))

	def testWrite(self):
		driver = self.driver
		driver.get(self.base_url)
		driver.switch_to_frame("editorContent")
		time.sleep(5)
		content = driver.find_element_by_css_selector("#editorBody")
		content.click()
		content.clear()
		SAMPLE_TEXT = 'Sample text.'
		content.send_keys(SAMPLE_TEXT)
		try: self.assertEqual(SAMPLE_TEXT, content.text)
		except AssertionError as e: self.verificationErrors.append(str(e))

	def tearDown(self):
		self.driver.quit()
		self.assertEqual([], self.verificationErrors)

class TestListButton(unittest.TestCase):

	def setUp(self):
		self.verificationErrors = []
		self.selenium = selenium("localhost", 4444, "*firefox", "http://localhost:8000/")
		self.selenium.start()

	def testButtonAction(self):
		sel = self.selenium
		sel.open("http://localhost:8000/")
		sel.select_window("null")
		sel.click("id=documentListButton")
		try: self.assertEqual("Select file from list", sel.get_text("css=h3"))
		except AssertionError, e: self.verificationErrors.append(str(e))
		sel.click("css=div.reveal-modal-bg")

	def tearDown(self):
		self.selenium.stop()
		self.assertEqual([], self.verificationErrors)