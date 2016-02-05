from .models import (RTEIPage,
                     AboutPage,
                     ContactUsPage,
                     PartnersPage,
                     ResourcesPage,
                     ExplorePage
                     )
from wagtail_modeltranslation.translation import TranslationOptions
from wagtail_modeltranslation.decorators import register


@register(RTEIPage)
class RTEIPageTR(TranslationOptions):
    fields = ('title', )


@register(AboutPage)
class AboutPageTR(TranslationOptions):
    fields = ('title', )


@register(ContactUsPage)
class ContactUsPageTR(TranslationOptions):
    fields = ('title', )


@register(PartnersPage)
class PartnersPageTR(TranslationOptions):
    fields = ('title', )


@register(ResourcesPage)
class ResourcesPageTR(TranslationOptions):
    fields = ('title', )


@register(ExplorePage)
class ExplorePageTR(TranslationOptions):
    fields = ('title', )
