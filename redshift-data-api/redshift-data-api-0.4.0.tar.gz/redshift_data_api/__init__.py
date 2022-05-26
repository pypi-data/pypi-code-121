import time

import boto3
import pandas as pd

MAX_CHECK_INTERVAL_SECONDS = 10


class Client:
    def __init__(
        self, cluster_id: str, db_name: str = "default_db", username: str = None
    ):
        self.cluster_id = cluster_id
        self.db_name = db_name
        self.username = username or self.get_username_from_sts()
        self.client = boto3.client("redshift-data")

    def get_username_from_sts(self):
        client = boto3.client("sts")
        arn = client.get_caller_identity()["Arn"]
        kind, username = arn.split(":")[-1].split("/")
        if kind != "user":
            raise Exception(
                f"identity of type {kind} not supported, only users allowed"
            )
        return username

    def _parse_cell(self, cell):
        if len(cell) != 1:
            raise Exception(f"invalid cell: {cell}")

        is_null = cell.get("isNull")
        if is_null:
            return None

        (value,) = cell.values()
        return value

    def _parse_row(self, row):
        return (self._parse_cell(cell) for cell in row)

    def execute_query(self, query_string: str, timeout=30, check_interval_seconds=1):
        query_id = self.client.execute_statement(
            ClusterIdentifier=self.cluster_id,
            Database="default_db",
            DbUser=self.username,
            Sql=query_string,
        )["Id"]

        start_time = time.time()

        while True:
            statement = self.client.describe_statement(Id=query_id)
            if statement.get("Error"):
                raise Exception(f"query failed: {statement['Error']}")
            if statement["Status"] == "FINISHED":
                end_time = time.time()
                elapsed_time = end_time - start_time
                print(
                    f"Query finished. Elapsed Time {elapsed_time:.1f} s. Fetching results..."
                )
                break

            if time.time() - start_time > timeout:
                self.client.cancel_statement(Id=query_id)
                raise RuntimeError("query timed out")

            check_interval_seconds = min(  # exponential backoff
                check_interval_seconds * 1.3, MAX_CHECK_INTERVAL_SECONDS
            )
            time.sleep(check_interval_seconds)

        if not statement["HasResultSet"]:
            return None

        result = self.client.get_statement_result(Id=query_id)

        records = result["Records"]
        columns = result["ColumnMetadata"]

        cur_num_rows = len(result["Records"])
        cur_page = 1

        print(
            f"""Fetched page {cur_page}, {cur_num_rows} of {result["TotalNumRows"]} row(s)"""
        )

        # check for the nextToken, and paginate through the results as necessary
        while "NextToken" in result:
            cur_page += 1
            result = self.client.get_statement_result(
                Id=query_id, NextToken=result["NextToken"]
            )
            cur_num_rows += len(result["Records"])
            print(
                f"""Fetched page {cur_page}, {cur_num_rows} of {result["TotalNumRows"]} rows"""
            )

            records.extend(result["Records"])

        print("Done fetching results.")

        colnames = [c["name"] for c in columns]
        rows = (self._parse_row(row) for row in records)
        df = pd.DataFrame(rows, columns=colnames)

        return df

    def get_data(self, table, where="", sort="", limit=1000):
        limit = min(limit, 5000)
        where_clause = where and f"where {where}"
        sort_clause = sort and f"order by {sort}"
        return self.execute_query(
            f"select * from  {table} {where_clause} {sort_clause} limit {limit}"
        )
