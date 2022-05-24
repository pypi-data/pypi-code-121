from google.cloud import pubsub_v1
from threading import Thread


class SubscriberThread(Thread):
    def __init__(self, project_id: str, subscription_id: str, number_of_messages: int, callback: callable):
        """ Constructor:
                - project_id: The id of the project where the Topic is created \n
                - subscription_id: The name of the subscription on the Topic \n
                - number_of_messages: The number of outstanding messages on the subscriber \n
                - callback: A reference to the method to invoke when receiving a message"""
        Thread.__init__(self, name="subscriber-thread")
        self.number_of_messages = number_of_messages
        self.callback = callback
        self.project_id = project_id
        self.subscription_id = subscription_id

    def run(self) -> None:
        """ Creates streaming connection to given PubSub subscription """
        print("Creating subscriber")
        subscriber = pubsub_v1.SubscriberClient()
        subscription_path = subscriber.subscription_path(self.project_id, self.subscription_id)

        # Limit the subscriber to only have <number_of_messages> outstanding messages at a time.
        flow_control = pubsub_v1.types.FlowControl(max_messages=self.number_of_messages)
        streaming_pull_future = subscriber.subscribe(
            subscription_path, callback=self.callback, flow_control=flow_control)

        # Wrap subscriber in a 'with' block to automatically call close() when done.
        with subscriber:
            try:
                streaming_pull_future.result()
            except Exception as e:
                print(
                    f"Listening for messages on {subscription_path} threw an exception: {e}."
                )
                # Kills the thread
                raise e
