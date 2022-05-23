from abc import ABCMeta, abstractmethod


class BaseStream(metaclass=ABCMeta):
    """ The abstract class setting up the minimum requirements of a stream.

    Raises
    ------
    NotImplementedError: This is an abstract class.

    """

    def __init__(self, iteration_scheme=None):
        self.n_samples = 0
        self.n_targets = 0
        self.n_features = 0
        self.n_classes = 0
        self.current_sample_x = None
        self.current_sample_y = None
        self.content_column = None
        self.target_columns = None
        self.target_values = list()
        self.name = None
        self.random_state = None
        self.task_type = None
        self.iteration_scheme = iteration_scheme


    @abstractmethod
    def prepare(self):
        """ prepare_for_use
        Prepare the stream for use. Can be the reading of a file, or
        the generation of a function.
        """
        raise NotImplementedError

    @abstractmethod
    def next(self, batch_size=1):
        """ Generates or returns next `batch_size` samples in the stream.

        """
        raise NotImplementedError

    def last(self):
        """ Retrieves last `batch_size` samples in the stream.
        Returns
        -------
        tuple or tuple list
            A numpy.ndarray of shape (batch_size, n_features) and an array-like of shape
            (batch_size, n_targets), representing the next batch_size samples.
        """
        return self.current_sample_x, self.current_sample_y

    def restart(self):
        """  Restart the stream. """
        self.prepare()

    def get_all_data(self, nb_samples=None):
        """Request  all the data from the dataset or the wrapped stream.

        Parameters
        ----------
        nb_samples : int
            the number of sample to be returned from the original dataset`.
        """
        raise NotImplementedError

    def get_next_document(self, iterator_scheme=None):
        raise NotImplementedError

    def has_more_samples(self):
        """
        Checks if stream has more samples.
        Returns
        -------
        Boolean
            True if stream has more samples.
        """
        return True

    def get_class_type(self):
        return 'stream'
