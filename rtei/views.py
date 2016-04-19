from django.shortcuts import redirect

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
