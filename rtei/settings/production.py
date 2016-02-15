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
    'rtei.herokuapp.com'
]

try:
    from .local import *
except ImportError:
    pass
