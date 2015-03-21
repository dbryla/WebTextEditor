from django.test import TestCase
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Create your tests here.
class TestEnv(TestCase):

	def testBaseDir(self):
		self.assertTrue(BASE_DIR.endswith('TextEditorServer'))
                                                      
