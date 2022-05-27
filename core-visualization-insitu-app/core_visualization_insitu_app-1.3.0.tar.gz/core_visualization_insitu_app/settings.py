"""Core Visualization Insitu App Settings
"""

from django.conf import settings

if not settings.configured:
    settings.configure()

# MENU
VISUALIZATION_USER_MENU_NAME = getattr(
    settings, "VISUALIZATION_INSITU_USER_MENU_NAME", "Insitu Data Visualization"
)
