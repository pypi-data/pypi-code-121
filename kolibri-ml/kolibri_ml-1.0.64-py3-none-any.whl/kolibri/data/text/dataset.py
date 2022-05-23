import collections
from abc import ABCMeta, abstractmethod
import numpy
from six import add_metaclass
import numbers
from picklable_itertools import iter_, izip
try:
    import h5py
except:
    pass

from kolibri.data.text.schemes import SequentialExampleScheme
from kolibri.data.text.streams import DataStream


def iterable_fancy_indexing(iterable, request):
    if isinstance(iterable, numpy.ndarray):
        return iterable[request]
    else:
        return [iterable[r] for r in request]


@add_metaclass(ABCMeta)
class Dataset(object):
    """A dataset.

    Dataset classes implement the interface to a particular dataset. The
    interface consists of a number of routines to manipulate so called
    "state" objects, e.g. open, reset and close them.

    Parameters
    ----------
    sources : tuple of strings, optional
        The data sources to load and return by :meth:`get_data`. By default
        all data sources are returned.
    axis_labels : dict, optional
        Maps source names to tuples of strings describing axis semantics,
        one per axis. Defaults to `None`, i.e. no information is available.

    Attributes
    ----------
    sources : tuple of strings
        The sources this dataset will provide when queried for data e.g.
        ``('features',)`` when querying only the data from MNIST.
    provides_sources : tuple of strings
        The sources this dataset *is able to* provide e.g. ``('features',
        'targets')`` for MNIST (regardless of which data the data stream
        actually requests). Any implementation of a dataset should set this
        attribute on the class (or at least before calling ``super``).
    example_iteration_scheme : :class:`.IterationScheme` or ``None``
        The iteration scheme the class uses in order to produce a stream of
        examples.
    default_transformers: It is expected to be a tuple with one element per
        transformer in the pipeline. Each element is a tuple with three
        elements:
            - the Transformer subclass to apply,
            - a list of arguments to pass to the subclass constructor, and
            - a dict of keyword arguments to pass to the subclass
              constructor.


    Notes
    -----
    Datasets should only implement the interface; they are not expected to
    perform the iteration over the actual data. As such, they are
    stateless, and can be shared by different parts of the library
    simultaneously.

    """
    provides_sources = None
    default_transformers = tuple()

    def __init__(self, sources=None, axis_labels=None):
        if not self.provides_sources:
            raise ValueError("dataset does not have `provides_sources`")
        if sources is not None:
            if not sources or not all(source in self.provides_sources
                                      for source in sources):
                raise ValueError("unable to provide requested sources")
            self.sources = sources
        self.axis_labels = axis_labels

    @property
    def sources(self):
        if not hasattr(self, '_sources'):
            return self.provides_sources
        return self._sources

    @sources.setter
    def sources(self, sources):
        self._sources = sources

    def apply_default_transformers(self, stream):
        """Applies default transformers to a stream.

        Parameters
        ----------
        stream : :class:`~.streams.AbstractDataStream`
            A data stream.

        """
        for (cls, args, kwargs) in self.default_transformers:
            args = [stream] + args
            stream = cls(*args, **kwargs)
        return stream

    @property
    def example_iteration_scheme(self):
        if not hasattr(self, '_example_iteration_scheme'):
            raise AttributeError("dataset does not provide an example "
                                 "iteration scheme")
        return self._example_iteration_scheme

    @example_iteration_scheme.setter
    def example_iteration_scheme(self, value):
        self._example_iteration_scheme = value

    def get_example_stream(self):
        return DataStream(self, iteration_scheme=self.example_iteration_scheme)

    def open(self):
        """Return the state if the dataset requires one.

        Datasets which e.g. read files from disks require open file
        handlers, and this sort of stateful information should be handled
        by the data stream.

        Returns
        -------
        state : object
            An object representing the state of a dataset.

        """
        pass

    def reset(self, state):
        """Resets the state.

        Parameters
        ----------
        state : object
            The current state.

        Returns
        -------
        state : object
            A reset state.

        Notes
        -----
        The default implementation closes the state and opens a new one. A
        more efficient implementation (e.g. using ``file.seek(0)`` instead
        of closing and re-opening the file) can override the default one in
        derived classes.

        """
        self.close(state)
        return self.open()

    def next_epoch(self, state):
        """Switches the dataset state to the next epoch.

        The default implementation for this method is to reset the state.

        Parameters
        ----------
        state : object
            The current state.

        Returns
        -------
        state : object
            The state for the next epoch.

        """
        return self.reset(state)

    def close(self, state):
        """Cleanly close the dataset e.g. close file handles.

        Parameters
        ----------
        state : object
            The current state.

        """
        pass

    @abstractmethod
    def get_data(self, state=None, request=None):
        """Request data from the dataset.

        .. todo::

           A way for the dataset to communicate which kind of requests it
           accepts, and a way to communicate what kind of request is being
           sent when supporting multiple.

        Parameters
        ----------
        state : object, optional
            The state as returned by the :meth:`open` method. The dataset
            can use this to e.g. interact with files when needed.
        request : object, optional
            If supported, the request for a particular part of the data
            e.g. the number of examples to return, or the indices of a
            particular minibatch of examples.

        Returns
        -------
        tuple
            A tuple of data matching the order of :attr:`sources`.

        """

    def filter_sources(self, data):
        """Filter the requested sources from those provided by the dataset.

        A dataset can be asked to provide only a subset of the sources it
        can provide (e.g. asking MNIST only for the features, not for the
        labels). A dataset can choose to use this information to e.g. only
        load the requested sources into memory. However, in case the
        performance gain of doing so would be negligible, the dataset can
        load all the data sources and then use this method to return only
        those requested.

        Parameters
        ----------
        data : tuple of objects
            The data from all the sources i.e. should be of the same length
            as :attr:`provides_sources`.

        Returns
        -------
        tuple
            A tuple of data matching :attr:`sources`.

        Examples
        --------
        >>> import numpy
        >>> class Random(Dataset):
        ...     provides_sources = ('features', 'targets')
        ...     def get_data(self, state=None, request=None):
        ...         data = (numpy.random.rand(10), numpy.random.randn(3))
        ...         return self.filter_sources(data)
        >>> Random(sources=('targets',)).get_data() # doctest: +SKIP
        (array([-1.82436737,  0.08265948,  0.63206168]),)

        """
        return tuple([d for d, s in zip(data, self.provides_sources)
                      if s in self.sources])


