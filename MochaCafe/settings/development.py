from .base import *
import sys

# Development-specific settings

DEBUG = True

# Allow all hosts for local development flexibility
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '*']

# Use a simple, non-secret key for development
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'a-default-secret-key-for-development')

# Use a file-based SQLite database for development to avoid external dependencies.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Use in-memory channel layer for development
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