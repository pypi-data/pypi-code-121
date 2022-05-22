import numpy as np
import logging

logger = logging.getLogger(__name__)
import os
from h5parm.datapack import DataPack
import astropy.time as at
import astropy.coordinates as ac
import astropy.units as au


def wrap(phi):
    """
    Wrap `phi` into (-pi, pi)
    Args:
        phi:

    Returns: wrapped phi
    """
    return (phi + np.pi) % (2 * np.pi) - np.pi


def create_empty_datapack(Nd, Nf, Nt, pols=None,
                          field_of_view_diameter=4.,
                          start_time=None,
                          time_resolution=30.,
                          min_freq=122.,
                          max_freq=166.,
                          array_file=None,
                          phase_tracking=None,
                          save_name='test_datapack.h5',
                          clobber=False,
                          seed=None) -> DataPack:
    """
    Creates an empty datapack with phase, amplitude and DTEC.

    Args:
        Nd: number of directions
        Nf: number of frequencies
        Nt: number of times
        pols: polarisations, ['XX', ...]
        array_file: array file else Lofar HBA is used
        phase_tracking: tuple (RA, DEC) in degrees in ICRS frame
        field_of_view_diameter: FoV diameter in degrees
        start_time: start time in modified Julian days (mjs/86400)
        time_resolution: time step in seconds.
        min_freq: minimum frequency in MHz
        max_freq: maximum frequency in MHz
        save_name: where to save the H5parm.
        clobber: Whether to overwrite.
        seed: Numpy seed int

    Returns:
        DataPack
    """

    logger.info("=== Creating empty datapack ===")
    if seed is not None:
        np.random.seed(seed)
    save_name = os.path.abspath(save_name)
    if os.path.isfile(save_name) and clobber:
        os.unlink(save_name)

    if array_file is None:
        array_file = DataPack.lofar_array_hba

    if start_time is None:
        start_time = at.Time("2019-01-01T00:00:00.000", format='isot').mjd

    if pols is None:
        pols = ['XX']
    assert isinstance(pols, (tuple, list))

    time0 = at.Time(start_time, format='mjd')

    datapack = DataPack(save_name, readonly=False)
    with datapack:
        datapack.add_solset('sol000', array_file=array_file)

        altaz = ac.AltAz(location=datapack.array_center.earth_location, obstime=time0)
        if phase_tracking is None:
            up = ac.SkyCoord(alt=90. * au.deg, az=0. * au.deg, frame=altaz).transform_to('icrs')
            phase_tracking = (up.ra.deg, up.dec.deg)
        phase_tracking = ac.ICRS(phase_tracking[0] * au.deg, phase_tracking[1] * au.deg)
        up = phase_tracking.transform_to(altaz)
        if up.alt.deg < 0.:
            logger.warning("Phase tracking center below horizon at start of observation.")
        else:
            logger.info(f"Phase tracking altitude: {up.alt.deg} degrees")
        logger.info(f"Phase tracking RA: {phase_tracking.ra.deg} deg, DEC {phase_tracking.dec.deg} deg")
        phase_tracking = (phase_tracking.ra.rad, phase_tracking.dec.rad)
        directions = get_uniform_directions_on_S2(Nd, phase_tracking, field_of_view_diameter)
        datapack.set_directions(None, directions)
        patch_names, _ = datapack.directions
        antenna_labels, _ = datapack.antennas
        _, antennas = datapack.get_antennas(antenna_labels)
        antennas = antennas.cartesian.xyz.to(au.km).value.T
        Na = antennas.shape[0]

        times = at.Time(time0.mjd + (np.arange(Nt) * time_resolution) / 86400., format='mjd').mjd * 86400.  # mjs
        freqs = np.linspace(min_freq, max_freq, Nf) * 1e6

        Npol = len(pols)
        dtecs = np.zeros((Npol, Nd, Na, Nt))
        phase = np.zeros((Npol, Nd, Na, Nf, Nt))
        amp = np.ones_like(phase)

        datapack.add_soltab('phase000', values=phase, ant=antenna_labels, dir=patch_names, time=times, freq=freqs,
                            pol=pols)
        datapack.add_soltab('amplitude000', values=amp, ant=antenna_labels, dir=patch_names, time=times, freq=freqs,
                            pol=pols)
        datapack.add_soltab('tec000', values=dtecs, ant=antenna_labels, dir=patch_names, time=times, pol=pols)
        return datapack


