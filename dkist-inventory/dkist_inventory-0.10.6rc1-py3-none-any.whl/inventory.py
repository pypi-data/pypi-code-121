"""
Helper functions for parsing files and processing headers.
"""
import datetime
import re
from functools import partial
from pathlib import Path
from typing import Any, Dict, List, Mapping

import astropy.units as u
import numpy as np
import scipy.stats
from astropy.io import fits
from astropy.table import Table
from dkist_fits_specifications.utils.formatter import reformat_spec214_header
from ndcube import NDCube

from dkist_inventory.transforms import TransformBuilder

__all__ = ['generate_inventory_from_frame_inventory', 'headers_from_filenames']


def process_json_headers(bucket, json_headers):
    """
    Extract the filenames and FITS headers from the inventory headers.

    Parameters
    ----------
    bucket: `str`
        The bucket in which the dataset resides.
    json_headers : `list` of `dict
        A list of dicts containing the JSON version of the headers as stored in inventory.

    Returns
    --------
    filenames
        The filenames (object keys) of the FITS files.
    fits_headers
        The FITS headers.
    extra_inventory
        The inventory keys directly extracted from the frame inventory

    """
    known_non_fits_keys = {
        "_id",
        "bucket",
        "frameStatus",
        "objectKey",
        "createDate",
        "updateDate",
        "lostDate",
        "headerHDU",
        "COMMENT",
        "",
    }
    fits_keys = set(json_headers[0].keys()).difference(known_non_fits_keys)

    def key_filter(keys, headers):
        return {x: headers[x] for x in keys if x in headers}

    non_fits_headers = list(map(partial(key_filter, known_non_fits_keys), json_headers))
    fits_headers = list(map(partial(key_filter, fits_keys), json_headers))

    filenames = [Path(h["objectKey"]).name for h in non_fits_headers]

    extra_inventory = {
        "original_frame_count": len(json_headers),
        "bucket": bucket,
        "create_date": datetime.datetime.utcnow().isoformat("T"),
    }

    return filenames, fits_headers, extra_inventory


def headers_from_filenames(filenames, hdu=0):
    """
    Generator to get the headers from filenames.
    """
    # Here we filter out empty cards and COMMENT cards
    filter_keys = ("", "COMMENT")
    headers = [dict(fits.getheader(fname, ext=hdu)) for fname in filenames]
    headers = [dict(filter(lambda x: x[0] not in filter_keys, h.items())) for h in headers]
    return Table(headers)


def table_from_headers(headers):
    """
    Convert a list of dicts into a table.

    This also orders the columns of the table as if it were a 214 FITS file.
    """
    formatted_header = reformat_spec214_header(fits.Header(headers[0]))
    ordered_keys = [key for key in formatted_header.keys() if key in headers[0].keys()]
    return Table(rows=headers, names=ordered_keys)


def validate_headers(table_headers):
    """
    Given a bunch of headers, validate that they form a coherent set.

    This function also adds the headers to a list as they are read from the
    file.

    Parameters
    ----------
    table_headers :  iterator
        An iterator of headers.

    Returns
    -------
    out_headers : `list`
        A list of headers.
    """
    t = table_headers

    # Let's do roughly the minimal amount of verification here for construction
    # of the WCS. Validation for inventory records is done independently.

    # For some keys all the values must be the same
    same_keys = ["NAXIS", "DNAXIS"]
    naxis_same_keys = ["NAXISn", "CTYPEn", "CUNITn"]
    dnaxis_same_keys = ["DNAXISn", "DTYPEn", "DPNAMEn", "DWNAMEn"]
    # Expand n in NAXIS keys
    for nsk in naxis_same_keys:
        for naxis in range(1, t["NAXIS"][0] + 1):
            same_keys.append(nsk.replace("n", str(naxis)))
    # Expand n in DNAXIS keys
    for dsk in dnaxis_same_keys:
        for dnaxis in range(1, t["DNAXIS"][0] + 1):
            same_keys.append(dsk.replace("n", str(dnaxis)))

    validate_t = t[same_keys]

    for col in validate_t.columns.values():
        if not all(col == col[0]):
            raise ValueError(f"The {col.name} values did not all match:\n {col}")

    return table_headers


def make_sorted_table(headers, filenames):
    """
    Return an `astropy.table.Table` instance where the rows are correctly sorted.
    """
    if not isinstance(headers, Table):
        raise TypeError("This function expects an Astropy Table.")

    theaders = headers.copy()
    theaders["filenames"] = filenames
    theaders["headers"] = headers
    dataset_axes = headers[0]["DNAXIS"]
    array_axes = headers[0]["DAAXES"]
    keys = [f"DINDEX{k}" for k in range(dataset_axes, array_axes, -1)]
    t = np.array(theaders[keys])
    return theaders[np.argsort(t, order=keys)]


def group_mosaic_tiles(table_headers):
    if "MINDEX1" not in table_headers.colnames:
        return table_headers
    return table_headers.group_by(("MINDEX1", "MINDEX2"))


