import typing
from collections import defaultdict

import orjson
from sqlalchemy import create_engine, tuple_
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker

from mlfoundry.exceptions import MlFoundryException

from ..inference_packet import ActualPacket, BasePacket, InferencePacket
from .abstract_inference_store import AbstractInferenceStore
from .db_models import Base, InferenceLog


def orjson_serializer(obj):
    return orjson.dumps(obj, option=orjson.OPT_SERIALIZE_NUMPY).decode()


def orjson_deserializer(serialized_obj):
    return orjson.loads(serialized_obj)


def create_sqlalchemy_engine(db_uri: str) -> Engine:
    engine = create_engine(
        db_uri, json_serializer=orjson_serializer, json_deserializer=orjson_deserializer
    )
    return engine


# NOTE: for now I am keeping the above helper function in this file,
# later we may need to create a seperate db util file to keep this functions


class SqlAlchemyInferenceStore(AbstractInferenceStore):
    def __init__(self, db_uri: str):
        self.engine: Engine = create_sqlalchemy_engine(db_uri)

        # TODO: Explore albemic later
        Base.metadata.create_all(self.engine)
        self.session = scoped_session(sessionmaker(self.engine))

    def _insert_inference(
        self, session, inference_packets: typing.List[InferencePacket]
    ):
        inference_log_objects = [
            InferenceLog(
                model_name=inference.model_name,
                model_version=inference.model_version,
                inference_id=inference.inference_id,
                features=inference.features,
                predictions=inference.predictions,
                occurred_at=inference.occurred_at,
                raw_data=inference.raw_data,
                actuals=inference.actuals,
            )
            for inference in inference_packets
        ]
        session.add_all(inference_log_objects)
        session.flush()

    def _update_actuals(self, session, actual_packets: typing.List[ActualPacket]):
        indexed_packets = {
            (packet.model_name, packet.inference_id): packet.actuals
            for packet in actual_packets
        }
        packets_present_in_db = (
            session.query(InferenceLog)
            .with_entities(
                InferenceLog.id, InferenceLog.model_name, InferenceLog.inference_id
            )
            .filter(
                tuple_(InferenceLog.model_name, InferenceLog.inference_id).in_(
                    indexed_packets.keys()
                )
            )
            # TODO: We should batch this operation instead of all().
            # there can be more than one row having a particular
            # model_name and inference_id
            .all()
        )
        packets_to_update = [
            {
                "id": packet.id,
                "actuals": indexed_packets[packet.model_name, packet.inference_id],
            }
            for packet in packets_present_in_db
        ]
        session.bulk_update_mappings(InferenceLog, packets_to_update)

    def batch_log_inference(self, inference_packets: typing.List[BasePacket]):
        grouped_packets = defaultdict(list)
        for packet in inference_packets:
            grouped_packets[type(packet)].append(packet)

        # https://github.com/sqlalchemy/sqlalchemy/issues/6519
        with self.session() as session, session.begin():
            for packet_type, packets in grouped_packets.items():
                if packet_type == InferencePacket:
                    self._insert_inference(session, packets)
                elif packet_type == ActualPacket:
                    self._update_actuals(session, packets)

    def list_inference(
        self,
        model_name: str,
        model_version: typing.Optional[str] = None,
        page: int = 0,
        page_size: typing.Optional[int] = None,
    ) -> typing.List[InferencePacket]:
        if page < 0:
            raise MlFoundryException("page cannot be neg")
        if page_size is not None and page_size < 0:
            raise MlFoundryException("page_size cannot be neg")
        if page > 0 and page_size is None:
            raise MlFoundryException("pass page_size")

        filters = {"model_name": model_name}
        if model_version is not None:
            filters["model_version"] = model_version
        with self.session() as session:
            query = (
                session.query(InferenceLog)
                .filter_by(**filters)
                .order_by(InferenceLog.id)
                .offset(page * (page_size or 1))
            )
            if page_size:
                query = query.limit(page_size)
            inference_logs = query.all()

        inference_packets = [
            InferencePacket(
                model_name=inference.model_name,
                model_version=inference.model_version,
                inference_id=inference.inference_id,
                features=inference.features,
                predictions=inference.predictions,
                occurred_at=inference.occurred_at,
                raw_data=inference.raw_data,
                actuals=inference.actuals,
            )
            for inference in inference_logs
        ]
        return inference_packets
