import posixpath
from typing import Type, List, Optional

from airflow.models import BaseOperator

from openlineage.airflow.extractors.base import TaskMetadata
from openlineage.common.dataset import Source, Dataset

from tokyo_lineage.models.base import BaseTask
from tokyo_lineage.metadata_extractor.base import BaseMetadataExtractor

from tokyo_lineage.utils.airflow import get_connection, instantiate_task
from tokyo_lineage.utils.dataset_naming_helper import (
    # Local filesystem dataset
    fs_scheme,
    fs_authority,
    fs_connection_uri,
    
    # GCS dataset
    gcs_scheme,
    gcs_authority,
    gcs_connection_uri
)

EXPORTER_OPERATOR_CLASSNAMES = ["PostgresToAvroOperator", "PostgresToJsonOperator", "MongoToAvroOperator", "MySqlToAvroOperator"]


class FileToGcsExtractor(BaseMetadataExtractor):
    def __init__(self, task: Type[BaseTask]):
        super().__init__(task)

    @classmethod
    def get_operator_classnames(cls) -> List[str]:
        return ["FileToGoogleCloudStorageOperator"]
    
    @property
    def operator(self) -> Type[BaseOperator]:
        return self.task.task

    def extract(self) -> Optional[TaskMetadata]:
        filesystem_source = Source(
            scheme=self._get_fs_scheme(),
            authority=self._get_fs_authority(),
            connection_url=self._get_fs_connection_uri()
        )

        inputs = [
            Dataset(
                name=self._get_input_dataset_name(),
                source=filesystem_source
            )
        ]

        output_gcs_source = Source(
            scheme=self._get_gcs_scheme(),
            authority=self._get_gcs_authority(),
            connection_url=self._get_gcs_connection_uri()
        )

        outputs = [
            Dataset(
                name=self._get_output_dataset_name(),
                source=output_gcs_source
            )
        ]

        return TaskMetadata(
            name=f"{self.operator.dag_id}.{self.operator.task_id}",
            inputs=[ds.to_openlineage_dataset() for ds in inputs],
            outputs=[ds.to_openlineage_dataset() for ds in outputs]
        )

    def _get_gcs_connection(self):
        conn = get_connection(self.operator.google_cloud_storage_conn_id)
        return conn

    def _get_gcs_scheme(self) -> str:
        return gcs_scheme()
    
    def _get_gcs_connection_uri(self) -> str:
        return gcs_connection_uri(self.operator.bucket, self.operator.dst)

    def _get_gcs_authority(self) -> str:
        return gcs_authority(self.operator.bucket)

    def _get_output_dataset_name(self) -> str:
        dataset_name = self.operator.dst
        # make sure path starts from root
        dataset_name = posixpath.join("/", dataset_name)
        return dataset_name

    def _get_fs_scheme(self) -> str:
        return fs_scheme()

    def _get_fs_connection_uri(self) -> str:
        return fs_connection_uri(self.operator.src)

    def _get_fs_authority(self) -> str:
        return fs_authority()

    def _get_input_dataset_name(self) -> str:
        exporter = self._get_nearest_exporter_upstream()
        execution_date = self.task.task_instance.execution_date

        exporter, _ = self._instantiate_task(exporter, execution_date)

        if hasattr(exporter, 'avro_output_path'):
            return exporter.avro_output_path
        elif hasattr(exporter, 'json_output_path'):
            return exporter.json_output_path

    def _get_nearest_exporter_upstream(self) -> Type[BaseOperator]:
        operator = self.operator
        
        upstream_operators: List[BaseOperator] = operator.upstream_list[::-1]

        for operator in upstream_operators:
            if operator.__class__.__name__ in EXPORTER_OPERATOR_CLASSNAMES:
                return operator
    
    def _instantiate_task(self, task, execution_date):
        return instantiate_task(task, execution_date)