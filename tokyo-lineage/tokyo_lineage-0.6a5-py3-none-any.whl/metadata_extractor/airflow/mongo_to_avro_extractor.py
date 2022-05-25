import json
from typing import Type, List, Any

from airflow.models import BaseOperator

from openlineage.client.facet import SqlJobFacet
from openlineage.airflow.extractors.base import TaskMetadata
from openlineage.common.dataset import Source, Dataset, Field
from openlineage.airflow.utils import get_connection

from tokyo_lineage.models.base import BaseTask
from tokyo_lineage.facets.annotation import Annotation
from tokyo_lineage.metadata_extractor.base import BaseMetadataExtractor
from tokyo_lineage.utils.dataset_naming_helper import (
    # Local filesystem dataset
    fs_scheme,
    fs_authority,
    fs_connection_uri,

    # Mongo dataset
    mongo_scheme,
    mongo_authority,
    mongo_connection_uri
)
from tokyo_lineage.utils.avro import get_avro_fields


class MongoToAvroExtractor(BaseMetadataExtractor):
    def __init__(self, task: Type[BaseTask]):
        super().__init__(task)

    @classmethod
    def get_operator_classnames(cls) -> List[str]:
        return ["MongoToAvroOperator"]

    @property
    def operator(self) -> Type[BaseOperator]:
        return self.task.task

    def extract(self) -> TaskMetadata:
        self.conn = get_connection(self._conn_id())

        mongo_source = Source(
            scheme=self._get_mongo_scheme(),
            authority=self._get_mongo_authority(),
            connection_url=self._get_mongo_connection_uri()
        )

        inputs = [
            Dataset(
                name=self._get_input_dataset_name(),
                source=mongo_source
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
                'query': SqlJobFacet(self.operator.query)
            }
        )

    def _get_mongo_connection_uri(self) -> str:
        return mongo_connection_uri(self.conn)

    def _get_mongo_scheme(self) -> str:
        return mongo_scheme()

    def _get_mongo_authority(self) -> str:
        return mongo_authority(self.conn)

    def _get_fs_connection_uri(self) -> str:
        return fs_connection_uri(self.operator.avro_output_path)

    def _get_fs_scheme(self) -> str:
        return fs_scheme()

    def _get_fs_authority(self) -> str:
        return fs_authority()

    def _get_input_dataset_name(self) -> str:
        collection = self.operator.collection
        database = self.operator.database
        return f'{database}.{collection}'

    def _get_output_dataset_name(self) -> str:
        return self.operator.avro_output_path

    def _get_avro_fields(self) -> List[Field]:
        return get_avro_fields(self._get_avro_schema())

    def _get_avro_schema(self) -> str:
        return open(self.operator.avro_schema_path, 'r+').read()
    
    def _conn_id(self) -> str:
        return self.operator.mongo_conn_id
    
    def _get_hook(self) -> Any:
        from tokyo_lineage.integrations.airflow.hooks import MongoHook
        return MongoHook(conn_id=self._conn_id())

    def _extract_annotations(
        self,
        datasets: List[Dataset]
    ) -> List[Dataset]:
        self.log.info("Extracting annotation from mongo")
        for dataset in datasets:
            _, _, table = self._safe_split_dataset_name(dataset.name)
            self.log.info("Getting table comment for table {}".format(table))
            raw_annotation = self._get_table_comment(table)
            
            # Skip if dataset don't have annotation
            if raw_annotation is None:
                continue

            annotation: dict = raw_annotation['annotation']

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
        return {'collection': table_name}

    def _get_table_comment(self, table_name: str) -> str:
        mongo_con = self._get_hook()
        annotation_coll = mongo_con.get_collection(
                                mongo_collection='annotations',
                                mongo_db=self.operator.database)
        result = annotation_coll.find(self._table_comment_query(table_name))
        docs = [doc for doc in result]

        if len(docs) == 0:
            return None

        return docs[0]

    def _safe_split_dataset_name(self, dataset_name) -> List[str]:
        splitted = dataset_name.split('.')

        if len(splitted) >= 3:
            return splitted[0:3]
        elif len(splitted) < 3: 
            filler = [''] * (3 - len(splitted))
            return filler + splitted