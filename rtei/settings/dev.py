from .base import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

for template_engine in TEMPLATES:
    template_engine['OPTIONS']['debug'] = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'or%s)8c==f0kgm^ifswz@c&!$y%o2x_59lere2)*32atguo1(z'


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

RTEI_CONTACT_FORM_EMAIL = 'example@example.com'

try:
    from .local import *
except ImportError:
    pass
