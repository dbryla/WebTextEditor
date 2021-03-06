"""
Django settings for TextEditorServer project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from mongoengine import *
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATABASES_NAME = 'local'
try:
    if os.environ['TEST'] == "1":
        DATABASES_NAME = 'test'
except KeyError:
    print 'Normal database mode.'



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'f7ddz66auhy+%20awtyyj&y^6jzyse^a9hpa@zp2w87s$3e(j)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django_jenkins',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mongoengine.django.mongo_auth',
    'django_socketio',
    'EditorApp'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'TextEditorServer.urls'

WSGI_APPLICATION = 'TextEditorServer.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.dummy'
    }
}
AUTHENTICATION_BACKENDS = (
    'mongoengine.django.auth.MongoEngineBackend',
)

AUTH_USER_MODEL = 'mongo_auth.MongoUser'

MONGOENGINE_USER_DOCUMENT = 'mongoengine.django.auth.User'

SESSION_ENGINE = 'mongoengine.django.sessions'

SESSION_SERIALIZER = 'mongoengine.django.sessions.BSONSerializer'

connect(DATABASES_NAME)

TEMPLATE_DIRS = (BASE_DIR + '/EditorApp/templates',)
TEMPLATE_LOADERS = (
 'django.template.loaders.filesystem.Loader',
 'django.template.loaders.app_directories.Loader',
)
LOGIN_REDIRECT_URL = (
 '/'
)

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Poland'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'


import logging
LOG_LEVEL = "DEBUG"
log_handler = logging.FileHandler('server.log')
log_handler.setFormatter(logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
db_logger = logging.getLogger('db_manager')
db_logger.addHandler(log_handler)
db_logger.setLevel(LOG_LEVEL)
events_logger = logging.getLogger('events')
events_logger.addHandler(log_handler)
events_logger.setLevel(LOG_LEVEL)
views_logger = logging.getLogger('views')
views_logger.addHandler(log_handler)
views_logger.setLevel(LOG_LEVEL)
test_log_handler = logging.FileHandler('test.log')
test_log_handler.setFormatter(logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
tests_logger = logging.getLogger('tests')
tests_logger.addHandler(test_log_handler)
tests_logger.setLevel(LOG_LEVEL)
