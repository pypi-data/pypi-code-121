import pytest

import numpy as np
from astropy.table import Table
from astropy.wcs import WCS
import astropy.units as u

from dkist_data_simulator.spec214.visp import TimeDependentVISPDataset

from dkist_inventory.header_parsing import HeaderParser


@pytest.fixture(scope="session")
def simple_header_table():
    """
    This is a minimal header table to test the header parser.

    It's pretty hacky but we want to get rid of everything we don't need to make it easier to inspect
    """
    ds = TimeDependentVISPDataset(
        n_steps=4,
        n_maps=5,
        n_stokes=6,
        time_delta=1,
        linewave=500*u.nm,
        detector_shape=(3, 2)
    )

    headers = ds.generate_headers()
    table = Table(headers)
    test_keys = [
        "DNAXIS",
        "DNAXISd",
        "DTYPEd",
        "DUNITd",
        "DAAXES",
        "DEAXES",
        "DINDEXk",
        "CRVALn",
        "PCi_j",
        "NAXIS",
        "NAXISn"
    ]
    header = table[0]
    DNAXIS, DAAXES, DEAXES, NAXIS = (
        int(header["DNAXIS"]),
        int(header["DAAXES"]),
        int(header["DEAXES"]),
        int(header["NAXIS"])
    )
    all_keys = []
    for key in test_keys:
        keys = [key]
        if key.endswith("d"):
            keys = [key[:-1] + str(d) for d in range(1, DNAXIS + 1)]
        if key.endswith("k"):
            keys = [key[:-1] + str(k) for k in range(DAAXES + 1, DAAXES + DEAXES + 1)]
        if key.endswith("n"):
            keys = [key[:-1] + str(n) for n in range(1, NAXIS + 1)]
        if key.startswith("PC"):
            keys = []
            for i in range(1, NAXIS + 1):
                for j in range(1, NAXIS + 1):
                    keys.append(f"PC{i}_{j}")
        all_keys += keys
    return table[all_keys]


@pytest.fixture
def parser(simple_header_table):
    return HeaderParser(simple_header_table)


def test_slice_for_file_axes(parser):
    assert parser.header["NAXIS1"] == 2
    assert parser.header["NAXIS2"] == 3
    assert parser.dataset_shape == (2, 3, 4, 5, 6)
    assert parser.files_shape == (4, 5, 6)

    assert parser.slice_for_file_axes(0) == (slice(None), 0, 0)
    assert parser.slice_for_file_axes(0, 2) == (slice(None), 0, slice(None))

    assert parser.varying_spatial_daxes == {'crval': [3, 4], 'pc': [3, 4]}

    assert parser.slice_for_dataset_array_axes(3, indexing="fits") == (slice(None), 0, 0)
    assert parser.slice_for_dataset_array_axes(4, indexing="fits") == (0, slice(None), 0)
    assert parser.slice_for_dataset_array_axes(5, indexing="fits") == (0, 0, slice(None))

    static_axes = parser.header_array[parser.slice_for_dataset_array_axes(5, indexing="fits")]
    assert static_axes.shape == (6,)
    assert np.allclose(static_axes["CRVAL2"], static_axes["CRVAL2"][0])

    varying_axes = parser.header_array[parser.slice_for_dataset_array_axes(4, indexing="fits")]
    assert varying_axes.shape == (5,)
    assert not np.allclose(varying_axes["CRVAL2"], varying_axes["CRVAL2"][0])

    varying_axes = parser.header_array[parser.slice_for_dataset_array_axes(3, indexing="fits")]
    assert varying_axes.shape == (4,)
    assert not np.allclose(varying_axes["CRVAL2"], varying_axes["CRVAL2"][0])