def _inventory_from_wcs(wcs):
    """
    This function extracts the extents of various world axes to put into
    inventory.

    It does this by calculating all the coordinates of all axes anywhere in the
    array and then finding the maxima.

    It aims to be as general as possible, despite this possibly being overkill,
    just to minimise the chances that this needs changing in the future. To do
    this is uses a bunch of wcs trickery which will be explained inline.
    """
    ndc = NDCube(np.broadcast_to(np.empty((1,)), wcs.array_shape), wcs=wcs)
    world_coords = ndc.axis_world_coords_values()._asdict()

    # These are the world axis physical types (mangled by axis_world_coords_values)
    # which we want to parse if they are present.
    known_fields = set(("custom_pos_helioprojective_lat",
                        "custom_pos_helioprojective_lon",
                        "em_wl",
                        "time",
                        "phys_polarization_stokes"))

    required_fields = set(("custom_pos_helioprojective_lat",
                           "custom_pos_helioprojective_lon",
                           "time"))

    # Validate the required fields are present
    present_world_types = known_fields.intersection(world_coords.keys())
    if not present_world_types.issuperset(required_fields):
        raise ValueError("The WCS being converted to inventory needs HPC lat and lon "
                         "as well as temporal axes."
                         f"This one only has {present_world_types}.")

    # Calculate the min and max values along each world axis
    for field in present_world_types:
        min_dict = {field: np.min(world_coords[field]) for field in present_world_types}
        max_dict = {field: np.max(world_coords[field]) for field in present_world_types}

    # Do some WCS trickery to extract the callable which converts the time
    # delta returned by axis_world_coords into a Time object that we can
    # convert to a string.
    time_index = wcs.world_axis_physical_types.index("time")
    time_key = wcs.world_axis_object_components[time_index][0]
    time_converter = wcs.world_axis_object_classes[time_key][3]

    # Construct all required inventory fields
    inventory = {'boundingBox': ((min_dict["custom_pos_helioprojective_lon"].to_value(u.arcsec),
                                  min_dict["custom_pos_helioprojective_lat"].to_value(u.arcsec)),
                                 (max_dict["custom_pos_helioprojective_lon"].to_value(u.arcsec),
                                  max_dict["custom_pos_helioprojective_lat"].to_value(u.arcsec))),
                 'startTime': time_converter(min_dict["time"],
                                             unit=min_dict["time"].unit).datetime.isoformat('T'),
                 'endTime': time_converter(max_dict["time"],
                                           unit=max_dict["time"].unit).datetime.isoformat('T')}

    # Add wavelength fields if the wavelength axis is present
    if "em_wl" in present_world_types:
        inventory["wavelengthMin"] = min_dict["em_wl"].to_value(u.nm)
        inventory["wavelengthMax"] = max_dict["em_wl"].to_value(u.nm)

    # Add the stokes fields if the stokes axis is present
    if "phys_polarization_stokes" in present_world_types:
        # Extract the stokes converter which converts the index to string representation.
        stokes_index = wcs.world_axis_physical_types.index("phys.polarization.stokes")
        stokes_key = wcs.world_axis_object_components[stokes_index][0]
        stokes_converter = wcs.world_axis_object_classes[stokes_key][3]
        stokes_components = stokes_converter(world_coords["phys_polarization_stokes"])

        inventory["hasAllStokes"] = len(stokes_components) > 1
        inventory["stokesParameters"] = list(map(str, stokes_components))
    else:
        inventory["stokesParameters"] = ['I']
        inventory["hasAllStokes"] = False

    return inventory


def _get_unique(column, singular=False):
    uniq = list(set(column))
    if singular:
        if len(uniq) == 1:
            if isinstance(uniq[0], np.str_):
                return str(uniq[0])
            return uniq[0]
        else:
            raise ValueError(
                f"Column '{column}' does not result in a singular unique value.\n {uniq}"
            )
    return uniq


def _get_number_apply(column, func):
    return func(column)


def _get_keys_matching(headers, pattern):
    """
    Get all the values from all the keys matching the given re pattern.

    Assumes that each matching column is singular (all values are the same)

    Parameters
    ----------
    headers : `astropy.table.Table`
        All the headers

    pattern : `str`
        A regex pattern
    """
    results = []

    prog = re.compile(pattern)
    for key in headers.colnames:
        if prog.match(key):
            results.append(_get_unique(headers[key], singular=True))
    return list(set(results))


