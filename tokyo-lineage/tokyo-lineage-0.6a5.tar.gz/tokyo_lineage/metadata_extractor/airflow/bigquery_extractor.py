import attr
import json
from typing import Type, List

from airflow.models import BaseOperator

from openlineage.client.facet import SqlJobFacet
from openlineage.common.dataset import Source, Dataset
from openlineage.airflow.extractors.base import TaskMetadata

from tokyo_lineage.utils.parser import Parser
from tokyo_lineage.models.base import BaseTask
from tokyo_lineage.metadata_extractor.base import BaseMetadataExtractor
from tokyo_lineage.utils.airflow import get_connection
from tokyo_lineage.utils.dataset_naming_helper import (
    bq_scheme,
    bq_authority,
    bq_connection_uri
)


@attr.s
class TableSchema:
    schema_name: str = attr.ib()
    table_name: str = attr.ib()


class BigQueryExtractor(BaseMetadataExtractor):
    def __init__(self, task: Type[BaseTask]):
        super().__init__(task)

    @classmethod
    def get_operator_classnames(cls) -> List[str]:
        return ["BigQueryOperator"]

    @property
    def operator(self) -> Type[BaseOperator]:
        return self.task.task

    def extract(self) -> TaskMetadata:
        parser = Parser(self.operator.sql)

        database = self._get_database()

        def source(dataset, table):
            return Source(
                scheme=self._get_bq_scheme(),
                authority=self._get_bq_authority(),
                connection_url=self._get_bq_connection_uri(dataset, table)
            )

        inputs = [
            Dataset.from_table(
                source=source(table_schema.schema_name, table_schema.table_name),
                table_name=table_schema.table_name,
                schema_name=table_schema.schema_name,
                database_name=database
            ) for table_schema in self._get_table_schemas(
                parser.tables
            )
        ]

        # Output source
        _, dataset, table = self._safe_split_dataset_name(
                                self._get_output_dataset_name())

        bq_source_out = Source(
            scheme=self._get_bq_scheme(),
            authority=self._get_bq_authority(),
            connection_url=self._get_bq_connection_uri(dataset, table)
        )

        outputs = [
            Dataset(
                name=self._get_output_dataset_name(),
                source=bq_source_out
            )
        ]

        return TaskMetadata(
            name=f"{self.operator.dag_id}.{self.operator.task_id}",
            inputs=[ds.to_openlineage_dataset() for ds in inputs],
            outputs=[ds.to_openlineage_dataset() for ds in outputs],
            job_facets={
                'sql': SqlJobFacet(self.operator.sql)
            }
        )

    def _get_bq_connection_uri(self, dataset, table) -> str:
        conn = self._get_bq_connection()
        return bq_connection_uri(conn, dataset, table)

    def _get_bq_scheme(self) -> str:
        return bq_scheme()

    def _get_bq_authority(self) -> str:
        return bq_authority(self._get_bq_connection())

    def _get_output_dataset_name(self) -> str:
        database = self._get_database()
        dataset_table = self.operator.destination_dataset_table
        return f"{database}.{dataset_table}"

    def _get_bq_connection(self):
        return get_connection(self._conn_id())

    def _conn_id(self) -> str:
        return self.operator.bigquery_conn_id

    def _get_database(self):
        bq_conn = self._get_bq_connection()
        extras = json.loads(bq_conn.get_extra())

        return extras['extra__google_cloud_platform__project']

    def _get_table_schemas(self, tables: List[str]) -> List[TableSchema]:
        for table in tables:
            _, schema_name, table_name = self._safe_split_dataset_name(table)
            yield TableSchema(schema_name, table_name)

    def _safe_split_dataset_name(self, dataset_name) -> List[str]:
        splitted = dataset_name.split('.')

        if len(splitted) >= 3:
            return splitted[0:3]
        elif len(splitted) < 3: 
            filler = [''] * (3 - len(splitted))
            return filler + splitted