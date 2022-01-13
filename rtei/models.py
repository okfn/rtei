
import sys
import json
from collections import OrderedDict
from smtplib import SMTPException

from django.db import models
from django.http import Http404
from django.utils.translation import ugettext as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.validators import RegexValidator, URLValidator
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings

from wagtail.core.models import Page, get_root_collection_id
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.documents.models import AbstractDocument


from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from taggit.models import TaggedItemBase

from rtei import data
from rtei.forms import ContactForm

import logging
log = logging.getLogger(__name__)


def get_chart_labels(indicators, themes):
    chart_labels = {}
    for indicator in indicators:
        chart_labels[indicator['code']] = _(indicator['title'])
        for subindicator in indicator['children']:
            chart_labels[subindicator['code']] = _(subindicator['title'])
    for theme in themes:
        for subtheme in theme['children']:
            chart_labels['t' + subtheme['code']] = _(subtheme['title'])
    return chart_labels


def get_map_context(context, year):
    '''
    In the map page we pass the level 1 and 2 indicators to the
    template with the `indicators` variable. It has the following form:

    [
        {
            'code': '1',
            'title': 'Governance',
            'level': 1,
            'indicators': [
                {
                    'code': '1.1',
                    'title': 'International Framework',
                    'level': 2,
                },
                {
                    'code': '1.2',
                    'title': 'National Law',
                    'level': 2,
                },
                ...
            ]
        },
        {
            'code': '2',
            'title': 'Availability',
            'level': 1,
            'indicators': [
                ...
            ]
        },
        ...
    ]

    We also pass the `themes` variable to build the second menu, with
    identical format.

    '''
    context['indicators'] = data.get_indicators(year)
    context['themes'] = data.get_themes(year)


def get_country_context(context, country_code, year):
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
        country_data = data.get_indicators_for_country(country_code, year)
        if not country_data:
            raise Http404(_('No data available for this country'))

        context['country_code'] = country_code

        context['country_name'] = data.get_country_name(country_code)

        context['country_indicators'] = country_data

        for country in data.get_c3_scores_per_country(year):
            if country['name'] == context['country_name']:
                chart_data = country
                break

        context['chart_data'] = json.dumps([chart_data])
        context['indicators'] = data.get_indicators(year)
        context['themes'] = data.get_themes(year)

        context['chart_labels'] = json.dumps(
            get_chart_labels(context['indicators'], context['themes']))

    context['available_countries'] = OrderedDict(
        sorted(list({code: data.get_country_name(code) for code, c
                in data.get_scores_per_country(year).items()}.items()),
               key=lambda t: t[1]))


def get_theme_context(context, year):
    context['indicators'] = data.get_indicators(year)
    context['themes'] = data.get_themes(year)
    context['chart_labels'] = json.dumps(
        get_chart_labels(context['indicators'], context['themes']))


class RTEIPage(Page):
    bakery_views = ('rtei.bakery_views.RTEIPageStatic',)

    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full")
    ]

    def get_context(self, request):
        context = super(RTEIPage, self).get_context(request)

        year = request.GET.get('year')
        if not year or year not in settings.YEARS:
            year = settings.YEARS[-1]

        context['year'] = year
        context['all_years'] = settings.YEARS

        if self.slug == 'map':
            get_map_context(context, year)
        elif self.slug == 'rtei-country':
            get_country_context(context, request.GET.get('id'), year)
        elif self.slug == 'rtei-theme':
            get_theme_context(context, year)

        return context

    def get_template(self, request, *args, **kwargs):
        # Define a template path derived from the app name and model instance
        # slug
        return "%s/%s.html" % (self._meta.app_label,
                               self.slug.replace('-', '_'))


class RTEIAncillaryPage(Page):
    '''About page and other static content pages.'''

    bakery_views = ('rtei.bakery_views.RTEIAncillaryPageStatic',)
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full")
    ]

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    def get_context(self, request):
        context = super(RTEIAncillaryPage, self).get_context(request)
        if self.slug == 'contact-us':
            if request.method == 'POST':
                contact_form = ContactForm(request.POST)
            else:
                contact_form = ContactForm()
            context['contact_form'] = contact_form
        elif self.slug in ['supporters', 'civil-society-partners']:
            context['listing'] = True
        return context

    def serve(self, request):
        if self.slug == 'contact-us' and request.method == 'POST':
            contact_form = ContactForm(request.POST)
            if contact_form.is_valid():
                try:
                    contact_form.save()
                except SMTPException:
                    messages.error(
                        request,
                        _('There was a problem submitting your contact '
                          'details.'))
                    log.error('Internal Server Error: %s', request.path,
                              exc_info=sys.exc_info(),
                              extra={
                                'status_code': 500,
                                'request': request
                              })
                else:
                    messages.success(
                        request,
                        _("Your contact details have been submitted."))
                redirect(self.url)

        return super(RTEIAncillaryPage, self).serve(request)

    def get_template(self, request, *args, **kwargs):
        if self.slug == 'contact-us':
            return "rtei/contact_us.html"
        elif self.get_parent().slug == 'partners':
            return "rtei/partners.html"
        else:
            return "rtei/about.html"


