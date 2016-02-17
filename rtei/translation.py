from .models import RTEIPage, ResourceIndexPage

from wagtail_modeltranslation.translation import TranslationOptions
from wagtail_modeltranslation.decorators import register


@register(RTEIPage)
class RTEIPageTR(TranslationOptions):
    fields = ('title', )


@register(ResourceIndexPage)
class ResourceIndexPageTR(TranslationOptions):
    fields = ('title', )
