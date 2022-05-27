""" explore tree Admin ajax file
"""
import json
import logging

from django.contrib import messages
from django.contrib.messages.storage.base import Message
from django.core.cache import caches
from django.http import HttpResponseBadRequest, HttpResponse
from django.urls import reverse_lazy

import core_cache_manager_app.components.data_cached.api as data_cached_api
import core_explore_tree_app.components.leaf.api as leaf_api
import core_explore_tree_app.components.navigation.api as navigation_api
import core_explore_tree_app.components.query_ontology.api as query_ontology_api
from core_explore_tree_app.commons.enums import QueryOntologyStatus
from core_explore_tree_app.components.leaf.models import Leaf
from core_explore_tree_app.components.navigation.models import Navigation
from core_explore_tree_app.components.query_ontology.models import QueryOntology
from core_explore_tree_app.views.admin.forms import EditOntologyForm
from core_explore_tree_app.views.user.ajax import load_view
from core_main_app.commons import exceptions
from core_main_app.views.common.ajax import EditObjectModalView, DeleteObjectModalView

logger = logging.getLogger(__name__)

html_tree_cache = caches["html_tree"]
navigation_cache = caches["navigation"]

leaf_cache = caches["leaf"]
branch_cache = caches["branch"]
link_cache = caches["link"]


def disable_query_ontology(request):
    """Disable a query ontology

    Args:
        request:

    Returns:

    """
    try:
        query_ontology_api.edit_status(
            query_ontology_api.get_by_id(request.POST["id"]),
            QueryOntologyStatus.disabled.value,
        )
        return HttpResponse(json.dumps({}), content_type="application/javascript")
    except Exception as e:
        return HttpResponseBadRequest(str(e), content_type="application/javascript")


def restore_query_ontology(request):
    """Restore a disabled query ontology

    Args:
        request:

    Returns:

    """
    try:
        query_ontology_api.edit_status(
            query_ontology_api.get_by_id(request.POST["id"]),
            QueryOntologyStatus.uploaded.value,
        )
        return HttpResponse(json.dumps({}), content_type="application/javascript")
    except Exception as e:
        return HttpResponseBadRequest(str(e), content_type="application/javascript")


def activate_query_ontology(request):
    """activate a query ontology

    Args:
        request:

    Returns:

    """
    try:
        query_ontology_api.edit_status(
            query_ontology_api.get_by_id(request.POST["id"]),
            QueryOntologyStatus.active.value,
        )
        return HttpResponse(json.dumps({}), content_type="application/javascript")
    except Exception as e:
        return HttpResponseBadRequest(str(e), content_type="application/javascript")


class EditOntologyView(EditObjectModalView):
    form_class = EditOntologyForm
    model = QueryOntology
    success_url = reverse_lazy("admin:core_explore_tree_app_query_ontology")
    success_message = "Ontology edited with success."

    def _save(self, form):
        # Save treatment.
        try:
            self.object.title = form.cleaned_data.get("title")
            self.object.template = form.cleaned_data.get("template")
            query_ontology_api.upsert(self.object)
        except exceptions.NotUniqueError:
            form.add_error(
                None,
                "An object with the same name already exists. Please choose "
                "another name.",
            )
        except Exception as e:
            form.add_error(None, str(e))

    def get_initial(self):
        initial = super(EditOntologyView, self).get_initial()
        initial["template"] = self.object.template.id
        return initial

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(EditOntologyView, self).get_form_kwargs(*args, **kwargs)
        kwargs["request"] = self.request
        return kwargs


class DeleteOntologyView(DeleteObjectModalView):
    model = QueryOntology
    success_url = reverse_lazy("admin:core_explore_tree_app_query_ontology")
    success_message = "Ontology deleted with success."
    field_for_name = "title"

    def _delete(self, request, *args, **kwargs):
        # Delete treatment.
        query_ontology_api.delete(self.object)

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(DeleteOntologyView, self).get_form_kwargs(*args, **kwargs)
        kwargs["request"] = self.request
        return kwargs


def core_cache_all_files(request):
    """Function that cache all files under the selected node.

    Args:
        request:

    Returns:

    """
    try:
        # cache all the files from the current node
        root_node_id = request.POST.get("node_id", None)
        root_node = Navigation.get_by_id(root_node_id)
        active_ontology = query_ontology_api.get_active()
        # get the navigation from the cache
        nav_key = str(active_ontology.id)
        # get id of the navigation root
        if nav_key in navigation_cache:
            navigation = navigation_cache.get(nav_key)
            nav_root_id = navigation.id
        dico_list = {}
        for navigation_id in root_node.children:
            leaves_nodes = []
            # Get all children leaves from the node
            get_leafs_nodes(navigation_id, leaves_nodes)
            dico_list[navigation_id] = leaves_nodes
        # Cache all includes files under the node
        if dico_list:
            for k, v in list(dico_list.items()):
                for leaf_id in v:
                    cache_docs_from_leaf(leaf_id, request, nav_root_id)
        else:
            cache_docs_from_leaf(root_node_id, request, nav_root_id)
        message = Message(messages.SUCCESS, "Documents cached with success.")
        return HttpResponse(
            json.dumps({"message": message.message, "tags": message.tags}),
            content_type="application/json",
        )
    except:
        message = Message(messages.ERROR, "An error occurred while caching the files.")
        return HttpResponseBadRequest(message, content_type="application/javascript")


def get_leafs_nodes(navigation_id, l):
    """Function that gets all leaves nodes under the current node.

    Args:
        navigation_id: node ID
        l: list
    Returns:
        list of leaves nodes for the current node
    """
    try:
        node = Navigation.get_by_id(navigation_id)
        if node.children:
            [get_leafs_nodes(child, l) for child in node.children]
        else:
            l.append(node.id)
    except Exception as e:
        logger.warning("get_leafs_nodes threw an exception: {0}".format(str(e)))


def cache_docs_from_leaf(node_id, request, nav_root_id):
    """Function that build the files from the current node, cache them, create a DataCached objects and save them in the Database.

    Args:
        request:

    Returns:

    """
    leaves = Leaf.get_all()
    for leaf in leaves:
        if leaf.current_node_id == str(node_id):
            # Get all docs under the node
            docslist = leaf.docs_list
            # Cache all files under the node
            for doc_id in docslist:
                request2 = request
                mutable = request2.POST._mutable
                request2.POST._mutable = True
                request2.POST["nav_id"] = nav_root_id
                request2.POST["doc_id"] = doc_id
                request2.POST["node_id"] = leaf.current_node_id
                request2.POST._mutable = mutable
                load_view(request2)


def core_clear_cache(request):
    # Delete caches objects from the database
    data_cached_api.clean_datacached_objects()
    leaf_api.clean_leaves_objects()
    navigation_api.clean_navigation_objects()

    # Clear real caches
    leaf_cache.clear()
    html_tree_cache.clear()
    navigation_cache.clear()
    branch_cache.clear()
    link_cache.clear()

    message = Message(messages.SUCCESS, "Cached objects deleted with success.")
    return HttpResponse(
        json.dumps({"message": message.message, "tags": message.tags}),
        content_type="application/json",
    )
