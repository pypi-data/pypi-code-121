""" Core Insitu visualization apps config
"""
import sys

from django.apps import AppConfig


class CoreInsituVisualizationAppConfig(AppConfig):
    """Insitu visualization configuration"""

    name = "core_visualization_insitu_app"
    verbose_name = "Core Insitu Visualization App Config"

    def ready(self):
        """Run once at startup"""
        if "migrate" not in sys.argv:
            from core_visualization_insitu_app import discover

            discover.init_periodic_tasks()
