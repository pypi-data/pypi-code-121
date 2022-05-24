import os
import pathlib
from importlib import resources
from typing import Iterable, Mapping, Tuple, Union, Any

import asdf
import astropy.table
import numpy as np
import numpy.typing as npt
from astropy.io.fits.hdu.base import BITPIX2DTYPE
from dkist.dataset import Dataset, TiledDataset
from dkist.io import FileManager
from dkist.io.loaders import AstropyFITSLoader

from dkist_inventory.inventory import (extract_inventory, group_mosaic_tiles,
                                       headers_from_filenames,
                                       make_sorted_table, validate_headers, table_from_headers)
from dkist_inventory.transforms import TransformBuilder

__all__ = ["references_from_filenames", "dataset_from_fits", "asdf_tree_from_filenames"]


def references_from_filenames(filenames: npt.NDArray[Any],
                              headers: npt.NDArray[Any],
                              array_shape: Tuple[int, ...],
                              hdu_index: int = 0,
                              relative_to: os.PathLike = None) -> FileManager:
    """
    Given an array of paths to FITS files create a `dkist.io.FileManager`.

    Parameters
    ----------
    filenames
        An array of filenames, in numpy order for the output array (i.e. ``.flat``)

    headers
        A list of headers for files

    array_shape
        The desired output shape of the reference array. (i.e the shape of the
        data minus the HDU dimensions.)

    hdu_index
        The index of the HDU to reference. (Zero indexed)

    relative_to
        If set convert the filenames to be relative to this path.

    Returns
    -------
    `dkist.io.FileManager`
        A container that represents a set of FITS files, and can generate a
        `dask.array.Array` from them.
    """
    filenames = np.asanyarray(filenames)
    filepaths = np.empty(array_shape, dtype=object)
    if filenames.size != filepaths.size:
        raise ValueError(
            f"An incorrect number of filenames ({filenames.size})"
            f" supplied for array_shape ({array_shape})"
        )

    dtypes = []
    shapes = []
    for i, (filepath, head) in enumerate(zip(filenames.flat, headers.flat)):
        dtypes.append(BITPIX2DTYPE[head["BITPIX"]])
        shapes.append(tuple([int(head[f"NAXIS{a}"]) for a in range(head["NAXIS"], 0, -1)]))

        # Convert paths to relative paths
        relative_path = filepath
        if relative_to:
            relative_path = os.path.relpath(filepath, str(relative_to))

        filepaths.flat[i] = str(relative_path)  # type: ignore

    # Validate all shapes and dtypes are consistent.
    dtype = set(dtypes)
    if len(dtype) != 1:
        raise ValueError("Not all the dtypes of these files are the same.")
    dtype = list(dtype)[0]

    shape = set(shapes)
    if len(shape) != 1:
        raise ValueError("Not all the shapes of these files are the same")
    shape = list(shape)[0]  #

    return FileManager(
        filepaths.tolist(), hdu_index, dtype, shape, loader=AstropyFITSLoader
    )


def dataset_object_from_filenames(sorted_table: astropy.table.Table,
                                  inventory: Mapping[str, Any],
                                  hdu: int,
                                  relative_to: os.PathLike = None) -> Dataset:
    """
    Generate a singular dataset object.

    Parameters
    ----------
    sorted_table
        The headers and filenames to process into a `dkist.Dataset`, in
        dataset index order.

    inventory
        Inventory record to use, if not specified will be generated.

    hdu
        The HDU to read the headers from and reference the data to.

    relative_to
        The path to reference the FITS files to inside the asdf. If not
        specified will be local to the asdf (i.e. ``./``).
    """
    sorted_filenames = np.array(sorted_table["filenames"])
    sorted_headers = np.array(sorted_table["headers"])
    sorted_table.remove_columns(["headers", "filenames"])

    ds_wcs = TransformBuilder(sorted_table)

    # Get the array shape
    shape = tuple(
        (int(sorted_headers[0][f"DNAXIS{n}"]) for n in range(sorted_headers[0]["DNAXIS"],
                                                             sorted_headers[0]["DAAXES"], -1))
    )
    # References from filenames
    array_container = references_from_filenames(
        sorted_filenames, sorted_headers, array_shape=shape, hdu_index=hdu, relative_to=relative_to
    )

    ds = Dataset(array_container._generate_array(),
                 ds_wcs.gwcs,
                 meta={'inventory': inventory, 'headers': sorted_table})

    ds._file_manager = array_container

    return ds


