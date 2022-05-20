from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import yaml

from fiddler.core_objects import BatchPublishType, Column, DatasetInfo, FiddlerTimestamp
from fiddler.utils import logging
from fiddler.v2.api.api import Client
from fiddler.v2.constants import FiddlerTimestamp as V2FiddlerTimestamp
from fiddler.v2.constants import FileType
from fiddler.v2.schema.common import Column as V2Column
from fiddler.v2.schema.common import DatasetInfo as V2DatasetInfo
from fiddler.v2.schema.dataset import Dataset

DATASET_MAX_ROWS = 50_000


logger = logging.getLogger(__name__)


class V1V2Compat:
    def __init__(self, client_v2: Client):
        self.client_v2 = client_v2

    # Projects
    def get_projects(self, get_project_details: bool = False) -> List[str]:
        projects = self.client_v2.get_projects()
        return [p.name for p in projects]

    def add_project(self, project_id: str) -> Dict[str, str]:
        project = self.client_v2.add_project(project_name=project_id)
        return {'project_name': project.name}

    def delete_project(self, project_id: str) -> None:
        self.client_v2.delete_project(project_name=project_id)

    # Datasets
    def get_datasets(self, project_id: str) -> List[str]:
        datasets = self.client_v2.get_datasets(project_name=project_id)
        return [d.name for d in datasets]

    def get_dataset_artifact(
        self,
        project_id: str,
        dataset_id: str,
        max_rows: int = 1_000,
        splits: Optional[List[str]] = None,
        sampling=False,
        dataset_info: Optional[DatasetInfo] = None,
        include_fiddler_id=False,
    ) -> Dict[str, pd.DataFrame]:
        raise NotImplementedError('This method is currently not implemented')

    def get_dataset(self, project_id: str, dataset_id: str) -> Dataset:
        dataset = self.client_v2.get_dataset(
            project_name=project_id, dataset_name=dataset_id
        )
        return dataset  # @todo: Make the response compatible with dataset info

    def get_dataset_info(self, project_id: str, dataset_id: str) -> DatasetInfo:
        dataset = self.get_dataset(project_id, dataset_id)
        dataset_info = DatasetInfo(
            display_name=dataset.name,
            columns=[
                Column.from_dict(col.dict(by_alias=True))
                for col in dataset.info.columns
            ],
            dataset_id=dataset_id,
        )
        return dataset_info

    def delete_dataset(self, project_id: str, dataset_id: str) -> None:
        # @todo: check that on the server side
        # 1. Delete the table in CH
        # 2. Delete the files from blob store
        # 3. Delete the entry from postgres table
        self.client_v2.delete_dataset(project_name=project_id, dataset_name=dataset_id)

    # Uploading Dataset
    def upload_dataset_dataframe(
        self,
        project_id: str,
        dataset: Dict[str, pd.DataFrame],
        dataset_id: str,
        info: Optional[DatasetInfo] = None,
        size_check_enabled: bool = True,
    ) -> Dict:
        v2_info = None
        if info:
            v2_info = V2DatasetInfo(
                columns=[V2Column.from_dict(col.to_dict()) for col in info.columns]
            )

        return self.client_v2.upload_dataset_dataframe(
            project_name=project_id,
            dataset_name=dataset_id,
            datasets=dataset,
            info=v2_info,
            is_sync=True,
        )

    def upload_dataset(
        self,
        project_id: str,
        dataset_id: str,
        file_path: str,
        file_type: str = 'csv',
        file_schema=Dict[str, Any],
        info: Optional[DatasetInfo] = None,
        size_check_enabled: bool = False,
    ) -> Dict:
        file_name = file_path.split('/')[-1]
        files = {file_name: Path(file_path)}
        # @todo as we only support csv on server side for now, throw an error saying the same.
        v2_info = None
        if info:
            v2_info = V2DatasetInfo(
                columns=[V2Column.from_dict(col.to_dict()) for col in info.columns]
            )
        if file_type == 'csv':
            return self.client_v2.upload_dataset(
                project_name=project_id,
                dataset_name=dataset_id,
                files=files,
                info=v2_info,
                file_type=FileType.CSV,
                file_schema=file_schema,
            )
        else:
            raise NotImplementedError('Only csv is supported in current implementation')

    def upload_dataset_dir(
        self,
        project_id: str,
        dataset_id: str,
        dataset_dir: Path,
        file_type: str = 'csv',
        file_schema=None,
        size_check_enabled: bool = False,
    ):
        # Input checks
        if file_type != 'csv':
            raise NotImplementedError('Only CSV filetype is supported')

        if not dataset_dir.is_dir():
            raise ValueError(f'{dataset_dir} is not a directory')

        dataset_yaml = dataset_dir / f'{dataset_id}.yaml'
        if not dataset_yaml.is_file():
            raise ValueError(f'Dataset YAML file not found: {dataset_yaml}')

        with dataset_yaml.open() as f:
            dataset_info = DatasetInfo.from_dict(yaml.safe_load(f))

        # Convert files into dataframes
        files = dataset_dir.glob(f'*.{FileType.CSV}')
        csv_files = [x for x in files if x.is_file()]

        dataset = {}
        csv_paths = []
        for file in csv_files:
            csv_name = str(file).split('/')[-1]
            csv_paths.append(csv_name)
            name = csv_name[:-4]

            # @TODO Change the flow so that we can read the CSV in chunks
            dataset[name] = pd.read_csv(file, dtype=dataset_info.get_pandas_dtypes())

        # size check
        size_exceeds = False
        for name, df in dataset.items():
            if df.shape[0] > DATASET_MAX_ROWS:
                size_exceeds = True
        if size_exceeds:
            raise RuntimeError(
                f'Dataset upload aborted as size exceeds {DATASET_MAX_ROWS}.'
            )

        self.upload_dataset_dataframe(
            project_id=project_id,
            dataset_id=dataset_id,
            dataset=dataset,
            info=dataset_info,
            size_check_enabled=size_check_enabled,
        )

    def upload_dataset_from_dir(
        self,
        project_id: str,
        dataset_id: str,
        dataset_dir: Path,
        file_type: str = 'csv',
        file_schema=None,
        size_check_enabled: bool = False,
    ):
        if file_type != 'csv':
            raise NotImplementedError('Only CSV filetype is supported')

        info_yaml = dataset_dir / f'{dataset_id}.yaml'

        if not info_yaml.exists():
            raise ValueError(f'DatasetInfo yaml ({info_yaml}) not found.')

        with open(info_yaml) as f:
            dataset_info = DatasetInfo.from_dict(yaml.safe_load(f))

        v2_info = V2DatasetInfo(
            columns=[V2Column.from_dict(col.to_dict()) for col in dataset_info.columns]
        )

        return self.client_v2.upload_dataset_from_dir(
            project_id,
            dataset_id,
            dataset_dir,
            v2_info,
            FileType.CSV,
            file_schema,
            is_sync=True,
        )

    def publish_events_batch(  # noqa
        self,
        project_id: str,
        model_id: str,
        batch_source: Union[pd.DataFrame, str],
        id_field: Optional[str] = None,
        update_event: Optional[bool] = False,
        timestamp_field: Optional[str] = None,
        timestamp_format: FiddlerTimestamp = FiddlerTimestamp.INFER,
        data_source: Optional[BatchPublishType] = None,
        casting_type: Optional[bool] = False,
        credentials: Optional[dict] = None,
        group_by: Optional[str] = None,
    ):
        v2_timestamp_format = V2FiddlerTimestamp(timestamp_format.value)
        if type(batch_source) == pd.DataFrame and (
            data_source is None or BatchPublishType.DATAFRAME == data_source
        ):
            self.client_v2.publish_events_batch_dataframe(
                project_name=project_id,
                model_name=model_id,
                events_df=batch_source,
                id_field=id_field,
                is_update=update_event,
                timestamp_field=timestamp_field,
                timestamp_format=v2_timestamp_format,
                group_by=group_by,
                is_sync=True,
            )
        elif type(batch_source) == str and (
            data_source is None or BatchPublishType.LOCAL_DISK == data_source
        ):
            self.client_v2.publish_events_batch(
                project_name=project_id,
                model_name=model_id,
                events_path=Path(batch_source),
                id_field=id_field,
                is_update=update_event,
                timestamp_field=timestamp_field,
                timestamp_format=v2_timestamp_format,
                group_by=group_by,
                file_type=FileType.CSV,
                is_sync=True,
            )
        else:
            raise NotImplementedError(
                'Batch source other than dataframe and csv is not implemented now'
            )

    def publish_event(
        self,
        project_id: str,
        model_id: str,
        event: dict,
        event_id: Optional[str] = None,
        update_event: Optional[bool] = None,
        event_timestamp: Optional[int] = None,
        timestamp_format: FiddlerTimestamp = FiddlerTimestamp.INFER,
        casting_type: Optional[bool] = False,
        dry_run: Optional[bool] = False,
    ):
        v2_timestamp_format = V2FiddlerTimestamp(timestamp_format.value)
        return self.client_v2.publish_event(
            project_name=project_id,
            model_name=model_id,
            event=event,
            event_id=event_id,
            is_update=update_event,
            event_timestamp=event_timestamp,
            timestamp_format=v2_timestamp_format,
        )
