from django.utils.translation import ugettext as _
from django.core.mail import send_mail
from django import forms

from django.conf import settings

import logging
log = logging.getLogger(__name__)


class ContactForm(forms.Form):
    contact_name = forms.CharField(
        label=_('Name'), max_length=100,
        widget=forms.TextInput(attrs={'class': "short"}))
    contact_email = forms.EmailField(
        label=_('Email'), widget=forms.TextInput(attrs={'class': "short"}))
    contact_affiliation = forms.CharField(
        label=_('Affiliation'), max_length=256,
        widget=forms.TextInput(attrs={'class': "short"}))

    def save(self):
        message = '''A user has submitted the contact form with the following details:

Name: {0}
Email: {1}
Affiliation: {2}'''.format(self.cleaned_data['contact_name'],
                           self.cleaned_data['contact_email'],
                           self.cleaned_data['contact_affiliation'])

        send_mail('[RTEI] New Contact', message, 'no-reply@results.org',
                  [settings.RTEI_CONTACT_FORM_EMAIL], fail_silently=False)
