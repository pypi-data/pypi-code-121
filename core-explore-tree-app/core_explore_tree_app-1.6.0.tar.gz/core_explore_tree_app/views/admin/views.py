""" Admin views
"""
import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.staticfiles import finders
from django.core.cache import caches
from django.urls import reverse
from django.http.response import HttpResponseRedirect
from django.utils.html import escape as html_escape

import core_explore_tree_app.components.query_ontology.api as query_ontology_api
from core_cache_manager_app.components.data_cached.models import DataCached
from core_cache_manager_app.views.admin.forms import FormSelectDatabaseObject
from core_explore_tree_app.commons.enums import QueryOntologyStatus
from core_explore_tree_app.components.navigation.models import Navigation
from core_explore_tree_app.components.query_ontology.models import QueryOntology
from core_explore_tree_app.views.admin.ajax import (
    EditOntologyView,
    DeleteObjectModalView,
)
from core_explore_tree_app.views.admin.forms import UploadQueryOntologyForm
from core_main_app.commons import exceptions
from core_main_app.utils.file import get_file_http_response
from core_main_app.utils.rendering import admin_render
from core_main_app.views.common.views import read_xsd_file

logger = logging.getLogger(__name__)

html_tree_cache = caches["html_tree"]
navigation_cache = caches["navigation"]
leaf_cache = caches["leaf"]
link_cache = caches["link"]


@staff_member_required
def manage_query_ontology(request):
    """View that allows ontology management.

    Args:
        request:

    Returns:

    """
    # get all ontologies
    ontologies = query_ontology_api.get_all()

    context = {
        "object_name": "OWL files",
        "available": [
            ontology
            for ontology in ontologies
            if ontology.status != QueryOntologyStatus.disabled.value
        ],
        "disabled": [
            ontology
            for ontology in ontologies
            if ontology.status == QueryOntologyStatus.disabled.value
        ],
        "status": QueryOntologyStatus.__members__,
    }

    assets = {
        "js": [
            {
                "path": "core_explore_tree_app/admin/js/query_ontology/list/activate.js",
                "is_raw": False,
            },
            {
                "path": "core_explore_tree_app/admin/js/query_ontology/list/disable.js",
                "is_raw": False,
            },
            {
                "path": "core_explore_tree_app/admin/js/query_ontology/list/restore.js",
                "is_raw": False,
            },
            EditOntologyView.get_modal_js_path(),
            DeleteObjectModalView.get_modal_js_path(),
        ]
    }

    modals = [
        EditOntologyView.get_modal_html_path(),
        DeleteObjectModalView.get_modal_html_path(),
    ]

    return admin_render(
        request,
        "core_explore_tree_app/admin/query_ontology/list.html",
        assets=assets,
        context=context,
        modals=modals,
    )


@staff_member_required
def upload_query_ontology(request):
    """Upload ontology.

    Args:
        request:

    Returns:

    """
    assets = {
        "js": [{"path": "core_main_app/common/js/backtoprevious.js", "is_raw": True}]
    }

    context = {
        "object_name": "OWL files",
        "url": reverse("admin:core_explore_tree_app_upload"),
        "redirect_url": reverse("admin:core_explore_tree_app_query_ontology"),
    }

    # method is POST
    if request.method == "POST":
        form = UploadQueryOntologyForm(request.POST, request.FILES, request=request)
        context["upload_form"] = form

        if form.is_valid():
            try:
                # save the query ontology
                _save_query_ontology(request, context)
                # redirect to the list of query ontology
                return HttpResponseRedirect(
                    reverse("admin:core_explore_tree_app_query_ontology")
                )
            except exceptions.NotUniqueError:
                context["errors"] = html_escape(
                    "An Ontology with the same name already exists. "
                    "Please choose another name."
                )
            except Exception as e:
                context["errors"] = html_escape(str(e))
    # method is GET
    else:
        # render the form to upload a query ontology
        context["upload_form"] = UploadQueryOntologyForm(request=request)

    # render the upload page
    return admin_render(
        request,
        "core_explore_tree_app/admin/query_ontology/upload.html",
        assets=assets,
        context=context,
    )


@staff_member_required
def download_blank_query_ontology(request):
    """Download ontology.

    Args:
        request:
        pk:

    Returns:

    """
    # open the blank owl file
    owl_file = open(finders.find("core_explore_tree_app/common/owl/blank.owl"))
    # retrieve the content of it
    content = owl_file.read()
    # return the file
    return get_file_http_response(
        file_content=content,
        file_name="blank",
        content_type="application/xml",
        extension=".owl",
    )


@staff_member_required
def download_query_ontology(request, pk=None):
    """Download ontology.

    Args:
        request:
        pk:

    Returns:

    """
    # get the ontology
    ontology = query_ontology_api.get_by_id(pk)
    # return the file
    return get_file_http_response(
        file_content=ontology.content,
        file_name=ontology.title,
        content_type="application/xml",
        extension=".owl",
    )


