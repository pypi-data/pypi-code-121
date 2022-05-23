from abc import abstractmethod, ABC
from typing import List


class ConsumerMessageQueue(ABC):
    """
    The base abstract class for all consumer functions
    """

    @abstractmethod
    def consume(self, topics: list, num_messages: int, timeout: float,
                process=None) -> List or None:
        """
          Confluent kafka consumer: Consumes a list of messages (possibly empty on timeout) from a
          list of
          topics.

          :param topics: The list of topics to be consumed.
          :param int num_messages: The number of messages to consume at once.
          :param float timeout: The maximum time to block waiting for message, event or callback (default: infinite (-1)). (Seconds)
          :param process: The function that will get the consumed message and process it
          :raises RuntimeError: if called on a closed consumer
          :raises KafkaError: in case of internal error
        """

        pass

    @abstractmethod
    def aio_consume(self, topics: list, num_messages: int, timeout: float,
                    process=None) -> List or None:
        """
          aiokafka consumer: Consumes a message (possibly empty on timeout) from a list of topics.

          :param topics: The list of topics to be consumed.
          :param int num_messages: The number of messages to consume at once.
          :param float timeout: The maximum time to block waiting for message, event or callback (default: infinite (-1)). (Seconds)
          :param process func: The function that will get the consumed message and process it
          :raises RuntimeError: if called on a closed consumer
          :raises KafkaError: in case of internal error
        """

        pass

    @abstractmethod
    def json_consume(self):
        pass
