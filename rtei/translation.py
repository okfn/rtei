from .models import RTEIPage

from wagtail_modeltranslation.translation import TranslationOptions
from wagtail_modeltranslation.decorators import register


@register(RTEIPage)
class RTEIPageTR(TranslationOptions):
    fields = ('title', )
