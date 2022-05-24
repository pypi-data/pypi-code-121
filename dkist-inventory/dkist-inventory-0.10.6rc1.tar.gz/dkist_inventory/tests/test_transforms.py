import numpy as np
import pytest

import astropy.units as u
import gwcs.coordinate_frames as cf
from astropy.io import fits
from astropy.modeling import Model, models
from astropy.time import Time
from astropy.table import Table

from dkist_inventory.transforms import (
    linear_spectral_model,
    linear_time_model,
    spatial_model_from_header,
    spectral_model_from_framewave,
    time_model_from_date_obs,
    TransformBuilder
)


@pytest.fixture
def wcs(transform_builder):
    return transform_builder.gwcs


@pytest.fixture
def non_varying_wcs(non_varying_transform_builder):
    return non_varying_transform_builder.gwcs


def test_transform(transform_builder):
    assert isinstance(transform_builder.transform, Model)


def test_frames(transform_builder):
    frames = transform_builder.frames
    assert all([isinstance(frame, cf.CoordinateFrame) for frame in frames])


def test_input_name_ordering(wcs):
    # Check the ordering of the input and output frames
    allowed_pixel_names = (
        ('wavelength', 'slit position', 'raster position', 'scan number'),
        ('wavelength', 'slit position', 'raster position'),
        ("spatial x", "spatial y", "scan position", "scan repeat number", "stokes"),
        ("wavelength", "slit position", "raster position", "scan number", "stokes"),
        ("spatial x", "spatial y", "frame number"),
    )
    assert wcs.input_frame.axes_names in allowed_pixel_names


def test_output_name_ordering(wcs):
    allowed_world_names = (
        ('wavelength', 'helioprojective latitude', 'helioprojective longitude', 'time'),
        ("helioprojective longitude", "helioprojective latitude", "wavelength", "time", "stokes"),
        ("wavelength", "helioprojective latitude", "helioprojective longitude", "time", "stokes"),
        ("helioprojective longitude", "helioprojective latitude", "time"),
    )
    assert wcs.output_frame.axes_names in allowed_world_names


def test_output_frames(wcs):
    allowed_frame_orders = (
        (cf.SpectralFrame, cf.CelestialFrame, cf.TemporalFrame),
        (cf.CelestialFrame, cf.SpectralFrame, cf.TemporalFrame, cf.StokesFrame),
        (cf.SpectralFrame, cf.CelestialFrame, cf.TemporalFrame, cf.StokesFrame),
        (cf.CelestialFrame, cf.TemporalFrame),
    )
    types = tuple((type(frame) for frame in wcs.output_frame.frames))
    assert types in allowed_frame_orders


def test_transform_models(non_varying_wcs):
    # Test that there is one lookup table and two linear models for both the
    # wcses
    sms = non_varying_wcs.forward_transform._leaflist
    smtypes = [type(m) for m in sms]
    if len(smtypes) == 4:  # VTF and VISP
        assert sum(mt is models.Linear1D for mt in smtypes) == 2
        assert sum(mt is models.Tabular1D for mt in smtypes) == 1
    if len(smtypes) == 2:  # VBI
        assert sum(mt is models.Linear1D for mt in smtypes) == 1


def first_header(header_filenames):
    return fits.getheader(header_filenames[0])


def test_spatial_model(header_filenames):
    sampling, spatial = spatial_model_from_header(first_header(header_filenames))
    assert isinstance(spatial, Model)


def test_spatial_model_fail(header_filenames):
    header = first_header(header_filenames)
    header["CTYPE2"] = "WAVE"
    with pytest.raises(ValueError):
        spatial_model_from_header(header)


def test_linear_spectral():
    lin = linear_spectral_model(10 * u.nm, 0 * u.nm)
    assert isinstance(lin, models.Linear1D)
    assert u.allclose(lin.slope, 10 * u.nm / u.pix)
    assert u.allclose(lin.intercept, 0 * u.nm)


def test_linear_time():
    lin = linear_time_model(10 * u.s)
    assert isinstance(lin, models.Linear1D)
    assert u.allclose(lin.slope, 10 * u.s / u.pix)
    assert u.allclose(lin.intercept, 0 * u.s)


@pytest.mark.parametrize("dataset_name", ["vbi"])
def test_time_from_dateobs(dataset_name, simulated_dataset):
    directory = simulated_dataset(dataset_name)
    header_filenames = directory.glob("*")
    date_obs = [fits.getheader(f)["DATE-BEG"] for f in header_filenames]
    date_obs.sort()
    delta = Time(date_obs[1]) - Time(date_obs[0])
    sampling, time = time_model_from_date_obs(np.array(date_obs))
    assert isinstance(time, models.Linear1D)
    np.testing.assert_allclose(time.slope, delta.to(u.s) / (1 * u.pix))


def test_time_from_dateobs_lookup(header_filenames):
    date_obs = [fits.getheader(f)["DATE-BEG"] for f in header_filenames]
    date_obs[3] = (Time(date_obs[3]) + 10 * u.s).isot
    deltas = Time(date_obs) - Time(date_obs[0])
    sampling, time = time_model_from_date_obs(np.array(date_obs))
    assert isinstance(time, models.Tabular1D)
    assert (time.lookup_table == deltas.to(u.s)).all()
    np.testing.assert_allclose(time.lookup_table, deltas.to(u.s))


def test_spectral_framewave(header_filenames):
    head = first_header(header_filenames)

    # Skip the VISP headers
    if "FRAMEWAV" not in head:
        return

    nwave = head["DNAXIS3"]
    framewave = [fits.getheader(h)["FRAMEWAV"] for h in header_filenames]

    sampling, m = spectral_model_from_framewave(framewave[:nwave])
    assert isinstance(m, models.Linear1D)

    sampling, m2 = spectral_model_from_framewave(framewave)
    assert isinstance(m2, models.Tabular1D)


def test_time_varying_vbi_wcs(vbi_time_varying_transform_builder):
    if not hasattr(Model, "_calculate_separability_matrix"):
        pytest.skip()
    wcs = vbi_time_varying_transform_builder.gwcs
    assert np.allclose(wcs.axis_correlation_matrix,
                       np.array([[True,  True,  True],  # noqa
                                 [True,  True,  True],  # noqa
                                 [False, False, True]]))


def test_non_time_varying_vtf(dataset):
    ds = dataset("vtf")
    headers = Table(ds.generate_headers())

    wcs = TransformBuilder(headers).gwcs
    assert wcs.forward_transform.n_inputs == 5
