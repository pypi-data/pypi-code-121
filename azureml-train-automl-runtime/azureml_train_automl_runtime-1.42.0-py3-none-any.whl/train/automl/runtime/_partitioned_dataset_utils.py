# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import random
from typing import List, cast

import dask.dataframe as dd
import dask.delayed as ddelayed
from azureml.automl.runtime.featurizer.transformer.timeseries._distributed.distributed_timeseries_util import (
    convert_grain_dict_to_str)
from azureml.data import TabularDataset
from azureml.data.abstract_dataset import _PartitionKeyValueCommonPath


def _get_sorted_partitions(partitioned_dataset: TabularDataset) -> List[_PartitionKeyValueCommonPath]:
    kvps = partitioned_dataset._get_partition_key_values_with_common_path()
    kvps.sort(key=lambda x: convert_grain_dict_to_str(x.key_values))
    return cast(List[_PartitionKeyValueCommonPath], kvps)


def _get_dataset_for_grain(grain_keyvalues_and_path: _PartitionKeyValueCommonPath,
                           partitioned_dataset: TabularDataset) -> TabularDataset:
    return partitioned_dataset._get_partition_using_partition_key_values_common_path(grain_keyvalues_and_path)


def _to_partitioned_dask_dataframe(partitioned_dataset: TabularDataset,
                                   all_grain_keyvalues_and_path: List[_PartitionKeyValueCommonPath]) -> dd:
    datasets_for_all_grains = [_get_dataset_for_grain(grain_keyvalues_and_path, partitioned_dataset)
                               for grain_keyvalues_and_path in all_grain_keyvalues_and_path]
    delayed_functions = [ddelayed(dataset_for_grain.to_pandas_dataframe)()
                         for dataset_for_grain in datasets_for_all_grains]
    ddf = dd.from_delayed(delayed_functions, verify_meta=False)
    return ddf


def _to_dask_dataframe_of_random_grains(partitioned_dataset: TabularDataset,
                                        all_grain_keyvalues_and_path: List[_PartitionKeyValueCommonPath],
                                        grain_count: int) -> dd:
    random_grain_key_values = all_grain_keyvalues_and_path
    if grain_count < len(all_grain_keyvalues_and_path):
        random_grain_key_values = random.sample(all_grain_keyvalues_and_path, grain_count)

    datasets_for_all_grains = [_get_dataset_for_grain(grain_keyvalues_and_path, partitioned_dataset)
                               for grain_keyvalues_and_path in random_grain_key_values]
    delayed_functions = [ddelayed(dataset_for_grain.to_pandas_dataframe)()
                         for dataset_for_grain in datasets_for_all_grains]
    ddf = dd.from_delayed(delayed_functions, verify_meta=False)
    return ddf
