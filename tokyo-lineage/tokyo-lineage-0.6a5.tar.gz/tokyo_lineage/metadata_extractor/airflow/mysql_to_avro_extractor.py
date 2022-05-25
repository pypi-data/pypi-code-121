import json
from typing import Type, List, Any, Optional

from contextlib import closing
from urllib.parse import urlparse

from airflow.models import BaseOperator

from openlineage.client.facet import SqlJobFacet
from openlineage.common.sql import SqlMeta, SqlParser
from openlineage.airflow.extractors.base import TaskMetadata
from openlineage.common.dataset import Source, Dataset, Field
from openlineage.common.models import (
    DbTableName,
    DbTableSchema,
    DbColumn
)
from openlineage.airflow.utils import (
    get_connection, safe_import_airflow
)

from tokyo_lineage.models.base import BaseTask
from tokyo_lineage.facets.annotation import Annotation
from tokyo_lineage.metadata_extractor.base import BaseMetadataExtractor
from tokyo_lineage.utils.dataset_naming_helper import (
    # Local filesystem dataset
    fs_scheme,
    fs_authority,
    fs_connection_uri,

    # MySQL dataset
    mysql_scheme,
    mysql_authority,
    mysql_connection_uri
)
from tokyo_lineage.utils.avro import get_avro_fields

_TABLE_SCHEMA = 0
_TABLE_NAME = 1
_COLUMN_NAME = 2
_ORDINAL_POSITION = 3
_COLUMN_TYPE = 4


