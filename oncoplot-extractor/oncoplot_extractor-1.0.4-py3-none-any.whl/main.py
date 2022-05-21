"""Contains OncoPlotExtractor class."""

import json
import os
from typing import DefaultDict

import pandas as pd
from PIL import Image

from .errors import OncoPlotExtractorError


class OncoplotExtractor:
    """Extracts oncoplot data from oncoplot image and exports to excel.

    :param path: path to oncoplot image [str] : required
    :param corners: (x1, y1, x2, y2) top left and bottom right corner of oncoplot [tuple] : optional
    :param background_color: background color of oncoplot [list] : optional
    :param gene_list: list of genes to extract [list] : optional

    :Example:
    .. code-block:: python

        oce = OncoplotExtractor(path="path/to/oncoplot.png", corners=(0,0,100,100), background_color=["#ffffff"])
        oce.extract()
        oce.export_to_excel("path/to/oncoplot.xlsx")

    """

    FILEPATH: str
    CORNERS: tuple
    IMG: Image.Image
    BG_COLOR: list
    DATA_AS_DICT: DefaultDict = DefaultDict()
    GENE_LIST: list

    def __init__(
        self,
        path: str,
        corners: tuple = None,
        background_color: list = ["#ffffff"],
        gene_list: list = None,
    ) -> None:
        """Extractor for oncoplot images, expects `path` of image
        file, `corners`,  `background_color` and `gene_list` of oncoplot. Format of corners is
        (x1, y1, x2, y2), top left and bottom right corner."""
        if not self._check_if_file_exists(path):
            raise OncoPlotExtractorError(f"File {path} does not exist.")
        self.FILEPATH = path
        self.CORNERS = corners
        self.IMG = self._get_rgb_image_data()
        self.BG_COLOR = background_color
        self.GENE_LIST = gene_list

    def _check_if_file_exists(self, path):
        """Checks if file exists at `path`."""
        return os.path.isfile(path)

    def _get_rgb_image_data(self) -> Image.Image:
        """Returns image data from `self.FILEPATH`."""
        return Image.open(self.FILEPATH).convert("RGB")

    def _crop_image(self, img: Image.Image, corners: tuple) -> Image.Image:
        """Crops image to oncoplot.
        :param img: image to crop
        :param corners: (x1, y1, x2, y2) top left and bottom right corner of oncoplot
        """
        return img.crop(corners)

    def _get_color_name_from_rgb(self, rgb: tuple) -> str:
        """Returns color hex code from
        :param name:rgb tuple format (r,g,b).
        """
        return "#{:02x}{:02x}{:02x}".format(*rgb)

    def _extract_row_poi(self, padding_left: int = 0) -> list:
        """Extracts row poi from oncoplot image.
        :param name:padding_left number of pixels to ignore left of image.
        :returns: list of row poi"""
        row_poi = []
        last_color = None
        for h in range(0, self.IMG.height):
            r, g, b = self.IMG.getpixel((padding_left, h))
            color = self._get_color_name_from_rgb((r, g, b))
            if color != last_color:
                if color not in self.BG_COLOR:
                    row_poi.append(h)
                last_color = color
        return row_poi

    def _extract_col_poi(self, row_pos: int) -> list:
        """
        Extracts column poi from oncoplot image.
        :param row_pos: row position of row poi
        :returns: list of column poi"""
        col_poi = []
        last_color = None
        for w in range(0, self.IMG.width):
            pixel = self.IMG.getpixel((w, row_pos))
            color = self._get_color_name_from_rgb(pixel)
            if color != last_color:
                if color not in self.BG_COLOR:
                    col_poi.append(color)
                last_color = color

        return col_poi

    def extract(self) -> None:
        """Extracts oncoplot data from image.
        Expects class to have been initialized with a valid image file
        """
        if self.CORNERS is not None:
            self.IMG = self._crop_image(self.IMG, self.CORNERS)
        rows = self._extract_row_poi()
        c = 0
        for row in rows:
            self.DATA_AS_DICT[c] = self._extract_col_poi(row)
            c += 1

    @property
    def as_dict(self) -> DefaultDict:
        """Returns oncoplot data as dictionary."""
        if len(self.DATA_AS_DICT) == 0:
            raise OncoPlotExtractorError(
                """
                Looks like you attempted to export data without extracting.
                Make sure you run `extract()` 
                function to generate data first."""
            )
        return self.DATA_AS_DICT

    @property
    def as_dataframe(self) -> pd.DataFrame:
        """Returns oncoplot data as pandas dataframe."""
        if self.GENE_LIST is not None:
            index = pd.Index(self.GENE_LIST)
            return pd.DataFrame(self.as_dict, index=index)
        return pd.DataFrame(self.as_dict)

    def export_to_excel(self, filepath: str) -> None:
        """Exports oncoplot data to excel.
        :param filepath: path to excel file to export to.
        """
        self.as_dataframe.to_excel(filepath)

    def export_to_json(self, filepath: str) -> None:
        """Exports oncoplot data to json.
        :param filepath: path to json file to export to."""
        with open(filepath, "w") as f:
            json.dump(self.as_dict, f)

    def pixel_to_hex(self, coord) -> str:
        """Returns hex value of pixel at `coord`."""
        return self._get_color_name_from_rgb(self.IMG.getpixel(coord))

    def background_color(self, coord: tuple) -> list:
        """Returns background color of pixel at `coord`.
        :param coord: (x,y) coordinate of pixel"""
        return [self.pixel_to_hex(coord)]

    def get_background_from_pixel(self, coord: tuple) -> None:
        """sets background color of image at `coord` so this pixel is filtered.
        :param coord: (x,y) coordinate of pixel"""
        self.BG_COLOR = self.background_color(coord)
