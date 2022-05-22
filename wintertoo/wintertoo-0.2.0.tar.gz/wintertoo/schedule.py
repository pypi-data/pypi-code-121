import pandas as pd
import os
import numpy as np
from astropy.time import Time
from astropy import units as u
import logging
from wintertoo.data import summer_filters, get_default_value
from wintertoo.fields import get_best_summer_field
from wintertoo.validate import validate_schedule_df, calculate_overall_priority

logger = logging.getLogger(__name__)


def to_date_string(
        time: Time
):
    return time.isot.split("T")[0]


def build_schedule(
        ra_degs: list,
        dec_degs: list,
        field_ids: list,
        start_times: list,
        end_times: list,
        program_name: str,
        program_id: int,
        pi: str,
        program_priority: float = 0.,
        filters: list = None,
        texp: float = get_default_value("visitExpTime"),
        nexp: int = 1,
        dither_bool: bool = get_default_value("dither"),
        dither_distance: float = get_default_value("ditherStepSize"),
        maximum_airmass: float = get_default_value("maxAirmass"),
        target_priorities: list = None,
        csv_save_file: str = None,
):

    if filters is None:
        filters = summer_filters

    schedule = pd.DataFrame()

    for i, ra_deg in enumerate(ra_degs):
        dec_deg = dec_degs[i]
        field_id = field_ids[i]
        start_time = start_times[i]
        end_time = end_times[i]

        priority = calculate_overall_priority(
            target_priority=target_priorities[i],
            program_base_priority=program_priority
        )

        for f in filters:
            for _ in range(nexp):
                new = pd.DataFrame([{
                    "fieldRA": np.radians(ra_deg),
                    "fieldDec": np.radians(dec_deg),
                    "fieldID": field_id,
                    "azimuth": -100,
                    "altitude": -100,
                    "filter": f,
                    "visitExpTime": texp,
                    "priority": priority,
                    "programPI": pi,
                    "progName": program_name,
                    "progID": program_id,
                    "validStart": start_time.mjd,
                    "validStop": end_time.mjd,
                    "observed": False,
                    "maxAirmass": maximum_airmass,
                    "dither": dither_bool,
                    "ditherStepSize": dither_distance,
                }])
                schedule = pd.concat([schedule, new], ignore_index=True)

    schedule = schedule.astype({
        "dither": bool,
        "observed": bool
    })

    schedule["obsHistID"] = range(len(schedule))
    schedule["requestID"] = range(len(schedule))

    validate_schedule_df(schedule)

    if csv_save_file is not None:
        logger.info(f"Saving schedule to {csv_save_file}")
        schedule.to_csv(csv_save_file, index=False)
    return schedule


def make_schedule(
        ra_degs: list,
        dec_degs: list,
        field_ids: list,
        start_times: list,
        end_times: list,
        filters: list,
        target_priorities: list,
        program_name: str,
        program_id: int,
        pi: str,
        program_priority: float = 0.,
        t_exp: float = get_default_value("visitExpTime"),
        n_exp: int = 1,
        dither_bool: bool = get_default_value("dither"),
        dither_distance: float = get_default_value("ditherStepSize"),
        maximum_airmass: float = get_default_value("maxAirmass"),
        csv_save_file: str = None,
):
    schedule = build_schedule(
        ra_degs=ra_degs,
        dec_degs=dec_degs,
        field_ids=field_ids,
        start_times=start_times,
        end_times=end_times,
        filters=filters,
        target_priorities=target_priorities,
        program_name=program_name,
        program_id=program_id,
        pi=pi,
        program_priority=program_priority,
        texp=t_exp,
        nexp=n_exp,
        dither_bool=dither_bool,
        dither_distance=dither_distance,
        maximum_airmass=maximum_airmass,
        csv_save_file=csv_save_file,
    )
    return schedule


def schedule_ra_dec(
        ra_deg: float,
        dec_deg: float,
        pi: str,
        program_name: str,
        program_id: int,
        target_priority: float = 1.,
        filters=None,
        t_exp: float = get_default_value("visitExpTime"),
        n_exp: int = 1,
        dither_bool: bool = get_default_value("dither"),
        dither_distance: float = get_default_value("ditherStepSize"),
        start_time: Time = None,
        end_time: Time = None,
        summer: bool = True,
        use_field: bool = True,
        csv_save_file: str = None,
):

    if start_time is None:
        logger.info(f"No start time specified. Using 'now' as start time.")
        start_time = Time.now()

    if end_time is None:
        logger.info(f"No end time specified. Using '1 day from now' as end time.")
        end_time = Time.now() + 1*u.day

    if summer:
        get_best_field = get_best_summer_field
        default_filters = summer_filters
    else:
        raise NotImplementedError

    if filters is None:
        logger.info(f"No filters specified. Using all as default: {default_filters}.")
        filters = default_filters
    if not isinstance(filters, list):
        filters = [filters]

    # Take RA/Dec and select nearest-centered field

    if use_field:
        best_field = get_best_field(ra_deg, dec_deg)
        ra_deg = best_field["RA"]
        dec_deg = best_field["Dec"]
        field_id = best_field["#ID"]
    else:
        field_id = get_default_value("fieldID")

    schedule = make_schedule(
        ra_degs=[ra_deg for _ in filters],
        dec_degs=[dec_deg for _ in filters],
        field_ids=[field_id for _ in filters],
        start_times=[start_time for _ in filters],
        end_times=[end_time for _ in filters],
        filters=filters,
        target_priorities=[target_priority for _ in filters],
        t_exp=t_exp,
        n_exp=n_exp,
        dither_bool=dither_bool,
        dither_distance=dither_distance,
        pi=pi,
        program_name=program_name,
        program_id=program_id,
        csv_save_file=csv_save_file
    )

    return schedule

