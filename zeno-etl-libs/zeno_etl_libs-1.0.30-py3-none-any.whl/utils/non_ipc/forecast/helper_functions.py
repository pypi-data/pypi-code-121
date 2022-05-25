'''
Author - vishal.gupta@generico.in
Objective - non ipc forecast reset main script
'''

import pandas as pd
from joblib import Parallel, delayed
from multiprocessing import cpu_count
from zeno_etl_libs.utils.warehouse.forecast.errors import error_report, wmape_report


def non_ipc_error_report(error_df, train_data, drug_class):
    drug_class = drug_class.copy()
    drug_class['bucket'] = drug_class['bucket_abc'] + drug_class['bucket_xyz']

    drug_history = drug_class.copy()[['drug_id']]
    drug_history['month_history'] = 12

    error_report(error_df, drug_class, drug_history)

    wmape_report(train_data, drug_class, drug_history)

    return 0


def apply_parallel_croston(
        dfGrouped, func, horizon=4, out_of_sample=4, croston_params=None):
    retLst = Parallel(n_jobs=cpu_count() - 4, verbose=10)(
        delayed(func)(
            group, horizon, out_of_sample, croston_params)
        for name, group in dfGrouped)
    return pd.concat(retLst)
