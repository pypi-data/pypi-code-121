""" Url router for the administration site
"""
from django.urls import re_path
from django.contrib import admin

from core_explore_tree_app.views.admin import views as admin_views
from core_explore_tree_app.views.admin import ajax as admin_ajax

admin_urls = [
    re_path(
        r"^query-ontology/upload$",
        admin_views.upload_query_ontology,
        name="core_explore_tree_app_upload",
    ),
    re_path(
        r"^query-ontology/download/$",
        admin_views.download_blank_query_ontology,
        name="core_explore_tree_app_download_blank",
    ),
    re_path(
        r"^query-ontology/download/(?P<pk>\w+)/$",
        admin_views.download_query_ontology,
        name="core_explore_tree_app_download",
    ),
    re_path(
        r"^query-ontology/disable$",
        admin_ajax.disable_query_ontology,
        name="core_explore_tree_app_disable",
    ),
    re_path(
        r"^query-ontology/activate$",
        admin_ajax.activate_query_ontology,
        name="core_explore_tree_app_activate",
    ),
    re_path(
        r"^query-ontology/restore$",
        admin_ajax.restore_query_ontology,
        name="core_explore_tree_app_restore",
    ),
    re_path(
        r"^query-ontology/(?P<pk>[\w-]+)/edit/$",
        admin_ajax.EditOntologyView.as_view(),
        name="core_explore_tree_app_edit",
    ),
    re_path(
        r"^query-ontology/(?P<pk>[\w-]+)/delete/$",
        admin_ajax.DeleteOntologyView.as_view(),
        name="core_explore_tree_app_delete",
    ),
    re_path(
        r"^query-ontology/$",
        admin_views.manage_query_ontology,
        name="core_explore_tree_app_query_ontology",
    ),
    re_path(
        r"^cache-manager-index/$",
        admin_views.core_cache_view_index,
        name="core_cache_view_index",
    ),
    re_path(
        r"^cache-manager-view/$",
        admin_views.core_cache_manager_index,
        name="core_cache_manager_index",
    ),
    re_path(
        r"^cache-manager-view/cache-all-files$",
        admin_ajax.core_cache_all_files,
        name="cache-all-files",
    ),
    re_path(
        r"^cache-manager-view/clear-cache$",
        admin_ajax.core_clear_cache,
        name="clear-cache",
    ),
]

urls = admin.site.get_urls()
admin.site.get_urls = lambda: admin_urls + urls
