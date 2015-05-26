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
from views import *
import datetime
import os
from selenium import selenium
from selenium import webdriver
import unittest, time
from pyvirtualdisplay import Display
from mongoengine.django.auth import AnonymousUser, User
from forms import UserForm, FileForm
from django.shortcuts import render
from selenium.common.exceptions import NoSuchElementException

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_ALIAS = 'testdb'
SAMPLE_TEXT = u'Użytkownik może wyświetlić i modyfikować dokument z jego zawartością.'
DOC_NAME = 'TestDocument'
EMPTY_DOC_STRING = '<p><br></p>'
LOREM_IPSUM = '<p>Lorem ipsum.</p>'

logger = logging.getLogger('tests')

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
		Doc.objects.delete()

class TestDBManager(TestCase):

	def testInsertText(self):
		doc = Doc(name=DOC_NAME, last_change=datetime.datetime.now(), text=SAMPLE_TEXT).save()
		creation_date = doc.last_change
		insert_text(doc, 'A', 3)
		doc = Doc.objects(name=DOC_NAME)[0]
		logger.debug('TestDBManager::testInsertText compare ' + str(creation_date) + ' and ' + str(doc.last_change))
		self.assertTrue(creation_date < doc.last_change)
		self.assertTrue(doc.text[3] == 'A')
		Doc.objects.delete()
		doc = Doc(name=DOC_NAME, text="").save()
		insert_text(doc, 'k', 0)
		insert_text(doc, 'o', 0)
		self.assertTrue(Doc.objects(name=DOC_NAME)[0].text == 'ok')

	def testRemoveText(self):
		doc = Doc(name=DOC_NAME, last_change=datetime.datetime.now(), text=SAMPLE_TEXT).save()
		creation_date = doc.last_change
		remove_text(doc, 'Uzytkownik', 0)
		doc = Doc.objects(name=DOC_NAME)[0]
		logger.debug('TestDBManager::testRemoveText compare ' + str(creation_date) + ' and ' + str(doc.last_change))
		self.assertTrue(creation_date < doc.last_change)
		self.assertTrue(doc.text[0] == ' ')
		Doc.objects.delete()
		doc = Doc(name=DOC_NAME, text="ok").save()
		remove_text(doc, 'o', 0)
		remove_text(doc, 'k', 0)
		self.assertTrue(Doc.objects(name=DOC_NAME)[0].text == '')

	def testPolishCharacters(self):
		doc = Doc(name=DOC_NAME, last_change=datetime.datetime.now(), text=SAMPLE_TEXT).save()
		remove_text(doc, u'Użytkownik', 0)
		doc = Doc.objects(name=DOC_NAME)[0]
		self.assertTrue(doc.text[0] == ' ')

	def testCreateDocument(self):
		create_document({}, DOC_NAME, '')
		doc = Doc.objects(name=DOC_NAME)[0]
		self.assertTrue(doc.text == '')
		self.assertTrue(doc.name == DOC_NAME)
		Doc.objects.delete()
		create_document({}, DOC_NAME, 'test')
		doc = Doc.objects(name=DOC_NAME)[0]
		self.assertTrue(doc.text == 'test')
		self.assertTrue(doc.name == DOC_NAME)

	def tearDown(self):
		Doc.objects.delete()

class MockRequest(object):
	user = AnonymousUser()	

class TestEvents(TestCase):

	def testHandleMsg(self):
		doc = Doc(name=DOC_NAME, last_change=datetime.datetime.now(), text=SAMPLE_TEXT).save()
		handle_msg({'type' : 'i', 'pos' : 0, 'text': 'ala'}, doc['id'])
		doc = Doc.objects(name=DOC_NAME)[0]
		self.assertTrue(doc.text[:3] == 'ala')
		Doc.objects.delete()
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
		handle_list(message, request)
		self.assertEqual(len(message['files']), 0)
		doc = Doc(name=DOC_NAME, last_change=datetime.datetime.now(), text=SAMPLE_TEXT).save()
		handle_list(message, request)
		self.assertEqual(len(message['files']), 1)
		self.assertTrue(message['files'][0]['name'] == DOC_NAME)
		doc = Doc(name=DOC_NAME + '1', last_change=datetime.datetime.now(), text=SAMPLE_TEXT).save()
		handle_list(message, request)
		self.assertEqual(len(message['files']), 2)

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
		Doc.objects.delete()

