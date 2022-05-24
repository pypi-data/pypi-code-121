"""
Messaging
---------

Low-level messaging interface to connect to various
messaging backends such as Kafka and processing pipelines
such as spark streaming.

"""
import json
import logging
import traceback

# pykafka library. To be phased out..
from pykafka import KafkaClient

# kafka-python
from kafka import KafkaConsumer, KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic

logger = logging.getLogger("kafka")
logger.setLevel(logging.CRITICAL)


class MessagingBase(object):
    """
    Base class to handle the interfacing with various messaging
    backends.

    """

    def __init__(self, config, *args, **kwargs):
        """
        Initialize the messaging object

        Args:
            config (dict): Configuration
        """
        self.config = config
        if not isinstance(config, dict):
            raise Exception("Invalid config type. Expecting dict")

    def connect(self):
        """
        Initialize the messaging backend
        """
        pass

    def topcs(self):
        """
        List available topics
        """
        return []

    def produce(self, topic, callback, params):
        """
        Generate and post records into the stream

        Args:
            topic (str): Kafka topic to produce
            callback (method): method to call to generate stream input
            params (dict): Parameters to pass to callback

        Returns:
            None
        """
        raise Exception("Not implemented")

    def consume(self, topic, callback, params):
        """
        Generate and post records into the stream

        Args:
            topic (str): Kafka topic to consume
            callback (method): method to call to consume stream input
            params (dict): Parameters to pass to callback

        Returns:
            None
        """
        raise Exception("Not implemented")

    def stop(self):
        pass


class PyKafkaMessaging(MessagingBase):
    """

    Implementation of an interface to PyKafka

    Is being deprecated in favor of kafka-python
    implementation.

    Example::

        mg = PyKafkaMessaging({
            "hosts": ["127.0.0.1:9092", "127.0.0.1:9093"],
            "consume_params": {
                "consumer_group": 'testgroup',
                "auto_commit_enable": True,
                "zookeeper_connect": 'localhost:2181'
            })
        mg.connect()
        def handler(params, data):
            ....
        mg.consume('orders', handler, {'region': 'south'})

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "hosts" not in self.config:
            raise Exception("Kafka hosts must be specified")

    def connect(self):
        hosts = self.config.get("hosts")
        hosts = ",".join(hosts)
        self.client = KafkaClient(hosts=hosts)

    def produce(self, topic, callback, params):
        topic = self.client.topics[topic]
        producer_params = self.config.get("produce_params", {})
        with topic.get_sync_producer(**producer_params) as producer:
            for data in callback(params):
                producer.produce(json.dumps(data).encode("utf-8"))

    def consume(self, topic, callback, params):
        topic = self.client.topics[topic]
        consume_params = self.config.get("consume_params", {})
        balanced_consumer = topic.get_balanced_consumer(**consume_params)
        try:
            for message in balanced_consumer:
                if message is not None:
                    try:
                        callback(params, message)
                    except:
                        traceback.print_exc()
        finally:
            balanced_consumer.stop()


class KafkaMessaging(MessagingBase):
    def topics(self):
        consumer = KafkaConsumer(**self.config)
        available = consumer.topics()
        consumer.close()
        return available

    def create_topic(self, topic, partitions=1, replication_factor=1):
        admin_client = KafkaAdminClient(**self.config)

        topic_list = []
        topic_list.append(NewTopic(name=topic, num_partitions=1, replication_factor=1))
        admin_client.create_topics(new_topics=topic_list, validate_only=False)

    def produce(self, topic, callback, params={}):

        producer = KafkaProducer(
            value_serializer=lambda v: json.dumps(v).encode("utf-8"), **self.config
        )

        try:
            if callable(callback):
                for data in callback(params):
                    producer.send(topic, data)
            else:
                data = callback
                producer.send(topic, data)
        finally:
            producer.close()

    def consume(self, topic, callback, params):

        consumer = KafkaConsumer(
            topic,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            **self.config
        )

        try:
            for msg in consumer:
                try:
                    callback(params, msg)
                except:
                    traceback.print_exc()
        finally:
            consumer.close()
