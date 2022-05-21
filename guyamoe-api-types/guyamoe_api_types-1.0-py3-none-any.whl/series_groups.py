from typing import Dict

from typing_extensions import TypedDict


class SeriesGroups(TypedDict):
    """
    SeriesGroups(data: Dict[str, Any]) -> SeriesGroups
    SeriesGroups(**attrs: Any) -> SeriesGroups
    A dictionary containing the groups that released chapters for the series."""

    groups: Dict[str, str]
    """A dictionary of group IDs and their respective names."""
