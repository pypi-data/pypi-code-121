from itertools import chain
import logging
from pathlib import Path
from typing import List, Optional, Union

import pyarrow as pa
import pyarrow.dataset as ds


def write_dataset(
    dataset: ds.dataset,
    location: Union[str, Path],
    schema: pa.Schema,
    format="parquet",
    filesystem: Optional[pa.fs.FileSystem] = None,
    partitioning: Optional[List[str]] = None,
    batch_size: int = 1_000_000,
    mode="append",
):
    """Write a dataset to a location, appending if there is an existing dataset. This can be tricky
    as the out-of-memory dataset might be too large to fit in memory. So we need to be careful to
    get the data in batches and only the part that needs to be appended to.
    """
    # Get the out-of-memory dataset to append to
    oom_dataset: Optional[ds.Dataset] = None
    try:
        oom_dataset = ds.dataset(
            location,
            schema=schema,
            format=format,
            filesystem=filesystem,
            partitioning=partitioning,
        )
    except Exception as e:
        logging.warning(f"Failed to retrieve existing dataset: {e}")
        pass

    if oom_dataset is not None and mode == "append":
        # We need to get the OOM dataset in batches, so we can append to it
        if partitioning is None:
            batch_filter = None
        else:
            partition_cols = dataset.to_table(columns=partitioning)
            unique_col_vals = [
                ds.field(col).isin(partition_cols.column(col).unique())
                for col in partition_cols.column_names
            ]
            batch_filter = unique_col_vals[0]
            if len(unique_col_vals) > 1:
                for each in unique_col_vals[1:]:
                    batch_filter = batch_filter and each

        if oom_dataset is not None:
            oom_batches = oom_dataset.scanner(
                batch_size=batch_size, filter=batch_filter
            ).to_batches()
        else:
            oom_batches = []

        im_batches = dataset.to_batches()

        if mode == "append":
            write_mode = "overwrite_or_ignore"
        elif mode == "write":
            write_mode = "delete_matching"
        else:
            raise ValueError(f"Unknown mode: {mode}")
        ds.write_dataset(
            chain(oom_batches, im_batches),
            location,
            schema=schema,
            filesystem=filesystem,
            partitioning=partitioning,
            format=format,
            existing_data_behavior=write_mode,
        )
    else:
        ds.write_dataset(
            dataset,
            location,
            schema=schema,
            filesystem=filesystem,
            partitioning=partitioning,
            format=format,
            existing_data_behavior="overwrite_or_ignore",
        )
