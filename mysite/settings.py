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

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '35&(($ud!+#l%+u8p(o3^9^#_kj-z09h#+owd^k(y^kqrel52u'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = '587'
EMAIL_HOST_USER = "adelprete87@gmail.com"
EMAIL_HOST_PASSWORD = "kb978caw"
EMAIL_USE_TLS = True
# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'datetimewidget',
    'registration',
    'mysite.base',
    'mysite.oscars',
    'mysite.survivor',
)

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


ROOT_URLCONF = 'mysite.urls'

WSGI_APPLICATION = 'mysite.wsgi.application'

STATICFILES_DIRS = (
    'C:/Users/Anthony/Desktop/March Madness Site/mysite/mysite/root/static/',
)

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'central',
        'HOST':'',
        'USER':'dev',
        'PASSWORD': 'needsmoredev',
        'PORT': 10061,
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = "America/New_York"

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGIN_REDIRECT_URL = '/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_ROOT = 'C:/Users/Anthony/Desktop/March Madness Site/mysite/static/'
STATIC_URL = '/static/'

MEDIA_ROOT = 'C:/Users/Anthony/Desktop/March Madness Site/mysite/media/'
MEDIA_URL = '/media/'
#ADMIN_MEDIA_PREFIX = '/media/'

OSCAR_POOLS_OPEN = True
