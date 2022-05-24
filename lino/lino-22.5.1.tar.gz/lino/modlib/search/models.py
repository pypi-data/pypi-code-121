# -*- coding: UTF-8 -*-
# Copyright 2021-2022 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import re
from html import escape
from django.conf import settings

from lino.api import rt, dd, _
from lino.core import constants
from lino.core.utils import get_models
from lino.core.site import has_elasticsearch, has_haystack

from etgen.html import E

from .roles import SiteSearcher


class SiteSearchBase(dd.VirtualTable):
    abstract = True

    required_roles = dd.login_required(SiteSearcher)
    label = _("Search")
    column_names = "description matches"
    private_apps = frozenset(['sessions', 'contenttypes', 'users'])

    display_mode_main = constants.DISPLAY_MODE_STORY

    card_layout = """description"""
    item_layout = """
    search_overview
    matches
    """

    # _site_search_tables = []
    # @classmethod
    # def register(cls, t):
    #     assert t not in cls._site_search_tables
    #     cls._site_search_tables.append(t)

    # disabled_models = set()
    # @classmethod
    # def disable_model(cls, m):
    #     cls.disabled_models.add(m)

    @dd.displayfield(_("Except"))
    def search_overview(cls, obj, ar):
        if obj is not None:
            t = cls.get_table_for_role(obj.get_default_table(), ar.get_user().user_type.role)
            sar = t.request(parent=ar)
            return obj.as_search_item(sar)

    @classmethod
    def get_table_for_role(cls, default_table, user_role):
        for t in [default_table] + default_table.__subclasses__():
            if user_role.has_required_roles(t.required_roles):
                return t
        return default_table

    @classmethod
    def get_card_title(cls, ar, elem):
        t = cls.get_table_for_role(elem.get_default_table(), ar.get_user().user_type.role)
        sar = t.request(parent=ar)
        return t.get_card_title(sar, elem)

    @classmethod
    def return_rows(cls, ar) -> bool:
        if ar.quick_search is None or len(ar.quick_search) < 2:
            return False
        return True

    @dd.displayfield(_("Description"))
    def description(self, obj, ar):
        elems = []
        elems.append(ar.obj2html(obj))
        # elems.append(u" ({})".format(obj._meta.verbose_name))
        elems += (" (", str(obj._meta.verbose_name), ")")
        return E.p(*elems)

    @dd.displayfield(_("Matches"))
    def matches(self, obj, ar):
        # if not obj.__class__.show_in_site_search:
        #     return ""
        def bold(mo):
            return "<b>{}</b>".format(mo.group(0))
        matches = {}
        # duplicate logic. Compare lino.core.models
        for w in ar.quick_search.split():
            char_search = True
            lst = None
            if w.startswith("#") and w[1:].isdigit():
                w = w[1:]
                char_search = False
            if w.isdigit():
                i = int(w)
                for de in obj.quick_search_fields_digit:
                    if de.value_from_object(obj) == i:
                    # if getattr(obj, fn) == int(w):
                        matches.setdefault(de, w)
            if char_search:
                for de in obj.quick_search_fields:
                    s = matches.get(de, None)
                    if s is None:
                        s = str(de.value_from_object(obj))
                        s = escape(s, quote=False)
                    r, count = re.subn(w, bold, s, flags=re.IGNORECASE)
                    if count:
                        matches[de] = r

        chunks = []
        for de in obj.quick_search_fields + obj.quick_search_fields_digit:
            lst = matches.get(de, None)
            if lst:
                chunks.append(de.name + ":" + lst)
        from lxml import etree
        s = ', '.join(chunks)
        s = "<span>" + s + "</span>"
        try:
            return etree.fromstring(s)
        except Exception as e:
            raise Exception("{} : {}".format(e, s))
        # return etree.fromstring(', '.join(chunks))
        # return E.raw(', '.join(chunks))

class SiteSearch(SiteSearchBase):

    display_mode_main = constants.DISPLAY_MODE_LIST

    @classmethod
    def get_data_rows(cls, ar):
        if cls.return_rows(ar):
            user_type = ar.get_user().user_type
            for model in get_models():
                if model._meta.app_label in cls.private_apps:
                    continue
                if model.show_in_site_search:
                    t = cls.get_table_for_role(model.get_default_table(), user_type.role)
                    # for t in cls._site_search_tables:
                    if not t.get_view_permission(user_type):
                        continue
                    sar = t.request(
                        parent=ar, quick_search=ar.quick_search)
                    for obj in sar:
                        if t.get_row_permission(obj, sar, t.get_row_state(obj), sar.bound_action) and obj.show_in_site_search:  # don't show calview.HeaderRow
                            yield obj


if settings.SITE.use_elasticsearch and has_elasticsearch:

    from .mixins import search, MultiMatch, execute_search

    class SearchQueries(dd.Table):
        model = 'elasticsearch_django.SearchQuery'
        column_names = "user index search_terms"

    class ElasticSiteSearch(SiteSearchBase):

        @classmethod
        def get_rows_from_search_query(cls, sq, ar):
            for hit in sq.response.hits:
                model = dd.resolve_model(hit['model'])
                t = model.get_default_table()
                if not t.get_view_permission(ar.get_user().user_type):
                    continue
                # yield model.objects.annotate_and_get(hit['id'], sq)
                yield model.objects.get(pk=hit['id'])

        @classmethod
        def get_request_queryset(cls, ar):
            if cls.return_rows(ar):
                user_type = ar.get_user().user_type
                query = MultiMatch(query=ar.quick_search)
                s = search.query(query)
                s = s[ar.offset:ar.offset+ar.limit]
                sq = execute_search(s, save=False)
                return sq
            return []

if settings.SITE.use_solr and has_haystack:
    from haystack.query import SearchQuerySet
    from haystack.inputs import AutoQuery

    class SolrSiteSearch(SiteSearchBase):

        @classmethod
        def get_rows_from_search_query(cls, sqs, ar):
            results = sqs[ar.offset:ar.offset+ar.limit]
            for result in results:
                yield result.model.objects.get(pk=result.pk)

        @classmethod
        def get_request_queryset(cls, ar):
            if cls.return_rows(ar):
                sqs = SearchQuerySet().auto_query(ar.quick_search)
                return sqs
            return []
