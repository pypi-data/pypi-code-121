import json
from typing import Callable, Dict, Iterable, Optional, Tuple

from feast import ValueType
from feast.data_source import DataSource
from feast.protos.feast.core.DataSource_pb2 import DataSource as DataSourceProto
from feast.repo_config import RepoConfig
from ..type_map import mysql_type_to_feast_value_type, mysql_type_code_to_mysql_type
from ..utils import _get_conn, get_cur


class MySQLSource(DataSource):
    def __init__(
        self,
        query: str,
        event_timestamp_column: Optional[str] = "",
        created_timestamp_column: Optional[str] = "",
        field_mapping: Optional[Dict[str, str]] = None,
        date_partition_column: Optional[str] = "",
        name: Optional[str] = "",
    ):
        self._mysql_options = MySQLOptions(query=query)

        super().__init__(
            name=name,
            event_timestamp_column=event_timestamp_column,
            created_timestamp_column=created_timestamp_column,
            field_mapping=field_mapping,
            date_partition_column=date_partition_column,
        )

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        if not isinstance(other, MySQLSource):
            raise TypeError(
                "Comparisons should only involve MySQLSource class objects."
            )

        return (
            self._mysql_options._query == other._mysql_options._query
            and self.event_timestamp_column == other.event_timestamp_column
            and self.created_timestamp_column == other.created_timestamp_column
            and self.field_mapping == other.field_mapping
        )

    @staticmethod
    def from_proto(data_source: DataSourceProto):
        assert data_source.HasField("custom_options")

        mysql_options = json.loads(data_source.custom_options.configuration)
        return MySQLSource(
            query=mysql_options["query"],
            field_mapping=dict(data_source.field_mapping),
            event_timestamp_column=data_source.event_timestamp_column,
            created_timestamp_column=data_source.created_timestamp_column,
            date_partition_column=data_source.date_partition_column,
        )

    def to_proto(self) -> DataSourceProto:
        data_source_proto = DataSourceProto(
            type=DataSourceProto.CUSTOM_SOURCE,
            field_mapping=self.field_mapping,
            custom_options=self._mysql_options.to_proto(),
        )

        data_source_proto.event_timestamp_column = self.event_timestamp_column
        data_source_proto.created_timestamp_column = self.created_timestamp_column
        data_source_proto.date_partition_column = self.date_partition_column

        return data_source_proto

    def validate(self, config: RepoConfig):
        pass

    @staticmethod
    def source_datatype_to_feast_value_type() -> Callable[[str], ValueType]:
        return mysql_type_to_feast_value_type

    def get_table_column_names_and_types(
        self, config: RepoConfig
    ) -> Iterable[Tuple[str, str]]:
        ret = None
        with _get_conn(config.offline_store) as conn, get_cur(conn) as cur:
            cur.execute(
                f"SELECT * FROM ({self.get_table_query_string()}) AS sub LIMIT 0"
            )
            ret = ((c[0], mysql_type_code_to_mysql_type(c[1])) for c in cur.description)
        return ret

    def get_table_query_string(self) -> str:
        return f"({self._mysql_options._query})"


class MySQLOptions:
    def __init__(self, query: Optional[str]):
        self._query = query

    @classmethod
    def from_proto(cls, mysql_options_proto: DataSourceProto.CustomSourceOptions):
        config = json.loads(mysql_options_proto.configuration.decode("utf8"))
        mysql_options = cls(
            query=config["query"],
        )

        return mysql_options

    def to_proto(self) -> DataSourceProto.CustomSourceOptions:
        mysql_options_proto = DataSourceProto.CustomSourceOptions(
            configuration=json.dumps({"query": self._query}).encode()
        )

        return mysql_options_proto
