import copy
import os
from typing import Dict, List, Optional

import pandas as pd

from fiddler.connection import Connection
from fiddler.core_objects import DatasetInfo
from fiddler.utils import df_from_json_rows
from fiddler.utils.general_checks import type_enforce


class Dataset:
    def __init__(self, connection: Connection, project_id: str, dataset_id: str):
        self.connection = connection
        self.project_id = project_id
        self.dataset_id = dataset_id

    def get_info(self) -> DatasetInfo:
        """Get DatasetInfo for a dataset.

        :returns: A fiddler.DatasetInfo object describing the dataset.
        """
        # Type enforcement
        project_id = type_enforce('project_id', self.project_id, str)
        dataset_id = type_enforce('dataset_id', self.dataset_id, str)

        path = ['dataset_schema', self.connection.org_id, project_id, dataset_id]
        res = self.connection.call(path, is_get_request=True)

        info = DatasetInfo.from_dict(res)
        info.dataset_id = dataset_id
        return info

    def _query_dataset(
        self,
        fields: List[str],
        max_rows: int,
        split: Optional[str] = None,
        sampling=False,
        sampling_seed=0.0,
    ):
        # Type enforcement
        project_id = type_enforce('project_id', self.project_id, str)
        dataset_id = type_enforce('dataset_id', self.dataset_id, str)

        payload = dict(
            fields=fields,
            limit=max_rows,
            sampling=sampling,
        )

        if sampling:
            payload['sampling_seed'] = sampling_seed
        if split is not None:
            payload['source'] = f'{split}.csv'

        path = [
            'dataset_query',
            self.connection.org_id,
            project_id,
            dataset_id,
        ]
        res = self.connection.call(path, json_payload=payload, stream=True)
        return res

    def download(
        self,
        max_rows: int = 1_000,
        splits: Optional[List[str]] = None,
        sampling=False,
        dataset_info: Optional[DatasetInfo] = None,
        include_fiddler_id=False,
    ) -> Dict[str, pd.DataFrame]:
        """Fetches data from a dataset on Fiddler.

        :param max_rows: Up to this many rows will be fetched from eash split
            of the dataset.
        :param splits: If specified, data will only be fetched for these
            splits. Otherwise, all splits will be fetched.
        :param sampling: If True, data will be sampled up to max_rows. If
            False, rows will be returned in order up to max_rows. The seed
            will be fixed for sampling.∂
        :param dataset_info: If provided, the API will skip looking up the
            DatasetInfo (a necessary precursor to requesting data).
        :param include_fiddler_id: Return the Fiddler engine internal id
            for each row. Useful only for debugging.

        :returns: A dictionary of str -> DataFrame that maps the name of
            dataset splits to the data in those splits. If len(splits) == 1,
            returns just that split as a dataframe, rather than a dataframe.
        """

        if dataset_info is None:
            dataset_info = self.get_info()
        else:
            dataset_info = copy.deepcopy(dataset_info)

        def get_df_from_split(split, fiddler_id=include_fiddler_id):
            column_names = dataset_info.get_column_names()
            if fiddler_id:
                column_names.insert(0, '__fiddler_id')
            dataset_rows = self._query_dataset(
                fields=column_names,
                max_rows=max_rows,
                split=split,
                sampling=sampling,
            )
            return df_from_json_rows(
                dataset_rows, dataset_info, include_fiddler_id=include_fiddler_id
            )

        if splits is None:
            use_splits = [
                os.path.splitext(filename)[0] for filename in dataset_info.files
            ]
        else:
            use_splits = splits
        res = {split: get_df_from_split(split) for split in use_splits}
        if splits is not None and len(splits) == 1:
            # unwrap single-slice results
            res = next(iter(res.values()))
        return res

    def delete(self):
        """Permanently delete a dataset.

        :returns: Server response for deletion action.
        """
        # Type enforcement
        project_id = type_enforce('project_id', self.project_id, str)
        dataset_id = type_enforce('dataset_id', self.dataset_id, str)

        path = ['dataset_delete', self.connection.org_id, project_id, dataset_id]
        result = self.connection.call(path)

        return result
