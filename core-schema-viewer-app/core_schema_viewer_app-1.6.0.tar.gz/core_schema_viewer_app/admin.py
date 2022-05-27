""" Url router for the administration site
"""
from django.contrib import admin
from django.urls import re_path

from core_schema_viewer_app.views.admin import views as admin_views, ajax as admin_ajax

admin_urls = [
    re_path(
        r"^schema-viewer$",
        admin_views.manage_template,
        name="core_schema_viewer_app_template",
    ),
    re_path(
        r"^schema-viewer/toggle-visibility$",
        admin_ajax.toggle_template_schema_visibility,
        name="core_schema_viewer_app_toggle_visibility",
    ),
    re_path(
        r"^schema-viewer/set-default$",
        admin_ajax.set_template_schema_default,
        name="core_schema_viewer_app_set_default",
    ),
]

urls = admin.site.get_urls()
admin.site.get_urls = lambda: admin_urls + urls
