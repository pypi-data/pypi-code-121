""" Add Visualization Insitu in main menu
"""
from django.urls import reverse
from menu import Menu, MenuItem

visualization_insitu_children = (
    MenuItem(
        "Manage Insitu Data",
        reverse("admin:core_visualization_insitu_manage_data"),
        icon="list",
    ),
)

Menu.add_item(
    "admin",
    MenuItem("INSITU DATA VISUALIZATION", None, children=visualization_insitu_children),
)

Menu.add_item(
    "main",
    MenuItem("Insitu Data Visualization", reverse("core_visualization_insitu_index")),
)