def asdf_tree_from_filenames(filenames: Iterable[os.PathLike],
                             headers: Iterable[Mapping[str, str]] = None,
                             inventory: Mapping[str, Any] = None,
                             hdu: int = 0,
                             relative_to: os.PathLike = None,
                             extra_inventory: Mapping[str, Any] = None) -> Mapping[str, Any]:
    """
    Build a DKIST asdf tree from a list of (unsorted) filenames.

    Parameters
    ----------
    filenames
        The filenames to process into a DKIST asdf dataset.

    headers
        The FITS headers if already known. If not specified will be read from
        filenames.

    inventory
        The frame inventory to put in the tree, if not specified a new one
        will be generated.

    hdu
        The HDU to read the headers from and reference the data to.

    relative_to
        The path to reference the FITS files to inside the asdf. If not
        specified will be local to the asdf (i.e. ``./``).

    extra_inventory
        An extra set of inventory to override the generated one.
    """
    if extra_inventory is None:
        extra_inventory = {}

    # In case filenames is a generator we cast to list.
    filenames = list(filenames)

    # headers is an iterator
    if not headers:
        headers = headers_from_filenames(filenames, hdu=hdu)
    else:
        headers = table_from_headers(headers)

    table_headers = make_sorted_table(headers, filenames)

    table_headers = group_mosaic_tiles(table_headers)

    if not inventory:
        inventory = extract_inventory(table_headers, **extra_inventory)

    datasets = []
    for tile_table_headers in table_headers.groups:
        validate_headers(tile_table_headers)

        datasets.append(dataset_object_from_filenames(tile_table_headers,
                                                      inventory,
                                                      hdu,
                                                      relative_to))

    if len(datasets) == 1:
        tree = {"dataset": datasets[0]}
    else:
        # All tiled datasets should have exactly the same dict as their inventory record
        for ds in datasets:
            assert ds.meta["inventory"] == datasets[0].meta["inventory"]
            ds.meta["inventory"] = datasets[0].meta["inventory"]

        # Extract dataset shape
        header = table_headers[0]
        mosaic_shape = tuple(header[f"MAXIS{m}"] for m in range(header["MAXIS"], 0, -1))
        datasets_arr = np.array(datasets, dtype=object).reshape(mosaic_shape)

        tree = {"dataset": TiledDataset(datasets_arr, inventory=datasets[0].meta["inventory"])}

    return tree


def dataset_from_fits(path: Union[str, os.PathLike],
                      asdf_filename: str,
                      inventory: Mapping[str, str] = None,
                      hdu: int = 0,
                      relative_to: os.PathLike = None,
                      **kwargs):
    """
    Given a path containing FITS files write an asdf file in the same path.

    Parameters
    ----------
    path
        The path to read the FITS files (with a `.fits` file extension) from
        and save the asdf file.

    asdf_filename
        The filename to save the asdf with in the path.

    inventory
        The dataset inventory for this collection of FITS. If `None` a random one will be generated.

    hdu
        The HDU to read from the FITS files.

    relative_to
        The base path to use in the asdf references. By default this is the
        parent of ``path=``, it's unlikely you should need to change this from
        the default.

    kwargs
        Additional kwargs are passed to `asdf.AsdfFile.write_to`.

    """
    path = pathlib.Path(path).expanduser()
    relative_to = relative_to or path.parent

    files = path.glob("*fits")

    tree = asdf_tree_from_filenames(
        list(files), inventory=inventory, hdu=hdu, relative_to=relative_to
    )

    with resources.path("dkist.io", "level_1_dataset_schema.yaml") as schema_path:
        with asdf.AsdfFile(tree, custom_schema=schema_path) as afile:
            afile.write_to(path / asdf_filename, **kwargs)
