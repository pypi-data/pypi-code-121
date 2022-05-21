from typing import List, Union

from typing_extensions import TypedDict


class SeriesPageData(TypedDict):
    """
    SeriesPageData(data: Dict[str, Any]) -> SeriesPageData
    SeriesPageData(**attrs: Any) -> SeriesPageData
    A dictionary containing various metadata about a page."""

    series: str
    """The title of the series."""

    alt_titles: List[str]
    """A list of alternate titles for the series."""

    alt_titles_str: str
    """A string containing all alternate titles for the series."""

    series_id: int
    """The internal ID of the series."""

    slug: str
    """The slug of the series."""

    cover_vol_url: str
    """A :ref:`relative url` to the cover image of the series."""

    cover_vol_url_webp: str
    """An URL similar to :attr:`.cover_vol_url`, but the file is a ``.webp`` file."""

    metadata: List[List[Union[str, int]]]
    """A list of lists containing the metadata for each volume in the series. Each sub-list is actually a key-value
    pair, where the first element is the name and the second element is the value. The value can be a string or an
    integer.

    So far, the structure of the metadata is as follows:

    .. code-block:: json

        [
            [
                "Author",
                "<author>"
            ],
            [
                "Artist",
                "<artist>"
            ],
            [
                "Views",
                123456
            ],
            [
                "Last Updated",
                "Ch. <latest chapter number> - <year>-<month>-<day>"
            ]
        ]
    """

    synopsis: str
    """The synopsis of the series."""

    author: str
    """The author of the series."""

    chapter_list: List[List[Union[str, int, List[int]]]]
    """A list of lists containing information on each chapter.

    The sub-lists can be thought of as a tuple where the elements mean the following, in order:

    1. The chapter number.
    2. The chapter number (again).
    3. The chapter title.
    4. A slugified version of the chapter number. Dots are replaced with dashes. For integer chapter numbers this
       value should be the same as the first and second elements.
    5. The name of the group that uploaded the chapter or ``Multiple Groups`` if the chapter is uploaded by multiple
       groups.
    6. The date and time the chapter was published. This is another tuple-like list that has these elements:

       1. The year.
       2. The month, starting from 0.
       3. The day.
       4. The hour.
       5. The minute.
       6. The second.

    7. The chapter's volume (integer) or the string ``null``.
    """

    volume_list: List[List[Union[int, List[List[Union[str, List[int]]]]]]]
    """A list of lists containing information on each volume.

    The sub-lists can be thought of as a tuple where the elements mean the following, in order:

    1. The volume number.
    2. A list of lists containing chapters in the volume. Each chapter entry can be thought of as a tuple where the
       elements mean the following, in order:

       1. The chapter number.
       2. A slugified version of the chapter number. Dots are replaced with dashes. For integer chapter numbers this
          value should be the same as the first and second elements.
       3. The name of the group that uploaded the chapter or ``Multiple Groups`` if the chapter is uploaded by multiple
          groups.
       4. The date and time the chapter was published. This is another tuple-like list that has these elements:

          1. The year.
          2. The month, starting from 0.
          3. The day.
          4. The hour.
          5. The minute.
          6. The second.
    """

    root_domain: str
    """The root domain of the series. This is a domain name without the protocol."""

    canonical_url: str
    """The full  URL to the series page on the website."""

    relative_url: str
    """The :ref:`relative url` to the series page on the website."""

    available_features: List[str]
    """A list of features that are available for the series. This list is static for all responses and currently
    looks like:

    .. code-block:: json

        [
            "detailed",
            "compact",
            "volumeCovers",
            "rss",
            "download"
        ]
    """

    reader_modifier: str
    """The part of the :attr:`.relative_url` that does not contain the slug. The modifier can be used in conjunction
    with :attr`.slug` to construct the relative url to the series page."""

    embed_image: str
    """A full URL to the image that should be shown for Facebook/Twitter/other social media embeds."""

    version_query: str
    """A query string containing the first 7 characters of the git commit's SHA-1 ID that the server is running off
    of."""
