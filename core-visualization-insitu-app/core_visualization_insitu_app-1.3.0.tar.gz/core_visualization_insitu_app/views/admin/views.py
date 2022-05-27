""" Visualization Insitu admin views
"""
from django.contrib.admin.views.decorators import staff_member_required

from core_main_app.utils.rendering import admin_render


@staff_member_required
def manage_visualization_data(request):
    """Visualization Insitu admin index

    Args:
        request:

    Returns:  view with buttons to  manage visualization data

    """
    assets = {
        "css": [
            "css/landing.css",
            "core_visualization_insitu_app/common/css/loading_background.css",
        ],
        "js": [
            {
                "path": "core_visualization_insitu_app/admin/js/build_visualization_data.js",
                "is_raw": False,
            },
            {
                "path": "core_visualization_insitu_app/admin/js/build_visualization_data_raw.js",
                "is_raw": True,
            },
        ],
    }

    return admin_render(
        request,
        "core_visualization_insitu_app/admin/manage_visualization_data.html",
        assets=assets,
    )
