# -*- coding: utf-8 -*-

def _map_factors(factors, used_factor_tables, diff_columns={'trade_date','code'}):
    factor_cols = {}
    factors = set(factors).difference({'trade_date', 'code'})
    to_keep = factors.copy()
    for f in factors:
        for t in used_factor_tables:
            if f in t.__table__.columns:
                factor_cols[t.__table__.columns[f]] = t
                to_keep.remove(f)
                break

    if to_keep:
        raise ValueError("factors in <{0}> can't be find".format(to_keep))

    return factor_cols