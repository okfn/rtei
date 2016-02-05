from __future__ import unicode_literals

from django.db import models

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel

from wagtail_modeltranslation.models import TranslationMixin


class RTEIBasePage(Page):
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full")
    ]


class RTEIPage(TranslationMixin, Page):

    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full")
    ]


class AboutPage(TranslationMixin, RTEIBasePage):
    pass


class ContactUsPage(TranslationMixin, RTEIBasePage):
    pass


class PartnersPage(TranslationMixin, RTEIBasePage):
    pass


class ResourcesPage(TranslationMixin, RTEIBasePage):
    pass


class ExplorePage(TranslationMixin, RTEIBasePage):
    pass
