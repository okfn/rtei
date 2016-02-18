from __future__ import unicode_literals
import json
from collections import OrderedDict

from django.db import models

from django.http import Http404
from django.utils.translation import ugettext as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import (FieldPanel, InlinePanel,
                                                MultiFieldPanel)
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailcore.models import Orderable

from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index


from wagtail_modeltranslation.models import TranslationMixin

from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from taggit.models import TaggedItemBase

from rtei import data

import logging
log = logging.getLogger(__name__)


def get_map_context(context):
    '''
    In the map page we pass the level 1 and 2 indicators to the
    template with the `indicators` variable. It has the following form:

    [
        {
            'code': '1',
            'title': 'Governance',
            'level': 1,
            'core': True,
            'subindicators': [
                {
                    'code': '1.1',
                    'title': 'International Framework',
                    'level': 2,
                    'core': True,
                },
                {
                    'code': '1.2',
                    'title': 'National Law',
                    'level': 2,
                    'core': True,
                },
                ...
            ]
        },
        {
            'code': '2',
            'title': 'Availability',
            'level': 1,
            'core': True,
            'subindicators': [
                ...
            ]
        },
        ...
    ]
    '''
    context['indicators'] = data.get_map_indicators()


def get_country_context(context, country_code):
    '''In the RTEI by Country page we pass the following variables:

    * `available_countries`: a dict with the countries where data is avaiable,
        ordered alphabetically by name:

        {
            'CL': 'Chile',
            'NG: 'Nigeria',
            ...
        }

    Only if there is a country selected (via `id` param):

    * `country_code`
    * `country_name`
    * `country_indicators`: full indicators data for the country, in the form:

        {
            '1': 74.34,
            '1.1': 23.43,
            '1.1.1': None,
            ...
        }

    * `chart_data`: data necessary to build the C3 chart for just this
        particular country, eg:

            [{
                'name': 'Tanzania',
                'index': 64.063,
                '1': 16.91,
                '3': 15.92,
                '2': 8.68,
                '5': 8.32,
                '4': 14.24
            }]

    '''

    if country_code:
        country_data = data.get_indicators_for_country(country_code)
        if not country_data:
            raise Http404(_('No data available for this country'))

        context['country_code'] = country_code

        context['country_name'] = data.get_country_name(country_code)

        context['country_indicators'] = country_data

        for country in data.get_c3_scores_per_country():
            if country['name'] == context['country_name']:
                chart_data = country
                break

        context['chart_data'] = json.dumps([chart_data])

    context['available_countries'] = OrderedDict(
        sorted({code: data.get_country_name(code) for code, c
                in data.get_scores_per_country().iteritems()}.items(),
               key=lambda t: t[1]))

    context['indicators'] = data.get_indicators()


class RTEIPage(TranslationMixin, Page):

    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full")
    ]

    def get_context(self, request):
        context = super(RTEIPage, self).get_context(request)

        if self.slug == 'map':
            get_map_context(context)
        elif self.slug == 'rtei-country':
            get_country_context(context, request.GET.get('id'))

        return context

    def get_template(self, request, *args, **kwargs):
        # Define a template path derived from the app name and model instance
        # slug
        return "%s/%s.html" % (self._meta.app_label,
                               self.slug.replace('-', '_'))


class ResourceIndexPage(TranslationMixin, Page):
    template = 'rtei/resources.html'

    content_panels = Page.content_panels + [
        InlinePanel('documents', label="Resource Documents"),
    ]

    def get_context(self, request):
        context = super(ResourceIndexPage, self).get_context(request)
        context['documents'] = self.documents.all()
        return context


class ResourceDocument(Orderable):
    page = ParentalKey(ResourceIndexPage, related_name='documents')

    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    document_file = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('description'),
        DocumentChooserPanel('document_file'),
    ]


class BlogIndexPage(TranslationMixin, Page):

    @property
    def blogs(self):
        # Get list of live blog pages that are descendants of this page
        blogs = BlogPage.objects.live().descendant_of(self)

        # Order by most recent date first
        blogs = blogs.order_by('-date')

        return blogs

    def get_context(self, request):
        # Get blogs
        blogs = self.blogs

        # Filter by tag
        tag = request.GET.get('tag')
        if tag:
            blogs = blogs.filter(tags__name=tag)

        # Pagination
        page = request.GET.get('page')
        paginator = Paginator(blogs, 10)  # Show 10 blogs per page
        try:
            blogs = paginator.page(page)
        except PageNotAnInteger:
            blogs = paginator.page(1)
        except EmptyPage:
            blogs = paginator.page(paginator.num_pages)

        # Update template context
        context = super(BlogIndexPage, self).get_context(request)
        context['blogs'] = blogs
        return context

BlogIndexPage.content_panels = [
    FieldPanel('title', classname="full title"),
]

BlogIndexPage.promote_panels = Page.promote_panels


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey('BlogPage', related_name='tagged_items')


class BlogPage(TranslationMixin, Page):

    body = RichTextField(blank=True)
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    date = models.DateField("Post date")
    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    search_fields = Page.search_fields + (
        index.SearchField('body'),
    )

    @property
    def blog_index(self):
        # Find closest ancestor which is a blog index
        return self.get_ancestors().type(BlogIndexPage).last()

BlogPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('date'),
    FieldPanel('body', classname="full"),
]

BlogPage.promote_panels = Page.promote_panels + [
    ImageChooserPanel('feed_image'),
    FieldPanel('tags'),
]