class IterableDataset(Dataset):
    """Creates a dataset from a set of iterables.

    Parameters
    ----------
    iterables : :class:`~collections.OrderedDict` or iterable
        The iterable(s) to provide interface to. The iterables' `__iter__`
        method should return a new iterator over the iterable. If an
        :class:`~collections.OrderedDict` is given, its values should be
        iterables providing data, and its keys strings that are used as
        source names. If a single iterable is given, it will be given the
        source ``data``.

    Attributes
    ----------
    iterables : list
        A list of :class:`~collections.Iterable` objects.

    Notes
    -----
    Internally, this method uses picklable iterools's ``_iter``
    function, providing picklable alternatives to some iterators such as
    :func:`range`, :func:`tuple`, and even :class:`file`. However, if the
    iterable returns a different kind of iterator that is not picklable,
    you might want to consider using the :func:`.do_not_pickle_attributes`
    decorator.

    To iterate over a container in batches, combine this dataset with the
    :class:`Batch` data stream.

    """
    example_iteration_scheme = None

    def __init__(self, iterables, **kwargs):
        if isinstance(iterables, dict):
            self.provides_sources = tuple(iterables.keys())
        else:
            self.provides_sources = ('data',)
        super(IterableDataset, self).__init__(**kwargs)
        if isinstance(iterables, dict):
            for iterable in iterables.values():
                if iterable is None:
                    continue
                if not isinstance(iterable, collections.Iterable):
                    raise ValueError
            self.iterables = [iterables[source] for source in self.sources if iterables[source] is not None]
        else:
            if not isinstance(iterables, collections.Iterable):
                raise ValueError
            self.iterables = [iterables]
        try:
            if len(set(len(iterable) for iterable in self.iterables)) != 1:
                raise ValueError("iterables are of different length")
        except TypeError:
            pass

    @property
    def num_examples(self):
        try:
            num_examples, = set(len(iterable) for iterable in self.iterables)
            return num_examples
        except TypeError:
            return float('nan')

    def open(self):
        iterators = [iter_(channel) for channel in self.iterables]
        return izip(*iterators)

    def get_data(self, state=None, request=None):
        if state is None or request is not None:
            raise ValueError
        return next(state)


