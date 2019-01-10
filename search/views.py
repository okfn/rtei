from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from wagtail.core.models import Page
from wagtail.search.models import Query

from rtei.models import RteiDocument
from rtei.data import get_countries_with_data


class CountryResult(object):

    def __init__(self, code, name):

        self.code = code
        self.name = name
        self.url = (reverse(
                            'wagtail_serve',
                            args=['explore/rtei-country/'])
                    + '?id=' + self.code)
        self.title = '{0}: {1}'.format(_('RTEI by Country'), self.name)


def search(request):
    search_query = request.GET.get('query', None)
    page = request.GET.get('page', 1)

    # Search
    if search_query:

        search_results_countries = []
        for code, name in get_countries_with_data().iteritems():
            if name.lower().startswith(search_query.lower()):
                search_results_countries.append(CountryResult(code, name))

        search_results_pages = Page.objects.live().search(search_query)
        search_results_resources = RteiDocument.objects.search(search_query)

        from itertools import chain
        search_results = list(chain(search_results_countries,
                                    search_results_pages,
                                    search_results_resources))

        query = Query.get(search_query)

        # Record hit
        query.add_hit()
    else:
        search_results = Page.objects.none()

    # Pagination
    paginator = Paginator(search_results, 10)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    return render(request, 'search/search.html', {
        'search_query': search_query,
        'search_results': search_results,
    })
