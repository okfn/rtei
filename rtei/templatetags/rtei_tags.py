import os

from django import template
from django.utils.translation import ugettext as _, get_language

from rtei.models import Page, RTEIAncillaryPage
from rtei.data import get_file_path

import logging
log = logging.getLogger(__name__)

register = template.Library()


@register.assignment_tag(takes_context=True)
def get_site_root(context):
    # NB this returns a core.Page, not the implementation-specific model used
    # so object-comparison to self will return false as objects would differ
    return context['request'].site.root_page


def has_menu_children(page):

    return page.get_children().live().in_menu().exists()


# Retrieves the top menu items - the immediate children of the parent page
# The has_menu_children method is necessary because the bootstrap menu requires
# a dropdown class to be applied to a parent
@register.inclusion_tag('rtei/tags/top_menu.html', takes_context=True)
def top_menu(context, parent, calling_page=None):

    base_menu_items = parent.get_children().live().in_menu()
    menu_items = []
    for base_menu_item in base_menu_items:
        menu_item = base_menu_item.specific

        # Don't show dropdown of children for About item.
        if menu_item.specific_class is RTEIAncillaryPage:
            menu_item.show_dropdown = False
        else:
            menu_item.show_dropdown = has_menu_children(menu_item)
        # We don't directly check if calling_page is None since the template
        # engine can pass an empty string to calling_page
        # if the variable passed as calling_page does not exist.
        menu_item.active = (
            calling_page.url.startswith(menu_item.url)
            if calling_page else False)
        menu_items.append(menu_item)

    return {
        'calling_page': calling_page,
        'menu_items': menu_items,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
        'language': get_language(),
    }


# Retrieves the children of the top menu items for the drop downs
@register.inclusion_tag('rtei/tags/top_menu_children.html', takes_context=True)
def top_menu_children(context, parent):
    menu_items_children = parent.get_children().specific()

    menu_items_children = menu_items_children.live().in_menu()
    return {
        'parent': parent,
        'menu_items_children': menu_items_children,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


@register.inclusion_tag('rtei/tags/breadcrumbs.html', takes_context=True)
def breadcrumbs(context):
    self = context.get('self')
    if self is None or self.depth <= 2:
        # When on the home page, displaying breadcrumbs is irrelevant.
        base_ancestors = ()
    else:
        base_ancestors = Page.objects.ancestor_of(
            self, inclusive=True).filter(depth__gt=2)
    ancestors = []
    for base_ancestor in base_ancestors:
        ancestors.append(base_ancestor.specific)
    return {
        'ancestors': ancestors,
        'request': context['request'],
    }


@register.filter
def get_indicator_value(dictionary, code):
    value = dictionary.get(code, '')
    if isinstance(value, basestring):
        value = _(value)
    else:
        value = int(value)
    return value


@register.inclusion_tag('rtei/tags/indicators.html')
def indicators_list(indicators, country_indicators, is_theme):
    return {
        'indicators': indicators,
        'country_indicators': country_indicators,
        'is_theme': is_theme,
    }


@register.inclusion_tag('rtei/tags/left_menu.html')
def left_menu(indicators, themes, for_map=False):
    return {
        'indicators': indicators,
        'themes': themes,
        'for_map': for_map,
    }


@register.inclusion_tag('rtei/tags/switcher.html')
def switcher(indicators, show_overall=True, show_second_level=True,
             themes=False):
    return {
        'indicators': indicators,
        'show_overall': show_overall,
        'show_second_level': show_second_level,
        'themes': themes,
    }


@register.inclusion_tag('rtei/tags/about_menu.html', takes_context=True)
def about_menu(context, parent, calling_page=None):

    # Get the root About page (either the parent or self of calling_page)
    parent = calling_page.get_parent()
    if parent.specific_class is calling_page.specific_class:
        about_root = parent
    else:
        about_root = calling_page

    base_menu_items = about_root.get_children().live().in_menu()
    menu_items = []
    for base_menu_item in base_menu_items:
        menu_item = base_menu_item.specific

        menu_item.active = (
            calling_page.url.startswith(menu_item.url)
            if calling_page else False)

        menu_items.append(menu_item)
    return {
        'calling_page': calling_page,
        'menu_items': menu_items,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


@register.assignment_tag()
def translated_field(obj, field, lang):
    if lang != 'en':
        field_name = '{0}_{1}'.format(field, lang)
        if hasattr(obj, field_name) and getattr(obj, field_name):
            return getattr(obj, field_name)
    return getattr(obj, field, '')


@register.inclusion_tag('rtei/tags/resource_list_item.html')
def resource_list_item(result):
    return {
        'result': result,
    }


@register.filter
def country_available(country_code, year):
    return os.path.exists(
        get_file_path('{0}.json'.format(country_code), year))


@register.simple_tag
def document_is_external_url(form):
    for field in form:
        if field.name == 'external_url' and field.value():
            return True
    return False
