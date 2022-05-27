from typing import List, Dict, Any, ClassVar

import pandas as pd
from graphdb.connection import GraphDbConnection
from graphdb.graph import GraphDb
from graphdb.schema import Node
from gremlin_python.driver import client


class Ingestor:

    def __init__(
            self,
            connection_uri: str
    ):
        self.graph = GraphDb.from_connection(
            GraphDbConnection.from_uri(connection_uri)
        )

    def load_data(
            self,
            path: str,
            is_from_s3: bool
    ) -> pd.DataFrame:
        """Load data from given path and convert as pandas object
        :param path: string path value
        :param is_from_s3: string path value
        :return: pandas object value
        """
        if is_from_s3:
            # download file from s3
            pass

        return pd.read_csv(path)

    def dumping_data_into_graph(
            self,
            payload: pd.DataFrame
    ) -> bool:
        """Inserting data from dataframe into graph database
        :param payload: dataframe object pandas
        :return: boolean (true, false)
        """
        tmp = []
        for doc in payload.to_dict(orient="records"):
            node = Node(**{
                "label": "Person",
                "properties": doc
            })
            tmp.append(node)

        return self.graph.create_multi_node(tmp)

    @classmethod
    def from_connection_uri(
            cls,
            connection_uri: str
    ) -> ClassVar:
        """Create new object based on connection uri
        :param connection_uri: string connection uri
        :return: object class
        """
        return cls(connection_uri)

    def callback_function(
            self,
            data: client.Client.submit_async,
    ) -> List[Dict[str, Any]]:
        """Setup callback function
        :param data: python generator object
        :return: list of dictionary
        """
        res = data.result(timeout=10)
        return res.next()

    def create_query(self):
        payload = {"param_name": "Ann"}
        return self.graph.custom_query(
            """g.V().has("name", "${param_name}").next()""",
            payload=payload,
            callback_func=self.callback_function,
        )
