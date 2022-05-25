import abc
import sys
import numpy as np
from copy import deepcopy
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import pickle
import autoai_ts_libs.deps.tspy
from autoai_ts_libs.deps.tspy.ml.causal_modeling import util
from math import floor

# Ensure compatibility with Python 2/3
if sys.version_info >= (3, 4):
    ABC = abc.ABC
else:
    ABC = abc.ABCMeta(str('ABC'), (), {})

PADDING_INDEX_MARKER = -1  # used in indexing arrays to indicate padding
autoai_ts_libs.deps.tspy_TIMESTAMP_COLNAME = "timestamps"

class InputAdapterRawToEncoded(ABC):
    """ Main user-application adapter template for extracting/transforming raw data (e.g. json)
    to an encoded format (e.g., one-hot)

    """

    def __init__(self, *argv, **kwargs):
        """
        """

    @abc.abstractmethod
    def fit(self, *argv, **kwargs):
        """ Perform fitting of any internal encoder parameters (e.g. dictionaries), if needed
        """
        raise NotImplementedError

    @abc.abstractmethod
    def encode(self, *argv, **kwargs):
        """ Perform encoding, return encoded data
        """
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, *argv, **kwargs):
        """ Method to save encoder parameters
        """
        raise NotImplementedError

    @abc.abstractmethod
    def load(self, *argv, **kwargs):
        """ Method to load encoder parameters
        """
        raise NotImplementedError

    # @abc.abstractmethod
    # def get_encoder_params(self, *argv, **kwargs):
    #     """ Retrieve parameters needed to encode
    #     """
    #     raise NotImplementedError
    #
    # @abc.abstractmethod
    # def set_encoder_params(self, *argv, **kwargs):
    #     """ Method to set encoder parameters
    #     """
    #     raise NotImplementedError


class embedder(ABC):
    """ adapter abstraction for transforming encoded data to vectors in an embedding space. These may include
    static embeddings (single encoded vector --> single embedded vector), or contextualized
    embeddings (multiple encoded vectors --> single embedded vector)
    """

    def __init__(self, *argv, **kwargs):
        """
        """

    @abc.abstractmethod
    def fit(self, *argv, **kwargs):
        """ Perform fitting of internal parameters
        """
        raise NotImplementedError

    @abc.abstractmethod
    def transform(self, *argv, **kwargs):
        """ Perform embedding, return transformed data
        """
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, *argv, **kwargs):
        """ Method to save parameters
        """
        raise NotImplementedError

    @abc.abstractmethod
    def load(self, *argv, **kwargs):
        """ Method to loadparameters
        """
        raise NotImplementedError