def get_uniform_directions_on_S2(Nd, phase_tracking, field_of_view_diameter, source_in_centre:bool=True):
    """
    Get uniform directions on the sphere constrained to a given angular separation.

    Args:
        Nd:
        phase_tracking: tuple RA,DEC in radians
        field_of_view_diameter: field of view in degrees

    Returns:
        [Nd, 2] array of ra,dec in radians
    """
    ra = phase_tracking[0]# * np.pi / 180.
    dec = phase_tracking[1]# * np.pi / 180.

    def dec_to_phi(dec):
        return 0.5 * np.pi - dec

    phi = dec_to_phi(dec)
    unit_phase_tracking = np.asarray([np.cos(ra) * np.sin(phi), np.sin(ra) * np.sin(phi), np.cos(phi)])
    if source_in_centre:
        directions = [unit_phase_tracking]
    else:
        directions = []
    while len(directions) < Nd:
        unit_directions = np.random.normal(size=(3,))
        unit_directions /= np.linalg.norm(unit_directions)

        if np.abs(np.arccos(unit_directions @ unit_phase_tracking)) < 0.5 * field_of_view_diameter * np.pi / 180.:
            directions.append(unit_directions)

    def phi_to_dec(phi):
        return 0.5 * np.pi - phi

    def to_ra_dec(unit_direction):
        dec = phi_to_dec(wrap(np.arccos(unit_direction[2])))
        ra = np.arctan2(unit_direction[1], unit_direction[0])
        return np.asarray([ra, dec])

    directions = list(map(to_ra_dec, directions))
    return np.asarray(directions)


def get_uniform_directions(Nd, phase_tracking, field_of_view_diameter):
    unit_directions = np.random.normal(size=(Nd, 2))
    unit_directions *= (np.pi / 180. * field_of_view_diameter / 2.) / np.linalg.norm(unit_directions, axis=1,
                                                                                     keepdims=True)
    directions = unit_directions * np.sqrt(np.random.uniform(0., 1., size=(Nd, 1)))
    directions = directions + np.asarray(phase_tracking)
    return directions


def make_example_datapack(Nd, Nf, Nt, pols=None,
                          save_name='test_datapack.h5',
                          clobber=False,
                          seed=0) -> DataPack:
    """
    Create a H5Parm for testing
    Args:
        Nd: number of directions
        Nf: number of frequencies
        Nt: number of times
        pols: list of pols XX,XY,YY, etc.
        save_name: name of file to save to
        clobber: bool, whether to overwrite
        seed: int, numpy seed

    Returns: DataPack
    """
    TEC_CONV = -8.4479745e6  # mTECU/Hz
    np.random.seed(seed)

    logger.info("=== Creating example datapack ===")
    save_name = os.path.abspath(save_name)
    if os.path.isfile(save_name) and clobber:
        os.unlink(save_name)

    datapack = DataPack(save_name, readonly=False)
    with datapack:
        datapack.add_solset('sol000', array_file=datapack.lofar_array_hba)
        time0 = at.Time("2019-01-01T00:00:00.000", format='isot')
        altaz = ac.AltAz(location=datapack.array_center.earth_location, obstime=time0)
        up = ac.SkyCoord(alt=90. * au.deg, az=0. * au.deg, frame=altaz).transform_to('icrs')
        directions = get_uniform_directions_on_S2(Nd, up, 3.5)
        datapack.set_directions(None, directions)
        patch_names, _ = datapack.directions
        antenna_labels, _ = datapack.antennas
        _, antennas = datapack.get_antennas(antenna_labels)
        antennas = antennas.cartesian.xyz.to(au.km).value.T
        Na = antennas.shape[0]

        times = at.Time(time0.gps + np.arange(Nt) * 30., format='gps').mjd * 86400.  # mjs
        freqs = np.linspace(120, 168, Nf) * 1e6
        if pols is not None:
            use_pols = True
            assert isinstance(pols, (tuple, list))
        else:
            use_pols = False
            pols = ['XX']
        Npol = len(pols)
        tec_conversion = TEC_CONV / freqs  # Nf

        dtecs = np.random.normal(0., 150., size=(Npol, Nd, Na, Nt))
        dtecs -= dtecs[:, :, 0:1, :]

        phase = wrap(dtecs[..., None, :] * tec_conversion[:, None])  # Npol, Nd, Na, Nf, Nt
        amp = np.ones_like(phase)

        datapack.add_soltab('phase000', values=phase, ant=antenna_labels, dir=patch_names, time=times, freq=freqs,
                            pol=pols)
        datapack.add_soltab('amplitude000', values=amp, ant=antenna_labels, dir=patch_names, time=times, freq=freqs,
                            pol=pols)
        datapack.add_soltab('tec000', values=dtecs, ant=antenna_labels, dir=patch_names, time=times, pol=pols)
        return datapack


