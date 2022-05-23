from abc import abstractmethod, ABC


class ProducerMessageQueue(ABC):
    """
    The base abstract class for all producer functions
    """

    @abstractmethod
    def confluent_produce(self, message: str, topic: str, encoding: str) -> bool:
        """

          Asynchronous confluent Producer: produce a message to a kafka topic. Callbacks may be
          executed as a side effect of calling this method.

          :param message:
          :param topic:
          :param encoding:
          :raises KafkaException: if producing a message fails
        """

        pass

    def aio_produce(self, message: str, topic: str, encoding: str) -> bool:
        """

          Asynchronous aiokafka Producer: Produce a message to a kafka topic.

          :param message:
          :param topic:
          :param encoding:
          :raises KafkaException: if producing a message fails
        """

        pass

    @abstractmethod
    def json_producer(self):
        pass
