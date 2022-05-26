from hashids import Hashids
import os

HASH_LENGTH = 5


class HashGetter:
    def __init__(self, id_to_hash):
        self.id = id_to_hash
        self.hashids = Hashids(
            min_length=HASH_LENGTH, salt=os.getenv('HASH_SALT', "")
        )

    def get(self):
        hashed_id = self.hashids.encode(self.id)
        return hashed_id


class IDGetter:
    def __init__(self, hash_to_id):
        self.hash_to_id = hash_to_id
        self.hashids = Hashids(
            min_length=HASH_LENGTH, salt=os.getenv('HASH_SALT', "")
        )

    def get(self):
        id_from_hash = self.hashids.decode(self.hash_to_id)
        return id_from_hash and id_from_hash[0]