class IndexableDataset(Dataset):
    """Creates a dataset from a set of indexable containers.

    Parameters
    ----------
    indexables : :class:`~collections.OrderedDict` or indexable
        The indexable(s) to provide interface to. This means it must
        support the syntax ```indexable[0]``. If an
        :class:`~collections.OrderedDict` is given, its values should be
        indexables providing data, and its keys strings that are used as
        source names. If a single indexable is given, it will be given the
        source ``data``.

    Attributes
    ----------
    indexables : list
        A list of indexable objects.

    Notes
    -----
    If the indexable data is very large, you might want to consider using
    the :func:`.do_not_pickle_attributes` decorator to make sure the data
    doesn't get pickled with the dataset, but gets reloaded/recreated
    instead.

    This dataset also uses the source names to create properties that
    provide easy access to the data.

    """
    def __init__(self, indexables, start=None, stop=None, **kwargs):
        if isinstance(indexables, dict):
            self.provides_sources = tuple(indexables.keys())
        else:
            self.provides_sources = ('data',)
        super(IndexableDataset, self).__init__(**kwargs)
        if isinstance(indexables, dict):
            self.indexables = [indexables[source][start:stop]
                               for source in self.sources]
            if not all(len(indexable) == len(self.indexables[0])
                       for indexable in self.indexables):
                raise ValueError("sources have different lengths")
        else:
            self.indexables = [indexables]

        self.example_iteration_scheme = SequentialExampleScheme(
            self.num_examples)

        self.start = start
        self.stop = stop
        self.subset = Subset(slice(start, stop), self.num_examples)

    def __getattr__(self, attr):
        if (attr not in ['sources', 'indexables', '_sources'] and
                attr in self.sources):
            return self.indexables[self.sources.index(attr)]
        raise AttributeError

    # Without explicitly defining a trivial __setstate__ method,
    # the __getattribute__ method would call the __getattr__ method,
    # which would raise an AttributeError. This causes problems
    # when unpickling.
    def __setstate__(self, dict):
        self.__dict__ = dict

    @property
    def num_examples(self):
        return len(self.indexables[0])

    def get_data(self, state=None, request=None):
        if state is not None or request is None:
            raise ValueError
        return tuple(self.subset.index_within_subset(indexable, request)
                     for indexable in self.indexables)


