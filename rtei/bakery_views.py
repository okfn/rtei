from wagtailbakery.views import BakeryView
from rtei import models

class RTEIPageStatic(BakeryView):
    bakery_model = models.RTEIPage


class RTEIAncillaryPageStatic(BakeryView):
    bakery_model = models.RTEIAncillaryPage


class ResourceIndexPageStatic(BakeryView):
    bakery_model = models.ResourceIndexPage


class BlogIndexPageStatic(BakeryView):
    bakery_model = models.BlogIndexPage


class BlogPageStatic(BakeryView):
    bakery_model = models.BlogPage