def make_soltab(datapack: DataPack, from_solset='sol000', to_solset='sol000', from_soltab='phase000',
                to_soltab='tec000',
                select=None, directions=None, patch_names=None, remake_solset=False, to_datapack=None):
    """
    Adds a new soltab to the h5parm with a soltab copying over structure from preexisting solset/soltab.
    Args:
        datapack: DataPack to alter, should be writable.
        from_solset: solset to copy from
        to_solset: solset to copy to/create
        from_soltab: soltab to copy structure from
        to_soltab: soltab to copy to
        select: dict, axes section, or None
        directions: ICRS of directions, or None to copy over (useful for adding extra directions but keep else the same)
        patch_names: patch_names corresponding to directions, or None
        remake_solset: bool, whether to forcefully delete the solset and remake.
        to_datapack: output datapack file to make
    """
    if not isinstance(to_soltab, (list, tuple)):
        to_soltab = [to_soltab]
    if select is None:
        select = dict(ant=None, time=None, dir=None, freq=None, pol=slice(0, 1, 1))

    if isinstance(datapack, str):
        datapack = DataPack(datapack)

    with datapack:
        datapack.current_solset = from_solset
        datapack.select(**select)
        axes = getattr(datapack, "axes_{}".format(from_soltab.replace('000', '')))
        antenna_labels, antennas = datapack.get_antennas(axes['ant'])
        _patch_names, _directions = datapack.get_directions(axes['dir'])
        if (directions is None):
            directions = _directions
        if (patch_names is None):
            patch_names = _patch_names
        if len(patch_names) != len(directions):
            patch_names = ['Dir{:02d}'.format(d) for d in range(len(directions))]
        timestamps, times = datapack.get_times(axes['time'])
        freq_labels, freqs = datapack.get_freqs(axes['freq'])
        pol_labels, pols = datapack.get_pols(axes['pol'])
        Npol, Nd, Na, Nf, Nt = len(pols), len(directions), len(antennas), len(freqs), len(times)
    if to_datapack is None:
        to_datapack = datapack.filename
    if isinstance(to_datapack, DataPack):
        to_datapack = to_datapack.filename
    with DataPack(to_datapack) as datapack:
        if remake_solset:
            if to_solset in datapack.solsets:
                datapack.delete_solset(to_solset)
        if to_solset not in datapack.solsets:
            datapack.add_solset(to_solset,
                                array_file=DataPack.lofar_array_hba,
                                directions=np.stack([directions.ra.to(au.rad).value,
                                                     directions.dec.to(au.rad).value], axis=1),
                                patch_names=patch_names)
        for soltab in to_soltab:
            if not soltab.endswith("000"):
                raise ValueError("By Losoto convention soltabs should end in XXX or similar. We only support XXX=000.")
            if 'tec' in soltab:
                datapack.add_soltab(soltab, weightDtype='f16', time=times.mjd * 86400., pol=pol_labels,
                                    ant=antenna_labels,
                                    dir=patch_names)
            if 'clock' in soltab:
                datapack.add_soltab(soltab, weightDtype='f16', time=times.mjd * 86400., pol=pol_labels,
                                    ant=antenna_labels, dir=patch_names)
            if 'const' in soltab:
                datapack.add_soltab(soltab, weightDtype='f16', time=times.mjd * 86400., pol=pol_labels,
                                    ant=antenna_labels, dir=patch_names)
            if 'phase' in soltab:
                datapack.add_soltab(soltab, weightDtype='f16', freq=freqs, time=times.mjd * 86400., pol=pol_labels,
                                    ant=antenna_labels, dir=patch_names)
            if 'amplitude' in soltab:
                datapack.add_soltab(soltab, weightDtype='f16', freq=freqs, time=times.mjd * 86400., pol=pol_labels,
                                    ant=antenna_labels, dir=patch_names)