class staticPCAEmbedder(embedder):
    """
    Implements linear PCA projection
    """

    def __init__(self, orig_dim, proj_dim, standardize=True, verbose=True):
        self.orig_dim = orig_dim
        self.proj_dim = proj_dim
        self.pcaobj = None
        self.stdscaler = StandardScaler() if standardize else None
        self.verbose = verbose
        self.verbose_prefix = self.__class__.__name__


    def _flatten_fit_transform(self, X, do_fit):
        assert(isinstance(X, (np.ndarray,list)))
        assert(len(X.shape)>1)
        X = np.asarray(X) if isinstance(X, list) else X
        orig_shape = X.shape
        flat_x = np.reshape(X, [-1, X.shape[-1]])
        if do_fit and self.stdscaler is not None:
            if self.verbose:
                print("%s (INFO): Generating standardization object." % self.verbose_prefix)
            flat_xs = self.stdscaler.fit_transform(flat_x)
        elif not do_fit and self.stdscaler is not None:
            flat_xs = self.stdscaler.transform(flat_x)
        else:
            flat_xs = flat_x
        if do_fit:
            self.pcaobj = PCA(n_components=self.proj_dim)
            flat_xst = self.pcaobj.fit_transform(flat_xs)
        else:
            flat_xst = self.pcaobj.transform(flat_xs)
        xst = np.reshape(flat_xst, list(orig_shape[:-1])+[self.proj_dim])
        return xst


    def fit(self, X):
        """
        Sets internal params needed to transform()
        Args:
            X:  ndarray [..., orig_dim]
        Returns:
            transformed X nadarray [..., proj_dim]
        """
        return self._flatten_fit_transform(X=X, do_fit=True)


    def transform(self, X):
        """
        Performs PCA transform using previously fitted parameters
        Args:
            X: ndarray [..., orig_dim]
        Returns:
            transformed X nadarray [..., proj_dim]
        """
        assert(self.pcaobj is not None)
        return self._flatten_fit_transform(X=X, do_fit=False)


    def _load_params(self,f):
        """
        internal routine
        Args:
            f: open file (read)
        Returns:
        """
        d = pickle.load(f)
        self.pcaobj = d['pcaobj']
        self.orig_dim = d['orig_dim']
        self.stdscaler = d['stdscaler']
        self.proj_dim = d['proj_dim']

    def _dump_params(self, f):
        """
        internal routine
        Args:
            f: open file handle for writing
        Returns:
        """
        d = {'pcaobj': self.pcaobj, 'stdscaler': self.stdscaler,
             'proj_dim': self.proj_dim, 'orig_dim': self.orig_dim}
        pickle.dump(d, f)

    def save(self, f):
        """
        Stores internal parameters to file
        Args:
            f: file handle (obtained via open()) OR file name (string)
        Returns:
        """
        if self.pcaobj is None:
            raise RuntimeError("%s (ERROR): Need to call fit() before save()" % self.verbose_prefix)
        if hasattr(f, 'write'):
            self._dump_params(f)
        elif isinstance(f, str):
            with open(f, 'wt') as of:
                self._dump_params(of)
        else:
            raise ValueError("%s (ERROR): unsupported handle type %s" % (self.verbose_prefix, type(f)))

    def load(self, f):
        if hasattr(f, 'read'):
            self._load_params(f)
        elif isinstance(f, str):
            with open(f, 'rb') as of:
                self._load_params(of)
        else:
            raise ValueError("%s (ERROR): unsupported handle type %s" % (self.verbose_prefix, type(f)))



