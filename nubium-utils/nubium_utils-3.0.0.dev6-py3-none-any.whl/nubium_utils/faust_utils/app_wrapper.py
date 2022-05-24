import logging
import os
import sys
from abc import ABC, abstractmethod

from faust import Record

from nubium_utils import parse_headers
from nubium_utils.metrics import MetricsManager as MetsMan
from .avro_utils import key_serializer
from .instrumented_app import InstrumentedApp
from .faust_runtime_vars import env_vars

LOGGER = logging.getLogger(__name__)


class FaustMessage(Record, serializer='json'):
    key: str
    value: dict
    headers: dict


class FaustAppWrapper(ABC):
    """
    A wrapper around the Faust app so that it may be more easily unit tested.
    """

    def __init__(self, faust_config, avro_client, metrics_manager: MetsMan):
        self.faust_config = faust_config
        self.avro_client = avro_client

        self.app = InstrumentedApp(**self.faust_config)
        self.app.wrapper = self
        self.metrics_manager = metrics_manager
        self.key_serializer = key_serializer(client=self.avro_client)
        self.input_topics = {}
        self.faust_input_topics = {}

        self._init_serializers()
        self._init_records()
        self._init_topics()
        self._init_tables()
        self._init_agents()
        self._init_metrics_pushing()

    def get_schema_path(self, file, schema_path_from_src_root='./schemas'):
        """
        Ensures that the Faust app's schema files are always correctly referenced/loaded regardless of your init path.
        :param file: name of the schema file
        :param schema_path_from_src_root: based on the root of the app, where the schemas folder is located.
        :return: relative path to load the schema at runtime
        """
        runtime_path = os.getcwd()
        app_file_path = os.path.abspath(sys.modules[self.__module__].__file__)
        common_path = os.path.commonpath([runtime_path, app_file_path])
        rel_path = os.path.relpath(common_path, runtime_path)
        return os.path.join(runtime_path, rel_path, schema_path_from_src_root,
                            file)

    def add_input_topic(self, topic_name, value_serializer):
        """
        Aids the 'self._init_message_parser' by adding faust topics to two different topic dicts:
        One dict is for the original input topics (self.input_topics) which is primarily for debugging/unit testing;
        the other (self.faust_input_topics) is for the FaustMessage version of the topic, where '_faust' appended to the
        original topic name, and the dict key is the original topic name so it's easily referenced.
        Basically, this allows you to call the FaustMessage topic version via self.faust_input_topics[orig_topic_name]
        :param topic_name: original topic name
        :type topic_name: str
        :param value_serializer: a FaustSerializer instance for Avro-encoded message values
        :type value_serializer: FaustSerializer
        """
        faust_name = f'{topic_name}_Internal_{self.app.conf.id}'

        input_topic = self.app.topic(
            topic_name,
            key_serializer=self.key_serializer,
            value_serializer=value_serializer)
        self.input_topics[topic_name] = input_topic

        faust_input_topic = self.app.topic(faust_name,
                                           internal=True,
                                           value_type=FaustMessage)
        self._add_input_agent(topic_name, input_topic, faust_input_topic)
        return faust_input_topic

    def _add_input_agent(self, topic_name, input_topic, faust_input_topic):
        @self.app.agent(input_topic, name=f'{topic_name}_agent_internal')
        async def parse_messages(input_messages):
            async for event in input_messages.events():
                headers = parse_headers(event.headers)
                LOGGER.info(f'Message consumed, GUID {headers["guid"]}')
                await faust_input_topic.send(
                    value=FaustMessage(
                        key=event.key,
                        value=event.value,
                        headers=headers
                    ),
                    key=event.key
                )
            yield None

    def format_headers(self, headers_dict):
        """
        Formats headers for an outgoing message
        :param headers_dict: the headers as a dict
        :type headers_dict: dict
        :return: the dict as a list of (key, b'value') tuples.
        :rtype: list
        """
        return [(key, value.encode()) for key, value in headers_dict.items()]

    @abstractmethod
    def _init_serializers(self):
        pass

    @abstractmethod
    def _init_records(self):
        pass

    @abstractmethod
    def _init_topics(self):
        pass

    @abstractmethod
    def _init_tables(self):
        pass

    @abstractmethod
    def _init_agents(self):
        pass

    def agent_exception(self, exc):
        """
        Increments the message errors metric by one
        :param exc:
        :return:
        """
        self.metrics_manager.inc_message_errors(exc)

    def _init_metrics_pushing(self):
        """
        Defines method for updating metrics from Faust sensor and pushing data
        :return: None
        """
        if env_vars()['DO_METRICS_PUSHING'].lower() == 'true':
            LOGGER.info('Metric pushing to gateway ENABLED')

            @self.app.timer(int(env_vars()['METRICS_PUSH_RATE']))
            async def push_metrics():
                """
                Updates gauges from Faust and pushes data to prometheus pushgateways
                :return: None
                """
                self.set_gauges()
                self.metrics_manager.push_metrics()
        else:
            LOGGER.info('Metric pushing to gateway DISABLED')

    def set_gauges(self):
        for topic, count in self.app.monitor.messages_received_by_topic.items():
            self.metrics_manager.messages_consumed.labels(
                job=self.metrics_manager.job,
                app=self.metrics_manager.app,
                topic=topic
            ).set(count)
        for topic, count in self.app.monitor.messages_sent_by_topic.items():
            self.metrics_manager.messages_produced.labels(
                job=self.metrics_manager.job,
                app=self.metrics_manager.app,
                topic=topic
            ).set(count)
