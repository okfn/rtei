from __future__ import unicode_literals
import json
import os
from collections import OrderedDict

from django.db import models

from django.http import Http404
from django.utils.translation import ugettext as _

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailcore.models import Orderable

from wagtail_modeltranslation.models import TranslationMixin
from modelcluster.fields import ParentalKey

import logging
log = logging.getLogger(__name__)

_file_cache = {}


def get_json_file(path):
    if _file_cache.get(path):
        return _file_cache[path]

    with open(path) as f:
        out = json.load(f, object_pairs_hook=OrderedDict)

    _file_cache[path] = out

    return out


def get_indicators():
    indicators_file = os.path.join(os.path.dirname(__file__),
                                   'static', 'data', 'indicators.json')
    return get_json_file(indicators_file)


def get_countries():
    countries_file = os.path.join(os.path.dirname(__file__),
                                  '..', 'data', 'countries.json')
    return get_json_file(countries_file)


def get_scores_per_country():
    scores_file = os.path.join(os.path.dirname(__file__),
                               'static', 'data', 'scores_per_country.json')
    return get_json_file(scores_file)

def get_c3_scores_per_country():
    scores_file = os.path.join(os.path.dirname(__file__),
                               'static', 'data', 'c3_scores_per_country.json')
    return get_json_file(scores_file)

def get_indicators_for_country(country_code):
    country_file = os.path.join(os.path.dirname(__file__),
                                'static', 'data',
                                '{0}.json'.format(country_code))
    if not os.path.exists(country_file):
        return None

    return get_json_file(country_file)


def get_country_name(country_code):
    '''
    Given a country code, return the corresponding country name.
    '''
    code_type = 'iso2'
    if len(country_code) == 3:
        code_type = 'iso3'

    return next(
        (c['name'] for code, c in get_countries().iteritems()
         if c[code_type] == country_code.upper()),
        None)


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
    indicators = get_indicators()
    map_indicators = []
    for code, indicator in indicators.iteritems():
        if (indicator['level'] <= 2 and not code[-1].isalpha()):
            indicator['code'] = code
            if indicator['level'] == 1:
                if not indicator.get('subindicators'):
                    indicator['subindicators'] = []
                map_indicators.append(indicator)
            else:
                indicators[code[:1]]['subindicators'].append(indicator)

    context['indicators'] = map_indicators


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

    '''

    if country_code:
        country_data = get_indicators_for_country(country_code)
        if not country_data:
            raise Http404(_('No data available for this country'))

        context['country_code'] = country_code

        context['country_name'] = get_country_name(country_code)

        context['country_indicators'] = country_data

        for country in get_c3_scores_per_country():
            if country['name'] == context['country_name']:
                chart_data = country
                break

        context['chart_data'] = json.dumps([chart_data])

    context['available_countries'] = OrderedDict(
        sorted({code: get_country_name(code) for code, c
                in get_scores_per_country().iteritems()}.items(),
               key=lambda t: t[1]))

    context['indicators'] = get_indicators()


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
