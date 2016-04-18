from django import template
from django.utils.translation import ugettext as _

from rtei.models import Page, RTEIAncillaryPage

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

    menuitems = parent.get_children().live().in_menu()

    for menuitem in menuitems:
        # Don't show dropdown of children for About item.
        if menuitem.specific_class is RTEIAncillaryPage:
            menuitem.show_dropdown = False
        else:
            menuitem.show_dropdown = has_menu_children(menuitem)
        # We don't directly check if calling_page is None since the template
        # engine can pass an empty string to calling_page
        # if the variable passed as calling_page does not exist.
        menuitem.active = (calling_page.url.startswith(menuitem.url)
                           if calling_page else False)
    return {
        'calling_page': calling_page,
        'menuitems': menuitems,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


# Retrieves the children of the top menu items for the drop downs
@register.inclusion_tag('rtei/tags/top_menu_children.html', takes_context=True)
def top_menu_children(context, parent):
    menuitems_children = parent.get_children().specific()

    menuitems_children = menuitems_children.live().in_menu()
    return {
        'parent': parent,
        'menuitems_children': menuitems_children,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


@register.inclusion_tag('rtei/tags/breadcrumbs.html', takes_context=True)
def breadcrumbs(context):
    self = context.get('self')
    if self is None or self.depth <= 2:
        # When on the home page, displaying breadcrumbs is irrelevant.
        ancestors = ()
    else:
        ancestors = Page.objects.ancestor_of(
            self, inclusive=True).filter(depth__gt=2)
    return {
        'ancestors': ancestors,
        'request': context['request'],
    }


@register.filter
def get_indicator_value(dictionary, code):
    value = dictionary.get(code, '')
    if isinstance(value, basestring):
        value = _(value)
    return value


@register.inclusion_tag('rtei/tags/indicators.html')
def indicators_list(indicators, country_indicators):
    return {
        'indicators': indicators,
        'country_indicators': country_indicators
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

    menuitems = about_root.get_children().live().in_menu()

    for menuitem in menuitems:
        menuitem.active = (calling_page.url.startswith(menuitem.url)
                           if calling_page else False)
    return {
        'calling_page': calling_page,
        'menuitems': menuitems,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }
