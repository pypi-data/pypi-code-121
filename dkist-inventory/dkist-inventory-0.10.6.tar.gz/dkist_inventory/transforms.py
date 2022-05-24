"""
Functionality relating to creating gWCS frames and Astropy models from SPEC 214 headers.
"""
import re
from functools import partial
from itertools import product

import astropy.modeling.models as m
import astropy.table
import astropy.units as u
import gwcs
import gwcs.coordinate_frames as cf
import numpy as np
from astropy.modeling import CompoundModel
from astropy.time import Time
from dkist.wcs.models import (CoupledCompoundModel,
                              VaryingCelestialTransformSlit,
                              VaryingCelestialTransformSlit2D,
                              generate_celestial_transform,
                              varying_celestial_transform_from_tables)
from sunpy.coordinates import Helioprojective

from dkist_inventory.header_parsing import HeaderParser

__all__ = [
    "TransformBuilder",
    "spectral_model_from_framewave",
    "time_model_from_date_obs",
    "generate_lookup_table",
    "linear_time_model",
    "linear_spectral_model",
    "spatial_model_from_header",
]


PRIMARY_WCS_CTYPE = re.compile(r"(CTYPE\d+$)")


def identify_spatial_axes(header):
    """
    Given a FITS WCS header identify which axis number is lat and which is lon.
    """
    latind = None
    lonind = None
    for k, v in header.items():
        key_is_not_primary_wcs_ctype = not bool(re.search(PRIMARY_WCS_CTYPE, k))
        if key_is_not_primary_wcs_ctype:
            continue
        if isinstance(v, str) and v.startswith("HPLN-"):
            lonind = int(k[5:])
        if isinstance(v, str) and v.startswith("HPLT-"):
            latind = int(k[5:])

    if latind is None or lonind is None:
        raise ValueError("Could not extract HPLN and HPLT from the header.")

    latalg = header[f"CTYPE{latind}"][5:]
    lonalg = header[f"CTYPE{lonind}"][5:]

    if latalg != lonalg:
        raise ValueError(
            "The projection of the two spatial axes did not match."
        )  # pragma: no cover

    return latind, lonind


def spatial_model_from_header(header):
    """
    Given a FITS compliant header with CTYPEx,y as HPLN, HPLT return a
    `~astropy.modeling.CompositeModel` for the transform.

    This function finds the HPLN and HPLT keys in the header and returns a
    model in Lon, Lat order.
    """
    latind, lonind = identify_spatial_axes(header)

    cunit1, cunit2 = u.Unit(header[f"CUNIT{lonind}"]), u.Unit(header[f"CUNIT{latind}"])
    crpix = (header[f"CRPIX{lonind}"], header[f"CRPIX{latind}"]) * u.pix
    crval = u.Quantity([header[f"CRVAL{lonind}"] * cunit1, header[f"CRVAL{latind}"] * cunit2])
    cdelt = u.Quantity([
        header[f"CDELT{lonind}"] * (cunit1 / u.pix),
        header[f"CDELT{latind}"] * (cunit2 / u.pix),
    ])
    pc = np.array([
        [header[f"PC{lonind}_{lonind}"], header[f"PC{lonind}_{latind}"]],
        [header[f"PC{latind}_{lonind}"], header[f"PC{latind}_{latind}"]],
    ]) * cunit1

    latproj = header[f"CTYPE{latind}"][5:]
    lonpole = header.get("LONPOLE")
    if not lonpole and latproj == "TAN":
        lonpole = 180

    if not lonpole:
        raise ValueError(f"LONPOLE not specified and not known for projection {latproj}")

    projections = {"TAN": m.Pix2Sky_TAN()}

    return (
        np.mean(cdelt).to_value(u.arcsec / u.pix),
        generate_celestial_transform(crpix, cdelt, pc, crval,
                                     lon_pole=lonpole, projection=projections[latproj])
    )


def varying_spatial_model_from_headers(axes: list[int], parser: HeaderParser):
    """
    Generate a varying celestial model from a set of headers.
    """
    header = dict(parser.header)
    varying_axes = parser.varying_spatial_daxes
    vaxes = parser.compute_varying_axes_numbers(varying_axes)

    latind, lonind = identify_spatial_axes(header)
    cunit1, cunit2 = u.Unit(header[f"CUNIT{lonind}"]), u.Unit(header[f"CUNIT{latind}"])
    crpix = (header[f"CRPIX{lonind}"], header[f"CRPIX{latind}"]) * u.pix
    cdelt = u.Quantity([
        header[f"CDELT{lonind}"] * (cunit1 / u.pix),
        header[f"CDELT{latind}"] * (cunit2 / u.pix),
    ])

    # Extract tables
    varying_header_array = parser.header_array[parser.slice_for_dataset_array_axes(*vaxes, indexing="fits")]
    varying_shape = [header[f"DNAXIS{d}"] for d in vaxes]

    if "crval" in varying_axes:
        crval_table = varying_header_array[[f"CRVAL{i}" for i in (lonind, latind)]]
        # Coerce the astropy table to a regular float numpy array
        crval_table = np.array(crval_table.tolist())
        crval_table = crval_table.reshape(varying_shape + [2])
        crval_table = crval_table << cunit1
    else:
        crval_table = u.Quantity([header[f"CRVAL{lonind}"] * cunit1, header[f"CRVAL{latind}"] * cunit2])

    if "pc" in varying_axes:
        pc_table = varying_header_array[[f"PC{i}_{j}" for i, j in product(*[(lonind, latind)] * 2)]]
        # Coerce the astropy table to a regular float numpy array
        pc_table = np.array(pc_table.tolist())
        pc_table = pc_table.reshape(varying_shape + [2, 2])
        pc_table = pc_table << cunit1
    else:
        pc_table = np.array([
            [header[f"PC{lonind}_{lonind}"], header[f"PC{lonind}_{latind}"]],
            [header[f"PC{latind}_{lonind}"], header[f"PC{latind}_{latind}"]],
        ]) * cunit1

    # Which daxes have DTYPE == "SPATIAL" (+1 to shift to FITS)
    primary_spatial_axes = (np.array(parser.axes_types) == "SPATIAL").nonzero()[0] + 1
    # If any axes the pointing is varying across have a primary type of SPATIAL
    # then we are a slit spectrograph where the pointing is changing with the
    # raster dimension (hopefully).
    slit = False
    if (np.array(vaxes)[:, None] == primary_spatial_axes).any():
        slit = True
    vct = varying_celestial_transform_from_tables(cdelt=cdelt, crpix=crpix,
                                                  crval_table=crval_table,
                                                  pc_table=pc_table,
                                                  slit=slit)

    return np.mean(cdelt).to_value(u.arcsec / u.pix), vct


@u.quantity_input
def linear_spectral_model(spectral_width: u.nm, reference_val: u.nm):
    """
    Linear model in a spectral dimension. The reference pixel is always 0.
    """
    return m.Linear1D(slope=spectral_width / (1 * u.pix), intercept=reference_val)


@u.quantity_input
def linear_time_model(cadence: u.s, reference_val: u.s = 0 * u.s):
    """
    Linear model in a temporal dimension. The reference pixel is always 0.
    """
    if reference_val is None:
        reference_val = 0 * cadence.unit
    return m.Linear1D(slope=cadence / (1 * u.pix), intercept=reference_val)


def generate_lookup_table(lookup_table, interpolation="linear", points_unit=u.pix, **kwargs):
    if not isinstance(lookup_table, u.Quantity):
        raise TypeError("lookup_table must be a Quantity.")

    kwargs = {"bounds_error": False, "fill_value": np.nan, "method": interpolation, **kwargs}

    points = tuple(np.arange(na) * u.pix for na in lookup_table.shape)
    if lookup_table.ndim == 1:
        # The integer location is at the centre of the pixel.
        return m.Tabular1D(points, lookup_table, **kwargs)
    elif lookup_table.ndim == 2:
        # TODO: This doesn't support inverse
        return m.Tabular2D(points, lookup_table, **kwargs)
    else:
        raise ValueError("Lookup tables with >2 dimensions are not supported.")



def time_model_from_date_obs(date_obs, date_beg=None):
    """
    Return a time model that best fits a list of dateobs's.
    """
    if not date_beg:
        date_beg = date_obs.flat[0]

    # TODO: WHHYYYY Do we need .T?!
    deltas = Time(date_obs.T.flat) - Time(date_beg.T.flat)

    # Work out if we have a uniform delta (i.e. a linear model)
    ddelta = deltas.to(u.s)[1:] - deltas.to(u.s)[:-1]

    deltas = deltas.reshape(date_obs.shape, order="F")

    # If the length of the axis is one, then return a very simple model
    if ddelta.size == 0:
        raise ValueError("Why do you have a temporal axis in the DTYPEn keys if you only have a len 1 time axis?")
    elif u.allclose(ddelta[0], ddelta) and deltas.ndim == 1:
        slope = ddelta[0]
        intercept = 0 * u.s
        return slope.to_value(u.s), linear_time_model(cadence=slope, reference_val=intercept)
    else:
        print(f"Creating tabular temporal axis. ddeltas: {ddelta}")
        return np.mean(deltas).to_value(u.s), generate_lookup_table(deltas.to(u.s))


