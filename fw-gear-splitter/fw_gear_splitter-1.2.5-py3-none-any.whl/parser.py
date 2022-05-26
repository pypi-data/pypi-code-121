"""Parser module to parse gear config.json."""
import typing as t
from pathlib import Path

from flywheel_gear_toolkit import GearToolkitContext


def parse_config(
    gear_context: GearToolkitContext,
) -> t.Tuple[Path, bool, t.List[str]]:
    """Parses gear_context config.json file.

    Returns:
        Tuple[Path, bool, t.List[str]]: tuple containing,
            - Path of dicom input
            - extract_localizer
            - group_by (unique tags to split archive on)
    """

    # INPUTS
    dcm_path = Path(gear_context.get_input_path("dicom"))

    # CONFIG
    extract_localizer = gear_context.config.get("extract_localizer")
    if gear_context.config.get("group_by", ""):
        group_by = gear_context.config.get("group_by").split(",")
    else:
        group_by = None

    return (
        dcm_path,
        extract_localizer,
        group_by,
    )
