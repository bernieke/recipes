import os

from collections import OrderedDict

from django.core.management.utils import get_random_secret_key

# Activate django extensions if present
DJANGO_EXTENSIONS_AVAILABLE = False
try:
    import django_extensions  # NOQA
    DJANGO_EXTENSIONS_AVAILABLE = True
except ModuleNotFoundError:
    pass


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY_FILE = os.path.join(BASE_DIR, 'secret.key')

if not os.path.exists(SECRET_KEY_FILE):
    with open(SECRET_KEY_FILE, 'w') as f:
        f.write(get_random_secret_key())
with open(SECRET_KEY_FILE) as f:
    SECRET_KEY = f.read().strip()

DEBUG = int(os.environ.get('DEBUG', '0'))
if os.environ.get('GUNICORN'):
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

INSTALLED_APPS = [
    'bootstrap4',
    'fontawesome_5',
    'recipes',
    'martor',
    'adminsortable2',
    'admin_interface',
    'colorfield',
    'dal',
    'dal_select2',
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
if DJANGO_EXTENSIONS_AVAILABLE:
    INSTALLED_APPS.append('django_extensions')
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
X_FRAME_OPTIONS = 'SAMEORIGIN'

SQL_DATABASE = os.environ.get('SQL_DATABASE')
if not SQL_DATABASE:
    if os.path.exists('/var/lib/recipes'):
        SQL_DATABASE = '/var/lib/recipes/db.sqlite3'
    else:
        SQL_DATABASE = os.path.join(BASE_DIR, 'db.sqlite3')
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('SQL_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': SQL_DATABASE,
        'USER': os.environ.get('SQL_USER', 'user'),
        'PASSWORD': os.environ.get('SQL_PASSWORD', 'password'),
        'HOST': os.environ.get('SQL_HOST', 'localhost'),
        'PORT': os.environ.get('SQL_PORT', '5432'),
    }
}
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

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

LANGUAGE_CODE = 'en'
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
STATIC_ROOT = '/var/www/recipes'

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
    'OurGroceries connectivity settings': [
        'OURGROCERIES_USERNAME',
        'OURGROCERIES_PASSWORD',
        'OURGROCERIES_LIST'
    ],
}

MARTOR_THEME = 'semantic'
MARTOR_ENABLE_CONFIGS = {
    'emoji': 'false',
    'imgur': 'false',
    'mention': 'false',
    'jquery': 'false',
    'living': 'false',
    'spellcheck': 'true',
    'hljs': 'true',
}
MARTOR_TOOLBAR_BUTTONS = [
    'bold', 'italic', 'horizontal', 'heading', 'pre-code',
    'blockquote', 'unordered-list', 'ordered-list',
    'link', 'image-link', 'toggle-maximize', 'help',
]
