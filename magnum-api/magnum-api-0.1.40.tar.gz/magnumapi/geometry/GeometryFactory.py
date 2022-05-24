from typing import List, Dict

import pandas as pd
from roxieapi.cadata.CableDatabase import CableDatabase

from magnumapi.geometry.GeometryBuilder import GeometryBuilder, SlottedGeometryBuilder
from magnumapi.geometry.Geometry import Geometry
import pymbse.commons.json_file as json_file
import roxieapi.tool_adapter.roxie_api as RoxieAPI


class GeometryFactory:
    """ GeometryFactory implements a factory design pattern and is used to produce:
    - rectangular geometry
    - absolute cos-theta geometry
    - relative cos-theta geometry
    - slotted absolute cos-theta geometry
    - slotted relative cos-theta geometry

    """

    @classmethod
    def init_with_json(cls, json_file_path: str, cadata: CableDatabase) -> Geometry:
        """ Class method initializing a Geometry instance from a JSON file.

        :param json_file_path: a path to a json file
        :param cadata: a CableDatabase instance
        :return: initialized geometry instance
        """
        json_content = json_file.read(json_file_path)
        return cls.init_with_dict(**json_content, cadata=cadata)

    @classmethod
    def init_with_dict(cls,
                       block_defs: List[Dict],
                       layer_defs: List[Dict],
                       cadata: CableDatabase) -> Geometry:
        """ Class method initializing a Geometry instance from a list of dictionaries with block definition.

        :param block_defs: a list of dictionaries with geometry definition (block definition)
        :param layer_defs: a list of dictionaries with layer definitions
        :param cadata: a CableDatabase instance
        :return: initialized geometry instance
        """
        return GeometryBuilder() \
            .with_block_defs(block_defs, cadata) \
            .with_layer_defs(layer_defs) \
            .build()

    @classmethod
    def init_slotted_with_json(cls, json_file_path: str, cadata: CableDatabase) -> Geometry:
        """ Class method initializing a Geometry instance from a JSON file.

        :param json_file_path: a path to a json file
        :param cadata: a CableDatabase instance
        :return: initialized geometry instance
        """
        json_content = json_file.read(json_file_path)
        return cls.init_slotted_with_dict(**json_content, cadata=cadata)

    @classmethod
    def init_slotted_with_dict(cls,
                               block_defs: List[Dict],
                               layer_defs: List[Dict],
                               cadata: CableDatabase,
                               r_aperture: float) -> Geometry:
        """ Class method initializing a Geometry instance from a list of dictionaries with block definition.

        :param block_defs: a list of dictionaries with geometry definition (block definition)
        :param layer_defs: a list of dictionaries with layer definitions
        :param cadata: a CableDatabase instance
        :param r_aperture: aperture radius in mm
        :return: initialized geometry instance
        """
        return SlottedGeometryBuilder() \
            .with_block_defs(block_defs, cadata) \
            .with_layer_defs(layer_defs) \
            .with_r_aperture(r_aperture) \
            .build()

    @classmethod
    def init_with_data(cls, data_file_path: str, cadata: CableDatabase) -> Geometry:
        """ Class method initializing a Geometry instance from a DATA ROXIE file.

        :param data_file_path: a path to a json file
        :param cadata: a CableDatabase instance
        :return: initialized geometry instance
        """
        block_df = RoxieAPI.read_bottom_header_table(data_file_path, keyword='BLOCK')
        layer_df = RoxieAPI.read_nested_bottom_header_table(data_file_path, keyword='LAYER')
        return cls.init_with_df(block_df, layer_df, cadata)

    @classmethod
    def init_with_csv(cls,
                      block_csv_file_path: str,
                      layer_csv_file_path: str,
                      cadata: CableDatabase) -> Geometry:
        """ Class method initializing a Geometry instance from a CSV file.

        :param block_csv_file_path: a path to a csv file with block definitions
        :param layer_csv_file_path: a path to a csv file with layer definitions
        :param cadata: a CableDatabase instance
        :return: initialized geometry instance
        """
        block_df = pd.read_csv(block_csv_file_path, index_col=0)
        layer_df = pd.read_csv(layer_csv_file_path, index_col=0)
        return cls.init_with_df(block_df, layer_df, cadata)

    @classmethod
    def init_with_df(cls, block_df: pd.DataFrame, layer_df, cadata: CableDatabase) -> Geometry:
        """ Class method initializing a Geometry instance from a dataframe with block definition.

        :param block_df: a dataframe with geometry definition (block definition)
        :param cadata: a CableDatabase instance
        :return: initialized geometry instance
        """
        return GeometryBuilder() \
            .with_block_df(block_df, cadata) \
            .with_layer_df(layer_df) \
            .build()

    @classmethod
    def init_slotted_with_data(cls, data_file_path: str, cadata: CableDatabase, r_aperture: float) -> Geometry:
        """ Class method initializing a Geometry instance from a DATA ROXIE file.

        :param data_file_path: a path to a json file
        :param cadata: a CableDatabase instance
        :param r_aperture: aperture radius in mm
        :return: initialized geometry instance
        """
        block_df = RoxieAPI.read_bottom_header_table(data_file_path, keyword='BLOCK')
        layer_df = RoxieAPI.read_nested_bottom_header_table(data_file_path, keyword='LAYER')
        return cls.init_slotted_with_df(block_df, layer_df, cadata, r_aperture)

    @classmethod
    def init_with_csv_slotted(cls,
                      block_csv_file_path: str,
                      layer_csv_file_path: str,
                      cadata: CableDatabase,
                      r_aperture: float) -> Geometry:
        """ Class method initializing a Geometry instance from a CSV file.

        :param block_csv_file_path: a path to a csv file with block definitions
        :param layer_csv_file_path: a path to a csv file with layer definitions
        :param cadata: a CableDatabase instance
        :param r_aperture: aperture radius in mm
        :return: initialized geometry instance
        """
        block_df = pd.read_csv(block_csv_file_path, index_col=0)
        layer_df = pd.read_csv(layer_csv_file_path, index_col=0)
        return cls.init_slotted_with_df(block_df, layer_df, cadata, r_aperture)

    @classmethod
    def init_slotted_with_df(cls,
                             block_df: pd.DataFrame,
                             layer_df: pd.DataFrame,
                             cadata: CableDatabase,
                             r_aperture: float) -> Geometry:
        """ Class method initializing a Geometry instance from a dataframe with block definition.

        :param block_df: a dataframe with geometry definition (block definition)
        :param cadata: a CableDatabase instance
        :param r_aperture: aperture radius in mm
        :return: initialized geometry instance
        """
        return SlottedGeometryBuilder() \
            .with_block_df(block_df, cadata) \
            .with_layer_df(layer_df) \
            .with_r_aperture(r_aperture) \
            .build()
