""" Schema viewer admin views
"""

from django.contrib.admin.views.decorators import staff_member_required

from core_main_app.utils.rendering import admin_render
from core_schema_viewer_app.components.template_schema_viewer import (
    api as template_schema_viewer_api,
)


@staff_member_required
def manage_template(request):
    """Manage exporters, Display as list

    Args:
        request:

    Returns:

    """
    schema_viewer_template_list = template_schema_viewer_api.get_all()

    context = {
        "schema_viewer_template_list": schema_viewer_template_list,
    }

    modals = []

    assets = {
        "js": [
            {
                "path": "core_schema_viewer_app/admin/list/schema_viewer.js",
                "is_raw": False,
            },
        ],
        "css": [],
    }

    return admin_render(
        request,
        "core_schema_viewer_app/admin/list_templates.html",
        assets=assets,
        context=context,
        modals=modals,
    )
