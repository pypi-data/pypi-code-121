from aiokafka import AIOKafkaProducer
from confluent_kafka import Message, Producer, KafkaException
from loguru import logger

from ...configuration.kafka_settings import KafkaSettings
from ..abstract_producer import ProducerMessageQueue


class KafkaProducer(ProducerMessageQueue):
    def __init__(self, bootstrap_servers):
        self.bootstrap_servers = bootstrap_servers
        self.configs={'bootstrap.servers': self.bootstrap_servers}

    kafka_settings = KafkaSettings()

    @staticmethod
    def delivery_report(error: Message, message: Message):
        """
        Called once for each message produced to indicate delivery result.
        A callback Triggered by poll() or flush().
        :param error:
        :param message:
        """
        if error is not None:
            logger.error('Message delivery failed: {}'.format(error))
        else:
            logger.info(' Message delivered to {} [partition {}]'.format(message.topic(),
                                                                         message.partition()))

    async def confluent_produce(self, topic: str, message: str, encoding: str =
    kafka_settings.KAFKA_DEFAULT_ENCODING) -> bool:

        producer = Producer(self.configs)
        logger.debug('Producing to topic : {}'.format(topic))
        try:
            producer.produce(topic=topic, value=message.encode(encoding),
                             callback=self.delivery_report)
            producer.poll(0.1)
            logger.debug('Message delivered to topic : {}'.format(topic))
        except KafkaException as e:
            logger.error('Message delivery failed: {}'.format(e.__str__()))
            return False
        return True

    async def aio_produce(self, topic: str, message: str, encoding: str =
    kafka_settings.KAFKA_DEFAULT_ENCODING):
        producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers)
        await producer.start()
        try:
            await producer.send_and_wait(topic, message.encode(encoding))
        finally:
            await producer.stop()

    def json_producer(self):
        pass
