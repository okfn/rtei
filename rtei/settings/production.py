import sys

from .base import *

DEBUG = False

# Update database configuration with $DATABASE_URL.
import dj_database_url
db_from_env = dj_database_url.config()
DATABASES['default'].update(db_from_env)

SECRET_KEY = os.environ.get('SECRET_KEY')

# AWS S3 settings
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
# Necessary to overcome broken pipe error if not default US location
# (https://github.com/boto/boto/issues/621).
if os.environ.get('AWS_S3_HOST', False):
    AWS_S3_HOST = os.environ.get('AWS_S3_HOST')
MEDIA_URL = "https://%s/" % (AWS_S3_CUSTOM_DOMAIN)

ALLOWED_HOSTS = [
    'localhost',
    'rtei.herokuapp.com',
    'rtei-production.herokuapp.com',
    'www.rtei.org',
]

# Email to receive contact requests from the form on /about/contact-us/
RTEI_CONTACT_FORM_EMAIL = os.environ.get('RTEI_CONTACT_FORM_EMAIL')

EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT', 587)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True


# Force HTTPS on Heroku
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'rtei': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}

WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.wagtailsearch.backends.elasticsearch',
        'URLS': [os.environ.get('ELASTICSEARCH_URL')],
        'INDEX': 'wagtail',
        'TIMEOUT': 5,
    }
}

try:
    from .local import *
except ImportError:
    pass
