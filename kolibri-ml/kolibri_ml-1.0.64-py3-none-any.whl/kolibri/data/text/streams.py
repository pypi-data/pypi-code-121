from abc import ABCMeta, abstractmethod

from six import add_metaclass, iteritems

from kolibri.data.text.iterator import DataIterator

@add_metaclass(ABCMeta)
class AbstractDataStream(object):
    """A stream of data separated into epochs.

    A data stream is an iterable stream of examples/minibatches. It shares
    similarities with Python file handles return by the ``open`` method.
    Data streams can be closed using the :meth:`close` method and reset
    using :meth:`reset` (similar to ``f.seek(0)``).
    """
    def __init__(self, iteration_scheme=None, axis_labels=None):
        self.iteration_scheme = iteration_scheme
        self.axis_labels = axis_labels

    @property
    def produces_examples(self):
        if self.iteration_scheme:
            return self.iteration_scheme.requests_examples
        elif not hasattr(self, '_produces_examples'):
            raise ValueError("cannot infer type of stream for {} instance; "
                             "set the produces_examples attribute to True "
                             "(for example streams) or False (for batch "
                             "streams).".format(self.__class__.__name__))
        else:
            return self._produces_examples

    @produces_examples.setter
    def produces_examples(self, value):
        if self.iteration_scheme:
            raise ValueError("cannot set produces_examples on {} instance; "
                             "determined by iteration scheme {}".format(
                                 self.__class__.__name__,
                                 self.iteration_scheme))
        self._produces_examples = value

    def get_data(self, request=None):
        """Request data from the dataset or the wrapped stream.

        Parameters
        ----------
        request : object
            A request fetched from the `request_iterator`.

        Notes
        -----
        It is possible to build a usable stream in terms of underlying
        streams for the purposes of training by only implementing
        `get_epoch_iterator`, thus this method is optional.

        """
        raise NotImplementedError

    def reset(self):
        """Reset the data stream."""

    def close(self):
        """Gracefully close the data stream, e.g. releasing file handles."""

    def next_epoch(self):
        """Switch the data stream to the next epoch."""

    @abstractmethod
    def get_epoch_iterator(self, as_dict=False):
        return DataIterator(self, self.iteration_scheme.get_request_iterator()
                            if self.iteration_scheme else None,
                            as_dict=as_dict)

    def iterate_epochs(self, as_dict=False):
        """Allow iteration through all epochs.

        Notes
        -----
        This method uses the :meth:`get_epoch_iterator` method to retrieve
        the :class:`DataIterator` for each epoch. The default
        implementation of this method resets the state of the data stream
        so that the new epoch can read the data from the beginning.
        However, this behavior only works as long as the ``epochs``
        property is iterated over using e.g. ``for epoch in
        stream.epochs``. If you create the data iterators in advance (e.g.
        using ``for i, epoch in zip(range(10), stream.epochs`` in legacy
        Python) you must call the :meth:`reset` method yourself.

        """
        while True:
            yield self.get_epoch_iterator(as_dict=as_dict)

class DataStream(AbstractDataStream):
    """A stream of data from a dataset.

    Parameters
    ----------
    dataset : instance of :class:`Dataset`
        The dataset from which the data is fetched.

    """
    def __init__(self, dataset, **kwargs):
        if dataset.axis_labels:
            kwargs.setdefault('axis_labels', dataset.axis_labels.copy())
        super(DataStream, self).__init__(**kwargs)
        # A DataStream with no iteration scheme is considered an example stream
        # by default
        if not self.iteration_scheme:
            self.produces_examples = True
        # If the data stream produces examples, remove 'batch' from axis labels
        if self.produces_examples and self.axis_labels:
            for source, labels in iteritems(self.axis_labels):
                self.axis_labels[source] = tuple(
                    label for label in labels if label != 'batch')
        self.dataset = dataset
        self.data_state = self.dataset.open()
        self._fresh_state = True

    @property
    def sources(self):
        if hasattr(self, '_sources'):
            return self._sources
        return self.dataset.sources

    @sources.setter
    def sources(self, value):
        self._sources = value

    def close(self):
        self.data_state = self.dataset.close(self.data_state)

    def reset(self):
        self.data_state = self.dataset.reset(self.data_state)
        self._fresh_state = True

    def next_epoch(self):
        self.data_state = self.dataset.next_epoch(self.data_state)

    def get_data(self, request=None):
        """Get data from the dataset."""
        return self.dataset.get_data(self.data_state, request)

    def get_epoch_iterator(self, **kwargs):
        """Get an epoch iterator for the data stream."""
        if not self._fresh_state:
            self.next_epoch()
        else:
            self._fresh_state = False
        return super(DataStream, self).get_epoch_iterator(**kwargs)

    @classmethod
    def default_stream(cls, dataset, **kwargs):
        data_stream = cls(dataset, **kwargs)
        return dataset.apply_default_transformers(data_stream)