class Subset(object):
    """A description of a subset of examples.

    Parameters
    ----------
    list_or_slice : :class:`list` or :class:`slice`
        List of positive integer indices or slice that describes which
        examples are part of the subset.
    original_num_examples: int
        Number of examples in the dataset this subset belongs to.

    Attributes
    ----------
    is_list : bool
        Whether the Subset is a list-based subset (as opposed to a
        slice-based subset).
    num_examples : int
        Number of examples the Subset spans.
    original_num_examples : int
        Number of examples in the dataset this subset is part of.

    """
    def __init__(self, list_or_slice, original_num_examples):
        self._subset_sanity_check(list_or_slice, original_num_examples)
        if self._is_list(list_or_slice):
            list_or_slice = self._beautify_list(list_or_slice)
        self.list_or_slice = list_or_slice
        self.original_num_examples = original_num_examples

    def __add__(self, other):
        """Merges two subsets together.

        Parameters
        ----------
        other : Subset
            Subset to merge with this subset.

        """
        # Adding two subsets only works if they're subsets of the same dataset,
        # wich can't possibly be the case if their original number of examples
        # differ.
        if self.original_num_examples != other.original_num_examples:
            raise ValueError("trying to add two Subset instances with "
                             "different numbers of original examples, they "
                             "can't possibly belong to the same dataset")
        # An empty subset is a neutral element in subset algebra
        if self.is_empty:
            return other
        # Merging list-based and slice-based subsets results in a list
        # conversion
        if self.is_list != other.is_list:
            return self.__class__(
                self.get_list_representation() +
                other.get_list_representation(),
                self.original_num_examples)
        # List-based subsets are merged by concatenating their indices.
        if self.is_list:
            return self.__class__(self.list_or_slice + other.list_or_slice,
                                  self.original_num_examples)
        # Slice-based subsets are merged into a slice-based subset if they
        # overlap, otherwise they're converted to a list-based subset.
        self_sss = self.slice_to_numerical_args(
            self.list_or_slice, self.original_num_examples)
        self_start, self_stop, self_step = self_sss
        other_sss = self.slice_to_numerical_args(
            other.list_or_slice, other.original_num_examples)
        other_start, other_stop, other_step = other_sss
        # In case of overlap, the solution is to choose the smallest start
        # value and largest stop value.
        if not (self_stop < other_start or self_start > other_stop):
            return self.__class__(slice(min(self_start, other_start),
                                        max(self_stop, other_stop),
                                        self_step),
                                  self.original_num_examples)
        # Everything else is transformed into lists before merging.
        return self.__class__(
            self.get_list_representation() + other.get_list_representation(),
            self.original_num_examples)

    def __getitem__(self, key):
        """Translates a request from this subset to the dataset.

        A request made in the context of this subset is translated into a
        request on the dataset itself.

        Parameters
        ----------
        key : :class:`list` or :class:`slice`
            A request made *within the context of this subset*.

        Returns
        -------
        :class:`list` or :class:`slice`
            The translated request to be used on the dataset.

        """
        self._request_sanity_check(key, self.num_examples)
        # slice(None, None, None) selects the whole subset, no need to index
        # anything
        if key == slice(None, None, None):
            return self.list_or_slice
        if self._is_list(key):
            if self.is_list:
                return [self.list_or_slice[index] for index in key]
            start, stop, step = self.slice_to_numerical_args(
                self.list_or_slice, self.original_num_examples)
            return [start + (index * step) for index in key]
        if self.is_list:
            return self.list_or_slice[key]
        start, stop, step = self.slice_to_numerical_args(
            self.list_or_slice, self.original_num_examples)
        key_start, key_stop, key_step = self.slice_to_numerical_args(
            key, self.num_examples)
        return slice(start + step * key_start,
                     start + step * key_stop,
                     step * key_step)

    @classmethod
    def subset_of(cls, subset, list_or_slice):
        """Construct a Subset that is a subset of another Subset.

        Parameters
        ----------
        subset : :class:`Subset`
            Subset to take the subset of.
        list_or_slice : :class:`list` or :class:`slice`
            List of positive integer indices or slice that describes which
            examples are part of the subset's subset.

        """
        return cls(subset[list_or_slice], subset.original_num_examples)

    @classmethod
    def empty_subset(cls, original_num_examples):
        """Construct an empty Subset.

        Parameters
        ----------
        original_num_examples : int
            Number of examples in the dataset this subset is part of.

        """
        return cls([], original_num_examples)

    @staticmethod
    def sorted_fancy_indexing(indexable, request):
        """Safe fancy indexing.

        Some objects, such as h5py datasets, only support list indexing
        if the list is sorted.

        This static method adds support for unsorted list indexing by
        sorting the requested indices, accessing the corresponding
        elements and re-shuffling the result.

        Parameters
        ----------
        request : list of int
            Unsorted list of example indices.
        indexable : any fancy-indexable object
            Indexable we'd like to do unsorted fancy indexing on.

        """
        if len(request) > 1:
            indices = numpy.argsort(request)
            data = numpy.empty(shape=(len(request),) + indexable.shape[1:],
                               dtype=indexable.dtype)
            data[indices] = indexable[numpy.array(request)[indices], ...]
        else:
            data = indexable[request]
        return data

    @staticmethod
    def slice_to_numerical_args(slice_, num_examples):
        """Translate a slice's attributes into structured attributes.

        Parameters
        ----------
        slice_ : :class:`slice`
            Slice for which structured attributes are wanted.
        num_examples : int
            Number of examples in the indexable that is to be sliced
            through. This determines the structured value for the `stop`
            attribute in case it's `None`.

        """
        start = slice_.start if slice_.start is not None else 0
        stop = slice_.stop if slice_.stop is not None else num_examples
        step = slice_.step if slice_.step is not None else 1
        return start, stop, step

    def get_list_representation(self):
        """Returns this subset's representation as a list of indices."""
        if self.is_list:
            return self.list_or_slice
        else:
            return self[list(range(self.num_examples))]

    def index_within_subset(self, indexable, subset_request,
                            sort_indices=False):
        """Index an indexable object within the context of this subset.

        Parameters
        ----------
        indexable : indexable object
            The object to index through.
        subset_request : :class:`list` or :class:`slice`
            List of positive integer indices or slice that constitutes
            the request *within the context of this subset*. This
            request will be translated to a request on the indexable
            object.
        sort_indices : bool, optional
            If the request is a list of indices, indexes in sorted order
            and reshuffles the result in the original order. Defaults to
            `False`.

        """
        # Translate the request within the context of this subset to a
        # request to the indexable object
        if isinstance(subset_request, numbers.Integral):
            request, = self[[subset_request]]
        else:
            request = self[subset_request]
        # Integer or slice requests can be processed directly.
        if isinstance(request, numbers.Integral) or hasattr(request, 'step'):
            return indexable[request]
        # If requested, we do fancy indexing in sorted order and reshuffle the
        # result back in the original order.
        if sort_indices:
            return self.sorted_fancy_indexing(indexable, request)
        # If the indexable supports fancy indexing (numpy array, HDF5 dataset),
        # the request can be processed directly.
        if isinstance(indexable, (numpy.ndarray, h5py.Dataset)):
            return indexable[request]
        # Anything else (e.g. lists) isn't considered to support fancy
        # indexing, so Subset does it manually.
        return iterable_fancy_indexing(indexable, request)

    def _is_list(self, list_or_slice):
        """Determines if an object is a list or a slice.

        Parameters
        ----------
        list_or_slice : :class:`list` or :class:`slice`
            It is assumed to be one or the other, **and nothing else**.

        Returns
        -------
        rval : bool
            `True` if the object is a list, `False` if it's a slice.

        """
        return not hasattr(list_or_slice, 'step')

    @property
    def is_list(self):
        """Whether this subset is list-based (as opposed to slice-based)."""
        return self._is_list(self.list_or_slice)

    @property
    def num_examples(self):
        """The number of examples this subset spans."""
        if self.is_list:
            return len(self.list_or_slice)
        else:
            start, stop, step = self.slice_to_numerical_args(
                self.list_or_slice, self.original_num_examples)
            return stop - start

    @property
    def is_empty(self):
        """Whether this subset is empty."""
        if self.is_list:
            return len(self.list_or_slice) == 0
        else:
            start, stop, step = self.slice_to_numerical_args(
                self.list_or_slice, self.original_num_examples)
            return stop - start == 0

    def _subset_sanity_check(self, list_or_slice, num_examples):
        if self._is_list(list_or_slice):
            self._list_subset_sanity_check(list_or_slice, num_examples)
        else:
            self._slice_subset_sanity_check(list_or_slice, num_examples)

    def _list_subset_sanity_check(self, indices, num_examples):
        if indices and min(indices) < 0:
            raise ValueError('Subset instances cannot be defined by a list '
                             'containing negative indices')
        if indices and max(indices) >= num_examples:
            raise ValueError('Subset instances cannot be defined by a list '
                             'containing indices greater than or equal to the '
                             'original number of examples')

    def _slice_subset_sanity_check(self, slice_, num_examples):
        numeric_args = (arg for arg in (slice_.start, slice_.stop, slice_.step)
                        if arg is not None)
        if any(arg < 0 for arg in numeric_args):
            raise ValueError('Subset instances cannot be defined by a slice '
                             'with negative start, stop or step arguments')
        if slice_.step is not None and slice_.step != 1:
            raise ValueError("Subset doesn't support slices with a step "
                             "greater than 1")
        if slice_.stop is not None and slice_.stop > num_examples:
            raise ValueError('Subset instances cannot be defined by a slice '
                             'whose stop value is greater than the original '
                             'number of examples')
        if slice_.start is not None and slice_.start >= num_examples:
            raise ValueError('Subset instances cannot be defined by a slice '
                             'whose start value is greater than or equal to '
                             'the original number of examples')
        if (slice_.start is not None and slice_.stop is not None and
                slice_.start > slice_.stop):
            raise ValueError('Subset instances cannot be defined by a slice '
                             'whose start value is greater than its stop '
                             'value')

    def _request_sanity_check(self, list_or_slice, num_examples):
        if self._is_list(list_or_slice):
            self._list_request_sanity_check(list_or_slice, num_examples)
        else:
            self._slice_request_sanity_check(list_or_slice, num_examples)

    def _list_request_sanity_check(self, indices, num_examples):
        if len(indices) == 0:
            raise ValueError('list-based requests cannot be empty (this would '
                             'produce an empty return value)')
        if any(index < 0 for index in indices):
            raise ValueError('Subset does not support list-based requests '
                             'with negative indices')
        if max(indices) >= num_examples:
            raise ValueError('list-based requests cannot contain indices '
                             'greater than or equal to the number of examples '
                             'the subset spans')

    def _slice_request_sanity_check(self, slice_, num_examples):
        numeric_args = (arg for arg in (slice_.start, slice_.stop, slice_.step)
                        if arg is not None)
        if any(arg < 0 for arg in numeric_args):
            raise ValueError('Subset does not support slice-based requests '
                             'with negative start, stop or step arguments')
        if slice_.stop is not None and slice_.stop > num_examples:
            raise ValueError('slice-based requests cannot have a stop value '
                             'greater than the number of examples the subset '
                             'spans (this would produce a return value with '
                             'smaller length than expected')
        if slice_.start is not None and slice_.start >= num_examples:
            raise ValueError('slice-based requests cannot have a start value '
                             'greater than the number of examples the subset '
                             'spans (this would produce an empty return '
                             'value)')
        if (slice_.start is not None and slice_.stop is not None and
                slice_.start >= slice_.stop):
            raise ValueError('slice-based requests cannot have a start value '
                             'greater than or equal to its stop value (this '
                             'would produce an empty return value)')

    def _beautify_list(self, indices):
        # List elements should be unique and sorted
        indices = list(sorted(set(indices)))
        # If indices are contiguous, convert them into a slice
        contiguous_indices = all(
            indices[i] + 1 == indices[i + 1] for i in range(len(indices) - 1))
        if indices and contiguous_indices:
            return slice(indices[0], indices[-1] + 1, None)
        else:
            return indices
