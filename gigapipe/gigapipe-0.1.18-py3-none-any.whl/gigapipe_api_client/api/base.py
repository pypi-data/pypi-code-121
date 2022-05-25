class Base(object):
    """
    Base containing the API object. All the API instances use inherit from this class.
    """
    def __init__(self, api):
        """
        Base Constructor
        :param api: the API instance
        """
        self.api = api
