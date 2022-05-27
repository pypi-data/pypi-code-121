"""Core Explore tree App Settings
"""
import os
from django.conf import settings

if not settings.configured:
    settings.configure()

BASE_DIR_EXPLORE_TREE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXPLORE_TREE_MENU_NAME = getattr(settings, "EXPLORE_TREE_MENU_NAME", "Explore Tree")
