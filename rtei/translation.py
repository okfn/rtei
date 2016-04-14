from .models import (RTEIPage,
                     RTEIAncillaryPage,
                     ResourceIndexPage,
                     BlogIndexPage,
                     BlogPage)

from wagtail_modeltranslation.translation import TranslationOptions
from wagtail_modeltranslation.decorators import register


@register(RTEIPage)
class RTEIPageTR(TranslationOptions):
    fields = ('title', )


@register(ResourceIndexPage)
class ResourceIndexPageTR(TranslationOptions):
    fields = ('title', )


@register(RTEIAncillaryPage)
class RTEIAncillaryPageTR(TranslationOptions):
    fields = ('body', )


@register(BlogIndexPage)
class BlogIndexPageTR(TranslationOptions):
    fields = ('title', )


@register(BlogPage)
class BlogPageTR(TranslationOptions):
    fields = ('title', )
    fields = ('body', )
