""" Menu configuration for core_explore_tree_app.
"""
from django.urls import reverse
from menu import Menu, MenuItem

from core_explore_tree_app.settings import EXPLORE_TREE_MENU_NAME

ontology_children = (
    MenuItem(
        "OWL files", reverse("admin:core_explore_tree_app_query_ontology"), icon="list"
    ),
    MenuItem(
        "Upload New OWL", reverse("admin:core_explore_tree_app_upload"), icon="upload"
    ),
)
cache_manager_children = (
    MenuItem("Cache status", reverse("admin:core_cache_view_index"), icon="sitemap"),
    MenuItem("Manual cache", reverse("admin:core_cache_manager_index"), icon="sitemap"),
)

Menu.add_item("admin", MenuItem("EXPLORATION TREE", None, children=ontology_children))
Menu.add_item(
    "admin",
    MenuItem("CACHE MANAGER EXPLORE TREE", None, children=cache_manager_children),
)

Menu.add_item(
    "main", MenuItem(EXPLORE_TREE_MENU_NAME, reverse("core_explore_tree_index"))
)
