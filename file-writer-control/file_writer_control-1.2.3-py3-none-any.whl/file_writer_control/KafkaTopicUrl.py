import re


class KafkaTopicUrl:
    """
    Class for extracting address, port and topic name from a Kafka topic url.
    """

    test_regexp = re.compile(
        r"^\s*(?:kafka://)?(?:(?P<host>[^/?#:]+)(?::(?P<port>\d+){1,5})?)/(?P<topic>[a-zA-Z0-9._-]+)\s*$"
    )

    def __init__(self, url: str):
        result = re.match(KafkaTopicUrl.test_regexp, url)
        if result is None:
            raise RuntimeError("Unable to match kafka url.")
        self.port = 9092  # Default Kafka broker port
        if result.group("port") is not None:
            self.port = int(result.group("port"))
        self.host = result.group("host")
        self.host_port = f"{self.host}:{self.port}"
        self.topic = result.group("topic")