class MySqlToAvroExtractor(BaseMetadataExtractor):
    
    def __init__(self, task: Type[BaseTask]):
        super().__init__(task)
    
    @classmethod
    def get_operator_classnames(cls) -> List[str]:
        return ["MySqlToAvroOperator"]

    @property
    def operator(self) -> Type[BaseOperator]:
        return self.task.task

    def extract(self) -> TaskMetadata:
        # (1) Parse sql statement to obtain input / output tables.
        sql_meta: SqlMeta = SqlParser.parse(self.operator.sql)

        # (2) Get database connection
        self.conn = get_connection(self._conn_id())

        # (3) Default all inputs / outputs to current connection.
        mysql_source = Source(
            scheme=self._get_mysql_scheme(),
            authority=self._get_mysql_authority(),
            connection_url=self._get_mysql_connection_uri()
        )

        database = self._get_database()

        # (4) Map input / output tables to dataset objects with source set
        # as the current connection. We need to also fetch the schema for the
        # input tables to format the dataset name as:
        # {schema_name}.{table_name}
        inputs = [
            Dataset.from_table(
                source=mysql_source,
                table_name=in_table_schema.table_name.name,
                schema_name=in_table_schema.schema_name,
                database_name=database
            ) for in_table_schema in self._get_table_schemas(
                sql_meta.in_tables
            )
        ]

        # Extracting annotation from source
        self._extract_annotations(inputs)

        filesystem_source = Source(
            scheme=self._get_fs_scheme(),
            authority=self._get_fs_authority(),
            connection_url=self._get_fs_connection_uri()
        )
        
        outputs = [
            Dataset(
                name=self._get_output_dataset_name(),
                source=filesystem_source,
                fields=self._get_avro_fields()
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

    def _get_mysql_connection_uri(self) -> str:
        return mysql_connection_uri(self.conn)

    def _get_mysql_scheme(self) -> str:
        return mysql_scheme()

    def _get_mysql_authority(self) -> str:
        return mysql_authority(self.conn)

    def _get_database(self) -> str:
        if self.conn.schema:
            return self.conn.schema
        else:
            parsed = urlparse(self.conn.get_uri())
            return f'{parsed.path}'

    def _get_fs_scheme(self) -> str:
        return fs_scheme()
    
    def _get_fs_connection_uri(self) -> str:
        return fs_connection_uri(self.operator.avro_output_path)

    def _get_fs_authority(self) -> str:
        return fs_authority()

    def _get_output_dataset_name(self) -> str:
        return self.operator.avro_output_path

    def _get_avro_fields(self) -> List[Field]:
        return get_avro_fields(self._get_avro_schema())
    
    def _get_avro_schema(self) -> str:
        return open(self.operator.avro_schema_path, 'r+').read()

    def _conn_id(self) -> str:
        return self.operator.mysql_conn_id

    def _get_hook(self) -> Any:
        MySqlHook = safe_import_airflow(
            airflow_1_path="airflow.hooks.mysql_hook.MySqlHook",
            airflow_2_path="airflow.providers.mysql.hooks.mysql.MySqlHook"
        )
        return MySqlHook(
            mysql_conn_id=self._conn_id(),
            schema=self.conn.schema
        )
    
    def _information_schema_query(self, table_names: str) -> str:
        return f"""
        SELECT 
            TABLE_SCHEMA,
            TABLE_NAME,
            COLUMN_NAME,
            ORDINAL_POSITION,
            COLUMN_TYPE
        FROM information_schema.`COLUMNS` c 
        WHERE table_name IN ({table_names});
        """
    
    def _get_table_schemas(
        self,
        table_names: List[DbTableName]
    ) -> List[DbTableSchema]:
        # Avoid querying mysql by returning an empty array
        # if no table names have been provided.
        if not table_names:
            return []
        
        # Keeps track of the schema by table.
        schemas_by_table = {}

        hook = self._get_hook()
        with closing(hook.get_conn()) as conn:
            with closing(conn.cursor()) as cursor:
                table_names_as_str = ",".join(map(
                    lambda name: f"'{name.name}'", table_names
                ))
                cursor.execute(
                    self._information_schema_query(table_names_as_str)
                )
                for row in cursor.fetchall():
                    table_schema_name: str = row[_TABLE_SCHEMA]
                    table_name: DbTableName = DbTableName(row[_TABLE_NAME])
                    table_column: DbColumn = DbColumn(
                        name=row[_COLUMN_NAME],
                        type=row[_COLUMN_TYPE],
                        ordinal_position=row[_ORDINAL_POSITION]
                    )

                    # Attempt to get table schema
                    table_key: str = f"{table_schema_name}.{table_name}"
                    table_schema: Optional[DbTableSchema] = schemas_by_table.get(table_key)

                    if table_schema:
                        # Add column to existing table schema.
                        schemas_by_table[table_key].columns.append(table_column)
                    else:
                        schemas_by_table[table_key] = DbTableSchema(
                            schema_name=table_schema_name,
                            table_name=table_name,
                            columns=[table_column]
                        )
                
                return list(schemas_by_table.values())
    
    def _extract_annotations(
        self,
        datasets: List[Dataset]
    ) -> List[Dataset]:
        self.log.info("Extracting annotation from mysql")
        for dataset in datasets:
            _, _, table = dataset.name.split('.')
            self.log.info("Getting table comment for table {}".format(table))
            raw_annotation = self._get_table_comment(table)

            # Skip if dataset don't have annotation
            if raw_annotation is None:
                continue

            annotation: dict = json.loads(raw_annotation)

            self.log.info("Table {} has this annotation: ".format(table))
            self.log.info(json.dumps(annotation))

            annotation_facet = Annotation()

            # Row annotation
            annotation_facet.row_annotation = annotation['rows'] \
                if 'rows' in annotation else None

            # Column annotation
            annotation_facet.column_annotation = annotation['columns'] \
                if 'columns' in annotation else None

            # Dataset annotation
            dataset_annotation = annotation.copy()
            dataset_annotation.pop('rows', None)
            dataset_annotation.pop('columns', None)
            annotation_facet.dataset_annotation = dataset_annotation

            dataset.custom_facets.update({
                "annotation": annotation_facet
            })
        
        return datasets
    
    def _table_comment_query(self, table_name: str) -> str:
        return f"""
        SELECT TABLE_COMMENT FROM INFORMATION_SCHEMA.TABLES t
        WHERE TABLE_NAME = '{table_name}'
        """
    
    def _get_table_comment(self, table_name: str) -> str:
        hook = self._get_hook()

        with closing(hook.get_conn()) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute(
                    self._table_comment_query(table_name)
                )
                row = cursor.fetchone()

                if row[0] is not '':
                    return row[0]

        return None