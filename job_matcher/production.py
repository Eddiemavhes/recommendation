from .settings import *

# Temporarily enable debug for troubleshooting
DEBUG = True

# Configure logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}

# Configure the production database
DATABASE_URL = 'postgresql://job_matcher_user:3AvZ3UDbTTI66biUpBNippV0K0ajLg3y@dpg-d3sdt7s9c44c73co21vg-a/job_matcher'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'job_matcher',
        'USER': 'job_matcher_user',
        'PASSWORD': '3AvZ3UDbTTI66biUpBNippV0K0ajLg3y',
        'HOST': 'dpg-d3sdt7s9c44c73co21vg-a',
        'PORT': '5432',
    }
}

# Allowed hosts
ALLOWED_HOSTS = ['.onrender.com', 'localhost', '127.0.0.1']
CSRF_TRUSTED_ORIGINS = ['https://*.onrender.com']

# Static files configuration
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Enable WhiteNoise for static file serving
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True