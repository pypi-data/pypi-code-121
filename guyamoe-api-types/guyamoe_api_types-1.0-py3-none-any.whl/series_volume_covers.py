from typing import List

from typing_extensions import TypedDict

from .series_volume_cover import SeriesVolumeCover


class SeriesVolumeCovers(TypedDict):
    """
    SeriesVolumeCovers(data: Dict[str, Any]) -> SeriesVolumeCovers
    SeriesVolumeCovers(**attrs: Any) -> SeriesVolumeCovers
    An object containing a list of volume covers for a series."""

    covers: List[SeriesVolumeCover]
    """The list of volume covers for the series."""
