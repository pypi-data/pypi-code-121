from typing import List, Union

SeriesVolumeCover = List[Union[str, int]]
"""A 4-element tuple containing the following elements:

1. The volume number.
2. A :ref:`relative url` to the png image of the cover.
3. A :ref:`relative url` to the webp image of the cover.
4. A :ref:`relative url` to the blurred png image of the cover.
"""
