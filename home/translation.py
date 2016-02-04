from .models import HomePage
from wagtail_modeltranslation.translation import TranslationOptions
from wagtail_modeltranslation.decorators import register


@register(HomePage)
class HomePageTR(TranslationOptions):
    fields = ('title', )
