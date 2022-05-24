import astropy.units as u
import pytest
from dkist.conftest import *
from dkist_data_simulator.spec214.vbi import (MosaicedVBIBlueDataset,
                                              SimpleVBIDataset,
                                              TimeDependentVBIDataset)
from dkist_data_simulator.spec214.visp import (SimpleVISPDataset,
                                               TimeDependentVISPDataset)
from dkist_data_simulator.spec214.vtf import SimpleVTFDataset
from dkist_inventory.asdf_generator import headers_from_filenames
from dkist_inventory.transforms import TransformBuilder


@pytest.fixture(scope="session")
def dataset():
    def _dataset(dataset_name):
        datasets = {
            "visp": SimpleVISPDataset(2, 2, 4, 5, linewave=500 * u.nm,
                                      detector_shape=(32, 32)),
            "vtf": SimpleVTFDataset(2, 2, 4, 5, linewave=500 * u.nm,
                                    detector_shape=(32, 32)),
            "vbi": SimpleVBIDataset(n_time=5, time_delta=5,
                                    linewave=500 * u.nm,
                                    detector_shape=(32, 32)),
            "vbi-mosaic": MosaicedVBIBlueDataset(n_time=2, time_delta=10, linewave=400 * u.nm,
                                                 detector_shape=(32, 32)),
            "vbi-time-varying": TimeDependentVBIDataset(n_time=4, time_delta=10,
                                                        linewave=400 * u.nm,
                                                        detector_shape=(32, 32)),
            "visp-time-varying-single": TimeDependentVISPDataset(n_maps=1, n_steps=4,
                                                                 n_stokes=1, time_delta=10,
                                                                 linewave=500 * u.nm,
                                                                 detector_shape=(16, 128)),
            "visp-time-varying-multi": TimeDependentVISPDataset(n_maps=2, n_steps=3,
                                                                n_stokes=4, time_delta=10,
                                                                linewave=500 * u.nm,
                                                                detector_shape=(16, 128)),
        }
        return datasets[dataset_name]
    return _dataset


@pytest.fixture(scope="session")
def simulated_dataset(cached_tmpdir, dataset):
    def _simulated_dataset(dataset_name):
        atmpdir = cached_tmpdir / dataset_name
        existed = atmpdir.exists()
        if not existed:
            ds = dataset(dataset_name)
            ds.generate_files(atmpdir, f"{dataset_name.upper()}_{{ds.index}}.fits")

        return atmpdir
    return _simulated_dataset


@pytest.fixture(scope="session", params=[
    "vtf",
    "vbi",
    "visp",
    "vbi-mosaic",
    "vbi-time-varying",
    "visp-time-varying-single",
    "visp-time-varying-multi",
])
def header_directory(request, simulated_dataset):
    return simulated_dataset(request.param)


@pytest.fixture
def vbi_time_varying_transform_builder(header_directory):
    if "vbi-time-varying" not in header_directory.as_posix():
        pytest.skip()

    headers = headers_from_filenames(header_directory.glob("*"))
    return TransformBuilder(headers)


@pytest.fixture
def header_filenames(header_directory):
    files = list(header_directory.glob("*"))
    files.sort()
    return files


@pytest.fixture
def transform_builder(header_filenames):
    # We can't build a single transform builder for a mosaic
    if "vbi-mosaic" in header_filenames[0].as_posix():
        pytest.skip()
    headers = headers_from_filenames(header_filenames)
    return TransformBuilder(headers)


@pytest.fixture
def non_varying_transform_builder(header_filenames):
    if ("varying" in header_filenames[0].as_posix() or "mosaic" in header_filenames[0].as_posix()):
        pytest.skip()
    headers = headers_from_filenames(header_filenames)
    return TransformBuilder(headers)