class timeStampedToTimeEquidistant:
    """ INPUT: array of events at arbitrary time stamps
        OUTPUT: time-equidistant array of events
        This class aligns the events' time stamps with an equidistant time grid, and reconciles
        collisions.
    """

    def __init__(self, time_resolution, padding_object, reconciliation_func=None, bucket_assignment_func=None,
                 verbose=True):
        self.verbose = verbose
        self.verbose_prefix = self.__class__.__name__
        self.time_resolution = time_resolution
        self.reconciliation_func = self._default_reconciliation_function if reconciliation_func is None else reconciliation_func
        self._default_bucket_assignment_function = self._causal_bucket_assignment_function
        self._bucket_assignment_func = self._default_bucket_assignment_function if bucket_assignment_func is None else bucket_assignment_func
        self.padding_object = padding_object

    def transform(self, events, timestamp_list):
        """
         Performs alignment/projection of timestamped events onto time-equidistant scale
         Args:
             events: can be (1) list or ndarray with events, OR (2) autoai_ts_libs.deps.tspy.TimeSeries object
             timestamp_list: ndarray containing numerical timestamps (e.g., number of (mili)seconds)
                            This can be also None if 'events' is an instance of autoai_ts_libs.deps.tspy.TimeSeries
         Returns:
             ndarray of aligned objects, ndarray of corresponding timestamps, ndarray of indexes to the original arrays
         """
        if not isinstance(events, autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries):
            return self._align_with_reconciliation_func(events, timestamp_list)
        else:
            return self._transform_ts(events)

    def _transform_ts(self, event_ts):
        """
         Performs alignment/projection of timestamped events onto time-equidistant scale
         Args:
             event_ts: autoai_ts_libs.deps.tspy.time_series container with events
         Returns:
             autoai_ts_libs.deps.tspy.time_series container with periodic timestamps, array of indexes to the original event sequence
        """
        # Shallow integration: time_series --> numpy
        assert(isinstance(event_ts, autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries))
        aux = event_ts.to_df(convert_dates=False).to_numpy()
        timestamps = aux[:,0]
        events = aux[:, 1:]
        aligned_events, aligned_timestamps, back_idx = self._align_with_reconciliation_func(events, timestamps)
        # Shallow integration: numpy -> time_series
        auxdf = util.numpy_to_dataframe(data=aligned_events, timestamps=aligned_timestamps, time_column_name=autoai_ts_libs.deps.tspy_TIMESTAMP_COLNAME)
        return autoai_ts_libs.deps.tspy.time_series(auxdf, ts_column=autoai_ts_libs.deps.tspy_TIMESTAMP_COLNAME), back_idx


    @staticmethod
    def _default_reconciliation_function(target_timestamp, candidates, timestamps):
        """
        Implements a resolution among multiple candidates competing for a target timeslot
        The winner is the closest in time to the bucket's grid time
        Args:
            target_timestamp: timestamp of the time slot to be occupied
            candidates: list of candidate objects
            timestamps: list of timestamp corresponding to candidate objects

        Returns:
            index of winning candidate
        """
        assert (isinstance(timestamps, np.ndarray))
        assert (len(candidates) > 0 and len(candidates) == len(timestamps))
        return np.argmin(np.abs(target_timestamp - timestamps))

    @staticmethod
    def _min_distance_bucket_assignment_function(grid, timestamp):
        """
        Function used in distributing individual objects into buckets, before reconciliation.
        Given a grid of buckets (list[(timestamp, set)]) and a timestamp, assign the timestamp to
        a grid point based on the following strategy: find the grid point closest in time (either
        from left or from right)
        Args:
            grid: list of tuples (grid timestamp, set with candidate indexes)
            timestamp: int or float representing the time

        Returns:
            integer - index of the bucket to which timestamp should be assigned
        """
        # assigns to the grid point closest in time (from both sides: pre- or succeeding)
        t0 = grid[0][0]
        if timestamp < t0:
            return 0
        elif timestamp >= grid[-1][0]:
            return len(grid)
        else:
            return round((timestamp - t0) / (grid[1][0] - t0))
        # return np.argmin(np.abs(np.asarray([i[0] for i in grid]) - timestamp))

    @staticmethod
    def _causal_bucket_assignment_function(grid, timestamp):
        """
        Function used in distributing individual objects into buckets, before reconciliation.
        Given a grid of buckets (list[(timestamp, set)]) and a timestamp, assign the timestamp to
        a grid point based on the following strategy: find the closest PRECEDING grid point.
        Args:
            grid: list of tuples (grid timestamp, set with candidate indexes)
            timestamp: int or float representing the time

        Returns:
            integer - index of the bucket to which timestamp should be assigned
        """
        # assigns to the grid point closest in time (from both sides: pre- or succeeding)
        t0 = grid[0][0]
        if timestamp < t0:
            return 0
        elif timestamp >= grid[-1][0]:
            return len(grid)
        else:
            return floor((timestamp - t0) / (grid[1][0] - t0))

        # d = timestamp - np.asarray([i[0] for i in grid])
        # return np.argmin(np.where(d < 0., np.inf, d))

    @staticmethod
    def _sort_events_by_time(event_list, timestamp_list):
        """
        Helper routine to sort both the event and timestamp array by the timestamps in ascending order
        Args:
            event_list: array-like, contains objects
            timestamp_list: array-like, contains numerical timestamps (e.g, number of seconds, miliseconds, etc. )

        Returns:
            sorted event list, sorted timestamps list, 0-based indexes wrt original ordering
        """
        assert (isinstance(event_list, np.ndarray))
        assert (isinstance(timestamp_list, np.ndarray))
        assert (len(event_list) == len(timestamp_list))
        idx = list(range(len(timestamp_list)))
        idx_srt = sorted(idx, key=lambda i: timestamp_list[i])
        return event_list[idx_srt], timestamp_list[idx_srt], idx_srt

    @staticmethod
    def _is_sorted_ascending(x):
        for i in range(len(x) - 1):
            if x[i + 1] < x[i]:
                return False
        return True

    def _align_with_reconciliation_func(self, event_list, timestamp_list):
        """
        Performs alignment/projection of timestamped events onto time-equidistant scale
        Args:
            event_list: ndarray or list with events
            timestamp_list: ndarray or list containing numerical timestamps (e.g., number of (milli)seconds)
        Returns:
            ndarray of aligned objects, ndarray of corresponding timestamps, ndarray of indexes to the original arrays
        """
        event_list = np.asarray(event_list) if isinstance(event_list, list) else event_list
        timestamp_list = np.asarray(timestamp_list) if isinstance(timestamp_list, list) else timestamp_list
        assert (isinstance(event_list, np.ndarray))
        assert (isinstance(timestamp_list, np.ndarray))
        assert (len(event_list) == len(timestamp_list))
        # adjust dimensionality of padding object if scalar
        if np.isscalar(self.padding_object) and len(event_list.shape)==2 and event_list.shape[1]==1:
            self.padding_object = np.asarray([self.padding_object])
        if len(event_list.shape) > 1:
          assert(event_list[0].shape==self.padding_object.shape)
        else:
          assert(np.isscalar(self.padding_object))
        num_grid_points = int(np.ceil((timestamp_list[-1] - timestamp_list[0]) / self.time_resolution)) + 1
        assert (num_grid_points > 0)
        # create a "bucket" at each grid point
        grid = [[timestamp_list[0] + k * self.time_resolution, set()] for k in range(num_grid_points)]

        # distribute events into grid buckets
        for index, (event, timestamp) in enumerate(zip(event_list, timestamp_list)):
            best_bucket_idx = self._bucket_assignment_func(grid, timestamp_list[index])
            grid[best_bucket_idx][1].add(index)  # register index of the event in the bucket closest in time

        # resolve collisions of multiple events competing for same time point
        nzeropad = 0
        ndropped = 0
        for c, g in enumerate(grid):
            set_idxs = list(g[1])
            if len(set_idxs) > 1:  # multiple cands - needs reconciliation step
                cand_timestamp_list = np.asarray([timestamp_list[i] for i in set_idxs])
                cand_event_list = np.asarray([event_list[i] for i in set_idxs])
                winner_idx = self.reconciliation_func(g[0], cand_event_list, cand_timestamp_list)
                # replace candidates by the winner
                grid[c][1] = set()
                grid[c][1].add(set_idxs[winner_idx])
                ndropped += len(cand_event_list) - 1
            elif len(set_idxs) == 0:  # pad
                grid[c][1].add(PADDING_INDEX_MARKER)
                nzeropad += 1
            else:  # uncontested candidate, leave as is
                pass

        # generate output arrays
        aligned_events = []
        aligned_times = []
        orig_indexes = []
        for g in grid:
            assert (len(g[1]) == 1)  # at this point there must be exactly one element
            aligned_times.append(g[0])
            oi = g[1].pop()  # orig idx
            orig_indexes.append(oi)
            event = event_list[oi] if oi != PADDING_INDEX_MARKER else deepcopy(self.padding_object)
            aligned_events.append(event)
        # remove trailing padded events
        while np.array_equal(aligned_events[-1], self.padding_object):
            del(aligned_times[-1])
            del(aligned_events[-1])
            del(orig_indexes[-1])
            nzeropad -= 1
        assert(len(orig_indexes)==len(aligned_events)==len(aligned_times))
        if self.verbose:
            print(
                "%s (INFO): Aligned %d original objects onto %d grid points (resolution %d)\n Padded %d (pads/obj = %.4f)\n"
                " Dropped %d (drops/obj = %.4f)" %
                (self.verbose_prefix, len(event_list), len(aligned_events), self.time_resolution,
                 nzeropad, nzeropad / len(event_list),
                 ndropped, ndropped / len(event_list)))
        return np.asarray(aligned_events), np.asarray(aligned_times), np.asarray(orig_indexes)



