""" Api for system operations
"""
from core_schema_viewer_app.components.sandbox_data_structure.models import (
    SandboxDataStructure,
)


def get_all_sandbox_data_structures():
    """

    Returns:

    """
    return SandboxDataStructure.get_all()
