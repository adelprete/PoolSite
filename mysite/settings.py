"""
Django settings for mysite project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ADMINS = (
    ('Anthony', 'adelprete87@gmail.com'),
)

#SERVER_EMAIL = "OfficePoolHub <no-reply@officepoolhub.com>"

#DEFAULT_FROM_EMAIL = "OfficePoolHub <no-reply@officepoolhub.com>"

ALLOWED_HOSTS = [
    'www.oscarpoolhub.com',
    '127.0.0.1:9001',
    '50.116.20.10',
    '127.0.0.1',
]


INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'datetimewidget',
    'registration',
    'rest_framework',
    'bootstrap3',
    'mysite.base',
    'mysite.oscars',
)

PAYPAL_TEST = True
PAYPAL_WPP_USER = "officepoolhub_api1.gmail.com"
PAYPAL_WPP_PASSWORD = "CFAKCEBV9A5CXFLT"
PAYPAL_WPP_SIGNATURE = "AiPC9BjkCyDFQXbSkoZcgqH3hpacAqzfmPfHN0MXaiW1JKRfvW0TRayB"

ACCOUNT_ACTIVATION_DAYS = 7

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'mysite.base.middleware.FinishProfile',
)

from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.SUCCESS: 'bg-success',
    messages.ERROR: 'bg-error'
}


ROOT_URLCONF = 'mysite.urls'

WSGI_APPLICATION = 'mysite.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = "America/New_York"

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGIN_REDIRECT_URL = '/'

REGISTRATION_OPEN = False

OSCARS_POOLS_OPEN = True
SURVIVOR_POOLS_OPEN = True
SURVIVOR_PICKSHEETS_OPEN = True
AMAZING_RACE_POOLS_OPEN = True
AMAZING_RACE_PICKSHEETS_OPEN = True
MARCH_MADNESS_POOLS_OPEN = True
MARCH_MADNESS_BRACKETS_OPEN = True
NFL_SURVIVOR_POOLS_OPEN = True

from mysite.private import *
