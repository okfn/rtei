from .models import (RTEIPage,
                     RTEIAncillaryPage,
                     ResourceIndexPage,
                     BlogIndexPage,
                     BlogPage)
from wagtail_modeltranslation.translator import WagtailTranslationOptions
from modeltranslation.decorators import register


@register(RTEIPage)
class RTEIPageTR(WagtailTranslationOptions):
    fields = ('title', )


@register(ResourceIndexPage)
class ResourceIndexPageTR(WagtailTranslationOptions):
    fields = ('title', )


@register(RTEIAncillaryPage)
class RTEIAncillaryPageTR(WagtailTranslationOptions):
    fields = ('body', )


@register(BlogIndexPage)
class BlogIndexPageTR(WagtailTranslationOptions):
    fields = ('title', )


@register(BlogPage)
class BlogPageTR(WagtailTranslationOptions):
    fields = ('title', )
    fields = ('body', )
