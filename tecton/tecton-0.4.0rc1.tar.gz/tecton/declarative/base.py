from abc import ABC
from abc import abstractmethod
from datetime import timedelta
from typing import List

from tecton._internals.fco import Fco
from tecton_proto.args import feature_view_pb2
from tecton_proto.args import virtual_data_source_pb2
from tecton_proto.args.repo_metadata_pb2 import SourceInfo
from tecton_proto.args.virtual_data_source_pb2 import VirtualDataSourceArgs
from tecton_proto.common.id_pb2 import Id


class BaseBatchDSConfig(ABC):
    @abstractmethod
    def _merge_batch_args(self, data_source_args: virtual_data_source_pb2.VirtualDataSourceArgs):
        pass


class BaseStreamDSConfig(ABC):
    @abstractmethod
    def _merge_stream_args(self, data_source_args: virtual_data_source_pb2.VirtualDataSourceArgs):
        pass


class BaseBatchConfig(ABC):
    @property
    @abstractmethod
    def data_delay(self) -> timedelta:
        pass

    @abstractmethod
    def _merge_batch_args(self, data_source_args: virtual_data_source_pb2.VirtualDataSourceArgs):
        pass


class BaseDataSource(Fco):
    _args: VirtualDataSourceArgs
    _source_info: SourceInfo

    @property
    def _id(self) -> Id:
        return self._args.virtual_data_source_id

    @property
    def name(self) -> str:
        """
        The name of this DataSource.
        """
        return self._args.info.name


class RequestSourceBase(ABC):
    @property
    @abstractmethod
    def schema(self):
        pass


class BaseEntity(Fco):
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Name of the entity.
        """
        pass

    @property
    @abstractmethod
    def join_keys(self) -> List[str]:
        """
        Join keys of the entity.
        """
        pass


class FWV5BaseDataSource(BaseDataSource):
    @property
    def timestamp_field(self) -> str:
        """
        The name of the timestamp column or key of this DataSource.
        """
        if self._args.HasField("hive_ds_config"):
            return self._args.hive_ds_config.common_args.timestamp_field
        if self._args.HasField("redshift_ds_config"):
            return self._args.redshift_ds_config.common_args.timestamp_field
        if self._args.HasField("snowflake_ds_config"):
            return self._args.snowflake_ds_config.common_args.timestamp_field
        if self._args.HasField("file_ds_config"):
            return self._args.file_ds_config.common_args.timestamp_field
        else:
            raise Exception(f"Unknown Data Source Type: {self.name}")


class OutputStream(ABC):
    @abstractmethod
    def _to_proto() -> feature_view_pb2.OutputStream:
        pass