def _save_query_ontology(request, context):
    """Save a query ontology.

    Args:
        request:
        context:

    Returns:

    """
    # get the schema name
    name = request.POST["name"]
    # get the file from the form
    owl_file = request.FILES["upload_file"]
    # check the extension file
    if not owl_file.name.endswith(".owl"):
        raise Exception("The extension file must be .owl")
    # retrieve the template id
    template_id = request.POST["templates_manager"]
    # read the content of the file
    # FIXME: this method should be renamed to read_file, can't be done in this commit
    owl_data = read_xsd_file(owl_file)
    owl = QueryOntology(title=name, content=owl_data, template=template_id)
    query_ontology_api.upsert(owl)


@staff_member_required
def core_cache_view_index(request):
    """View that allows to see the cache status.

    Args:
        request:

    Returns:

    """
    context = {"object_name": "Cache"}
    error = None

    try:
        # get the active ontology
        active_ontology = query_ontology_api.get_active()

        # get the navigation from the cache
        nav_key = str(active_ontology.id)
        if nav_key in navigation_cache:
            navigation = navigation_cache.get(nav_key)
            context["navigation_id"] = str(navigation.id)
            # get the tree from the cache ### REMOVE if we don't display the tree
            tree_key = str(navigation.id)
            if tree_key in html_tree_cache:
                html_tree = html_tree_cache.get(tree_key)
                context["navigation_tree"] = html_tree
                number_cached_docs = 0
                cache_list = []
                listof_leaf = DataCached.get_all()

                for datacached in listof_leaf:
                    dict_keys_docs_id = datacached.cached_documents_dict
                    for dict_key_docid in dict_keys_docs_id:
                        key_docid_list = list(dict_key_docid.keys())
                        for key in key_docid_list:
                            if key in leaf_cache or key in link_cache:
                                number_cached_docs += 1
                    cache_list.append(datacached)
                context["nodes"] = cache_list
                context["number_cached_docs"] = number_cached_docs
    except exceptions.DoesNotExist:
        error = {
            "error": "An Ontology should be active to explore. Please contact an admin."
        }
    except Exception as e:
        error = {"error": "An error occurred when displaying the cache status."}
        logger.error("ERROR : {0}".format(str(e)))

    if error:
        context.update(error)

    assets = {}
    modals = []
    return admin_render(
        request,
        "core_explore_tree_app/admin/cache/index.html",
        assets=assets,
        context=context,
        modals=modals,
    )


@staff_member_required
def core_cache_manager_index(request):
    """View to the Manual cache.

    Args:
        request:

    Returns:

    """
    context = {"object_name": "Manual Cache"}
    error = None

    try:
        # get the active ontology
        active_ontology = query_ontology_api.get_active()
    except exceptions.DoesNotExist:
        error = {
            "error": "An Ontology should be active to explore. Please contact an admin."
        }

    if error is None:
        try:
            # get the navigation from the cache
            nav_key = str(active_ontology.id)
            if nav_key in navigation_cache:
                navigation = navigation_cache.get(nav_key)
                context["navigation_root_id"] = navigation.id
                # get the tree from the cache
                tree_key = str(navigation.id)
                if tree_key in html_tree_cache:
                    html_tree = html_tree_cache.get(tree_key)
                    context["navigation_tree"] = html_tree
                if navigation.children:
                    context["children"] = [
                        Navigation.get_by_id(child) for child in navigation.children
                    ]
            # Create the form to select which node to cache
            form = FormSelectDatabaseObject()
            form.set_objects(context["children"])
            context["form"] = form
        except exceptions.DoesNotExist:
            error = {"error": "Error when retrieve the navigation's children."}
        except Exception as e:
            error = {
                "error": "No navigation tree generated. "
                "Please go to the 'Data Exploration' menu to build the tree before using the cache."
            }
            logger.error("ERROR : {0}".format(str(e)))

    if error:
        context.update(error)

    assets = {
        "js": [
            {
                "path": "core_explore_tree_app/admin/js/cache/load_cache_view.js",
                "is_raw": True,
            },
            {"path": "core_explore_tree_app/user/js/tree.js", "is_raw": True},
            {
                "path": "core_explore_tree_app/user/js/resize_tree_panel.js",
                "is_raw": True,
            },
            {"path": "core_explore_tree_app/user/js/mock.js", "is_raw": True},
        ],
        "css": [
            "core_explore_tree_app/user/css/tree.css",
            "core_explore_tree_app/user/css/loading_background.css",
            "core_explore_tree_app/admin/css/cache/style.css",
        ],
    }
    modals = [
        "core_explore_tree_app/admin/cache/view/data_cache_popup.html",
        "core_explore_tree_app/admin/cache/view/data_clear_cache_popup.html",
    ]
    return admin_render(
        request,
        "core_explore_tree_app/admin/cache/manual_cache.html",
        assets=assets,
        context=context,
        modals=modals,
    )
