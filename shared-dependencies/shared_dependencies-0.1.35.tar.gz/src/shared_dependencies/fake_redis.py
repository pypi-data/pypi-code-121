from datetime import datetime, timedelta


class FakeRedis:
    def __init__(self, *args, **kwargs):
        self.data = {}

    def get(self, id: str, *args, **kwargs):
        result = self.data.get(id, None)

        if result is not None:
            if result[1] > datetime.now():
                return result[0]
            else:
                del self.data[id]
                result = None

        return result

    def set(self, id: str, content: str, ex: int, *args, **kwargs):
        expiration_date = datetime.now() + timedelta(seconds=ex)
        self.data[id] = (content.encode(), expiration_date)