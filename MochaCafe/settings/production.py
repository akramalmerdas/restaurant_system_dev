from .base import *

# Production-specific settings

DEBUG = False

# Load the secret key from an environment variable
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

# Throw an error if the secret key is not set in production
if not SECRET_KEY:
    raise ValueError("No DJANGO_SECRET_KEY set for production environment")

# Configure allowed hosts from an environment variable
# The variable should be a comma-separated list of hostnames
ALLOWED_HOSTS_STR = os.getenv('DJANGO_ALLOWED_HOSTS')
if ALLOWED_HOSTS_STR:
    ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STR.split(',')]
else:
    ALLOWED_HOSTS = []

# Use PostgreSQL for production
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

# Security headers for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Add django-csp for Content Security Policy
MIDDLEWARE.insert(2, 'csp.middleware.CSPMiddleware')

# Define a more practical Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net", "https://fonts.googleapis.com")
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net", "https://code.jquery.com")
CSP_IMG_SRC = ("'self'", "data:")
CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com")
CSP_CONNECT_SRC = ("'self'",)
CSP_FORM_ACTION = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)

# Static files storage for production with compression
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}