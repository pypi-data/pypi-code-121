"""
AWS DynamoDB Module for accessing AWS DDB server via AWS IAM.
"""

import boto3
from datetime import datetime
from datetime import timedelta


class DynamoDB:
    def __init__(
        self,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        aws_region="ap-southeast-1",
    ):
        if aws_access_key_id and aws_secret_access_key:
            self.ddb_client = boto3.resource(
                "dynamodb",
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=aws_region,
            )
        else:
            self.ddb_client = boto3.resource("dynamodb", region_name=aws_region)

    def _date_to_sec(self, dt):
        epoch = datetime.utcfromtimestamp(0)
        return int((dt - epoch).total_seconds())

    def get_ddb_connection(self):
        """
        Initializes DDB client; Returns HTTP response
        """
        return self.ddb_client

    def put_ddb_object(self, table_name, item_dict):
        """
            Puts an item into the DynamoDB table
        ​
            Parameters:
            table_name - name of the DynamoDB table; should already exist in the DynamoDB
            item_dict - a key-value pair of items; partition key should exist in the dictionary
        """

        table = self.ddb_client.Table(table_name)
        response = table.put_item(Item=item_dict)
        print(f"Successfully uploaded item to table {table_name}")

        return response

    def put_ddb_df_pyspark(self, table_name, pyspark_df):
        """
        This function takes a PySpark dataframe, transforms it into a Pandas dataframe and inserts it to the specified dynamodb table object.

        Parameters:
        table_name (dynamodb object) - table should already exist in the dynamodb
        df (DataFrame) - PySpark dataframe should contain the primary key of the dynamodb table
        """
        dynamo = self.ddb_client

        pandas_df = pyspark_df.toPandas().astype(str)
        pandas_df["expiry"] = self._date_to_sec(datetime.today() + timedelta(days=2))

        table = dynamo.Table(table_name)

        with table.batch_writer() as bw:
            for i, record in enumerate(pandas_df.to_dict("records")):
                bw.put_item(Item=record)

        print(
            "Successfully inserted {} rows into DynamoDB Table: {}".format(
                pyspark_df.count(), table_name
            )
        )

    def put_ddb_df_pandas(self, table_name, pd_df):
        """
        This function takes a Pandas dataframe

        Parameters:
        table_name (dynamodb object) - table should already exist in the dynamodb
        df (DataFrame) - Pandas dataframe should contain the primary key of the dynamodb table
        """
        table = self.ddb_client.Table(table_name)

        with table.batch_writer() as bw:
            for i, record in enumerate(pd_df.to_dict("records")):
                bw.put_item(Item=record)

        print(
            "Successfully inserted {} rows into DynamoDB Table: {}".format(
                pd_df.shape[0], table_name
            )
        )

    def get_ddb_object(self, table_name, key_name, search_key):
        """
            Returns an item from the table based on the specified key and item
        ​
            Parameters:
            table_name -  name of the DynamoDB table
            key_name - name of the partition key
            search_key - value of the partition key
        """
        table = self.ddb_client.Table(table_name)
        response = table.get_item(Key={key_name: search_key})
        print(f"Successfully retrieved {search_key} from {table_name}")

        return response
