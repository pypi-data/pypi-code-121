import json


class MockSQS():
    counter = 0

    def get_pypers_queue(self):
        pass

    def reset_history(self, runid, collection):
        pass

    def send_message(self, *args, **kwargs):
        self.counter += 1
        return {}

    def get_messges(self):
        return None, None

    def delete_message(self, message_id):
        pass

    def create_queue(self, *args, **kwargs):
        pass

    def get_queue_by_name(self, *args, **kwargs):
        return self

    def receive_messages(self, *args, **kwargs):
        return [MockMessage()]


class MockMessage():
    message_id = '1234'
    body = json.dumps({'foo': 'bar'})

    def delete(self):
        pass