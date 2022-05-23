from .logging import get_logger
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd
from google.cloud.exceptions import NotFound

logger = get_logger(__name__)


class BigQuery:
    def __init__(self, project_id: str, auth_file: str, location: str) -> None:
        self.project_id = project_id
        self.location = location
        self.credentials = service_account.Credentials.from_service_account_file(auth_file)
        self.client = bigquery.Client(
            credentials=self.credentials,
            project=self.project_id,
            location=self.location,
        )
        self.logger = get_logger(__name__)

    def query(self, query: str, location: str = None) -> pd.DataFrame:
        job_config = bigquery.QueryJobConfig()
        job_config.use_legacy_sql = False
        job = self.client.query(
            query,
            job_config=job_config,
            location=location,
        )
        if job.errors:
            self.logger.error(f"Failed to query {query}.")
            raise Exception(job.errors)
        else:
            self.logger.info(f"Executed query {query}.")
        return job.to_dataframe()

    def table_exists(self, table_id: str) -> bool:
        try:
            self.client.get_table(f"{table_id}")
            return True
        except NotFound:
            return False

    def load_dataframe(
        self,
        df: pd.DataFrame,
        table_id: str,
        write_disposition: bigquery.WriteDisposition = "WRITE_APPEND",
    ) -> None:
        job_config = bigquery.LoadJobConfig()
        job_config.write_disposition = write_disposition
        job_config.autodetect = True
        job_config.schema_update_options = [
            bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION,
            bigquery.SchemaUpdateOption.ALLOW_FIELD_RELAXATION,
        ]

        try:
            self.client.load_table_from_dataframe(
                df,
                table_id,
                job_config=job_config,
            ).result()
            self.logger.info(f"Loaded {table_id}.")
        except Exception as e:
            self.logger.error(f"Failed to load {table_id}.")
            raise e

    def get_last_load_date(self, table_id: str, date_field: str) -> pd.DataFrame:
        try:
            return self.query(
                f"""
                SELECT
                    MAX({date_field}) AS last_load_date
                FROM `{self.project_id}.{table_id}`
                """
            )
        except Exception as e:
            self.logger.error("Failed to get last load date.")
            raise e

    def merge_table(
        self,
        source_table_id: str,
        target_table_id: str,
        key_field: str,
        update_fields: list[str],
    ) -> None:
        try:
            self.query(
                f"""
                MERGE INTO `{self.project_id}.{target_table_id}` AS target
                USING `{self.project_id}.{source_table_id}` AS source
                ON target.{key_field} = source.{key_field}
                WHEN MATCHED THEN UPDATE SET
                {','.join(f"target.{field} = IFNULL(source.{field}, target.{field})" for field in update_fields)}
                WHEN NOT MATCHED THEN INSERT
                ({','.join(update_fields)})
                VALUES
                ({','.join(f"source.{field}" for field in update_fields)});
                """
            )
            self.logger.info(f"Merged {source_table_id} to {target_table_id}.")
        except Exception as e:
            self.logger.error(f"Failed to merge {source_table_id} to {target_table_id}.")
            raise e

    def delete_table(self, table_id: str) -> None:
        if self.table_exists(table_id):
            self.client.delete_table(table_id)
            self.logger.info(f"Deleted table {table_id}.")
        else:
            self.logger.info(f"Table {table_id} does not exist.")

    def create_dataset(self, dataset_id: str, location: str = None) -> None:
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = location or self.location
        self.client.create_dataset(dataset)
        self.logger.info(f"Created dataset {dataset_id}.")

    def create_table(self, table_id: str, schema: list[dict]) -> None:
        table = bigquery.Table(table_id, schema=schema)
        self.client.create_table(table)
        self.logger.info(f"Created table {table_id}.")
