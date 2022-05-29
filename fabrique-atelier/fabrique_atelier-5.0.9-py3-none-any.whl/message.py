from enum import Enum, unique
import msgpack
import uuid


@unique
class MessageType(Enum):
    ERROR = 'ERROR'  # err
    DATA = 'DATA'  # data


class Header(object):
    def __init__(self, session_id,
                 message_type,
                 source,
                 corr_id=None,
                 pipeline_name=None,
                 pipeline_ver=None,
                 fabrique_out_topic=None,
                 fabrique_error_topic=None,
                 session_start_time=None,
                 ):
        if not corr_id:
            corr_id = str(uuid.uuid4())

        self.corr_id = corr_id
        self.session_id = session_id
        self.pipeline_ver = pipeline_ver
        self.pipeline_name = pipeline_name
        self.message_type = message_type
        self.source = source
        self.fabrique_out_topic = fabrique_out_topic
        self.fabrique_error_topic = fabrique_error_topic
        self.session_start_time = session_start_time

    def to_dict(self):
        return dict(session_id=self.session_id,
                    message_type=self.message_type,
                    source=self.source,
                    corr_id=self.corr_id,
                    pipeline_name=self.pipeline_name,
                    pipeline_ver=self.pipeline_ver,
                    fabrique_out_topic=self.fabrique_out_topic,
                    fabrique_error_topic=self.fabrique_error_topic,
                    session_start_time=self.session_start_time,
                    )


class Message(object):
    """fabrique pipeline message"""

    def __init__(self, header, body, kafka_header=None):
        if kafka_header is None:
            kafka_header = {}
        self.kafka_header = kafka_header
        self.header = header
        self.body = body

    def serialize(self):
        header_dict = self.header.to_dict()
        val_dict = dict(header=header_dict, body=self.body)
        packed = msgpack.dumps(val_dict, use_bin_type=True)
        return packed

    @classmethod
    def parse_mes(cls, mes):
        kafka_header = dict(topic=mes.topic(), timestamp=mes.timestamp(), key=mes.key())
        value = mes.value()
        val_dict = msgpack.loads(value, raw=False)
        header_dict = val_dict['header']
        body = val_dict['body']
        header = Header(**header_dict)
        return cls(header, body, kafka_header)

    @classmethod
    def gen_message_by_header(cls, header, body, message_type=None, source=None, preserve_corr_id=True):
        if not preserve_corr_id:
            header.corr_id = str(uuid.uuid4())
        if message_type:
            header.message_type = message_type
        if source:
            header.source = source
        return cls(header, body)
