""" Schema Viewer app user views
"""
from abc import ABCMeta
from os.path import join

from django.contrib import messages
from django.contrib.staticfiles import finders
from django.urls import reverse_lazy

from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import RedirectView, View
from core_parser_app.views.common.views import get_context

import core_main_app.utils.decorators as decorators
import core_schema_viewer_app.permissions.rights as rights
from core_main_app.components.template import api as template_api
from core_main_app.utils.file import get_file_http_response
from core_main_app.utils.rendering import render, django_render
from core_parser_app.tools.parser.renderer.xml import XmlRenderer
from core_schema_viewer_app.views.user.forms import FormDefaultTemplate
from core_schema_viewer_app.components.sandbox_data_structure import (
    api as sandbox_data_structure_api,
)
from core_schema_viewer_app.utils.parser import render_form


@decorators.permission_required(
    content_type=rights.schema_viewer_content_type,
    permission=rights.schema_viewer_access,
    login_url=reverse_lazy("core_main_app_login"),
)
def index(request):
    """Schema views homepage provides the following features :
        - Download a schema as a xsd file
        - Browse a schema by using one of the following views :
            # <oXygen>
            # Tabbed
            # Sandbox

    Args:
        request:

    Returns:

    """

    context = {"form": FormDefaultTemplate()}
    assets = {
        "js": [
            {"path": "core_schema_viewer_app/user/js/index.js", "is_raw": False},
        ],
        "css": [
            "core_schema_viewer_app/user/css/index.css",
        ],
    }

    return render(
        request,
        "core_schema_viewer_app/user/index.html",
        context=context,
        assets=assets,
    )


@decorators.permission_required(
    content_type=rights.schema_viewer_content_type,
    permission=rights.schema_viewer_access,
    login_url=reverse_lazy("core_main_app_login"),
)
def oxygen_viewer(request, pk):
    """

    Args:
        request:
        pk:

    Returns:

    """
    template = template_api.get(pk, request=request)
    file_name_html = template.filename.replace(".xsd", ".html")

    # find a file under static
    url_file = finders.find(
        join("core_schema_viewer_app", "common", "oxygen", file_name_html)
    )
    if url_file:
        # render a file under templates
        return django_render(
            request, "core_schema_viewer_app/common/oxygen/" + file_name_html
        )
    else:
        message = (
            "The oxygen documentation file associated to the request template is not available. "
            "Please contact your administrator for further information."
        )
        messages.add_message(request, messages.WARNING, message)
        return redirect(reverse("core_schema_viewer_index"))


def download_template(request):
    """Download template.

    Args:
        request:

    Returns:

    """
    template_id = request.GET.get("template_id", None)
    if template_id:
        template = template_api.get(template_id, request=request)
        # return the file
        return get_file_http_response(
            file_content=template.content,
            file_name=template.display_name,
            content_type="application/xsd",
            extension=".xsd",
        )
    else:
        return redirect(reverse("core_schema_viewer_index"))


class SchemaViewerRedirectView(RedirectView, metaclass=ABCMeta):
    def get_redirect_url(self, *args, **kwargs):
        # here we receive a template id
        template_id = self.request.GET.get("template_id", None)
        destination_view = self.request.GET.get("destination_view", None)

        if template_id and destination_view:
            destination_url = ""
            if destination_view == "oxygen":
                destination_url = "core_schema_viewer_oxygen_viewer"
            elif destination_view == "tabbed":
                destination_url = "core_schema_viewer_schema_viewer_tabbed"
            elif destination_view == "sandbox":
                destination_url = "core_schema_viewer_sandbox_view"

            # then redirect to the result page core_schema_viewer_schema_viewer_tabbed with /<template_id>/
            return reverse(destination_url, kwargs={"pk": str(template_id)})
        else:
            # messages.add_message(self.request, messages.ERROR, 'The given URL is not valid.')
            return reverse("core_schema_viewer_index")


