from django.shortcuts import redirect
from django.http import Http404

from wagtail.wagtailcore.models import Collection

from rtei.models import RteiDocument


import logging
log = logging.getLogger(__name__)


def latest_document(request):
    '''Redirects to latest Completed Questionnaire document url'''

    questionnaire_collection_id = \
        Collection.objects.get(name='Completed Questionnaires').id

    latest_doc = RteiDocument.objects.filter(
        collection=questionnaire_collection_id).latest()

    return redirect(latest_doc.url)


def document_by_year(requesti, year):
    '''Redirects to Completed Questionnaire document url for the relevant
        year
    '''

    questionnaire_collection_id = \
        Collection.objects.get(name='Completed Questionnaires').id

    doc = RteiDocument.objects.filter(
        collection=questionnaire_collection_id, year=year).first()
    if not doc:
        raise Http404

    return redirect(doc.url)
