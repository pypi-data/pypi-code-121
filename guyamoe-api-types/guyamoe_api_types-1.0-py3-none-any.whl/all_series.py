from typing import Dict

from typing_extensions import TypedDict


class SeriesSummary(TypedDict):
    """
    SeriesSummary(data: Dict[str, Any]) -> SeriesSummary
    SeriesSummary(**attrs: Any) -> SeriesSummary
    A series dictionary that contains a subset of the attributes found on a normal :class:`.Series`.
    This is returned on the API endpoint for all series.
    """

    author: str
    """The author of the series."""

    artist: str
    """The artist of the series."""

    description: str
    """The description of the series. May or may not contain HTML."""

    slug: str
    """The slug of the series."""

    cover: str
    """A :ref:`relative url` to the primary cover image of the series."""

    groups: Dict[str, str]
    """A dictionary of group IDs and their respective names.

    .. note::
        The groups dictionary is the **same** dictionary for all series when obtained
        via the ``/get_all_series`` endpoint. This dictionary may be different from
        the one obtained from the individual series endpoint.
    """

    last_updated: float
    """The Unix timestamp of when the series was last updated."""


AllSeries = Dict[str, SeriesSummary]
"""The root JSON document for all series is a dictionary where the keys are the title
of the series and the values are the :class:`.SeriesSummary` for that series.

A sample JSON document can be found at https://guya.moe/api/get_all_series/.
"""
