""" Url router for the visualization insitu application
"""
from django.urls import re_path

import core_visualization_insitu_app.views.user.ajax as user_ajax
import core_visualization_insitu_app.views.user.views as user_views

urlpatterns = [
    re_path(r"^$", user_views.index, name="core_visualization_insitu_index"),
    re_path(
        r"^select-project-form/$",
        user_ajax.update_selected_project,
        name="core_visualization_insitu_select_project_form",
    ),
    re_path(
        r"^select-build-form/$",
        user_ajax.update_selected_build,
        name="core_visualization_insitu_select_build_form",
    ),
    re_path(
        r"^select-part-form/$",
        user_ajax.update_selected_part,
        name="core_visualization_insitu_select_part_form",
    ),
    re_path(
        r"^get-frames/$",
        user_ajax.get_frames,
        name="core_visualization_insitu_get_frames",
    ),
    re_path(
        r"^update-insitu-data-info/$",
        user_ajax.update_data_information,
        name="core_visualization_insitu_update_data_information",
    ),
    re_path(
        r"^download-image/$",
        user_ajax.download_image,
        name="core_visualization_insitu_download_image",
    ),
    re_path(
        r"^previous-layer/$",
        user_ajax.previous_layer,
        name="core_visualization_insitu_previous_layer",
    ),
    re_path(
        r"^next-layer/$",
        user_ajax.next_layer,
        name="core_visualization_insitu_next_layer",
    ),
    re_path(
        r"^access-layer-number/$",
        user_ajax.access_layer_by_number,
        name="core_visualization_insitu_access_custom_layer",
    ),
    re_path(
        r"^update-3d/$",
        user_ajax.update_3d_visualization,
        name="core_visualization_insitu_update_3d_visualization",
    ),
]