class timeEquidistantToWindowed:
    """ INPUT: array of (time-equidistant) events; window length
        OUTPUT: array of window slices created by running window through the linear input
    """
    PADDING_MODE_NOPADDING = 'nopadding'
    PADDING_MODE_HEADPADDING = 'headpadding'
    PADDING_MODE_TAILPADDING = 'tailnopadding'
    PADDING_INDEX_MARKER = -1

    def __init__(self, wlen, step=1, padding_mode=PADDING_MODE_NOPADDING, verbose=True):
        """
        Args:
            wlen: int window length
            step: int stepsize for windowing
            padding_mode: string, one of {'nopadding', 'headpadding', 'tailpadding'}. See descr for fit()
            verbose: print out certain statistics
        """
        self.verbose = verbose
        self.verbose_prefix = self.__class__.__name__
        self.wlen = wlen
        self.wstep = step
        self.padding_mode = padding_mode


    def _drop_all_zero_windows(self, idx):
        """
        TODO: this may be moved out of the class (jiri)
        removes windows that contain only padding from sequence
        Args:
            idx: windowed sequence [nsamples, windowlen]
        Returns:
            windowed sequence [new nsamples, windowlen], where new_nsamples = nsamples - all_zero_windows
        """
        assert(isinstance(idx, np.ndarray))
        if timeEquidistantToWindowed.PADDING_INDEX_MARKER not in idx:
            return idx
        all_zero_window_patt = timeEquidistantToWindowed.PADDING_INDEX_MARKER * np.ones(idx.shape[1:])
        new_idx = []
        for i in range(idx.shape[0]):
            if idx[i] == all_zero_window_patt:
                continue
            new_idx.append(idx[i])
        return np.asarray(idx)

    def _drop_full_pad_windows(self, d, zeroobj):
        """
        Removes windows that contain purely series of 'zeroobj'
        Args:
            d: ndarray [nwindows, windowseries, feadim]
            zeroobj: [feadim]

        Returns:
            ndarray (modified d), nadarray (indexes of elements kept along axis 0)
        """
        assert(isinstance(d, np.ndarray))
        assert(len(d.shape)==3)
        assert(len(zeroobj)==d.shape[-1])

        zerowin = np.tile(np.expand_dims(zeroobj, axis=-1), self.wlen).T  # this is a zeroobj window
        keepidx = []
        for n in range(d.shape[0]):
            if np.array_equal(d[n], zerowin):
                continue
            keepidx.append(n)
        if len(keepidx) != d.shape[0]:
            new_d = d[keepidx]
        else:
            new_d = d

        print("%s (INFO): Dropped %d (%.1f%%) windows due to all-pad." % (self.verbose_prefix, d.shape[0]-len(keepidx),
                                                                          100 * (d.shape[0]-len(keepidx))/d.shape[0]))
        return new_d, keepidx


    def _grep_data_by_index(self, d, idx, zeroobj=None):
        """
        data from 'd' will be assembled according to indexing stored in 'idx'
        for indexes that == PADDING_INDEX_MARKER, the zeroobj padding object will be inserted
        Args:
            d: data with dims [nsamples, ...]
            idx: index array [nsamples + padding, ...]

        Returns:
            windowed version of d, with optional head/tail padding
        """
        if timeEquidistantToWindowed.PADDING_INDEX_MARKER in idx:
            # append a zero object to the data reservoir and point the -1 index to it
            zeroobj = zeroobj if zeroobj is not None else np.zeros(d.shape[1:])
            assert(zeroobj.shape==d.shape[1:])
            if len(d.shape) > 1:
                D = np.vstack([d, zeroobj])
            else:
                D = np.squeeze(np.vstack([np.expand_dims(d, axis=-1), np.expand_dims(zeroobj, axis=-1)]))
            zeroobj_idx = D.shape[0]-1
            idx = deepcopy(idx)
            # rewrite -1 by the pointer to the actual object appended above
            idx = np.where(idx==timeEquidistantToWindowed.PADDING_INDEX_MARKER, zeroobj_idx, idx)
        else:
            D = d
        return D[idx]  # this is where the magic happens


    def getOriginalIndexes(self):
        """
        Returns: ndarray of original indexes pointing to input, aligned with the first dimension of the windowed output
        E.g.: -1, -1, -1, 0, 1, 2, -1, 4 ... (where -1 is a padding marker (timeEquidistantToWindowed.PADDING_INDEX_MARKER)
        """
        return self._fitted_index_array


    def fit(self, x, zeroobj=None, dropz=False):
        """
        Will generate an overlapping-windowed sequence based on a linear array x. x has dims [nsamples, ...]
        Internal index array will be kept and will be applied to process any other array with same
        1st dimension as 'x'.
        Example: Input x = [1, 2, 3, 4, 5, 6, 7],
                 wlen = 3, step = 1
                 Output without padding
                        [[1, 2, 3], [2, 3, 4], [3, 4, 5], [4, 5, 6,], [5, 6, 7]]
                 Output with trailing padding
                        [[1, 2, 3], [2, 3, 4], [3, 4, 5], [4, 5, 6,], [5, 6, 7], [6, 7, pad], [7, pad, pad]
                 Output with lead padding:
                        [[pad, pad, 1], [pad, 1, 2], [1, 2, 3], [2, 3, 4], [3, 4, 5], [4, 5, 6,], [5, 6, 7]]
        Args:
            x: input ndarray w/dim [nsamples, ...]
            zeroobj: object used for padding. If None, an 0.0-object will be generated to match the data dimensions
        Returns:
            array with windowed [nsamples-winlen, winlen, ...]
        """
        if isinstance(x, autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries):
            x, _ = util.timeseries_to_numpy(x)

        assert(isinstance(x, np.ndarray))
        zeroobj = zeroobj if zeroobj is not None else np.zeros(x.shape[1:])
        zeroobj = np.asarray(zeroobj) if isinstance(zeroobj, list) else zeroobj
        nsamples = x.shape[0]
        headpadwin = [timeEquidistantToWindowed.PADDING_INDEX_MARKER for _ in range(self.wlen-1)]\
                            if self.padding_mode == timeEquidistantToWindowed.PADDING_MODE_HEADPADDING else []
        tailpadwin = [timeEquidistantToWindowed.PADDING_INDEX_MARKER for _ in range(self.wlen-1)]\
                            if self.padding_mode == timeEquidistantToWindowed.PADDING_MODE_TAILPADDING else []
        # all windowing done on this index array first, only later actual data access
        I = np.asarray(headpadwin + list(range(nsamples)) + tailpadwin)
        windowed_I = []
        for t in range(0, len(I), self.wstep):
            if t + self.wlen > len(I):
                break
            windowed_I.append(I[t:t + self.wlen])
        windowed_I = np.asarray(windowed_I)
        self._fitted_index_array = deepcopy(windowed_I)
        d = self._grep_data_by_index(x, self._fitted_index_array, zeroobj=zeroobj)
        if dropz:
            d, idx = self._drop_full_pad_windows(d, zeroobj=zeroobj)
            self._fitted_index_array = self._fitted_index_array[idx]
        return d


