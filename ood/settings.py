import os
from datetime import timedelta


# All settings here are trumped by settings_local.py, which is imported last.
# In particular, you'll need to set a SECRET_KEY.
# SECRET_KEY = '<some random string>'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = False

ALLOWED_HOSTS = []

INSTALLED_APPS = (
    'django.contrib.admin.apps.SimpleAdminConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social.apps.django_app.default',
    'ood',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'social.backends.google.GooglePlusAuth',
    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'ood.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social.apps.django_app.context_processors.backends',
                'social.apps.django_app.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'ood.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ood',
        'USER': 'ood',
    }
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'main'
SOCIAL_AUTH_LOGIN_URL = 'login'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = 'main'

# OoD settings.

MAX_MINUTES_NO_PLAYERS = 15
UPDATE_STATE_PERIOD_SECONDS = 60
MAX_SNAPSHOTS_PER_INSTANCE = 2

# Auth settings.

SOCIAL_AUTH_GOOGLE_PLUS_KEY = None

# Celery config.

BROKER_URL = 'amqp://'
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']

# Local settings trump any above.

try:
    from settings_local import *
except ImportError:
    pass

CELERYBEAT_SCHEDULE = {
    'update-state': {
        'task': 'ood.tasks.update_state',
        # TODO: The schedule should be frequent, but
        # DropletController.update_state() should be smarter about
        # timeouts.  Right now that can be controlled for testing by setting
        # UPDATE_STATE_PERIOD_SECONDS to a small value in settings_local.py.
        'schedule': timedelta(seconds=UPDATE_STATE_PERIOD_SECONDS),
    },
}
