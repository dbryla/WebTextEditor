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
from pyvirtualdisplay import Display
from mongoengine.django.auth import AnonymousUser  

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_ALIAS = 'testdb'
SAMPLE_TEXT = u'Użytkownik może wyświetlić i modyfikować dokument z jego zawartością.'
DOC_NAME = 'TestDocument'
EMPTY_DOC_STRING = '<p><br></p>'
LOREM_IPSUM = '<p>Lorem ipsum.</p>'

class TestEnv(TestCase):

	def testBaseDir(self):
		self.assertTrue(BASE_DIR.endswith('TextEditorServer'))

	def testEnvVarTest(self):
		self.assertTrue(os.environ["TEST"] == "1")

class TestDB(TestCase):

	def testGetDocumentOr404(self):
		Doc(name=DOC_NAME, text=SAMPLE_TEXT).save()
		self.assertTrue(get_document_or_404(Doc, name=DOC_NAME).name == DOC_NAME)
		with self.assertRaisesMessage(Http404, 'No Document matches the given query.'):
			get_document_or_404(Doc, name='not_exisitng')

	def testDocumentModel(self):
		with self.assertRaisesMessage(ValidationError, '(Document:None) (Field is required: [\'name\'])'):
			Doc(text=SAMPLE_TEXT).save()
		with self.assertRaisesMessage(ValidationError, '(Document:None) (StringField only accepts string values: [\'name\'])'):
			Doc(name=1).save()
		with self.assertRaisesMessage(InvalidId, '\'piec\' is not a valid ObjectId, it must be a 12-byte input of type \'str\' or a 24-character hex string'):
			Doc(id='piec', name='DOC_NAME').save()

	def tearDown(self):
		Doc.drop_collection()

class TestDBManager(TestCase):

	def testInsertText(self):
		doc = Doc(name=DOC_NAME, last_change=datetime.datetime.now(), text=SAMPLE_TEXT).save()
		creation_date = doc.last_change
		insert_text(doc, 'A', 3)
		doc = Doc.objects(name=DOC_NAME)[0]
		self.assertTrue(creation_date < doc.last_change)
		self.assertTrue(doc.text[3] == 'A')
		Doc.drop_collection()
		doc = Doc(name=DOC_NAME, text="").save()
		insert_text(doc, 'k', 0)
		insert_text(doc, 'o', 0)
		self.assertTrue(Doc.objects(name=DOC_NAME)[0].text == 'ok')

	def testRemoveText(self):
		doc = Doc(name=DOC_NAME, last_change=datetime.datetime.now(), text=SAMPLE_TEXT).save()
		creation_date = doc.last_change
		remove_text(doc, 'Uzytkownik', 0)
		doc = Doc.objects(name=DOC_NAME)[0]
		self.assertTrue(creation_date < doc.last_change)
		self.assertTrue(doc.text[0] == ' ')
		Doc.drop_collection()
		doc = Doc(name=DOC_NAME, text="ok").save()
		remove_text(doc, 'o', 0)
		remove_text(doc, 'k', 0)
		self.assertTrue(Doc.objects(name=DOC_NAME)[0].text == '')

	def testPolishCharacters(self):
		doc = Doc(name=DOC_NAME, last_change=datetime.datetime.now(), text=SAMPLE_TEXT).save()
		creation_date = doc.last_change
		remove_text(doc, u'Użytkownik', 0)
		doc = Doc.objects(name=DOC_NAME)[0]
		self.assertTrue(doc.text[0] == ' ')

	def testCreateDocument(self):
		create_document({}, DOC_NAME, '')
		doc = Doc.objects(name=DOC_NAME)[0]
		self.assertTrue(doc.text == '')
		self.assertTrue(doc.name == DOC_NAME)
		Doc.drop_collection()
		create_document({}, DOC_NAME, 'test')
		doc = Doc.objects(name=DOC_NAME)[0]
		self.assertTrue(doc.text == 'test')
		self.assertTrue(doc.name == DOC_NAME)

	def tearDown(self):
		Doc.drop_collection()

class MockRequest(object):
	user = AnonymousUser()	

