import os
import pathlib

import pytest

import asdf
import numpy as np

from dkist.dataset import Dataset, TiledDataset
from dkist.io import FileManager

from dkist_inventory.asdf_generator import (
    asdf_tree_from_filenames,
    dataset_from_fits,
    references_from_filenames,
)
from dkist_inventory.inventory import (
    headers_from_filenames,
    validate_headers,
    make_sorted_table,
    group_mosaic_tiles,
)


def test_array_container_shape(header_filenames):
    headers = headers_from_filenames(header_filenames, hdu=0)
    table_headers = make_sorted_table(headers, header_filenames)
    table_headers = group_mosaic_tiles(table_headers)
    if len(table_headers.groups) > 1:
        table_headers = table_headers.groups[0]
    sorted_headers = np.array(table_headers["headers"])
    sorted_filenames = np.array(table_headers["filenames"])

    # Get the array shape
    shape = tuple(
        (headers[0][f"DNAXIS{n}"] for n in range(headers[0]["DNAXIS"], headers[0]["DAAXES"], -1))
    )
    # References from filenames
    array_container = references_from_filenames(
        sorted_filenames, sorted_headers, array_shape=shape, hdu_index=0, relative_to="."
    )

    assert array_container.output_shape == array_container._generate_array().shape


def test_asdf_tree(header_filenames):
    tree = asdf_tree_from_filenames(header_filenames)
    assert isinstance(tree, dict)


def test_asdf_tree_with_headers_and_inventory_args():
    # given
    file_count = 5
    from dkist_data_simulator.spec214.vbi import SimpleVBIDataset
    import astropy.units as u
    headers = []
    file_names = []
    for i, ds in enumerate(SimpleVBIDataset(
            n_time=file_count,
            time_delta=1,
            linewave=550 * u.nm,
            detector_shape=(10, 10),)):
        h = ds.header()
        h['BITPIX'] = 8
        headers.append(h)
        file_names.append(f"wibble_{i}.fits")
    tree = asdf_tree_from_filenames(file_names, headers)
    assert isinstance(tree, dict)


def test_validator(header_filenames):
    headers = headers_from_filenames(header_filenames)
    headers[3]["NAXIS"] = 5
    with pytest.raises(ValueError) as excinfo:
        validate_headers(headers)
        assert "NAXIS" in str(excinfo)


def test_references_from_filenames_shape_error(header_filenames):
    headers = headers_from_filenames(header_filenames, hdu=0)
    with pytest.raises(ValueError) as exc:
        references_from_filenames(header_filenames, headers, [2, 3])

        assert "incorrect number" in str(exc)
        assert "2, 3" in str(exc)
        assert str(len(header_filenames)) in str(exc)


def test_references_from_filenames(header_filenames):
    headers = headers_from_filenames(header_filenames, hdu=0)
    base = os.path.split(header_filenames[0])[0]
    refs: FileManager = references_from_filenames(
        header_filenames,
        np.array([dict(h) for h in headers], dtype=object),
        (len(header_filenames),),
        relative_to=base,
    )

    for ref in refs.filenames:
        assert base not in ref


def test_dataset_from_fits(header_directory):
    asdf_filename = "test_asdf.asdf"
    asdf_file = pathlib.Path(header_directory) / asdf_filename
    try:
        dataset_from_fits(header_directory, asdf_filename)

        assert asdf_file.exists()

        with asdf.open(asdf_file) as adf:
            assert isinstance(adf["dataset"], (Dataset, TiledDataset))
    finally:
        asdf_file.unlink()
