#!/usr/bin/env python3

"""
The utils module contains simple helper functions that are used in other submodules
"""

import warnings
from itertools import islice
from zipfile import ZipFile

# Non-builtin imports
from osgeo import ogr

#: Define cast order for SQL data types starting being possible to be casted from left to right
casts_order = ["Integer", "Real", "Double precision", "Date", "DateTime", "String"]

#: Define possible type casts for OGR SQL
ogr_casts = {
    "String": "character(0)",
    "Integer": "integer",
    "Date": "date",
    "Time": "time",
    "DateTime": "timestamp",
    "Real": "float",
    "Double precision": "numeric",
}


def slice_dict(data_dict, number_of_chunks):
    """
    Split a ditct in to a given number of chunks
    e.g. in order to distribute chunks to paralel processing

    :param data_dict: A dict object to slice
    :type data_dict: dict
    :param number_of_chunks: Number of chunks to produce (e.g. = number of cores to use)
    :type number_of_chunks: int

    :returns: A copy of the input string with norwegian non-ascii characters replaced
    :rtype: str
    """

    data_iterator = iter(data_dict)
    chunk_size = (
        int(len(data_dict) // number_of_chunks) + 1
        if len(data_dict) // number_of_chunks > 0
        else 0
    )
    for element in range(0, len(data_dict), chunk_size):
        yield {e: data_dict[e] for e in islice(data_iterator, chunk_size)}


def norwegian_to_ascii(string):
    """
    Replace norwegian non-ascii characters

    :param string: A string from that norwegian non-ascii characters should be replaced
    :type string: str

    :returns: A copy of the input string with norwegian non-ascii characters replaced
    :rtype: str

    :example:
    >>> print(norwegian_to_ascii("Gjærsjømåke"))
    'Gjarsjomake'
    """
    replacement_dict = {
        "Å": "A",
        "å": "a",
        "Ø": "O",
        "ø": "o",
        "Æ": "A",
        "æ": "a",
    }
    ascii_string = ""
    for s in string:
        ascii_string += replacement_dict[s] if s in replacement_dict else s
    return ascii_string


def compile_ogr_cmd(
    connection_string,
    schema,
    projection_handling,
    ogr_file,
    table_name,
    layer=None,
    sql_string=None,
    where=None,
    overwrite=False,
):
    """
    Compile ogr2ogr command to load data to PostGIS

    :param connection_string: A string from that norwegian non-ascii characters should be replaced
    :type connection_string: str
    :param schema: Name of the schema to add to
    :type schema: str
    :param connection_string: A string from that norwegian non-ascii characters should be replaced
    :type connection_string: str
    :param table_name: Name of the table to write to
    :type table_name: str
    :param file: Path to the file to import
    :type file: str
    :param layer: Name of the layer to import (alternative to sql_string option)
    :type layer: str
    :param sql_string: SQL select statement to define import from file (alternative to layer option)
    :type sql_string: str
    :param where: SQL WHERE-clause without the 'WHERE' keyword to limit import
    :type where: str
    :param overwrite: Allow overwriting of existing table
    :type overwrite: bool

    :returns: A copy of the input string with norwegian non-ascii characters replaced
    :rtype: str
    """

    if sql_string and layer:
        raise ValueError("sql_string and layer are mutually excusive")
    if sql_string and where:
        raise ValueError("sql_string and where are mutually excusive")
    if not sql_string and not layer:
        raise ValueError("Either sql_string or layer have to be given")

    # Define create or update mode
    cmd = [
        "/home/NINA.NO/stefan.blumentrath/gdal_inst/bin/ogr2ogr",
        "-lco",
        "GEOMETRY_NAME=geom",
        "-lco",
        "FID=gid",
        "-lco",
        "SPATIAL_INDEX=NONE",
    ]

    if overwrite:
        cmd += ["-overwrite"]
    else:
        cmd += [
            "-update",
            "-append",
        ]

    cmd += [
        "--config",
        "PG_USE_COPY",
        "YES",
        *projection_handling,
        "-f",
        "PostgreSQL",
        "-makevalid",
        "-skipfailure",
        "-nlt",
        "PROMOTE_TO_MULTI",
        "-nln",
        f"{schema}.{table_name}",
    ]

    if sql_string:
        cmd += [
            "-sql",
            sql_string,
        ]

    if where:
        cmd += [
            "-where",
            where,
        ]

    cmd += [f"PG:{connection_string} active_schema={schema}", ogr_file]

    if layer:
        cmd += [layer]

    return cmd


def remove_suffixes(string, suffixes):
    """
    Remove suffix of a string (helper function for Python < 3.9 which contains
    that a similar function

    :param string: String to remove suffix from
    :type string: str
    :param suffixes: Suffix(es) to remove from string
    :type suffixes: str or tuple of str

    :returns: A string with suffix removed
    :rtype: str
    """
    if type(suffixes) == str:
        if string.endswith(suffixes):
            string = string[: -len(suffixes)]
    else:
        for suffix in suffixes:
            if string.endswith(suffix):
                string = string[: -len(suffix)]
    return string


def extract_zip(zip_path, workdir="./"):
    """
    Extract all members of a zip archive to the given working directory

    :param zip_path: Path to a zipfile containing files from geonorge
    :type zip_path: str
    :param workdir: Path to the working directory to which files should be unpacked
    :type workdir: str

    :returns: A list of members of the zip file
    :rtype: list
    """
    with ZipFile(zip_path) as zip_file:
        zip_file.extractall(path=workdir)
        return (zip_path, zip_file.namelist())


def extract_metadata(
    ogr_file,
    target_srs=(32633, 25833, 3045, 5973),
    split_by_objtype=False,
    layer_name=None,
):
    """
    Get metadata from a OGR readable file
    incl. column names and types, SRS match

    :param ogr_file: Path to an OGR readable file
    :type ogr_file: str
    :param target_srs: EPSG codes for target SRS
    :type target_srs: list of int
    :param split_by_objtype: Extract object types from attribute column
    :type split_by_objtype: bool
    :param layer_name: Name of the sosi layer to process
    :type layer_name: str

    :returns: Dict with metadata
    :rtype: dict
    """

    attributes_count = {}

    # Open OGR file
    ogr_ds = ogr.Open(ogr_file)

    if not ogr_ds:
        raise OSError(f"Could not open datset {ogr_file}")

    # List layers
    layers = [
        ogr_ds.GetLayerByIndex(idx).GetName() for idx in range(ogr_ds.GetLayerCount())
    ]

    result_dict = {}

    if layer_name:
        if layer_name not in layers:
            warnings.warn(f"Layer {layer_name} not found in {ogr_file}")
            return result_dict
        layers = [layer_name]

    if not layers:
        warnings.warn(f"No layers found to parse in {ogr_file}")
        return result_dict

    for layer_name in layers:
        # Extract relevant layers
        layer = ogr_ds.GetLayerByName(layer_name)
        # Get SRS and check if it matches the target SRS
        srs = layer.GetSpatialRef()
        if srs:
            projection_match = int(srs.GetAttrValue("AUTHORITY", 1)) in target_srs
        else:
            projection_match = None

        # List fields
        layer_def = layer.GetLayerDefn()
        fields = sorted(
            [
                (
                    layer_def.GetFieldDefn(fid).GetName(),
                    layer_def.GetFieldDefn(fid).GetTypeName(),
                )
                for fid in range(layer_def.GetFieldCount())
            ]
        )
        # field_names = [field[0] for field in fields]
        # field_names_lower = [field[0].lower() for field in fields]
        # List object types
        # Get a list of non-null attribute columns per object type
        # Could be limited to relevant object types
        # layer.SetAttributeFilter(f"objekttypenavn = '{object_type}'")
        if split_by_objtype:
            for feature in layer:
                f_dict = feature.items()
                object_type = f_dict["objekttypenavn"]
                if object_type not in attributes_count:
                    attributes_count[object_type] = {}
                for a in f_dict:
                    if (
                        a not in attributes_count[object_type]
                        or not attributes_count[object_type][a]
                    ):
                        attributes_count[object_type][a] = f_dict[a]

                for object_type in attributes_count:
                    attributes_count[object_type] = {
                        key: val
                        for key, val in attributes_count[object_type].items()
                        if val
                    }
        else:
            attributes_count = None

        result_dict[layer_name] = {
            "object_types": attributes_count,
            "projection_match": projection_match,
            "fields": fields,
        }

    ogr_ds = None
    return result_dict


def consolidate_attributes(file_content_dict):
    """
    Consolidates attributes of SOSI layers unifying data types to smallest common data type

    :param file_content_dict: A dictionary with file content from extract_and_parse_sosi function
    :type file_content_dict: dict

    :returns: A copy of the input dictionary with consolidated attributes
    :rtype: dict

    """
    file_fields = {}
    for sos_file, sos_content in file_content_dict.items():
        for layer, sos_metadata in sos_content.items():
            if layer not in file_fields:
                file_fields[layer] = {}
            for object_type in sos_metadata["object_types"]:
                if object_type not in file_fields:
                    file_fields[layer][object_type] = {}

                for field in sos_metadata["fields"]:
                    if field[0] in sos_metadata["object_types"][object_type] and (
                        field[0].lower() not in file_fields[layer][object_type]
                        or casts_order.index(field[1])
                        > casts_order.index(
                            file_fields[layer][object_type][field[0].lower()]
                        )
                    ):
                        file_fields[layer][object_type][field[0].lower()] = field[1]
    return file_fields
