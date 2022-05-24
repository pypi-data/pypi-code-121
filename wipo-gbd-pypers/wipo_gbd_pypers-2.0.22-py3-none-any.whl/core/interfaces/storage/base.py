
class StorageBase:

    def __init__(self, *args, **kwargs):
        self.create_space_if_not_exists()

    def create_space_if_not_exists(self):
        raise NotImplementedError()