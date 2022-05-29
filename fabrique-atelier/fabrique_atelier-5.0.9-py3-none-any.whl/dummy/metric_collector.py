import json
import os
from datetime import datetime

from fabrique_atelier.constants import MessageFieldsConstants as fld
from fabrique_atelier.message import Message
from .pipeline_actors import Actor

FABRIQUE_METRIC_COLLECTOR_TOPIC = os.getenv('FABRIQUE_METRIC_COLLECTOR_TOPIC', 'monitor.in')

def_config = {
    "message_bus": {
        "pipeline_name": "all",
        "pipeline_ver": "all",
        "in_topic": FABRIQUE_METRIC_COLLECTOR_TOPIC,
        "client_id": "metric_collector",
        "group_id": None,
        "servers": None,
    }
}


class MetricCollector(Actor):
    def __init__(self, store, out_pth='./out/metrics.ndjson'):
        config = def_config
        os.makedirs(os.path.dirname(out_pth), exist_ok=True)

        self.out_pth = out_pth
        config['store'] = store

        super().__init__(config)

        self.process_result = lambda res_body, session_id: None

    def preprocess_msg(self, mes):
        msg = Message.parse_mes(mes)
        if msg:
            # add all kafka fields to msg body
            msg.body = dict(body=msg.body,
                            kafka_header=msg.kafka_header,
                            header=msg.header.to_dict(),
                            session_id=msg.header.session_id)
            return msg

    def close_all(self):
        pass

    def batch_callback(self, batch):
        for message_dict in batch:
            self.callback(message_dict)

    def callback(self, message_dict):
        session_id = message_dict["session_id"]
        client_id = message_dict["header"]["source"]
        source_id = client_id.rsplit('__')[0]

        pipeline_name = message_dict["header"]["pipeline_name"]
        pipeline_ver = message_dict["header"]["pipeline_ver"]

        body = message_dict['body']

        if fld.timestamp in body:
            timestamp = body[fld.timestamp]
        else:
            timestamp = datetime.utcnow().timestamp()

        def write_metric(_field, _session_id, _pipeline_name, _pipeline_ver, _source_id, _value=None, _timestamp=None):

            with open(self.out_pth, 'a') as f:
                f.write(json.dumps(dict(field=_field, session_id=_session_id, value=_value,
                                        pipeline_name=_pipeline_name, pipeline_ver=_pipeline_ver,
                                        source_id=_source_id, timestamp=_timestamp)) + '\n')

        if body.get(fld.error):
            write_metric(fld.error, session_id, pipeline_name, pipeline_ver, source_id, _timestamp=timestamp)

        if body.get(fld.metrics):
            for field, value in body[fld.metrics].items():
                write_metric(field, session_id, pipeline_name, pipeline_ver, source_id, value, _timestamp=timestamp)

        if body.get(fld.alerts):
            for field, value in body[fld.alerts].items():
                write_metric(field, session_id, pipeline_name, pipeline_ver, source_id, value, _timestamp=timestamp)
