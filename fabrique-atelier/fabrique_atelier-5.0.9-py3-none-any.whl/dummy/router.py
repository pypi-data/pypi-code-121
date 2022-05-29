from fabrique_atelier.message import Message, MessageType, Header
from time import time
import uuid


class Router:
    def __init__(self, store,
                 pipeline_in,
                 kafka_out,
                 errors,
                 input_iterator=None,
                 ):

        self.store = store

        if not input_iterator:
            raise Exception('input_iterator parameter required')
        self.pipeline_in = pipeline_in
        self.kafka_out = kafka_out
        self.errors = errors
        self.input_iterator = input_iterator

    def send_messages2pipeline(self):
        for data in self.input_iterator:
            session_id = str(uuid.uuid4())
            kafka_key = None
            header = Header(session_id,
                            MessageType.DATA.value,
                            "router",
                            pipeline_name='test_pipeline',
                            pipeline_ver='test_ver',
                            fabrique_out_topic=self.kafka_out,
                            fabrique_error_topic=self.errors,
                            session_start_time=time())

            msg = Message(header, {'data': data}).serialize()

            self.store.produce(self.pipeline_in, msg, kafka_key)
