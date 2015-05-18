from mongoengine.django.auth import User
from django import forms

class UserForm(forms.Form):
	username = forms.CharField(max_length=254)
	password = forms.CharField(label=("Password"), widget=forms.PasswordInput)
	error = ''

	def __init__(self, request=None):
		if request == None:
			forms.Form.__init__(self)
		else:
			self.username = request["username"] 
			self.password = request["password"]

	def is_valid(self):
		if len(User.objects(username = self.username)) != 0:
			self.error = 'User exists'
			return False
		elif len(self.username) == 0 or len(self.password) == 0:
			self.error = 'Invalid username or password, can not be empty'
			return False
		else:
			return True

class FileForm(forms.Form):
	docfile = forms.FileField(
		label='Select a file'
	)
	error = ''