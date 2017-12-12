import logging

from django.templatetags.static import static
from django.shortcuts import redirect
from django.http import Http404
from django.conf import settings


log = logging.getLogger(__name__)


def latest_document(request):
    '''Redirects to latest Completed Questionnaire document url'''
    year = settings.YEARS[-1]
    return redirect_to_year(year)


def document_by_year(request, year):
    '''Redirects to Completed Questionnaire document url for the relevant
        year
    '''

    if year not in settings.YEARS:
        raise Http404

    return redirect_to_year(year)


def redirect_to_year(year):
    return redirect(static('data/rtei_data_{}.xlsx'.format(year)))
