import json
import posixpath
from typing import Type, List, Optional

from airflow.models import BaseOperator
from airflow.contrib.hooks.bigquery_hook import BigQueryHook

from openlineage.airflow.extractors.base import TaskMetadata
from openlineage.common.dataset import Source, Dataset, Field

from tokyo_lineage.metadata_extractor.base import BaseMetadataExtractor
from tokyo_lineage.models.base import BaseTask

from tokyo_lineage.utils.airflow import get_connection, instantiate_task
from tokyo_lineage.utils.dataset_naming_helper import (
    # GCS dataset
    gcs_scheme,
    gcs_authority,
    gcs_connection_uri,
    # BigQuery dataset
    bq_scheme,
    bq_authority,
    bq_connection_uri
)

UPLOADER_OPERATOR_CLASSNAMES = ["FileToGoogleCloudStorageOperator"]

class GcsToBigQueryExtractor(BaseMetadataExtractor):
    def __init__(self, task: Type[BaseTask]):
        super().__init__(task)
    
    @classmethod
    def get_operator_classnames(cls) -> List[str]:
        return ["GoogleCloudStorageToBigQueryOperator"]
    
    @property
    def operator(self) -> Type[BaseOperator]:
        return self.task.task
    
    def extract(self) -> Optional[TaskMetadata]:

        # input_dataset_name is bucket name
        inputs = [
            Dataset(
                name=self._get_input_dataset_name(),
                source=Source(
                    scheme=self._get_gcs_scheme(),
                    authority=self._get_gcs_authority(),
                    connection_url=gcs_connection_uri(self.operator.bucket,
                                                        source_object)
                )
            ) for source_object in self.operator.source_objects
        ]

        # output_source generated from bigquery_conn_id
        output_source = Source(
            scheme=self._get_bq_scheme(),
            authority=self._get_bq_authority(),
            connection_url=self._get_bq_connection_uri()
        )

        # output_dataset_name is dataset + table name
        outputs = [
            Dataset(
                name=self._get_output_dataset_name(),
                source=output_source,
                fields=self._get_output_fields()
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
    
    def _get_gcs_authority(self) -> str:
        return gcs_authority(self.operator.bucket)
    
    def _get_project_dataset_table(self):
        project_dataset_table = self.operator.destination_project_dataset_table
        filler = [None] * (3-len(project_dataset_table.split('.')))
        splitted = project_dataset_table.split('.')
        project, dataset, table = filler + splitted

        return project, dataset, table

    def _get_bq_connection(self):
        conn = get_connection(self.operator.bigquery_conn_id)
        return conn
    
    def _get_bq_scheme(self) -> str:
        return bq_scheme()
    
    def _get_bq_connection_uri(self) -> str:
        _, dataset, table = self._get_project_dataset_table()
        conn = self._get_bq_connection()
        return bq_connection_uri(conn, dataset, table)
    
    def _get_bq_authority(self) -> str:
        conn = self._get_bq_connection()
        return bq_authority(conn)

    def _get_output_dataset_name(self) -> str:
        project, dataset, table = self._get_project_dataset_table()
        
        if project is None:
            conn = self._get_bq_connection()
            extras = json.loads(conn.get_extra())
            project = extras['extra__google_cloud_platform__project']

        return f"{project}.{dataset}.{table}"
    
    def _get_output_fields(self) -> List[Field]:
        _, dataset, table = self._get_project_dataset_table()
        sql = f"""
        SELECT
            *
        FROM
            {dataset}.INFORMATION_SCHEMA.COLUMNS
        WHERE table_name = '{table}'
        ORDER BY ordinal_position;
        """

        bq_hook = BigQueryHook(bigquery_conn_id=self.operator.bigquery_conn_id,
                                delegate_to=self.operator.delegate_to,
                                use_legacy_sql=False)
        conn = bq_hook.get_conn()
        cursor = conn.cursor()

        cursor.execute(sql)
        _fields = cursor.fetchall()

        fields = [
            Field(
                name=f[3],
                type=f"{f[6]}".lower()
            ) for f in _fields
        ]

        return fields

    def _get_input_dataset_name(self) -> str:
        uploader = self._get_nearest_uploader_upstream()
        execution_date = self.task.task_instance.execution_date

        uploader, _ = instantiate_task(uploader, execution_date)

        # make sure path starts from root
        dataset_name = posixpath.join("/", uploader.dst)

        return dataset_name

    def _get_nearest_uploader_upstream(self) -> Type[BaseOperator]:
        operator = self.operator
        
        upstream_operators: List[BaseOperator] = operator.upstream_list[::-1]

        for operator in upstream_operators:
            if operator.__class__.__name__ in UPLOADER_OPERATOR_CLASSNAMES:
                return operator