class TestUI(unittest.TestCase):

	def setUp(self):
		User.drop_collection()
		self.display = Display(visible=0, size=(800, 600))
		self.display.start()
		self.driver = webdriver.Firefox()
		self.driver.implicitly_wait(30)
		self.base_url = "http://localhost:8000"
		self.verificationErrors = []
		self.accept_next_alert = True

	def testRead(self):
		Doc.objects.delete()
		Doc(name=DOC_NAME, text=LOREM_IPSUM).save()
		driver = self.driver
		time.sleep(1)
		driver.get(self.base_url)
		time.sleep(1)
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
		logger.debug('TestUI::testSaveAs documents: ' + str(Doc.objects()))
		driver = self.driver
		time.sleep(1)
		driver.get(self.base_url)
		time.sleep(1)
		driver.find_element_by_css_selector("td").click()
		time.sleep(1)
		driver.find_element_by_id("saveDocument").click()
		time.sleep(1)
		driver.find_element_by_id("documentName").clear()
		driver.find_element_by_id("documentName").send_keys(DOC_NAME)
		driver.find_element_by_id("saveDocumentButton").click()
		self.assertTrue(Doc.objects(name=DOC_NAME)[0]['text'] == LOREM_IPSUM)

	def testNewDocument(self):
		Doc(name=DOC_NAME + '1', text=LOREM_IPSUM).save()
		driver = self.driver
		time.sleep(1)
		driver.get(self.base_url)
		time.sleep(1)
		driver.find_element_by_css_selector("td").click()
		time.sleep(1)
		driver.find_element_by_id("newDocument").click()
		time.sleep(1)
		driver.find_element_by_id("documentName").clear()
		driver.find_element_by_id("documentName").send_keys(DOC_NAME)
		driver.find_element_by_id("saveDocumentButton").click()
		self.assertTrue(Doc.objects(name=DOC_NAME)[0]['text'] == EMPTY_DOC_STRING)

	def testCreateUser(self):
		logger.debug('Start TestUI::testCreateUser.')
		USER_NAME = 'test12'
		driver = self.driver
		url = self.base_url + '/createUser/'
		logger.debug('TestUI::testCreateUser try to open browser at ' + url)
		driver.get(url)
		logger.debug('TestUI::testCreateUser opened browser at ' + url)
		time.sleep(2)
		driver.find_element_by_id("id_username").clear()
		driver.find_element_by_id("id_username").send_keys(USER_NAME)
		driver.find_element_by_id("id_password").clear()
		driver.find_element_by_id("id_password").send_keys(USER_NAME)
		driver.find_element_by_css_selector("input[type=\"submit\"]").click()
		time.sleep(5)
		self.assertEqual(User.objects().count(), 1)
		logger.debug('End TestUI::testCreateUser.')

	def testAccount(self):
		# for sure
		Doc.objects.delete()
		logger.debug('Start TestUI::testAccount.')
		USER_NAME = 'testLogin'
		driver = self.driver
		driver.get(self.base_url)
		time.sleep(1)
		driver.find_element_by_css_selector("i.fa.fa-sign-in").click()
		time.sleep(1)
		driver.find_element_by_id("id_username").clear()
		driver.find_element_by_id("id_username").send_keys(USER_NAME)
		driver.find_element_by_id("id_password").clear()
		driver.find_element_by_id("id_password").send_keys(USER_NAME)
		driver.find_element_by_css_selector("input[type=\"submit\"]").click()
		time.sleep(1)
		self.assertEqual("Your username and password didn't match. Please try again.", driver.find_element_by_css_selector("p").text)
		User.create_user(USER_NAME, USER_NAME)
		time.sleep(1)
		driver.get(self.base_url)
		time.sleep(1)
		driver.find_element_by_css_selector("i.fa.fa-sign-in").click()
		time.sleep(1)
		driver.find_element_by_id("id_username").clear()
		driver.find_element_by_id("id_username").send_keys(USER_NAME)
		driver.find_element_by_id("id_password").clear()
		driver.find_element_by_id("id_password").send_keys(USER_NAME)
		driver.find_element_by_css_selector("input[type=\"submit\"]").click()
		time.sleep(1)
		self.assertEqual("Welcome, " + USER_NAME + ".", driver.find_element_by_css_selector("p").text)
		PRIVATE_DOC_NAME = "prywatny"
		driver.find_element_by_class_name("has-menu").click()
		driver.find_element_by_id("newDocumentMenu").click()
		time.sleep(1)
		driver.find_element_by_id("documentNameAtStart").clear()
		driver.find_element_by_id("documentNameAtStart").send_keys(PRIVATE_DOC_NAME)
		driver.find_element_by_id("privateFlagAtStart").click()
		driver.find_element_by_id("saveDocumentButtonAtStart").click()
		time.sleep(10)
		logger.debug('Critical point of TestUI::testAccount.')
		doc = Doc.objects()[0]
		self.assertEqual(doc.name, PRIVATE_DOC_NAME)
		self.assertTrue(doc.priv)
		driver.get(self.base_url)
		time.sleep(1)
		driver.find_element_by_class_name("has-menu").click()
		driver.find_element_by_id("documentListButton").click()
		time.sleep(1)
		self.assertEqual(PRIVATE_DOC_NAME, driver.find_element_by_css_selector("td").text)
		driver.find_element_by_id('accounts').click()
		driver.find_element_by_id("logout").click()
		time.sleep(1)
		with self.assertRaises(NoSuchElementException):
			driver.find_element_by_css_selector("td")
		logger.debug('End TestUI::testAccount.')

	def testImport(self):
		driver = self.driver
		driver.get(self.base_url + "/")
		time.sleep(1)
		driver.find_element_by_class_name("has-menu").click()
		driver.find_element_by_id("import").click()
		time.sleep(1)
		path = BASE_DIR + '/test_files/test.odt'
		logger.debug('Path: ' + path)
		driver.find_element_by_id("id_docfile").send_keys(path)
		driver.find_element_by_name("press").click()
		time.sleep(5)
		self.assertEqual('test.odt', driver.find_element_by_css_selector("td").text)


	def tearDown(self):
		self.driver.quit()
		self.assertEqual([], self.verificationErrors)
		self.display.stop()
		Doc.objects.delete()
		User.drop_collection()
 
