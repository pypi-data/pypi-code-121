try:
    import mmh3
except ImportError:
    from lib import pymmh3 as mmh3


class Bucketer(object):
    def __init__(self):
        return

    def bucketing(self, bucket, user):
        slot_number = self._calculate_slot_number(user.id, bucket.seed, bucket.slot_size)
        return bucket.get_slot_or_none(slot_number)

    def _calculate_slot_number(self, user_id, seed, slot_size):
        hash_value = mmh3.hash(user_id, seed)
        return abs(hash_value) % abs(slot_size)
