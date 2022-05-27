""" Template Schema viewer Admin ajax file
"""
import json

from django.http import HttpResponseBadRequest, HttpResponse

from core_schema_viewer_app.components.template_schema_viewer import (
    api as template_schema_viewer_api,
)


def toggle_template_schema_visibility(request):
    """change the template schema visibility

    Args:
        request:

    Returns:

    """
    try:
        template_schema_id = request.POST.get("template_schema_id", None)
        template_schema = template_schema_viewer_api.get_by_id(template_schema_id)
        template_schema_viewer_api.toggle_visibility(template_schema)
        return HttpResponse(json.dumps({}), content_type="application/javascript")
    except Exception as e:
        return HttpResponseBadRequest(str(e), content_type="application/javascript")


def set_template_schema_default(request):
    """set the template schema to default

    Args:
        request:

    Returns:

    """
    try:
        template_schema_id = request.POST.get("template_schema_id", None)
        template_schema = template_schema_viewer_api.get_by_id(template_schema_id)
        template_schema_viewer_api.set_default(template_schema)
        return HttpResponse(json.dumps({}), content_type="application/javascript")
    except Exception as e:
        return HttpResponseBadRequest(str(e), content_type="application/javascript")
