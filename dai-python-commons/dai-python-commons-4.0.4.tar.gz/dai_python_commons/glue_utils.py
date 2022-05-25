"""Functionality to fetch/modify info in glue database"""
from typing import List


class GlueUtils:  # pylint: disable=too-few-public-methods
    """Used to fetch/modify info in glue database

        FUNCTIONS
            get_columns_info :func:`~dai_python_commons.GlueUtils.get_columns_info`
    """
    @staticmethod
    def get_columns_info(boto3_client, database_name: str, table_name: str) -> List[dict]:
        """
        Gets a list with column information. Each element of the list is a dict including the Name, Type, Comment and
        Parameters
        :param boto3_client: Glue boto3 client
        :param database_name: Name of the database
        :param table_name: Name of the table
        :return: A list of dictionaries including column information. Example:
        [{"Name": "messageid", "Type": "string", "Comment": "The Message id", "Parameters": {}}]
        """
        table_info = boto3_client.get_table(DatabaseName=database_name, Name=table_name)
        columns_info = table_info["Table"]["StorageDescriptor"]["Columns"]

        return columns_info
