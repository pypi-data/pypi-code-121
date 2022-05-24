import logging

from django import template
from django.conf import settings
from django.templatetags.static import static

from cms.menus.models import NavigationBarItem

from .. settings import *


register = template.Library()


@register.simple_tag
def is_mega_menu(item):
    if not item: return False
    childs = item.get_childs()
    if not childs: return False
    with_childs = 0
    enum_childs = enumerate(childs)
    for index,child in enum_childs:
        if index>0 and child.has_childs(): return True
        if child.has_childs(): with_childs += 1
        if index>0 and with_childs: return True
    return False


@register.simple_tag
def editorial_board_news_add(webpath):
    if not webpath: return None
    if not hasattr(settings, 'EDITORIAL_BOARD_NEWS_ADD_URL'): return '#'
    return settings.EDITORIAL_BOARD_NEWS_ADD_URL.format(website=webpath.site.pk,
                                                        webpath=webpath.pk)


@register.simple_tag
def editorial_board_news_edit(item):
    if not item: return None
    if not hasattr(settings, 'EDITORIAL_BOARD_NEWS_EDIT_URL'): return '#'
    return settings.EDITORIAL_BOARD_NEWS_EDIT_URL.format(website=item.webpath.site.pk,
                                                         webpath=item.webpath.pk,
                                                         news=item.pk)


@register.simple_tag
def editorial_board_page_publication_edit(item):
    if not item: return None
    if not hasattr(settings, 'EDITORIAL_BOARD_PAGE_PUBLICATION_EDIT_URL'): return '#'
    return settings.EDITORIAL_BOARD_PAGE_PUBLICATION_EDIT_URL.format(website=item.page.webpath.site.pk,
                                                                     webpath=item.page.webpath.pk,
                                                                     page=item.page.pk,
                                                                     publication=item.pk)


@register.simple_tag
def unicms_template_italia_static_path(resource):
    if not resource: return ''
    if settings.UNICMS_TEMPLATE_ITALIA_USE_CDN:
        return f'{settings.UNICMS_TEMPLATE_ITALIA_CDN}/{resource}'
    return static(resource)
