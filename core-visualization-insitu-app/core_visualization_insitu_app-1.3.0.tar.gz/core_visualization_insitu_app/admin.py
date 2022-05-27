""" Url router for the administration site
"""
from django.urls import re_path
from django.contrib import admin

from core_visualization_insitu_app.views.admin import ajax as admin_ajax
from core_visualization_insitu_app.views.admin import views as admin_views

admin_urls = [
    re_path(
        r"^visualization-insitu/$",
        admin_views.manage_visualization_data,
        name="core_visualization_insitu_manage_data",
    ),
    re_path(
        r"^visualization-insitu/build-visualization-data$",
        admin_ajax.build_visualization_data,
        name="core_visualization_insitu_build_data",
    ),
    re_path(
        r"^visualization-insitu/get-visualization-data$",
        admin_ajax.get_visualization_data,
        name="core_visualization_insitu_get_data",
    ),
]

urls = admin.site.get_urls()
admin.site.get_urls = lambda: admin_urls + urls
