from __future__ import unicode_literals

from django.db import models

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel

from wagtail_modeltranslation.models import TranslationMixin

import logging
log = logging.getLogger(__name__)


class RTEIPage(TranslationMixin, Page):

    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full")
    ]

    def get_template(self, request, *args, **kwargs):
        # Define a template path derived from the app name and model instance
        # slug
        return "%s/%s.html" % (self._meta.app_label, self.slug.replace('-', '_'))