class TestGoogleDrive(unittest.TestCase):

	def setUp(self):
		self.display = Display(visible=0, size=(800, 600))
		self.display.start()
		self.driver = webdriver.Firefox()
		self.driver.implicitly_wait(30)
		self.base_url = "http://localhost:8000"
		self.verificationErrors = []
		self.accept_next_alert = True
	
	def testLoginWindow(self):
		Doc(name=DOC_NAME, text=LOREM_IPSUM).save()
		driver = self.driver
		time.sleep(5)
		driver.get(self.base_url + "/")
		time.sleep(5)
		driver.find_element_by_css_selector("td").click()
		time.sleep(5)
		driver.find_element_by_id("gDriveIntegration").click()
		driver.find_element_by_id("authorizeGDriveLink").click()
		time.sleep(1)
		driver.switch_to_window(driver.window_handles[1])
		self.assertTrue(u"Logowanie – Konta Google" ==  driver.title 
			or u'Sign in - Google Accounts' == driver.title)
	
	def tearDown(self):
		self.driver.quit()
		self.assertEqual([], self.verificationErrors)
		self.display.stop()

class MockRequestWithMethod():
	
	def __init__(self, method, post):
		self.method = method
		self.POST = post
		self.META = {"CSRF_COOKIE_USED": True}

class TestViews(unittest.TestCase):

	def testCreateUser(self):
		request = MockRequestWithMethod('POST', {'username': 'test', 'password': 'test'})
		self.assertTrue(isinstance(createUser(request), HttpResponseRedirect))
		request = MockRequestWithMethod('POST', {'username': 'test1', 'password': ''})
		self.assertEqual(str(createUser(request)), str(render(request, 'registration/createUser.html', 
			{'form': UserForm(), 'error': 'Invalid username or password, can not be empty'})))
		request = MockRequestWithMethod('POST', {'username': 'test', 'password': 'test'})
		self.assertEqual(str(createUser(request)), str(render(request, 'registration/createUser.html', 
			{'form': UserForm(), 'error': 'User exists'})))
		request = MockRequestWithMethod('GET', {})
		self.assertEqual(str(createUser(request)), str(render(request, 'registration/createUser.html', 
														{'form': UserForm()})))

	def tearDown(self):
		User.drop_collection()
