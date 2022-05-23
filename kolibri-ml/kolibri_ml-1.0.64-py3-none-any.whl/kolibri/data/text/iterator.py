import six


class DataIterator(six.Iterator):
    """An iterator over data, representing a single epoch.
    """
    def __init__(self, data_stream, request_iterator=None):
        self.data_stream = data_stream
        self.request_iterator = request_iterator

    def __iter__(self):
        return self

    def __next__(self):
        if self.request_iterator is not None:
            data = self.data_stream.get_data(next(self.request_iterator))
        else:
            data = self.data_stream.get_data()

        return data
