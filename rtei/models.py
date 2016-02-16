from __future__ import unicode_literals

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel

from wagtail_modeltranslation.models import TranslationMixin

import logging
log = logging.getLogger(__name__)


import json
import os
from collections import OrderedDict


class RTEIPage(TranslationMixin, Page):

    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full")
    ]

    def get_context(self, request):
        context = super(RTEIPage, self).get_context(request)

        if self.slug == 'map':
            '''
            In the map page we pass the level 1 and 2 indicators to the
            template in the following form:

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
            indicators_file = os.path.join(os.path.dirname(__file__),
                                           'static', 'data', 'indicators.json')

            with open(indicators_file) as f:
                indicators = json.load(f, object_pairs_hook=OrderedDict)
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

        return context

    def get_template(self, request, *args, **kwargs):
        # Define a template path derived from the app name and model instance
        # slug
        return "%s/%s.html" % (self._meta.app_label,
                               self.slug.replace('-', '_'))
