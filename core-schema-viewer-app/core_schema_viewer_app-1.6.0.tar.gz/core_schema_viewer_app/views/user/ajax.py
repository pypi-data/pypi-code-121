"""Schema Viewer app Ajax views
"""
import json

from django.http import HttpResponse
from django.http.response import HttpResponseBadRequest
from django.utils.html import escape

from core_main_app.access_control.exceptions import AccessControlError
from core_main_app.commons.exceptions import DoesNotExist
import core_main_app.utils.decorators as decorators
from core_main_app.components.template import api as template_api
import core_schema_viewer_app.permissions.rights as rights
from core_schema_viewer_app.components.sandbox_data_structure import (
    api as sandbox_data_structure_api,
)
from core_schema_viewer_app.utils.parser import (
    remove_form_element,
    get_parser,
    generate_form,
    render_form,
)
from core_parser_app.tools.parser.renderer.list import ListRenderer
from core_parser_app.components.data_structure_element import (
    api as data_structure_element_api,
)
from core_parser_app.views.user.ajax import (
    get_data_structure_element_value,
    save_data_structure_element_value,
)


@decorators.permission_required(
    content_type=rights.schema_viewer_content_type,
    permission=rights.schema_viewer_access,
    raise_exception=True,
)
def generate_element(request, sandbox_data_structure_id):
    """Generate an element absent from the form.

    Args:
        request:
        sandbox_data_structure_id:

    Returns:

    """
    try:
        element_id = request.POST["id"]
        sandbox_data_structure = sandbox_data_structure_api.get_by_id(
            sandbox_data_structure_id
        )
        template = template_api.get(
            str(sandbox_data_structure.template.id), request=request
        )
        xsd_parser = get_parser(request=request)
        html_form = xsd_parser.generate_element_absent(
            element_id,
            template.content,
            data_structure=sandbox_data_structure,
            renderer_class=ListRenderer,
        )
    except Exception as e:
        return HttpResponseBadRequest(
            "An unexpected error occurred: %s" % escape(str(e)),
            content_type="application/javascript",
        )
    except Exception as e:
        return HttpResponseBadRequest()

    return HttpResponse(html_form)


@decorators.permission_required(
    content_type=rights.schema_viewer_content_type,
    permission=rights.schema_viewer_access,
    raise_exception=True,
)
def generate_choice(request, sandbox_data_structure_id):
    """Generate a choice branch absent from the form.

    Args:
        request:
        sandbox_data_structure_id:

    Returns:

    """
    try:
        # get sandbox data structure
        element_id = request.POST["id"]
        sandbox_data_structure = sandbox_data_structure_api.get_by_id(
            sandbox_data_structure_id
        )
        # generate form
        template = template_api.get(
            str(sandbox_data_structure.template.id), request=request
        )
        # renders the form
        xsd_parser = get_parser(request=request)
        html_form = xsd_parser.generate_choice_absent(
            element_id,
            template.content,
            data_structure=sandbox_data_structure,
            renderer_class=ListRenderer,
        )
    except Exception as e:
        return HttpResponseBadRequest(
            "An unexpected error occurred: %s" % escape(str(e)),
            content_type="application/javascript",
        )
    return HttpResponse(html_form)


@decorators.permission_required(
    content_type=rights.schema_viewer_content_type,
    permission=rights.schema_viewer_access,
    raise_exception=True,
)
def remove_element(request):
    """Remove an element from the form.

    Args:
        request:

    Returns:

    """
    element_id = request.POST["id"]
    code, html_form = remove_form_element(request, element_id)
    return HttpResponse(json.dumps({"code": code, "html": html_form}))


@decorators.permission_required(
    content_type=rights.schema_viewer_content_type,
    permission=rights.schema_viewer_access,
    raise_exception=True,
)
def clear_fields(request):
    """Clear fields of the current form.

    Args:
        request:

    Returns:

    """
    try:
        # get sandbox data structure
        sandbox_data_structure_id = request.POST["id"]
        sandbox_data_structure = sandbox_data_structure_api.get_by_id(
            sandbox_data_structure_id
        )

        # generate form
        template = template_api.get(
            str(sandbox_data_structure.template.id), request=request
        )
        root_element = generate_form(
            template.content, data_structure=sandbox_data_structure, request=request
        )
        # save the root element in the data structure
        sandbox_data_structure_api.update_data_structure_root(
            sandbox_data_structure, root_element
        )

        # renders the form
        xsd_form = render_form(request, root_element)

        return HttpResponse(
            json.dumps({"xsdForm": xsd_form}), content_type="application/javascript"
        )
    except:
        return HttpResponseBadRequest()


def data_structure_element_value(request):
    """Endpoint for data structure element value

    Args:
        request:

    Returns:

    """
    if request.method == "GET":
        return get_data_structure_element_value(request)
    elif request.method == "POST":
        return save_data_structure_element_value(request)