def _inventory_from_headers(headers: Table):
    inventory = {}

    mode = partial(scipy.stats.mode, axis=None, nan_policy="raise")

    # These keys might get updated by parsing the gwcs object.
    inventory["wavelengthMin"] = inventory["wavelengthMax"] = _get_unique(headers['LINEWAV'])[0]

    inventory["datasetId"] = _get_unique(headers["DSETID"], singular=True)
    inventory["exposureTime"] = _get_number_apply(headers['XPOSURE'], mode).mode[0]
    inventory["instrumentName"] = _get_unique(headers['INSTRUME'], singular=True)
    inventory["recipeId"] = int(_get_unique(headers['RECIPEID'], singular=True))
    inventory["recipeInstanceId"] = int(_get_unique(headers['RINSTID'], singular=True))
    inventory["recipeRunId"] = int(_get_unique(headers['RRUNID'], singular=True))
    inventory["targetTypes"] = list(map(str, _get_unique(headers['OBJECT'])))
    inventory["primaryProposalId"] = _get_unique(headers['PROP_ID'], singular=True)
    inventory["primaryExperimentId"] = _get_unique(headers['EXPER_ID'], singular=True)
    inventory["dataset_size"] = (_get_number_apply(headers['FRAMEVOL'], np.sum) * u.Mibyte).to_value(u.Gibyte)
    inventory["contributingExperimentIds"] = list(map(str, (_get_keys_matching(headers, r"EXPERID\d\d$") +
                                                            [_get_unique(headers["EXPER_ID"], singular=True)])))
    inventory["contributingProposalIds"] = list(map(str, (_get_keys_matching(headers, r"PROPID\d\d$") +
                                                          [_get_unique(headers["PROP_ID"], singular=True)])))
    friedval = np.nan
    if 'ATMOS_R0' in headers.colnames:
        friedval = _get_number_apply(headers['ATMOS_R0'], np.mean)

    inventory["qualityAverageFriedParameter"] = friedval

    polsens = np.nan
    if 'POL_SENS' in headers.colnames:
        polsens = _get_number_apply(headers['POL_SENS'], np.mean)
    inventory["qualityAveragePolarimetricAccuracy"] = polsens

    return inventory


def extract_inventory(headers: Table,
                      transform_builder: TransformBuilder = None,
                      **extra_inventory: Mapping[str, Any]) -> Mapping[str, Any]:
    """
    Generate the inventory record for an asdf file from an asdf tree.

    Parameters
    ----------
    headers
       The raw sorted header with `'filenames'` and `'headers'` columns as
       returned by `.make_sorted_table`.

    extra_inventory
        Additional inventory keys that can not be computed from the headers or the WCS.

    Returns
    -------
    tree: `dict`
        The updated tree with the inventory.

    """
    headers = group_mosaic_tiles(headers)

    if transform_builder is None:
        transforms = [TransformBuilder(tile_headers) for tile_headers in headers.groups]
    else:
        transforms = [transform_builder]

    wcs_inventory = _inventory_from_wcs(transforms[0].gwcs)

    if len(transforms) != 1:
        # If we have a tiled dataset then we need to use the boundingBox keys
        # for each tile to calculate the global bounding box. We assume all the
        # other keys are invariant over the tiles, if they turn out not to be,
        # this is the place to calculate them.
        bounding_boxes = []
        for transform in transforms:
            inv = _inventory_from_wcs(transform.gwcs)
            bounding_boxes.append(inv["boundingBox"])

        boxes = np.array(bounding_boxes, dtype=float)

        global_bbox = ((boxes[:, 0, 0].min(), boxes[:, 0, 1].min()),
                       (boxes[:, 1, 0].max(), boxes[:, 1, 1].max()))
        wcs_inventory["boundingBox"] = global_bbox

    # The headers will populate passband info for VBI and then wcs will
    # override it if there is a wavelength axis in the dataset, any supplied
    # kwargs override things extracted from dataset.
    inventory = {**_inventory_from_headers(headers), **wcs_inventory, **extra_inventory}

    # After this point we are assuming all these keys do not vary between mosaic tiles.
    transform_builder = transforms[0]
    inventory['hasSpectralAxis'] = transform_builder.spectral_sampling is not None
    inventory['hasTemporalAxis'] = transform_builder.temporal_sampling is not None
    inventory['averageDatasetSpectralSampling'] = transform_builder.spectral_sampling
    inventory['averageDatasetSpatialSampling'] = transform_builder.spatial_sampling
    inventory['averageDatasetTemporalSampling'] = transform_builder.temporal_sampling

    # Calculate the asdfObjectKey
    instrument = inventory['instrumentName'].upper()
    start_time = datetime.datetime.fromisoformat(inventory['startTime'])
    asdf_filename = f"{instrument}_L1_{start_time:%Y%m%dT%H%M%S}_{inventory['datasetId']}.asdf"
    inventory["asdfObjectKey"] = f"{inventory['primaryProposalId']}/{inventory['datasetId']}/{asdf_filename}"

    return inventory


# This is the function called by dataset-inventory-maker
def generate_inventory_from_frame_inventory(bucket: str, json_headers: List[Dict[str, Any]]):
    """
    Generate the complete inventory record from frame inventory.

    Parameters
    ----------
    bucket
        The bucket in which the dataset resides.
    json_headers
        A list of dicts containing the JSON version of the headers as stored in inventory.

    Returns
    -------
    dataset_inventory
        The complete dataset inventory
    """
    filenames, fits_headers, extra_inventory = process_json_headers(bucket, json_headers)
    table_headers = Table(fits_headers)
    table_headers = make_sorted_table(table_headers, filenames)

    return extract_inventory(table_headers, **extra_inventory)
