from .base import *


DEBUG = False

# Update database configuration with $DATABASE_URL.
import dj_database_url
db_from_env = dj_database_url.config()
DATABASES['default'].update(db_from_env)

SECRET_KEY = os.environ['SECRET_KEY']

try:
    from .local import *
except ImportError:
    pass
