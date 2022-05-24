"""
Spark Streaming
----------------

Direct and Regular spark streaming are supported

.. warning::
   One major limitation of the implementation is that one topic
   or topic group is supported.

"""
import logging
import json
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils

from .messaging import MessagingBase

logger = logging.getLogger("app")


class SparkKafkaDirectMessaging(MessagingBase):
    """
    Implement sparkstreaming+kafka (DirectStream)

    Example::

        mg = SparkKafkaDirectMessaging({
            "hosts": ["127.0.0.1:9092", "127.0.0.1:9093"],
            "broker": "127.0.0.1:2181",
            "jars": ["spark-streaming-kafka-0-8-assembly_2.11-2.2.0.jar"],
            "batchDuration": 2,
        mg.connect()
        def handler(params, data):
            ....
        mg.consume('orders', handler, {'region': 'south'})

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if ("hosts" not in self.config) or ("broker" not in self.config):
            raise Exception(
                "Kafka hosts and broker must be specified must be specified"
            )

        # if 'jars' not in self.config:
        #    raise Exception("kafka jars have to be specified")

        if ("jars" in self.config) and (not isinstance(self.config["jars"], list)):
            raise Exception("kafka jars have to be a lsit")

        if ("batchDuration" not in self.config) or (
            not isinstance(self.config["batchDuration"], int)
        ):
            raise Exception("Spark streaming batch duration should be specified (int)")

    def connect(self):

        conf = SparkConf()
        if "jars" in self.config:
            jars = self.config["jars"]
            conf.set("spark.jars", ",".join(jars))

        batchDuration = self.config["batchDuration"]

        sc = SparkContext(appName="kafka", conf=conf)
        self.ssc = StreamingContext(sc, batchDuration=batchDuration)

    def consume(self, topic, callback, params):

        ssc = self.ssc

        hosts = self.config["hosts"]

        params = self.config.get("consume_params", {})

        directKafkaStream = KafkaUtils.createDirectStream(
            ssc,
            [topic],
            kafkaParams={"metadata.broker.list": ",".join(hosts)},
            **params
        )

        handler = lambda rdd: callback(params, rdd)
        directKafkaStream.foreachRDD(handler)

        try:
            ssc.start()
            ssc.awaitTermination()
        finally:
            ssc.stop()


class SparkKafkaMessaging(SparkKafkaDirectMessaging):
    """
    Implement sparkstreaming+kafka (with WAL)

    Example::

        mg = SparkKafkaMessaging({
            "hosts": ["127.0.0.1:9092", "127.0.0.1:9093"],
            "broker": "127.0.0.1:2181",
            "jars": ["spark-streaming-kafka-0-8-assembly_2.11-2.2.0.jar"],
            "batchDuration": 2,
            "consume_params": {
                 "groupId": "raw-event-streaming-consumer"
            })
        mg.connect()
        def handler(params, data):
            ....
        mg.consume('orders', handler, {'region': 'south'})

    """

    def consume(self, topic, callback, params):

        ssc = self.ssc

        broker = self.config["broker"]

        if isinstance(topic, str):
            topics = {topic: 1}
        elif isinstance(topic, dict):
            topics = topic
        else:
            raise Exception("topic must be a string or a dictionary")

        params = self.config.get("consume_params", {})

        kafkaStream = KafkaUtils.createStream(
            ssc, zkQuorum=broker, topics=topics, **params
        )
        # Call for each rdd obtained...
        handler = lambda rdd: callback(params, rdd)
        kafkaStream.foreachRDD(handler)

        try:
            ssc.start()
            ssc.awaitTermination()
        except:
            logger.exception("Terminated the stream")
        finally:
            ssc.stop()
