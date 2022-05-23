
class NotKnownType:
    """ Singleton for 'NotKnown' constant """

    not_known_single_instance = None

    def __new__(cls):
        if cls.not_known_single_instance is None:
            cls.not_known_single_instance = super().__new__(cls)
        return cls.not_known_single_instance

NotKnown = NotKnownType()  ## the only possible instance