def spectral_model_from_framewave(framewav):
    """
    Construct a linear or lookup table model for wavelength based on the
    framewav keys.
    """
    framewav = u.Quantity(framewav, unit=u.nm)
    wave_beg = framewav[0]

    deltas = wave_beg - framewav
    ddeltas = deltas[:-1] - deltas[1:]
    # If the length of the axis is one, then return a very simple model
    if ddeltas.size == 0:
        raise ValueError("Why do you have a spectral axis in the DTYPEn keys if you only have a len 1 spectral axis?")
    if u.allclose(ddeltas[0], ddeltas):
        slope = ddeltas[0]
        return slope.to_value(u.nm), linear_spectral_model(slope, wave_beg)
    else:
        print(f"creating tabular wavelength axis. ddeltas: {ddeltas}")
        return np.mean(ddeltas).to_value(u.nm), generate_lookup_table(framewav)


class TransformBuilder:
    """
    This class builds compound models and frames in order when given axes types.
    """
    def __init__(self, headers: astropy.table.Table):
        if not isinstance(headers, astropy.table.Table):
            raise TypeError("headers should be an astropy table")

        self.header = dict(headers[0])
        self.headers = headers
        self.parser = HeaderParser(self.headers)

        self.spectral_sampling = None
        self.spatial_sampling = None
        self.temporal_sampling = None

        # This must be last
        # Build the components of the transform
        self._build()

    @property
    def pixel_frame(self):
        """
        A `gwcs.coordinate_frames.CoordinateFrame` object describing the pixel frame.
        """
        DNAXIS = self.header["DNAXIS"]
        return cf.CoordinateFrame(
            naxes=DNAXIS,
            axes_type=["PIXEL"] * DNAXIS,
            axes_order=range(DNAXIS),
            unit=[u.pixel] * DNAXIS,
            axes_names=[self.header[f"DPNAME{n}"] for n in range(1, DNAXIS + 1)],
            name="pixel",
        )

    @property
    def gwcs(self):
        """
        `gwcs.WCS` object representing these headers.
        """
        world_frame = cf.CompositeFrame(self.frames)

        out_wcs = gwcs.WCS(
            forward_transform=self.transform, input_frame=self.pixel_frame, output_frame=world_frame
        )
        out_wcs.pixel_shape = self.parser.dataset_shape
        out_wcs.array_shape = self.parser.dataset_shape[::-1]

        return out_wcs

    @property
    def frames(self):
        """
        The coordinate frames, in Python order.
        """
        return self._frames

    @property
    def transform(self):
        """
        Return the compound model.
        """
        # self._transforms is a tuple of (pixel_axes, model, callable(right)).
        # The callable returns a CompoundModel instance when the right hand
        # side of the operator is passed.
        # We iterate backwards through the models generating the model for the
        # right hand side of the next step up the tree (i.e. from the inner
        # most operator to the outermost). So we start with the last model
        # instance (ignoring the callable), then pass that model to the next
        # callable as the right hand side, and continue to work our way back up
        # the tree.
        axes, right, _ = self._transforms[-1]
        pixel_inputs = [*axes]
        for axes, _, func in self._transforms[:-1][::-1]:
            pixel_inputs = [*axes, *pixel_inputs]
            right = func(right=right)

        # If the number of inputs to the generated transform doesn't match the
        # number of pixel dimensions in the dataset then we construct a mapping
        # to share some pixel inputs between multiple models
        expected_inputs = len(self.parser.dataset_shape)
        if right.n_inputs != expected_inputs:
            mapping = m.Mapping(pixel_inputs)
            right = mapping | right

        # If the number of inputs *still* doesn't match something has gone very wrong.
        if right.n_inputs != expected_inputs:
            raise ValueError(
                f"The transform that has been constructed has {right.n_inputs} inputs "
                f"which does not match the expected number ({expected_inputs}) of pixel inputs."
            )  # pragma: no cover
        return right

    """
    Internal Stuff
    """

    @staticmethod
    def _compound_model_partial(left, op="&"):
        return partial(CompoundModel, left=left, op=op)

    def _build(self):
        """
        Build the state of the thing.
        """
        make_map = {
            "STOKES": self.make_stokes,
            "TEMPORAL": self.make_temporal,
            "SPECTRAL": self.make_spectral,
            "SPATIAL": self.make_spatial,
        }

        self._frames = []
        self._transforms = []
        self.world_index = 0

        type_map = self.parser.pixel_axis_type_map
        for dtype, axes in type_map.items():
            frame, transform_pair = make_map[dtype](axes)
            self._frames.append(frame)
            self._transforms.append((axes, *transform_pair))

    def get_units(self, *iargs):
        """
        Get zee units
        """
        u = [self.header.get(f"DUNIT{i + 1}", None) for i in iargs]
        return u

    def make_stokes(self, axes):
        """
        Add a stokes axes to the builder.
        """
        if not len(axes) == 1:
            raise ValueError("There can only be one STOKES axis.")
        i = axes[0]

        name = self.header[f"DWNAME{i + 1}"]
        frame = cf.StokesFrame(axes_order=(self.world_index,), name=name)
        transform = generate_lookup_table([0, 1, 2, 3] * u.one, interpolation="nearest")
        self.world_index += 1

        return frame, (transform, self._compound_model_partial(left=transform))

    def make_spectral(self, axes):
        """
        Decide how to make a spectral axes.
        """
        if not len(axes) == 1:
            raise ValueError("There can only be one SPECTRAL axis.")
        i = axes[0]
        n = i + 1
        name = self.header[f"DWNAME{n}"]
        frame = cf.SpectralFrame(
            axes_order=(self.world_index,), axes_names=(name,), unit=self.get_units(i), name=name
        )

        if "WAV" in self.header.get(f"CTYPE{n}", ""):  # Matches AWAV and WAVE
            self.spectral_sampling, transform = self.make_spectral_from_wcs(n)
        elif "FRAMEWAV" in self.header.keys():
            self.spectral_sampling, transform = self.make_spectral_from_dataset(n)
        else:
            raise ValueError(
                "Could not parse spectral WCS information from this header."
            )  # pragma: no cover

        self.world_index += 1
        return frame, (transform, self._compound_model_partial(left=transform))

    def make_temporal(self, axes):
        """
        Add a temporal axes to the builder.
        """
        frame = cf.TemporalFrame(
            axes_order=(self.world_index,),
            name="temporal",
            axes_names=("time",),
            unit=(u.s,),
            reference_frame=Time(self.header["DATE-AVG"]),
        )
        dslice = self.parser.slice_for_dataset_array_axes(*axes, indexing="python")
        dates = self.parser.header_array[dslice]["DATE-AVG"]
        self.temporal_sampling, transform = time_model_from_date_obs(dates)
        self.world_index += 1
        return frame, (transform, self._compound_model_partial(left=transform))

    def make_spatial(self, axes):
        """
        Add a helioprojective spatial pair to the builder.
        """
        daxes = (np.array(axes) + 1).tolist()
        name = self.header[f"DWNAME{daxes[0]}"]
        name = name.split(" ")[0]

        # TODO: don't just use the first obstime
        obstime = Time(self.header["DATE-AVG"])

        # The dataset axes with a type of SPATIAL
        spatial_dind = [d for d in range(1, self.header["DNAXIS"] + 1)
                        if self.header[f"DTYPE{d}"] == "SPATIAL"]
        axes_names = [self.header[f"DWNAME{da}"] for da in spatial_dind]

        # Identify the indices of lat, lon based on CTYPE
        spatial_ind = identify_spatial_axes(self.header)
        # Generate a sorted list of [lat, lon] based on the indices.
        axes_types = [t for _, t in sorted(zip(spatial_ind, ["lat", "lon"]))]
        frame = cf.CelestialFrame(
            axes_order=(self.world_index, self.world_index + 1),
            name=name,
            # TODO: Add (varying) observer location
            reference_frame=Helioprojective(obstime=obstime),
            axes_names=axes_names,
            unit=self.get_units(*np.array(spatial_dind) - 1),
            axis_physical_types=(
                f"custom:pos.helioprojective.{axes_types[0]}",
                f"custom:pos.helioprojective.{axes_types[1]}",
            ),
        )

        varying_spatial_axes = self.parser.varying_spatial_daxes
        if varying_spatial_axes:
            self.spatial_sampling, transform = varying_spatial_model_from_headers(axes, self.parser)
            # At this point we have already verified that if there are both pc and
            # crval keys in this dict they are the same length, so just use the
            # first one.
            shared_inputs = len(list(varying_spatial_axes.values())[0])
            transform_pair = (transform, partial(CoupledCompoundModel, op="&",
                                                 left=transform, shared_inputs=shared_inputs))
        else:
            self.spatial_sampling, transform = spatial_model_from_header(self.header)
            transform_pair = (transform, self._compound_model_partial(left=transform))

        self.world_index += 2
        return frame, transform_pair

    def make_spectral_from_dataset(self, n):
        """
        Make a spectral axes from (VTF) dataset info.
        """
        s = self.parser.slice_for_dataset_array_axes(n - 1, indexing="python")
        framewave = np.array(self.parser.header_array[s]["FRAMEWAV"])
        return spectral_model_from_framewave(framewave)

    def make_spectral_from_wcs(self, n):
        """
        Add a spectral axes from the FITS-WCS keywords.
        """
        unit = u.Unit(self.header[f"CUNIT{n}"])
        spectral_cdelt = self.header[f"CDELT{n}"] * unit
        return spectral_cdelt.to_value(u.nm), linear_spectral_model(
            spectral_cdelt, self.header[f"CRVAL{n}"] * unit
        )
