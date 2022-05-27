import time
import uuid


class GenerateId:
    def generate_id(self):
        return str(uuid.uuid4())

    def time_hash(self):
        return str(time.time())[0:10]
