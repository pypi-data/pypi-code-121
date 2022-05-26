"""Queries for saving and retrieving openquake hazard results with convenience."""
from typing import Iterable, Iterator

import toshi_hazard_store.model as model


def batch_save_hcurve_stats(toshi_id: str, models: Iterable[model.ToshiOpenquakeHazardCurveStats]) -> None:
    """Save list of ToshiOpenquakeHazardCurveStats updating hash and range keys."""
    with model.ToshiOpenquakeHazardCurveStats.batch_write() as batch:
        for item in models:
            item.hazard_solution_id = toshi_id
            item.vs30_imt_loc_agg_rk = f"{item.vs30}:{item.imt_code}:{item.location_code}:{item.aggregation}"
            batch.save(item)


def batch_save_hcurve_rlzs(toshi_id, models: Iterable[model.ToshiOpenquakeHazardCurveRlzs]):
    """Save list of ToshiOpenquakeHazardCurveRlzs updating hash and range keys."""
    with model.ToshiOpenquakeHazardCurveRlzs.batch_write() as batch:
        for item in models:
            item.hazard_solution_id = toshi_id
            item.vs30_imt_loc_rlz_rk = f"{item.vs30}:{item.imt_code}:{item.location_code}:{item.rlz_id}"
            batch.save(item)


mOHCS = model.ToshiOpenquakeHazardCurveStats


def get_hazard_curves_stats(
    hazard_solution_id: str,
    vs30_val: int,
    imt_code: str,
    loc_codes: Iterable[str] = None,
    agg_codes: Iterable[str] = None,
) -> Iterator[mOHCS]:
    """Use ToshiOpenquakeHazardCurveStats.vs30_imt_loc_agg_rk range key as much as possible."""

    range_key_first_val = f"{vs30_val}:{imt_code}"
    condition_expr = (mOHCS.vs30 == vs30_val) & (mOHCS.imt_code == imt_code)

    if loc_codes:
        first_loc = sorted(loc_codes)[0]
        range_key_first_val += f":{first_loc}"
        condition_expr = condition_expr & mOHCS.location_code.is_in(*loc_codes)
    if agg_codes:
        condition_expr = condition_expr & mOHCS.aggregation.is_in(*agg_codes)

    for hit in model.ToshiOpenquakeHazardCurveStats.query(
        hazard_solution_id, mOHCS.vs30_imt_loc_agg_rk >= range_key_first_val, filter_condition=condition_expr
    ):
        yield (hit)
