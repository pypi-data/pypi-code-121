from google.cloud.pubsub_v1 import publisher
from google.cloud.pubsub_v1.subscriber.message import Message


class Publisher:
    """ Utility class to set up connection to PubSub and publish message to Topic"""
    def __init__(self, project_id: str, topic_id: str):
        self.project_id = project_id
        self.topic_id = topic_id

    def publish(self, message: Message) -> str:
        """ Publishes a message to the given topic"""
        pubsub_client = publisher.client.Client()
        topic_path = pubsub_client.topic_path(self.project_id, self.topic_id)
        try:
            result = pubsub_client.publish(topic_path, bytes(str(message.data), 'utf-8'), ).result(timeout=10)
            print(f'Posted message to topic "{topic_path}" with id: {result}')
            return result
        except Exception as e:
            print(f'Exception encountered on publish: {e}')
            raise e

    def publish_string_content(self, message: str) -> str:
        pubsub_client = publisher.client.Client()
        topic_path = pubsub_client.topic_path(self.project_id, self.topic_id)
        try:
            result = pubsub_client.publish(topic_path, bytes(message, 'utf-8'), ).result(timeout=10)
            print(f'Posted message to topic "{topic_path}" with id: {result}')
            return result
        except Exception as e:
            print(f'Exception encountered on publish: {e}')
            raise e