class TestEvents(TestCase):

	def testHandleMsg(self):
		doc = Doc(name=DOC_NAME, last_change=datetime.datetime.now(), text=SAMPLE_TEXT).save()
		handle_msg({'type' : 'i', 'pos' : 0, 'text': 'ala'}, doc['id'])
		doc = Doc.objects(name=DOC_NAME)[0]
		self.assertTrue(doc.text[:3] == 'ala')
		Doc.drop_collection()
		doc = Doc(name=DOC_NAME, last_change=datetime.datetime.now(), text=SAMPLE_TEXT).save()
		handle_msg({'type' : 'r', 'pos' : 0, 'text': u'Użytkownik'}, doc['id'])
		doc = Doc.objects(name=DOC_NAME)[0]
		print doc.text[0]
		self.assertTrue(doc.text[0] == ' ')
		with self.assertRaisesMessage(Http404, 'No Document matches the given query.'):
			handle_msg({}, 'not_exisitng')

	def testHandleList(self):
		message = {}
		request = MockRequest()
		with self.assertRaisesMessage(Http404, 'No Document matches the given query.'):
			handle_list(message, request)
		doc = Doc(name=DOC_NAME, last_change=datetime.datetime.now(), text=SAMPLE_TEXT).save()
		handle_list(message, request)
		self.assertTrue(len(message['files']), 1)
		self.assertTrue(message['files'][0]['name'] == DOC_NAME)
		doc = Doc(name=DOC_NAME + '1', last_change=datetime.datetime.now(), text=SAMPLE_TEXT).save()
		handle_list(message, request)
		self.assertTrue(len(message['files']), 2)

	def testHandleCreateDocument(self):
		msg = {'name': DOC_NAME, 'text': EMPTY_DOC_STRING, 'priv': False}
		handle_create_document(msg, {})
		id = msg['id']
		created_document = Doc.objects(id=id)[0]
		self.assertTrue(created_document['name'] == DOC_NAME)
		self.assertTrue(created_document['text'] == EMPTY_DOC_STRING)
		msg = {'name': DOC_NAME, 'text': SAMPLE_TEXT, 'priv': False}
		handle_create_document(msg, {})
		id = msg['id']
		created_document = Doc.objects(id=id)[0]
		self.assertTrue(created_document['name'] == DOC_NAME)
		self.assertTrue(created_document['text'] == SAMPLE_TEXT)

	def tearDown(self):
		Doc.drop_collection()

class TestUI(unittest.TestCase):

	def setUp(self):
		self.display = Display(visible=0, size=(800, 600))
		self.display.start()
		self.driver = webdriver.Firefox()
		self.driver.implicitly_wait(30)
		self.base_url = "http://localhost:8000/"
		self.verificationErrors = []
		self.accept_next_alert = True

	def testRead(self):
		Doc(name=DOC_NAME, text=LOREM_IPSUM).save()
		driver = self.driver
		time.sleep(1)
		driver.get(self.base_url)
		driver.find_element_by_css_selector("td").click()
		time.sleep(1)
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
		SAMPLE_TEXT = 'Sample-text.'
		content.send_keys(SAMPLE_TEXT)
		try: self.assertEqual(SAMPLE_TEXT, content.text)
		except AssertionError as e: self.verificationErrors.append(str(e))

	def testListButton(self):
		driver = self.driver
		driver.get(self.base_url)
		time.sleep(5)
		driver.find_element_by_class_name("has-menu").click()
		driver.find_element_by_id("documentListButton").click()
		time.sleep(5)
		try: self.assertEqual("Select file from list", driver.find_element_by_css_selector("#fileListModal > h3").text)
		except AssertionError as e: self.verificationErrors.append(str(e))
		driver.find_element_by_css_selector("div.reveal-modal-bg").click()

	def testSaveAs(self):
		Doc(name=DOC_NAME + '1', text=LOREM_IPSUM).save()
		driver = self.driver
		time.sleep(1)
		driver.get(self.base_url)
		driver.find_element_by_css_selector("td").click()
		driver.find_element_by_id("saveDocument").click()
		driver.find_element_by_id("documentName").clear()
		driver.find_element_by_id("documentName").send_keys(DOC_NAME)
		driver.find_element_by_id("saveDocumentButton").click()
		self.assertTrue(Doc.objects(name=DOC_NAME)[0]['text'] == LOREM_IPSUM)

	def testNewDocument(self):
		Doc(name=DOC_NAME + '1', text=LOREM_IPSUM).save()
		driver = self.driver
		time.sleep(1)
		driver.get(self.base_url)
		driver.find_element_by_css_selector("td").click()
		driver.find_element_by_id("newDocument").click()
		driver.find_element_by_id("documentName").clear()
		driver.find_element_by_id("documentName").send_keys(DOC_NAME)
		driver.find_element_by_id("saveDocumentButton").click()
		self.assertTrue(Doc.objects(name=DOC_NAME)[0]['text'] == EMPTY_DOC_STRING)

	def tearDown(self):
		self.driver.quit()
		self.assertEqual([], self.verificationErrors)
		self.display.stop()
		Doc.drop_collection()