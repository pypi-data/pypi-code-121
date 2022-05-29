#!/usr/bin/env python3

"""
The sosi module contains functions for dealing with data from
geonorge in the Norwegian SOSI format using OSGeo tools
esp. GDAL and the OGR SOSI driver
"""

import os
from zipfile import ZipFile

from osgeo import ogr


def recode_sosi(sosi_path):
    """
    Re-code a SOSI file to encodings supported byt OpenFYBA lib if needed

    :param sosi_path: Path to a SOSI file
    :type sosi_path: str

    :returns: Path to the re-coded SOSI path
    :rtype: str
    """
    sosi_path_iso = sosi_path.replace(".sos", "_iso.sos")
    # Valid encodings according to SOSI standard
    sosi_encodings = (
        "UTF-8",
        "ISO8859-1",
        "ISO8859-10",
        "ANSI",
        "DOSN8",
        "DECN7",
        "ND7",
    )

    # Most comprehensive encoding supported by the GDAL SOSI driver
    target_encoding = "ISO8859-10"
    source_encoding = None
    for encoding in sosi_encodings:
        try:
            with open(sosi_path, "r", encoding=encoding) as sos:
                sosi_content = sos.read()
                source_encoding = encoding
                break
        except UnicodeDecodeError as e:
            print(f"Encoding of {sosi_path} is not {encoding}")
            pass
    if source_encoding is None:
        raise Exception(f"Could not read SOSI file {sosi_path} with valid encodings")
    if source_encoding == "UTF-8":
        # Remove BOM
        if sosi_content.startswith("\ufeff"):
            sosi_content = sosi_content.lstrip("\ufeff")
        sosi_content = sosi_content.split("\n")
        for idx in range(10):
            if "..TEGNSETT " in sosi_content[idx]:
                sosi_content[idx] = f"..TEGNSETT {target_encoding}"
        try:
            with open(sosi_path_iso, "w", encoding=target_encoding) as iso_sos:
                iso_sos.write("\n".join(sosi_content))
        except UnicodeDecodeError as e:
            print(f"Could not encode data in {sosi_file} with {target_encoding}")
            print(f"Got the following error:\n{e}")
            print("Replacing invalid characters")
            with open(
                sosi_path_iso, "w", encoding=target_encoding, errors="replace"
            ) as iso_sos:
                iso_sos.write("\n".join(sosi_content))
        os.replace(sosi_path_iso, sosi_path)
    return sosi_path


def extract_metadata(opath, target_srs=(32633, 25833, 3045), layer_name="polygons"):
    """
    Get metadata from a SOSI file spit by objecttype
    incl. column names and types, SRS match

    :param opath: Path to a SOSI file
    :type opath: str
    :param target_srs: EPSG codes for target SRS
    :type target_srs: list of int
    :param layer_name: Name of the sosi layer to process
    :type layer_name: str

    :returns: Dict with metadata
    :rtype: dict
    """

    attributes_count = {}

    # Open SOSI file
    ogr_ds = ogr.GetDriverByName("SOSI").Open(opath)
    # Get SRS and check if it matches the target SRS
    srs = ogr_ds.GetLayerByIndex(0).GetSpatialRef()
    # List layers
    layers = [
        ogr_ds.GetLayerByIndex(idx).GetName() for idx in range(ogr_ds.GetLayerCount())
    ]
    # Extract relevant layers
    layer = ogr_ds.GetLayerByName(layer_name)
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
    field_names = [field[0] for field in fields]
    field_names_lower = [field[0].lower() for field in fields]
    # List object types
    # Get a list of non-null attribute columns per object type
    # Could be limited to relevant object types
    # layer.SetAttributeFilter(f"objekttypenavn = '{object_type}'")
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

    ogr_ds = None
    for object_type in attributes_count:
        attributes_count[object_type] = {
            key: val for key, val in attributes_count[object_type].items() if val
        }

    return {
        "object_types": attributes_count,
        "projection_match": srs.GetAttrValue("AUTHORITY", 1) in target_srs,
        "fields": fields,
    }


def extract_and_parse_sosi(zip_file, workdir="./"):
    """
    Extract SOSI files from ZIP, recode if needed and compile metadata

    :param zip_file: Path to a zipfile containing SOSI files
    :type zip_file: str
    :param workdir: Path to the working directory to which files should be unpacked
    :type workdir: str

    :returns: A dictionary with sosi path as ky and etadata as content
    :rtype: dict
    """
    zipname = zip_file
    file_content = {}
    with ZipFile(zip_file) as zip_file:
        members = [
            sos_name for sos_name in zip_file.namelist() if sos_name.endswith(".sos")
        ]
        if len(members) == 0:
            print(f"No data to extract from {zip_file.filename}")
            zip_file.close()
            return

        for member in members:
            # if any([kid in member for kid in ["1576", "1573"]]):
            #     print("Skipping: ", os.path.join(workdir, member))
            #     zip_file.close()
            #     continue
            print("Processing", os.path.join(workdir, member))
            sosi_path = os.path.join(workdir, member)
            if os.path.exists(sosi_path):
                print(
                    f"""File "{os.path.join(workdir, member)} from {zipname} exists."""
                )
            # Extract SOSI file
            zip_file.extract(member, path=workdir)

            # print(f"""Processing file "{os.path.join(workdir, member)} from {zipname}""")

            # Recode SOSI file if required
            opath = recode_sosi(sosi_path)
            # Add file info to metadata dict
            file_content[opath] = extract_metadata(opath)
        zip_file.close()
    return file_content
