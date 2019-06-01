import os

from collections import OrderedDict


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# TODO move to config file
SECRET_KEY = '&2g1@+@g#n#!r)qe5j(x-py2x5c)rqn_8_rt2n0@t^6t&6hhap'
# TODO turn off
DEBUG = True
# TODO move to config file
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'bootstrap4',
    'fontawesome_5',
    'recipes',
    'adminsortable2',
    'dal',
    'dal_select2',
    'admin_interface',
    'colorfield',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'constance',
    'constance.backends.database',
    'vinaigrette',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
ROOT_URLCONF = 'recipes.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.static',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
WSGI_APPLICATION = 'recipes.wsgi.application'

# TODO move to config file
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.'
        'UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
        'MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
        'CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
        'NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
LANGUAGES = [
    ('en', 'English'),
    ('nl', 'Nederlands'),
]
TIME_ZONE = 'Europe/Brussels'
USE_I18N = True
USE_L10N = True
USE_THOUSAND_SEPARATOR = True
USE_TZ = True

STATIC_URL = '/static/'

BOOTSTRAP4 = {
    'base_url': '/static/bootstrap/',
    'include_jquery': True,
}

MEDIA_URL = '/images/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'images/')

LOGIN_URL = 'admin:login'

AMOUNT_PRECISION = 2

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'
CONSTANCE_CONFIG = OrderedDict([
    ('OURGROCERIES_USERNAME', ('', 'Username to access OurGroceries')),
    ('OURGROCERIES_PASSWORD', ('', 'Password to access OurGroceries')),
    ('OURGROCERIES_LIST', ('', 'OurGroceries list to send shopping list to')),
])
CONSTANCE_CONFIG_FIELDSETS = {
    'OurGroceries connectivity settings': (
        'OURGROCERIES_USERNAME',
        'OURGROCERIES_PASSWORD',
        'OURGROCERIES_LIST'
    ),
}
