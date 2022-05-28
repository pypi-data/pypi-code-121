"""
.. _core:

Core Functionality
------------------

Module with functions to perform the rigid waist shift and matching through a
`~cpymad.madx.Madx` object.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import tfs

from cpymad._rpc import RemoteProcessClosed, RemoteProcessCrashed
from cpymad.madx import Madx, TwissFailed
from loguru import logger
from rich.console import Console

from pyhdtoolkit.cpymadtools import lhc, matching, orbit, twiss
from pyhdtoolkit.utils._misc import fullpath
from pyhdtoolkit.utils.contexts import timeit
from pyrws.constants import VARIED_IR_QUADRUPOLES
from pyrws.utils import (
    get_independent_quadrupoles_powering_knobs,
    get_triplets_powering_knobs,
    get_tunes_and_chroma_knobs,
)

console = Console()


@dataclass
class BeamConfig:
    twiss_tfs: tfs.TfsDataFrame
    triplets_knobs: Dict[str, float]
    quads_knobs: Dict[str, float]
    working_point_knobs: Dict[str, float]


# ----- Nominal Setup ----- #


def get_nominal_beam_config(madx: Madx, energy: float, beam: int, ip: int, qx: float, qy: float) -> BeamConfig:
    """
    Provided with an active `~cpymad.madx.Madx` object, will match to the working point defined
    by the provided tunes *qx* and *qy* and return the nominal configuration for the provided *beam*
    (twiss table, triplet knobs, independent IR quadrupoles knobs).

    .. note::
        This will re-cycle the appropriate sequence from ``MSIA.EXIT.B[12]`` point, create **lhcb1**
        and **lhcb2** beams for 6.8 TeV, setup a flat orbit configuration (crossing angles, separation
        bumps at 0 etc.) and use the appropriate sequence for the provided *beam*.

    .. warning::
        IN OPERATION IN THE CCC, REMEMBER TO LEAVE THE ORBIT FEEDBACK ON!

    .. important::
        It is assumed that the sequence and opticsfile have already been called beforehand.

    Args:
        madx (cpymad.madx.Madx): an instanciated `~cpymad.madx.Madx` object.
        energy (float): beam energy for the setup, in [GeV].
        beam (int): the beam number, should be 1 or 2.
        ip (int): the IP for which to get triplets and independent quadrupoles powering
            knobs values.
        qx (float): the horizontal tune to match to.
        qy (float): the vertical tune to match to.

    Returns:
        A custom `~.BeamConfig` object containing: the result of a ``TWISS`` call as a `~tfs.TfsDataFrame`,
        a `dict` with the names and values of the triplets powering knobs, a `dict` with the names and values
        of the independent IR quadrupoles powering knobs and a `dict` with the names and values of the working
        point knobs (tunes and chroma).
    """
    assert beam in (1, 2)
    assert ip in (1, 2, 5, 8)
    logger.debug("Setting up nominal beam and matching tunes")
    lhc.re_cycle_sequence(madx, sequence=f"lhcb{beam:d}", start=f"MSIA.EXIT.B{beam:d}")
    lhc.make_lhc_beams(madx, energy=energy, emittance=3.75e-6)
    _ = orbit.setup_lhc_orbit(madx, scheme="flat")
    madx.command.use(sequence=f"lhcb{beam:d}")

    matching.match_tunes(madx, "lhc", f"lhcb{beam:d}", qx, qy, calls=200)
    matching.match_chromaticities(madx, "lhc", f"lhcb{beam:d}", 2.0, 2.0, calls=200)
    matching.match_tunes_and_chromaticities(madx, "lhc", f"lhcb{beam:d}", qx, qy, 2.0, 2.0, calls=200)
    twiss_df = twiss.get_twiss_tfs(madx, chrom=True)
    triplets_knobs = get_triplets_powering_knobs(madx, ip=ip)
    quads_knobs = get_independent_quadrupoles_powering_knobs(madx, quad_numbers=VARIED_IR_QUADRUPOLES, ip=ip, beam=beam)
    working_point_knobs = get_tunes_and_chroma_knobs(madx, beam=beam)
    return BeamConfig(
        twiss_tfs=twiss_df,
        triplets_knobs=triplets_knobs,
        quads_knobs=quads_knobs,
        working_point_knobs=working_point_knobs,
    )


# ----- Implement Bare Waist Shift ----- #


def get_bare_waist_shift_beam1_config(
    madx: Madx, ip: int, rigidty_waist_shift_value: float, energy: float, qx: float, qy: float
) -> BeamConfig:
    """
    Applies the rigid waist shift at the provided *ip* for beam 1, and returns the corresponding
    configuration for beam 1 (twiss table, triplet knobs, independent IR quadrupoles knobs).

    .. note::
        All the caveats of applying the rigid waist shift apply here as well. For more information
        see the documentation of `pyhdtoolkit.cpymadtools.lhc.apply_lhc_rigidity_waist_shift_knob`.

    .. important::
        It is assumed that the sequence and opticsfile have already been called beforehand.

    Args:
        madx (cpymad.madx.Madx): an instanciated `~cpymad.madx.Madx` object.
        ip (int): the IP at which to apply the rigid waist shift.
        rigidty_waist_shift_value (float): applied unit setting of the rigidity
            waist shift knob. A value of 1 changes the powering of the triplets
            knob by 0.5%.
        energy (float): beam energy for the setup, in [GeV].
        qx (float): the horizontal tune to re-match to after applying the rigid
            waist shift.
        qy (float): the vertical tune to re-match to after applying the rigit
            waist shift.

    Returns:
        A custom `~.BeamConfig` object containing: the result of a ``TWISS`` call as a `~tfs.TfsDataFrame`,
        a `dict` with the names and values of the triplets powering knobs, a `dict` with the names and values
        of the independent IR quadrupoles powering knobs and a `dict` with the names and values of the working
        point knobs (tunes and chroma).
    """
    _ = get_nominal_beam_config(madx, energy=energy, beam=1, ip=ip, qx=qx - 0.04, qy=qy + 0.04)
    logger.debug(f"Applying rigidity waist shift to beam 1 at IP{ip}")
    lhc.apply_lhc_rigidity_waist_shift_knob(madx, rigidty_waist_shift_value=rigidty_waist_shift_value, ir=ip)
    matching.match_tunes(madx, "lhc", "lhcb1", qx, qy, calls=200)
    matching.match_chromaticities(madx, "lhc", "lhcb1", 2.0, 2.0, calls=200)
    matching.match_tunes_and_chromaticities(madx, "lhc", "lhcb1", qx, qy, 2.0, 2.0, calls=200)
    logger.debug(f"Managed to rematch B1 to Qx = {madx.table.summ.q1[0]} and Qy = {madx.table.summ.q2[0]}")

    twiss_df = twiss.get_twiss_tfs(madx, chrom=True)
    triplets_knobs = get_triplets_powering_knobs(madx, ip=ip)
    quads_knobs = get_independent_quadrupoles_powering_knobs(madx, quad_numbers=VARIED_IR_QUADRUPOLES, ip=ip, beam=1)
    working_point_knobs = get_tunes_and_chroma_knobs(madx, beam=1)
    return BeamConfig(
        twiss_tfs=twiss_df,
        triplets_knobs=triplets_knobs,
        quads_knobs=quads_knobs,
        working_point_knobs=working_point_knobs,
    )


def get_bare_waist_shift_beam2_config(
    madx: Madx, ip: int, triplet_knobs: Dict[str, float], energy: float, qx: float, qy: float
) -> BeamConfig:
    """
    Applies the rigid waist shift at the provided *ip* for beam 1, and returns the corresponding
    configuration for beam 1 (twiss table, triplet knobs, independent IR quadrupoles knobs).

    .. note::
        This is similar to `~.get_bare_waist_shift_beam1_config` except that instead of applying the
        waist shift with a unit setting, it applies to powering knob for the triplets that were
        determined for beam 1. This is because the powering circuit is identical for beam 1 and beam
        2 triplets, so we need to make sure they are powered the same.

    .. important::
        It is assumed that the sequence and opticsfile have already been called beforehand.

    Args:
        madx (cpymad.madx.Madx): an instanciated `~cpymad.madx.Madx` object.
        ip (int): the IP at which to apply the rigid waist shift.
        triplet_knobs (float): the triplets powering knob values for the given *ip*, as returned by
            `~.get_bare_waist_shift_beam1_config`.
        energy (float): beam energy for the setup, in [GeV].
        qx (float): the horizontal tune to re-match to after applying the rigid
            waist shift.
        qy (float): the vertical tune to re-match to after applying the rigit
            waist shift.

    Returns:
        A custom `~.BeamConfig` object containing: the result of a ``TWISS`` call as a `~tfs.TfsDataFrame`,
        a `dict` with the names and values of the triplets powering knobs, a `dict` with the names and values
        of the independent IR quadrupoles powering knobs and a `dict` with the names and values of the working
        point knobs (tunes and chroma).
    """
    _ = get_nominal_beam_config(madx, energy=energy, beam=2, ip=ip, qx=qx - 0.04, qy=qy + 0.04)
    logger.info(f"Applying rigidity waist shift to beam 2 at IP{ip}, as determined by the beam 1 triplet knobs")
    logger.debug(f"Triplet knobs are: {triplet_knobs}")
    with madx.batch():
        madx.globals.update(triplet_knobs)
    matching.match_tunes(madx, "lhc", "lhcb2", qx, qy, calls=200)
    matching.match_chromaticities(madx, "lhc", "lhcb2", 2.0, 2.0, calls=200)
    matching.match_tunes_and_chromaticities(madx, "lhc", "lhcb2", qx, qy, 2.0, 2.0, calls=200)
    logger.debug(f"Managed to rematch B2 to Qx = {madx.table.summ.q1[0]} and Qy = {madx.table.summ.q2[0]}")

    twiss_df = twiss.get_twiss_tfs(madx, chrom=True)
    triplets_knobs = get_triplets_powering_knobs(madx, ip=ip)
    quads_knobs = get_independent_quadrupoles_powering_knobs(madx, quad_numbers=VARIED_IR_QUADRUPOLES, ip=ip, beam=2)
    working_point_knobs = get_tunes_and_chroma_knobs(madx, beam=2)
    return BeamConfig(
        twiss_tfs=twiss_df,
        triplets_knobs=triplets_knobs,
        quads_knobs=quads_knobs,
        working_point_knobs=working_point_knobs,
    )


# ----- Match for the Improved Waist Shift ----- #


def get_matched_waist_shift_config(
    madx: Madx, beam: int, ip: int, nominal_twiss: tfs.TfsDataFrame, bare_twiss: tfs.TfsDataFrame, qx: float, qy: float
) -> BeamConfig:
    """
    Performs relevant matchings to improve the rigid waist shift at the provided *ip* for beam 1,
    and returns the corresponding configuration for beam the provided *beam* (twiss table, triplet
    knobs, independent IR quadrupoles knobs).

    .. note::
        There is a bunch of hard-coded logic in this function, such as the matching points location
        etc.

    .. important::
        This assumes to whole setups from `~.get_nominal_beam_config` and then
        `~.get_bare_waist_shift_beam1_config` or `~.get_bare_waist_shift_beam2_config` have been
        called beforehand (aka the waist shift is applied).

    Args:
        madx (cpymad.madx.Madx): an instanciated `~cpymad.madx.Madx` object.
        beam (int): the beam number, should be 1 or 2.
        ip (int): the IP at which to apply the rigid waist shift.
        nominal_twiss (tfs.TfsDataFrame): the `~tfs.TfsDataFrame` with the ``TWISS`` table from the
            nominal scenario, which is used to determine matching constraint values.
        bare_twiss (tfs.TfsDataFrame): the `~tfs.TfsDataFrame` with the ``TWISS`` table from the
            bare waist shift scenario, which is used to determine matching constraint values.
        qx (float): the horizontal tune to re-match to after applying the rigid
            waist shift.
        qy (float): the vertical tune to re-match to after applying the rigit
            waist shift.

    Returns:
        A custom `~.BeamConfig` object containing: the result of a ``TWISS`` call as a `~tfs.TfsDataFrame`,
        a `dict` with the names and values of the triplets powering knobs, a `dict` with the names and values
        of the independent IR quadrupoles powering knobs and a `dict` with the names and values of the working
        point knobs (tunes and chroma).
    """
    assert beam in (1, 2)
    assert ip in (1, 2, 5, 8)
    logger.debug("Defining matching points to improve the waist shift")
    MATCH_IP_POINT = f"IP{ip:d}"  # IP marker
    MATCH_Q3_LEFT = f"MQXA.3L{ip:d}"  # Q3 left of provided IP
    MATCH_Q3_RIGHT = f"MQXA.3R{ip:d}"  # Q3 right of provided IP
    MATCH_Q11_LEFT = f"MQ.11L{ip:d}.B{beam:d}"  # Q11 left of provided IP
    MATCH_Q11_RIGHT = f"MQ.11R{ip:d}.B{beam:d}"  # Q11 right of provided IP
    SEQUENCE = f"lhcb{beam:d}"  # sequence name, depending on the beam
    logger.debug(
        "Match point names are: "
        f"'{MATCH_IP_POINT}', '{MATCH_Q3_LEFT}', '{MATCH_Q3_RIGHT}', '{MATCH_Q11_LEFT}', '{MATCH_Q11_RIGHT}'"
    )

    logger.debug("Matching for the beta-functions and dispersion")
    madx.command.match(sequence=SEQUENCE, chrom=True)
    # First we give constraints for the IP point, same as in the bare waist
    madx.command.constraint(
        sequence=SEQUENCE,
        range_=MATCH_IP_POINT,
        betx=bare_twiss.BETX[MATCH_IP_POINT],
        bety=bare_twiss.BETY[MATCH_IP_POINT],
        dx=0,
        dy=0,
    )
    # Then constraints at Q3 matching points, also same as in the bare waist
    madx.command.constraint(
        sequence=SEQUENCE,
        range_=MATCH_Q3_LEFT.upper(),
        betx=bare_twiss.BETX[MATCH_Q3_LEFT],
        bety=bare_twiss.BETY[MATCH_Q3_LEFT],
    )
    madx.command.constraint(
        sequence=SEQUENCE,
        range_=MATCH_Q3_RIGHT.upper(),
        betx=bare_twiss.BETX[MATCH_Q3_RIGHT],
        bety=bare_twiss.BETY[MATCH_Q3_RIGHT],
    )
    # Then constraints at Q11 matching points, now the same as in the nominal scenario
    madx.command.constraint(
        sequence=SEQUENCE,
        range_=MATCH_Q11_LEFT.upper(),
        betx=nominal_twiss.BETX[MATCH_Q11_LEFT],
        bety=nominal_twiss.BETY[MATCH_Q11_LEFT],
    )
    madx.command.constraint(
        sequence=SEQUENCE,
        range_=MATCH_Q11_RIGHT.upper(),
        betx=nominal_twiss.BETX[MATCH_Q11_RIGHT],
        bety=nominal_twiss.BETY[MATCH_Q11_RIGHT],
    )
    # TODO: maybe we add some constraints for the alpha at Q11 match points with a lower weight (let's say 0.5 to get half of the beta weight)
    # this may help the matching a little bit

    # We make a knob varying Q4 to Q10 included and we match
    lhc.vary_independent_ir_quadrupoles(madx, quad_numbers=VARIED_IR_QUADRUPOLES, sides=("R", "L"), ip=ip, beam=beam)
    try:
        with timeit(lambda spanned: logger.debug(f"Rematched the waist shift in {spanned} seconds")):
            madx.command.jacobian(calls=25, strategy=1, tolerance=1.0e-21)
            madx.command.endmatch()
    except (RemoteProcessClosed, RemoteProcessCrashed, TwissFailed):
        logger.error("A crash occured in MAD-X when trying to rematch the waist shift")
        console.print_exception()

    # Sanity check: use MQTs (minimal beta-beating impact) to get back to working point in case of drift
    matching.match_tunes(madx, "lhc", SEQUENCE, qx, qy, calls=200)
    matching.match_chromaticities(madx, "lhc", SEQUENCE, 2.0, 2.0, calls=200)
    matching.match_tunes_and_chromaticities(madx, "lhc", SEQUENCE, qx, qy, 2.0, 2.0, calls=200)
    logger.debug(f"Managed to rematch B{beam:d} to Qx = {madx.table.summ.q1[0]} and Qy = {madx.table.summ.q2[0]}")

    twiss_df = twiss.get_twiss_tfs(madx, chrom=True)
    triplets_knobs = get_triplets_powering_knobs(madx, ip=ip)
    quads_knobs = get_independent_quadrupoles_powering_knobs(madx, quad_numbers=VARIED_IR_QUADRUPOLES, ip=ip, beam=beam)
    working_point_knobs = get_tunes_and_chroma_knobs(madx, beam=beam)
    return BeamConfig(
        twiss_tfs=twiss_df,
        triplets_knobs=triplets_knobs,
        quads_knobs=quads_knobs,
        working_point_knobs=working_point_knobs,
    )


# ----- Apply a Different Config's Knobs ----- #


def get_waist_shift_config_from_applied_existing_knobs(
    madx: Madx, use_knobs_from: Path, beam: int, ip: int, qx: float, qy: float
) -> BeamConfig:
    """
    Performs relevant matchings to improve the rigid waist shift at the provided *ip* for beam 1,
    and returns the corresponding configuration for beam the provided *beam* (twiss table, triplet
    knobs, independent IR quadrupoles knobs).

    .. important::
        This assumes to whole setups from `~.get_nominal_beam_config` and then
        `~.get_bare_waist_shift_beam1_config` or `~.get_bare_waist_shift_beam2_config` have been
        called beforehand (aka the waist shift is applied).

    Args:
        madx (cpymad.madx.Madx): an instanciated `~cpymad.madx.Madx` object.
        beam (int): the beam number, should be 1 or 2.
        use_knobs_from (pathlib.Path): the directory of a previous configuration's output, from where the
            knobs to use will be looked for.
        ip (int): the IP at which to apply the rigid waist shift.
        qx (float): the horizontal tune to re-match to after applying the rigid
            waist shift.
        qy (float): the vertical tune to re-match to after applying the rigit
            waist shift.

    Returns:
        A custom `~.BeamConfig` object containing: the result of a ``TWISS`` call as a `~tfs.TfsDataFrame`,
        a `dict` with the names and values of the triplets powering knobs, a `dict` with the names and values
        of the independent IR quadrupoles powering knobs and a `dict` with the names and values of the working
        point knobs (tunes and chroma).
    """
    # The waist shift is already applied when calling this function and there will be a rematching of the
    # working point later on so the only knobsfile called from the previous configuration is the independent
    # quadrupoles powering.
    previous_conf_quads_knob_file: Path = use_knobs_from / f"BEAM{beam:d}" / "KNOBS" / "quadrupoles.madx"
    logger.debug(f"Applying the knobs from '{previous_conf_quads_knob_file}' on this configuration")
    madx.call(fullpath(previous_conf_quads_knob_file))

    # Sanity check: use MQTs (minimal beta-beating impact) to get back to working point in case of drift
    matching.match_tunes(madx, "lhc", f"lhcb{beam:d}", qx, qy, calls=200)
    matching.match_chromaticities(madx, "lhc", f"lhcb{beam:d}", 2.0, 2.0, calls=200)
    matching.match_tunes_and_chromaticities(madx, "lhc", f"lhcb{beam:d}", qx, qy, 2.0, 2.0, calls=200)
    logger.debug(f"Managed to rematch B{beam:d} to Qx = {madx.table.summ.q1[0]} and Qy = {madx.table.summ.q2[0]}")

    # Query and return all the relevant knobs
    twiss_df = twiss.get_twiss_tfs(madx, chrom=True)
    triplets_knobs = get_triplets_powering_knobs(madx, ip=ip)
    quads_knobs = get_independent_quadrupoles_powering_knobs(madx, quad_numbers=VARIED_IR_QUADRUPOLES, ip=ip, beam=beam)
    working_point_knobs = get_tunes_and_chroma_knobs(madx, beam=beam)
    return BeamConfig(
        twiss_tfs=twiss_df,
        triplets_knobs=triplets_knobs,
        quads_knobs=quads_knobs,
        working_point_knobs=working_point_knobs,
    )
