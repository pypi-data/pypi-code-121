""" Add View Schema in main menu
"""
from django.urls import reverse

from menu import Menu, MenuItem
from core_schema_viewer_app.settings import SCHEMA_VIEWER_MENU_NAME

Menu.add_item(
    "main", MenuItem(SCHEMA_VIEWER_MENU_NAME, reverse("core_schema_viewer_index"))
)

schema_viewer_children = (
    MenuItem(
        "Templates Visibility",
        reverse("admin:core_schema_viewer_app_template"),
        icon="list",
    ),
)

Menu.add_item("admin", MenuItem("SCHEMA VIEWER", None, children=schema_viewer_children))