class ResourceIndexPage(Page):

    bakery_views = ('rtei.bakery_views.ResourceIndexPageStatic',)
    template = 'rtei/resources.html'

    def resources(self):
        '''Return a queryset of resource documents, filtered based on query
        string args in the passed request.'''
        resources = RteiDocument.objects.filter(is_resource=True)

        # Don't want documents from the root collection.
        resources = resources.exclude(collection__id=get_root_collection_id())

        return resources

    def years(self, resources):
        '''Return a list of years used as values for the `year` property of
        document model.'''
        years = resources.order_by('-year') \
            .exclude(year__exact='') \
            .values_list('year', flat=True) \
            .distinct()
        return years

    def countries(self, resources):
        '''Return a list of counties used as values for the `country` property
        of document models.'''
        countries = resources.order_by('country') \
            .exclude(country__exact='') \
            .values_list('country', flat=True) \
            .distinct()
        return countries

    def collections(self, resources):
        '''Return a list of collections used as values for the `collection`
        property of document models.'''
        collections = resources.order_by('collection') \
            .exclude(collection__id=get_root_collection_id()) \
            .values_list('collection__id', 'collection__name') \
            .distinct()
        return collections

    def get_context(self, request):
        context = super(ResourceIndexPage, self).get_context(request)
        # Get all resource documents as a queryset
        resources = self.resources()

        # Get data to populate filter dropdowns from resources.
        context['years'] = self.years(resources)
        context['countries'] = self.countries(resources)
        context['collections'] = self.collections(resources)

        # Get the resource documents to display
        resources_to_display = resources.order_by('-created_at')

        # Filter resources to display as necessary.
        has_filter = False
        for filter_name in ['year', 'country', 'collection']:
            filter_value = request.GET.get(filter_name)
            if filter_value:
                if filter_value != "all":
                    kwargs = {'{0}'.format(filter_name): filter_value}
                    resources_to_display = resources_to_display.filter(
                        **kwargs)
                has_filter = True

        page = request.GET.get('page')
        paginator = Paginator(resources_to_display, 10)
        try:
            resources_to_display = paginator.page(page)
        except PageNotAnInteger:
            resources_to_display = paginator.page(1)
        except EmptyPage:
            resources_to_display = paginator.page(paginator.num_pages)

        context['documents'] = resources_to_display
        context['has_filter'] = has_filter

        return context


class RteiDocument(AbstractDocument, index.Indexed):
    '''A custom Document adding fields needed by RTEI Resource items.'''

    year = models.CharField(validators=[
        RegexValidator(regex='^\d{4}$',
                       message=_('Must be 4 numbers'),
                       code='nomatch')],
        help_text='e.g. 1999',
        max_length=4,
        blank=True)

    file = models.FileField(
        upload_to='documents', verbose_name=_('file'), blank=True, null=True,
        default='empty.txt',
        help_text="Use this to upload a file and list it as a resource")
    external_url = models.CharField(
        validators=[URLValidator(message=_('Must be a valid URL'))],
        blank=True,
        max_length=1000,
        verbose_name=_('External Link'),
        help_text="Use this to add an external website as a listed resource")
    country = models.CharField(max_length=256, blank=True)
    is_resource = models.BooleanField(default=True,
                                      help_text="Determines whether document "
                                      "appears on the Resources page.")
    description = RichTextField(blank=True)

    admin_form_fields = (
        'title',
        'description',
        'file',
        'external_url',
        'collection',
        'country',
        'year',
        'is_resource',
        'tags'
    )

    search_fields = AbstractDocument.search_fields + [
        index.SearchField('title'),
        index.SearchField('description'),
        index.SearchField('country'),
        index.SearchField('year'),
        index.RelatedFields('tags', [
            index.SearchField('name'),
        ])

    ]

    class Meta:
        get_latest_by = "created_at"


class BlogIndexPage(Page):

    bakery_views = ('rtei.bakery_views.BlogIndexPageStatic',)

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

        ## Pagination
        #page = request.GET.get('page')
        #paginator = Paginator(blogs, 10)  # Show 10 posts per page
        #try:
        #    blogs = paginator.page(page)
        #except PageNotAnInteger:
        #    blogs = paginator.page(1)
        #except EmptyPage:
        #    blogs = paginator.page(paginator.num_pages)

        ## Update template context
        context = super(BlogIndexPage, self).get_context(request)
        context['blogs'] = blogs
        return context

BlogIndexPage.content_panels = [
    FieldPanel('title', classname="full title"),
]

BlogIndexPage.promote_panels = Page.promote_panels


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey('BlogPage', related_name='tagged_items')


class BlogPage(Page):

    bakery_views = ('rtei.bakery_views.BlogPageStatic',)
    intro = models.TextField(blank=True)
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
    is_featured = models.BooleanField(
        default=False,
        help_text="Determines whether document appears in the Featured Contents."
    )

    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.RelatedFields('tags', [
            index.SearchField('name'),
        ])
    ]

    @property
    def blog_index(self):
        # Find closest ancestor which is a blog index
        return self.get_ancestors().type(BlogIndexPage).last()

BlogPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('date'),
    FieldPanel('is_featured'),
    FieldPanel('intro', classname="full"),
    FieldPanel('body', classname="full"),
]

BlogPage.promote_panels = Page.promote_panels + [
    ImageChooserPanel('feed_image'),
    FieldPanel('tags'),
]
