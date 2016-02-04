from __future__ import unicode_literals

from django.db import models

from wagtail.wagtailcore.models import Page
from wagtail_modeltranslation.models import TranslationMixin


class HomePage(TranslationMixin, Page):
    pass
