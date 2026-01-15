from .base import *
import sys

# Development-specific settings

DEBUG = True

# Allow all hosts for local development flexibility
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '*']

# Use a simple, non-secret key for development
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'a-default-secret-key-for-development')

# Use PostgreSQL for local development, loading credentials from .env file
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}

# Redis configuration is inherited from base.py
# No need to override CHANNEL_LAYERS here unless specific to development

# For running tests, switch to a fast in-memory SQLite database to avoid conflicts
# and speed up test execution.
if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
    # Use in-memory channel layer for tests
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }

# Use the default storage backend for development
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}