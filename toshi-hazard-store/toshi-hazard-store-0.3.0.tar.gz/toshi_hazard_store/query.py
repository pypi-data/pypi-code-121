"""Queries for saving and retrieving openquake hazard results with convenience."""
from typing import Iterable, Iterator

import toshi_hazard_store.model as model


def batch_save_hcurve_stats(toshi_id: str, models: Iterable[model.ToshiOpenquakeHazardCurveStats]) -> None:
    """Save list of ToshiOpenquakeHazardCurveStats updating hash and range keys."""
    with model.ToshiOpenquakeHazardCurveStats.batch_write() as batch:
        for item in models:
            item.haz_sol_id = toshi_id
            item.imt_loc_agg_rk = f"{item.imt}:{item.loc}:{item.agg}"
            batch.save(item)


def batch_save_hcurve_rlzs(toshi_id, models: Iterable[model.ToshiOpenquakeHazardCurveRlzs]):
    """Save list of ToshiOpenquakeHazardCurveRlzs updating hash and range keys."""
    with model.ToshiOpenquakeHazardCurveRlzs.batch_write() as batch:
        for item in models:
            item.haz_sol_id = toshi_id
            item.imt_loc_rlz_rk = f"{item.imt}:{item.loc}:{item.rlz}"
            batch.save(item)


mOHCS = model.ToshiOpenquakeHazardCurveStats
mOHCR = model.ToshiOpenquakeHazardCurveRlzs
mOHM = model.ToshiOpenquakeHazardMeta


def get_hazard_stats_curves(
    haz_sol_id: str,
    imts: Iterable[str] = None,
    locs: Iterable[str] = None,
    aggs: Iterable[str] = None,
) -> Iterator[mOHCS]:
    """Use ToshiOpenquakeHazardCurveStats.imt_loc_agg_rk range key as much as possible."""

    range_key_first_val = ""
    condition_expr = None

    if imts:
        first_imt = sorted(imts)[0]
        range_key_first_val += f"{first_imt}"
        condition_expr = condition_expr & mOHCS.imt.is_in(*imts)
    if locs:
        condition_expr = condition_expr & mOHCS.loc.is_in(*locs)
    if aggs:
        condition_expr = condition_expr & mOHCS.agg.is_in(*aggs)

    if imts and locs:
        first_loc = sorted(locs)[0]
        range_key_first_val += f":{first_loc}"
    if imts and locs and aggs:
        first_agg = sorted(aggs)[0]
        range_key_first_val += f":{first_agg}"

    for hit in model.ToshiOpenquakeHazardCurveStats.query(
        haz_sol_id, mOHCS.imt_loc_agg_rk >= range_key_first_val, filter_condition=condition_expr
    ):
        yield (hit)


def get_hazard_rlz_curves(
    haz_sol_id: str,
    imts: Iterable[str] = None,
    locs: Iterable[str] = None,
    rlzs: Iterable[str] = None,
) -> Iterator[mOHCR]:
    """Use ToshiOpenquakeHazardCurveRlzs.imt_loc_agg_rk range key as much as possible."""

    range_key_first_val = ""
    condition_expr = None

    if imts:
        first_imt = sorted(imts)[0]
        range_key_first_val += f"{first_imt}"
        condition_expr = condition_expr & mOHCR.imt.is_in(*imts)
    if locs:
        condition_expr = condition_expr & mOHCR.loc.is_in(*locs)
    if rlzs:
        condition_expr = condition_expr & mOHCR.rlz.is_in(*rlzs)

    if imts and locs:
        first_loc = sorted(locs)[0]
        range_key_first_val += f":{first_loc}"
    if imts and locs and rlzs:
        first_rlz = sorted(rlzs)[0]
        range_key_first_val += f":{first_rlz}"

    print(f"range_key_first_val: {range_key_first_val}")
    print(condition_expr)

    for hit in model.ToshiOpenquakeHazardCurveRlzs.query(
        haz_sol_id, mOHCR.imt_loc_rlz_rk >= range_key_first_val, filter_condition=condition_expr
    ):
        yield (hit)


def get_hazard_metadata(
    haz_sol_ids: Iterable[str] = None,
    vs30_vals: Iterable[int] = None,
) -> Iterator[mOHM]:
    """Fetch ToshiOpenquakeHazardMeta based on criteria."""

    condition_expr = None
    if haz_sol_ids:
        condition_expr = condition_expr & mOHM.haz_sol_id.is_in(*haz_sol_ids)
    if vs30_vals:
        condition_expr = condition_expr & mOHM.vs30.is_in(*vs30_vals)

    for hit in model.ToshiOpenquakeHazardMeta.query(
        "ToshiOpenquakeHazardMeta", filter_condition=condition_expr  # NB the partition key is the table name!
    ):
        yield (hit)