@decorators.permission_required(
    content_type=rights.schema_viewer_content_type,
    permission=rights.schema_viewer_access,
    login_url=reverse_lazy("core_main_app_login"),
)
def sandbox_view(request, pk):
    """Loads view to customize sandbox tree

    Args:
        request:
        pk: template id

    Returns:

    """
    try:
        # Set the assets
        assets = {
            "js": [
                {"path": "core_main_app/common/js/XMLTree.js", "is_raw": False},
                {"path": "core_schema_viewer_app/user/js/autosave.js", "is_raw": False},
                {"path": "core_parser_app/js/autosave_checkbox.js", "is_raw": False},
                {
                    "path": "core_schema_viewer_app/user/js/autosave.raw.js",
                    "is_raw": True,
                },
                {"path": "core_parser_app/js/buttons.js", "is_raw": False},
                {
                    "path": "core_schema_viewer_app/user/js/buttons.raw.js",
                    "is_raw": True,
                },
                {"path": "core_parser_app/js/choice.js", "is_raw": False},
                {
                    "path": "core_schema_viewer_app/user/js/choice.raw.js",
                    "is_raw": True,
                },
                {"path": "core_parser_app/js/modules.js", "is_raw": False},
                {"path": "core_schema_viewer_app/user/js/sandbox.js", "is_raw": False},
            ],
            "css": [
                "core_main_app/common/css/XMLTree.css",
                "core_schema_viewer_app/user/css/xsd_form.css",
                "core_parser_app/css/use.css",
            ],
        }

        template = template_api.get(pk, request=request)

        # create the data structure
        sandbox_data_structure = sandbox_data_structure_api.create_and_save(
            template, request
        )

        # renders the form
        xsd_form = render_form(
            request, sandbox_data_structure.data_structure_element_root
        )

        # Set the context
        context = {
            "data_structure_id": str(sandbox_data_structure.id),
            "xsd_form": xsd_form,
        }

        return render(
            request,
            "core_schema_viewer_app/user/sandbox.html",
            assets=assets,
            context=context,
        )
    except Exception as e:
        return render(
            request,
            "core_main_app/common/commons/error.html",
            assets={},
            context={"errors": "An error occurred while rendering the tree."},
        )


@decorators.permission_required(
    content_type=rights.schema_viewer_content_type,
    permission=rights.schema_viewer_access,
    login_url=reverse_lazy("core_main_app_login"),
)
def download_xml(request, sandbox_data_structure_id):
    """Download XML file

    Args:
        request:
        sandbox_data_structure_id:

    Returns:

    """
    # get sandbox data structure
    sandbox_data_structure = sandbox_data_structure_api.get_by_id(
        sandbox_data_structure_id
    )

    # build XML renderer
    xml_renderer = XmlRenderer(
        sandbox_data_structure.data_structure_element_root, request
    )

    # generate xml data
    xml_data = xml_renderer.render()

    # build response with file
    return get_file_http_response(
        file_content=xml_data,
        file_name=sandbox_data_structure.name,
        content_type="application/xml",
        extension="xml",
    )


@decorators.permission_required(
    content_type=rights.schema_viewer_content_type,
    permission=rights.schema_viewer_access,
    login_url=reverse_lazy("core_main_app_login"),
)
def preview_xml(request, sandbox_data_structure_id):
    """Preview XML file

    Args:
        request:
        sandbox_data_structure_id:

    Returns:

    """
    # get sandbox data structure
    sandbox_data_structure = sandbox_data_structure_api.get_by_id(
        sandbox_data_structure_id
    )
    # build XML renderer
    xml_renderer = XmlRenderer(
        sandbox_data_structure.data_structure_element_root, request
    )
    # generate xml data
    xml_data = xml_renderer.render()
    # build response with file
    return render(
        request,
        "core_schema_viewer_app/user/sandbox_preview.html",
        assets={"css": ["core_main_app/common/css/XMLTree.css"]},
        context={"xml_data": xml_data},
    )
