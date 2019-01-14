from .models import (RTEIPage,
                     RTEIAncillaryPage,
                     ResourceIndexPage,
                     BlogIndexPage,
                     BlogPage)
from modeltranslation.translator import TranslationOptions
from modeltranslation.decorators import register


@register(RTEIPage)
class RTEIPageTR(TranslationOptions):
    pass


@register(ResourceIndexPage)
class ResourceIndexPageTR(TranslationOptions):
    pass


@register(RTEIAncillaryPage)
class RTEIAncillaryPageTR(TranslationOptions):
    fields = ('body', )


@register(BlogIndexPage)
class BlogIndexPageTR(TranslationOptions):
    pass


@register(BlogPage)
class BlogPageTR(TranslationOptions):
    fields = ('body', )
