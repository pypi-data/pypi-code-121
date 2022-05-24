import json
from pathlib import Path

import datetime as dt
# import appdirs
import types
import sys
from typing import Optional, Sequence
import numpy as np
# from numpy.lib import recfunctions as rf

import limonade.loaders as ldr
import limonade.exceptions as ex
from limonade import utils as ut
from limonade import misc


class TimeCache:
    """
    TimeCache controls timing data and provides dead/live time of the detector plus maintains lists of index - time
    pairs of the time information insertions times so that quick retrieval of time periods is possible. Each interval
    holds variable amount of events. Because both indices and timestamps are monotonously increasing, they can both be
    used to find intervals from the data.
    The timing datafile is saved with data and should be read only. It contains index of insertion (int64) plus
    the dead_time delta of the interval for each channel in float32 type. First row always points to first event with
    zero dead times for all channels. First real dead time value is stored to the second row.

    """

    def __init__(self, parent):
        """
        A component for time caching and dead time handling. Takes calling Data instance as parent for data access.

        :param parent: Parent Data instance.

        """
        self.parent = parent
        self.dlen = len(parent.ch_list)
        type_list = [('idx', '<u8'), ('t', '<u8')]
        for x in range(self.dlen):
            type_list.append(('dt{}'.format(x), '<f4'))
        self.timing = np.zeros((0,), dtype=type_list)  # first entry is aways zeros

    def set(self, timing):
        """

        :param timing: a np.array containing the timing data (retrieved by read_binary_data)

        """
        self.timing = timing

    def add(self, timing, t_offset):
        """
        When adding timing data, the index and t values of the new timing data are updated with the
        t_max and num_evt values of the existing data (the idx, and t values of the last timing entry).

        These should correspond with the values returned by get_end_time and get_num_events of Data class just 
        before any data is added.

        :param timing:      The timing data.
        :param t_offset:    This is the gap between stop of previous file and start of current file in ns. It is
                            the dead time between last timing index of the last file and the first of the current 
                            file. 
        """
        if self.timing.shape[0] == 0:
            self.timing = timing
        else:
            timing['idx'] += int(self.timing[-1]['idx'] + 1)  # Ha! gotcha!
            timing['t'] += int(self.timing[-1]['t'] + t_offset)
            for ch in range(self.parent.num_ch):
                timing[0]['dt{}'.format(ch)] = t_offset
            self.timing = np.concatenate((self.timing, timing[1:]))

    def get_timing(self, t_slice=None):
        """
        Return timing data for a slice. The first entry is zeros and the second one is interpolated to start
        from t_slice[0]. Last one is an extra row interpolated to t_slice[1].

        If t_slice is not defined this method returns timing data as it is.

        :param t_slice: Time slice (in ns)

        :return: (interpolated) timing data for time slice

        """
        if t_slice is None:
            return self.timing

        indices = np.zeros((self.dlen, 2), dtype='u8')
        dts = np.zeros((self.dlen, 2))
        for ch in range(self.dlen):
            # first interp the first index
            indices[ch, :] = self.find(t_slice, ch)

            dts[ch, 0] = self._interp(ch, t_slice[0], indices[ch, 0], prev=True)[1]  # pick the part after t_val
            if indices[ch, 1] == indices[ch, 0] + 1:  # if both ends of t_slice fit within a single timing interval
                dts[ch, 1] = dts[ch, 0] - self._interp(ch, t_slice[1], int(indices[ch, 1]), prev=False)[1]  # subtract the rest
            else:
                dts[ch, 1] = self._interp(ch, t_slice[1], int(indices[ch, 1]), prev=False)[0]  # pick the part before t_val

        timing_idx_0 = indices[:, 0].min()
        timing_idx_1 = int(indices[:, 1].max())
        retval = self.timing[timing_idx_0:timing_idx_1 + 1].copy()  # include the last index
        ch_list = ['dt{}'.format(x) for x in range(self.dlen)]
        retval[ch_list][0] = 0
        retval[ch_list][1] = tuple(dts[:, 0])
        retval[ch_list][-1] = tuple(dts[:, 1])
        return retval

    def get_dead_time(self, t_slice=None):
        """
        Return the dead time of the time slice.

        :param t_slice:
        :return: All dead times in a numpy array. Live and dead times are float values of seconds.
        """
        timing = self.get_timing(t_slice)
        ch_list = ['dt{}'.format(x) for x in range(self.dlen)]
        dead_time = np.zeros((self.dlen,))
        for ch_idx in range(self.dlen):
            dead_time[ch_idx] = (timing[ch_list[ch_idx]].sum())
        return dead_time

    def get_live_time(self, t_slice=None):
        """
        Return live time of the slice.

        :param t_slice:
        :return: All live times in a numpy array. Live and dead times are float values of seconds.

        """
        livetime = self.get_total_time(t_slice)*1e-9 - self.get_dead_time(t_slice)

        return livetime

    def get_total_time(self, t_slice=None):
        """

        Return total time of the time slice or total time of measurement, if t_slice is None.
        :param t_slice:
        :return: Total time value in nanoseconds

        """
        if t_slice is None:
            tottime = self.parent.get_end_time()
        else:
            tottime = int(t_slice[1] - t_slice[0])

        return tottime

    def _interp(self, ch, t_val, index, prev=True):
        """
        Interpolates dead time values for time slices. Timing array lists the dead time of each channel by some
        interval that depends on the loader. If a time_slice does not hit the interval boundary the value has to be
        somehow interpolated for the slice. This is especially true if the dead time itself is being plotted and the
        time bin is smaller than the interval.

        :param ch: The channel in question.
        :param t_val: A nanosecond value defining a point in time.
        :param index: The last timing index that is earlier than t_val for the channel. For start point of a time slice
                      this is just the start idx returned by find(t_slice, channel), for the endpoint it is the
                      stop idx - 1.
        :param prev: whether index points to timing index previous to t_val or after it.
        :return: Return a tuple with a dead time value for the part before the t_val and after it so that an interval
                 in timing array can be sliced.

        """
        t_min = self.parent.get_data('time', 0)  # cannot to go before the first event
        t_val = max(t_min, t_val)
        if prev:  # idx0 is given
            idx0 = self.timing['idx'][index]
            t0 = self.parent.get_data('time', idx0)
            # find next nonzero index (index is uint64, so it automatically casts itself to float on a mathematical
            # operation, hence the int()
            mask = self.timing['dt{}'.format(ch)][int(index + 1):] != 0
            index1 = int(index + 1 + np.argmax(mask))
            idx1 = int(self.timing['idx'][index1])
            t1 = self.parent.get_data('time', idx1)
            dt = self.timing['dt{}'.format(ch)][index1]
        else:  # idx1 is given
            idx1 = int(self.timing['idx'][index])
            # print('idx of end', self.timing[index-1:], self.parent.get_end_time())
            # print('time of idx', self.parent.get_data('time', idx1))
            # print('time of end', self.parent.get_data('energy', idx1))
            # print('channel', ch)
            t1 = self.parent.get_data('time', idx1)
            # find previous nonzero index
            mask = self.timing['dt{}'.format(ch)][int(index - 1)::-1] != 0
            index0 = int(index - 1 - np.argmax(mask))
            idx0 = int(self.timing['idx'][index0])
            t0 = self.parent.get_data('time', idx0)
            dt = self.timing['dt{}'.format(ch)][index]

        if t0 > t_val or t_val > t1:  # sanity check
            t_val = t1
            #raise ValueError('Invalid t_val in get_timing.')

        return dt*(t_val - t0)/(t1 - t0), dt*(t1 - t_val)/(t1 - t0)

    def find(self, t_slice, ch=None):
        """
        Finding indices in self.timing that contain the t_slice time.

        :param t_slice: tuple of nanosecond values defining a slice in time
        :param ch: If specified will return only indices in which dead time has been given for ch. This is mainly used
                   by get_timing to interpolate the dead time.

        :return: indices to self.timing containing the time slice.

        """

        if ch is None:
            mask = np.ones((self.timing.shape[0],), dtype='bool')
        else:
            mask = np.zeros((self.timing.shape[0],), dtype='bool')
            mask[0] = True  # include zero in the beginning
            nonz = self.timing['dt{}'.format(ch)] > 0
            mask[nonz] = True

        # last index under t_slice[0] or 0
        idx1 = 0
        prev = 0
        for idx, t_idx in enumerate(self.timing['idx']):
            if mask[idx]:
                if self.parent.get_data(self.parent.index_data, t_idx) >= t_slice[0]:
                    #went over, now need to go back to previous event with mask True
                    idx1 = prev
                    break
                prev = idx
        # first index over t_slice[1] or last index in mask
        try:
            for idxn, t_idx2 in enumerate(self.timing[idx1+1:]['idx']):

                if self.parent.get_data(self.parent.index_data, t_idx2) >= t_slice[1] and mask[idx1 + 1 + idxn]:
                    break
        except:
            print('Error in TCache')
            print(self.parent.get_num_events, t_idx2, t_slice, mask.shape)
            raise

        idx2 = idx1 + 1 + idxn
        return idx1, idx2

    def get_indices(self, t_slice=None):
        """
        Return start and stop event indices (endpoint not inclusive) that contain the time slice fully using timing
        info as a hash.

        :param t_slice: tuple of nanosecond values defining a slice in time. If None full data is returned.

        :return: indices to event data containing the the time slice

        """
        if t_slice is None:
            return 0, self.parent._data_store.num_evt

        if self.timing.shape[0] == 0:
            start = 0
            stop = self.parent._data_store.num_evt
            print('Time cache not set!')
            return start, stop

        idx1, idx2 = self.find(t_slice)
        start = self.timing['idx'][idx1]
        stop = int(self.timing['idx'][idx2] + 1)  # idx2 is included in the range
        return start, stop


class Metadata:
    """
    Metadata is responsible for the loading and manipulation of metadata within the Data class. It contains a reference
    to parent class (Data or OnlineData), but will never change anything through it. The link is used to access
    configuration and get number of counts, dead time etc.

    Under normal circumstances the metadata is present in a json file, and is loaded by the metadata class. (If,
    however, metadata is missing or needs to be changed the metadata class provides methods for updating, validating
    and saving the changes.)

    """

    def __init__(self, parent, num_ch=None):
        """
        As a component the metadata needs reference to the calling Data class instance as parent for data access. If 
        None is given, then a standalone instance of Metadata is created. A fake parent is created, which only has the 
        detector configuration in it. A standalone metadata only supports data loading and setting of properties.

        :param parent: Parent Data instance or None for standalone metadata.
        :param num_ch: Number of channels. Only used by standalone metadata with no access to Data class. Deprecated?

        """

        # The prototype of minimal metadata fields.
        self.metadata_proto = {'start': None,
                               'stop': None,
                               'input_counts': 0,
                               'counts': 0,
                               'events': 0,
                               'total_time': 0,
                               'live_time': 0.,
                               'dead_time': 0.,
                               'name': '',
                               'run_id': '',
                               'notes': ''}

        self.parent = parent
        if self.parent is None:
            self.standalone = True
            self.num_ch = num_ch
        else:
            self.standalone = False
            self.num_ch = parent.num_ch
        
        self._run_data = []
        if self.num_ch is not None:
            for idx in range(self.num_ch):
                # definition of the (per channel) metadata is here
                self._run_data.append(self.metadata_proto.copy())
        #self.name = self.parent.config.det['name']
        self.initialized = False

    # Few of the metadata items can be easily implemented as properties, so why not.
    # start, stop, total time and events are the same for every channel. Counts are handled
    # as np.arrays.
    @property
    def start(self):
        return self._run_data[0]['start']

    @start.setter
    def start(self, value: dt.timedelta):
        for i in range(len(self._run_data)):
            self._run_data[i]['start'] = value

    @property
    def stop(self):
        return self._run_data[0]['stop']

    @stop.setter
    def stop(self, value: dt.timedelta):
        for i in range(len(self._run_data)):
            self._run_data[i]['stop'] = value

    @property
    def total_time(self):
        if not isinstance(self._run_data[0]['total_time'], (int, np.integer)):
            raise ex.LimonadeMetadataSetError('Invalid type for total time in metadata!')
        return self._run_data[0]['total_time']

    @total_time.setter
    def total_time(self, value):
        if not isinstance(value, (int, np.integer)):
            raise ex.LimonadeMetadataSetError('Invalid type given for total time!')

        if not self.standalone:
            dt = self.parent.get_dead_time()
            for ch in range(len(self._run_data)):
                self._run_data[ch]['total_time'] = value
                self._run_data[ch]['dead_time'] = dt[ch]
                self._run_data[ch]['live_time'] = value * 1e-9 - dt[ch]
        else:
            for ch in range(len(self._run_data)):
                self._run_data[ch]['total_time'] = value
                self._run_data[ch]['live_time'] = float(value * 1e-9 - self._run_data[ch]['dead_time'])

    @property
    def dead_time(self):
        """This is only for standalone Metadata, which cannot access t_cache."""
        #if self.standalone:
        if not isinstance(self._run_data[0]['dead_time'], (float, np.float32)):
            print('The type of metadata in _run_data:', type(self._run_data[0]['dead_time']))
            raise ex.LimonadeMetadataSetError('Invalid type for dead time in metadata!')
        ldata = len(self._run_data)
        dt = np.zeros((ldata,), dtype='float')
        for ch in range(ldata):
            dt[ch] = self._run_data[ch]['dead_time']
        return dt
        #else:
        #    raise ex.LimonadeMetadataError('Attempted to access timing data via Metadata! Use t_cache instead.')

    @dead_time.setter
    def dead_time(self, value):
        """This is only for standalone Metadata, which cannot access t_cache."""
        # a killer here, json fails to handle numpy floats, so these will have to be cast to python floats
        #if self.standalone:
        ldata = len(self._run_data)
        for ch in range(ldata):
            self._run_data[ch]['dead_time'] = float(value[ch])
            self._run_data[ch]['live_time'] = float(self._run_data[ch]['total_time'] * 1e-9 - value[ch])
        #else:
        #    raise ex.LimonadeMetadataError('Attempted to set timing data via Metadata! Use t_cache instead.')

    @property
    def live_time(self):
        return [float(self.total_time * 1e-9 - self.dead_time[ch]) for ch in range(self.num_ch)]

    @property
    def events(self):
        return self._run_data[0]['events']

    @events.setter
    def events(self, value: np.uint64):
        for i in range(len(self._run_data)):
            self._run_data[i]['events'] = value

    @property
    def input_counts(self):
        ldata = len(self._run_data)
        i_c = np.zeros((ldata,))
        for i in range(ldata):
            i_c[i] = self._run_data[i]['input_counts']
        return i_c

    @input_counts.setter
    def input_counts(self, value):
        ldata = len(self._run_data)
        for i in range(ldata):
            self._run_data[i]['input_counts'] = value[i]

    @property
    def counts(self):
        ldata = len(self._run_data)
        i_c = np.zeros((ldata,))
        for i in range(ldata):
            i_c[i] = self._run_data[i]['counts']
        return i_c

    @counts.setter
    def counts(self, value):
        ldata = len(self._run_data)
        for i in range(ldata):
            self._run_data[i]['counts'] = value[i]

    @property
    def run_id(self):
        return self._run_data[0]['run_id']

    @run_id.setter
    def run_id(self, value: str):
        for i in range(len(self._run_data)):
            self._run_data[i]['run_id'] = value

    @property
    def name(self):
        return self._run_data[0]['name']

    @name.setter
    def name(self, value: str):
        for i in range(len(self._run_data)):
            self._run_data[i]['name'] = value

    @property
    def notes(self):
        return self._run_data[0]['notes']

    @notes.setter
    def notes(self, value: str):
        for i in range(len(self._run_data)):
            self._run_data[i]['notes'] = value

    def load(self, apath, aname)->None:
        """
        Loads metadata from a json file. 

        In case of chainloaded data, all metadata is loaded one by one using this method. The loading is controlled by 
        the Data class via the _join method, so here we always load a single file and return it. The loader supports 
        standalone data. 

        :return:    None

        """
        metadata = []
        try:
            for ch_idx in range(self.num_ch):
                metadata.append(ut.read_channel_metadata(apath, aname, ch_idx))

        except FileNotFoundError as e:
                print('No metadata found, please run calculate.')
                raise ex.LimonadeMetadataError('Metadata file not found!')
        self.set_from_dict(metadata)

    def set_from_dict(self, metadata: list):
        required_fields = set(self.metadata_proto.keys())
        self.num_ch = len(metadata)
        self._run_data = []
        for ch_idx, ch_meta in enumerate(metadata):
            if required_fields <= ch_meta.keys():  # required fields is subset of what is loaded

                self._run_data.append(misc.desanitize_json(ch_meta))
            else:
                print('Set metadata fails.')
                raise ex.LimonadeMetadataSetError('Incomplete metadata!')

    def dump(self):
        """
        Dumps the metadata as a list of dictionaries.
        """
        temp_data = self._run_data.copy()

        return temp_data


    # This is necessary method, but will only be invoked after the (possible) chain loading of data is complete.
    # It is also called during the run of OnlineData, but never with a time slice. Therefore the reference to
    # data_dict does not get used. 
    def calculate_slice(self, t_slice: Optional[Sequence] = None) -> list:
        """
        Calculate metadata for a given time slice and return it as a list of dictionaries. OnlineData is only ever 
        plotted by SimplePlot, which always uses None for t_slice.

        """
        if self.standalone:
            raise ex.LimonadeMetadataError('Attempted calculations with a standalone instance of Metadata!')

        if t_slice is None:  # return full metadata if full time was given
            return self._run_data
        elif t_slice[0] == 0 and t_slice[1] >= self.total_time:  # return full metadata if full time was given
            return self._run_data
        else:
            # ddict = self.parent.data_dict
            # The time in ns
            delta = t_slice[1] - t_slice[0]
            # the data indices for the interval
            inds = self.parent.t_cache.get_indices(t_slice)
            temp_data = []
            # Here we need to loop through the bloody data from all files to get the counts.
            # Events we could get from the indices, but it is just the same to use the looping.
            counts = 0
            input_counts = 0
            events = 0
            while True:
                blk, isdata = self.parent.get_data_block(t_slice)
                nrgy = blk['energy']
                input_counts += np.count_nonzero(nrgy >= 0, axis=0)
                counts += np.count_nonzero(nrgy > 0, axis=0)
                events += nrgy.shape[0]
                if not isdata:
                    break
            events = inds[1] - inds[0]  # ddict['time'].shape[0]
            #name = self.parent.name
            name = self.name
            #run_id = self.parent.base_name
            run_id = self.run_id
            #if self.start is None:
            #        ex.LimonadeMetadataError('Cannot slice an unstarted measurement!')
            start = self.start + dt.timedelta(seconds=t_slice[0] / 1e9)
            #if self.stop is None:
            #        ex.LimonadeMetadataError('Cannot slice an ongoing measurement!')
            stop = min(self.stop, self.start + dt.timedelta(seconds=t_slice[1] / 1e9))

            # next line seems to make no sense, but there are cases, when end of time slice can be bigger than the
            # largest timestamp. In that case the value needs to be taken from the total time and start of slice
            total_time = min(delta, self.total_time - t_slice[0])
            live_time = self.parent.t_cache.get_live_time(t_slice)
            dead_time = self.parent.t_cache.get_dead_time(t_slice)

            for ch in range(self.parent.num_ch):
                temp_data.append(dict())
                # basic data shared by all channels
                temp_data[-1]['name'] = name
                temp_data[-1]['run_id'] = run_id
                temp_data[-1]['counts'] = counts[ch]
                temp_data[-1]['input_counts'] = input_counts[ch]
                temp_data[-1]['events'] = events
                temp_data[-1]['total_time'] = total_time
                temp_data[-1]['live_time'] = live_time[ch]
                temp_data[-1]['dead_time'] = dead_time[ch]
                # Start and stop times need to be set
                temp_data[-1]['start'] = start
                temp_data[-1]['stop'] = stop
                
                temp_data[-1]['notes'] = self.notes + 'Sliced from {} s to {} s. '.format(t_slice[0] / 1e9,
                                                                                          t_slice[1] / 1e9)
                # maintain special metadata
                for kw in self._run_data[ch]:
                    if kw not in self.metadata_proto.keys():
                        temp_data[-1][kw] = self._run_data[ch][kw]
            return temp_data

    def set(self, key, value, channel):
        """
        Set an extra metadata item for one or all channels. For example some sample related information can be retrieved from
        database and added to metadata after the data is created. This method exists to give easy access to
        metadata for the loader functions of vendor specific data. This method should not be used to set the
        minimal metadata handled by the properties of Metadata class. LimonMetadataSetError is raised if even tried.

        :param key:     Key to _run_data dict
        :param value:   A value to set. If setting all channels, same value will be used for all channels or a list of 
                        values can be given
        :param channel: Channel to modify. If channel is less than 0, then all channels are updated.

        :return:

        """
        if key in self.metadata_proto.keys():
            raise ex.LimonadeMetadataSetError('Set method received a key that is handled as a property!')

        if channel < 0:
            for ch_idx in range(len(self.parent.ch_list)):
                if isinstance(value, (list, tuple)):
                    self._run_data[ch_idx][key] = value[ch_idx]
                else:
                    self._run_data[ch_idx][key] = value
        else:
            self._run_data[channel][key] = value

    def get(self, key, channel):
        """
        Get a metadata item that is not one of the properties. This is simply wrapping the dict indexing.

        :param key: keyword to get
        :param channel: Channel. If channel is less than 0, then all channels are returned.
        :return: value
        """
        if key in self.metadata_proto.keys():  
            raise ex.LimonadeMetadataSetError('Get method received a key that is handled as a property!')
        if channel < 0:
            return [self._run_data[ch][key] for ch in range(self.num_ch)]
        return self._run_data[channel][key]

    def extra_data(self):
        """
        Returns a list of any extra keywords not handled by properties (i.e. the mandatory metadata). Only first 
        channel is searched for extra keys. As a rule of thumb the extra data should be the same all across. 
        """
        extras = []
        for key, value in self._run_data[0].items():
            if key not in self.metadata_proto.keys():
                extras.append(key)
        return extras

    def add(self, meta_in)->None:
        """
        Adds a standalone metadata instance into main metadata. Some metadata items, such as counts, can be
        combined very easily, but some will not be as simple. Here are guidelines:

        - Run_id will be appended as strings
        - Name will never change, it is the detector configuration name which is the same for all datafiles
        - All counts and events will be added together.
        - Notes are appended as strings
        - Start is the start of the first file, Stop is taken from the meta_in. If there is an overlap 
          between Stop of original and Start of meta_in an error is raised.
        - Time data needs to be calculated after merge, hence Data._join should run metadata combination
          as last step.
        - collection info and other extra fields, if present, are taken from first file.

        """
        if self.standalone:
            raise ex.LimonadeMetadataError('Attempted to combine metadata into a standalone instance!')

        # go through the mandatory stuff in prototype manually, then add possible extras
        num_ch = len(self._run_data)
        self.run_id = self.run_id + ' ' + meta_in.run_id
        self.notes = self.notes + ' ' + meta_in.notes
        self.events = self.events + meta_in.events
        if self.initialized:
            if self.stop > meta_in.start:
                raise ex.LimonadeMetadataSetError('Attempted to combine overlapping data.')
        else:
            self.start = meta_in.start
        self.stop = meta_in.stop
        self.input_counts = self.input_counts + meta_in.input_counts
        self.counts = self.input_counts + meta_in.input_counts

        # Any extra keys present in the first channel of metadata in meta_in are added to _run_data. If a given key
        # already exists, it is not replaced
        for key in meta_in.extra_data():
            if key not in self._run_data[0]:
                self.set(key, meta_in.get(key, -1), -1)


class DataStore:
    """
    DataStore is responsible of holding all data of opened datafiles and of maintaining a sort of hash 
    table so that Data.get_data_block can easily traverse through all the data. t_cache has a mapping between 
    time and indices, so it is enough for DataStore to know the event indices of the file transitions.
    Timestamps in t_data are immutable, so time offsets are added on the go as data is requested.

    DataStore is totally data agnostic with regard to number of channels, types of data in the dict etc. Only 
    the index variable needs to be accessed for each data_dict.

    """

    def __init__(self, index_var, block_size=1000000):
        """
        The data block that is returned is preallocated. It may need to be copied when returned, because both
        dictionary and numpy arrays are mutable. If data keeps changing we might run into errors that are impossible to
        debug.

        Anyhow, the way it is working now, there is no parallelism, so the data should be processed sequentially and
        be safe of mutability induced errors.

        The whole class should be able to work with the following data members.

        _store:         List of data_dicts.
        _index_table:   True index to the first element of the each datafile is saved into _index_table.
                        Index of the first datafile is of course 0, always, but the list is initialized as
                        zero length.
        _t_offsets:     The offset, in ns, of each data file relative to the start of datataking. Again first
                        offset will be 0, but the list is initialized as zero length
        size:           Number of datafiles loaded into the DataStore. Last file index in _index_table is 
                        size - 1. This is a property.
        max_t:          Last timestamp of the last datafile corrected with the last _t_offset. This is a 
                        property.
        num_evt:        Number of events (last true index + 1) in the data. This is a property.
         
        """
        self.index_var = index_var
        self._block_size = block_size
        self._index_table = np.zeros((0,), dtype='uint64')
        self._t_offsets = np.zeros((0,), dtype='uint64')
        self._store = []
        self._block = dict()
        self._multi_file = False  # used to skip multi-file code when only one file is loaded. This is likely the
                                 # most often used case.


    @property
    def size(self):
        return len(self._store)

    @property
    def max_t(self):
        try:
            return int(self._store[-1][self.index_var][-1] + self._t_offsets[-1])

        except IndexError as e:
            #print('Error in max_t', e)
            return 0

    @property
    def num_evt(self):
        try:
            return int(self._store[-1][self.index_var].shape[0] + self._index_table[-1])
        except IndexError as e:
            #print('Error in num_evt', e)
            return 0

    def add(self, data_dict, t_offset):
        """
        :param data_dict:   The data dict.
        :param t_offset:    The time gap between the files, in ns. This is the time gap between previous
                            stop time and consecutive start time and has to be added explicitly into t_offsets
                            value to make the timestamps match the real data.
        """
        if len(self._store) == 0:  # first datafile
            print('############## start DATASTORE')
            self._t_offsets = np.append(self._t_offsets, 0)
            self._index_table = np.append(self._index_table, 0)
            self._store.append(data_dict)  # size increased by 1
            for name, item in data_dict.items():
                item_shape = list(item.shape)
                item_shape[0] = self._block_size
                self._block[name] = np.zeros(item_shape, dtype=item.dtype)

        else:
            print('############## ADD IN DATASTORE')
            self._multi_file = True
            self._t_offsets = np.append(self._t_offsets, self.max_t + t_offset)
            self._index_table = np.append(self._index_table, self.num_evt)
            self._store.append(data_dict)  # size increased by 1


    def get(self, idx, data_type):
        """
        Access a single data entry by its index.
        """
        file_idx, event_idx = self._get_idx(idx)
        return self._store[file_idx][data_type][event_idx]

    def get_block(self, start, stop):
        """
        The get_block method returns all data between start and stop indices as a data dict. It is primarily called by
        get_data_block of Data class. The caller is responsible of querying a valid data block (indices falling between
        zero and num_evt).

        """

        if not self._multi_file:

            # Simple case, when full block is retrieved
            if stop - start < self._block_size or stop >= self.num_evt:
                # Cannot reuse self._block if the queried range is smaller than block_size
                # This should only happen in the end of time_slices or in the end of file.
                block = dict()
                for name, item in self._store[0].items():
                    block[name] = item[start:stop, ...]
                return block
            elif stop < self.num_evt:  # reusing the arrays in _block
                for name, item in self._store[0].items():
                    self._block[name][:stop-start, ...] = item[start:stop, ...]
                return self._block

        else:
            # On multi_file case we need more calculations.
            # Absolute start and stop indices are known. Now each file on the range is looped through and data is
            # concatenated into a big block. Time values are corrected with _t_offsets.

            # There are several cases that need to be handled separately:
            # 1. Both indices are in the same file, but not truncated by end of data: Simple case
            # 2. Indices span several files, not truncated: Need to fill block on several loop iterations
            # 3. Indices span several files, but there are less events than the block_size: concatenate to temp block
            # 4. Both indices in last file, less events that the block_size: fill to temp block

            start_f_idx, start_e_idx = self._get_idx(start)
            # A bit of gymnastics is needed for the stop index though. The end of range is always one past the last idx
            # so that we actually need to ask for idx of stop -1 and return one past the value, as it is the stop idx.
            stop_f_idx, stop_e_idx = self._get_idx(stop - 1)
            stop_e_idx += 1

            if start_f_idx == stop_f_idx:  # Cases 1 and 4
                if stop < self.num_evt:  # Case 1
                    # Simple case, when full block is retrieved
                    for name, item in self._store[start_f_idx].items():
                        self._block[name][:, ...] = item[start_e_idx:stop_e_idx, ...]
                    return self._block
                else:  # and 2
                    # Last block is probably smaller than the block size. Redoing the dict
                    block = dict()
                    for name, item in self._block.items():
                        block[name] = item[start_e_idx:stop_e_idx, ...]
                    return block

            block = dict()   # for Case 3
            first = True

            cur_idx = 0
            idx1 = 0
            for file_idx in range(start_f_idx, stop_f_idx + 1):  # cases 2 and 3
                # Calculating indices for current file
                if file_idx == start_f_idx:
                    idx1 = start_e_idx

                if file_idx == stop_f_idx:  # idx 2 is the last idx in the file
                    idx2 = stop_e_idx
                elif file_idx == self.size - 1:  # this should never fire though
                    # last file has no entry for the next file, so index is (last event) - (event at start of file).
                    # todo: make so that the index lists have size + 1 entries, with last giving
                    # the max_t, num_evt values
                    raise
                    idx2 = int(self.num_evt - self._index_table[file_idx])
                else:
                    # or taken from _index table at the start of next file
                    idx2 = int(self._index_table[file_idx + 1] - self._index_table[file_idx])
                delta = idx2 - idx1

                if stop < self.num_evt:  # Case 2
                    for name, item in self._store[file_idx].items():
                        if name == 'time':
                            item = item + self._t_offsets[file_idx]
                        self._block[name][cur_idx:cur_idx + delta, ...] = item[idx1:idx2, ...]
                else:  # Case 3
                    if first:
                        for name, item in self._store[file_idx].items():
                            if name == 'time':
                                item = item + self._t_offsets[file_idx]
                            block[name] = item[idx1:idx2, ...]
                            first = False
                    else:
                        for name, item in self._store[file_idx].items():
                            if name == 'time':
                                item = item + self._t_offsets[file_idx]
                            block[name] = np.concatenate((block[name], item[idx1:idx2, ...]), axis=0)
                cur_idx += delta

            if stop < self.num_evt:
                return self._block
            else:
                return block

    def _get_idx(self, idx):

        if idx == 0:  # needs to be checked separately and is probably most commonly used
            file_idx = 0
        elif idx > self._index_table[-1]:  # in the last file beyond _index_table
            if idx >= self.num_evt or idx < 0:  # If we overflow the whole thing
                print('===== Index error in DataStore get idx')
                print('Asked for index', idx)
                print('Only have', self.num_evt, 'events!')
                raise ex.LimonadeDataStoreError('Index outside acceptable range!')
            file_idx = self.size - 1  # self._index_table[-1]
        else:
            # Next line returns -1 if idx = 0 and 0 if idx is in the last file. These were
            # checked earlier. Feel free to improve!
            file_idx = np.argmax(idx < self._index_table) - 1
        event_idx = int(idx - self._index_table[file_idx])

        return file_idx, event_idx


class Data:
    """
    Sort of generic data class, with plug-in dataloader for vendor specific raw data
    and extra data items configurable via configuration file.

    All data is defined by info-dictionaries that are of the form:
    info_dict = {"name": "some_data",
                "type": "u1",
                "num_col": 2,
                "aggregate": "col",
                "ch_mask": [1, 1, 0, 0],
                "multi": "mean"}

    Data is held in a data dictionary, with data name as key and the data as the value. All data is stored in
    numpy memmaps. The data dict always contains indexing variable and primary data, e.g. time
    and energy information of events. Primary data is by default the first member of the "datas" list in the
    configuration file, but can be set up differently using the "primary_data" keyword giving the index.

    Data dict can contain extra data, defined by additional entries in 'datas' list of info dicts in the configuration
    file. Few types of extra data are hardcoded into limonade and are handled in a special way if they are present:
    coord:  coordinate information. Correspondence of channels to coordinate columns is given by the data mask in its
    respective info_dict. This is used for data selection and plots.

    latency:timing information. Each column is the time difference between 'main' channel and other channels in the
            event. Used to tune the latency and coincidence window.

    multihit: A flag that is raised if a channel has several hits per event. A type of nondestuctive pileup. The
            energy value of a multihit event is calculated using a function defined by the 'multi' keyword.

    All other data is just loaded from disk and can be plotted or used for event selection.

    Indexing variable (e.g. timestamp or index number) has to be present in all kinds of data. It stores the event
    index and is needed for ordering the data. Index variable has to be monotonically increasing and of an integer type.
    Coincidences are calculated using the index variable of the data and a coincidence window used to detect
    simultaneous events in all channels. The index_variable has an optional calibration factor (for example from a tick
    value into nanoseconds). It is handled in a special way by limonade. It is defined with similar info dict, but only
    uses following keywords:

    "index_info": {"name": "time",
                   "type": "u8",
                   "raw_unit": "tick",
                   "unit": "ns",
                   "cal": 10}
    """
    
    def __init__(self, config):
        """
        Configuration file contains a recipe to the data and is loaded on the beginning of the creation of the data.
        All data structures, time cache and metadata are created here, but the data is still empty and has to be loaded
        with load_data-method.

        :param config: A pathlib path to detector configuration file or the configuration dict itself.

        """
        self.listmode = True  # A full limonade Data-class with full functionality.
        # do init stuff
        self.config = config
        self.name = config.det['name']
        try:
            self.primary_data = config.det['datas'][config.det['primary_data']]['name']  # get primary data name
        except KeyError:
            self.primary_data = config.det['datas'][0]['name']  # first data is the default
        self.index_data = config.det['index_variable']['name']
        self.data_type = self.config.det['data_type']
        # initializing correct raw data loader
        self.data_model = ldr.loader_dict[self.config.det['data_type']](self)

        self.chunk_size = 1000000
        print('Loading data', config.det['data_type'])

        # detector init
        self.num_ch = len(self.config.det['ch_cfg'])

        # this should only be used to map loader channels into native format consecutive channels.
        self.ch_list = self.config.det['ch_list']

        # init data_store
        self._data_store = DataStore(block_size=self.chunk_size, index_var=self.index_data)
        # init time cache
        self.t_cache = TimeCache(self)
        # init metadata
        self.metadata = Metadata(self)

        self.chunk_idx = 0  # for block based data processing


    def _join(self, data_dict, timing_data, metadata):
        """
        Data is added to master data_dict and t_cache is updated.

        :param data_dict:   data_dict
        :param timing_data: timing data
        :param metadata:    metadata
        :param first:       timing data

        :return:            None

        """
        stop = self.metadata.stop
        if stop is not None:
            start = metadata.start
            if start < stop:
                raise ex.LimonadeMetadataError("Overlap in datafile times!")
            gap = int((start - stop).seconds*1e9)
        else: 
            gap = 0
        self._data_store.add(data_dict, gap)
        self.t_cache.add(timing_data, gap)
        self.metadata.add(metadata)
        # recalculate timing to take the 
        self.metadata.total_time = self.t_cache.get_total_time()  # set total time to update dead time
        # self.metadata.dead_time = self.t_cache.get_dead_time()

    def get_num_events(self):
        return self._data_store.num_evt
    
    #def load_data(self, data_path_str, name=None, reset=False):
    def load_data(self, paths: Sequence, names: Sequence, reset: bool=False)->None:
        """
        Loads data preferably from event mode .dat files. If this fails, then channel data is searched for. (Channel
        data may be saved as intermediary step when doing slow conversion from other data formats.) Otherwise
        data_model.loader method is called. Native format has no raw data and will fail.

        :param paths: List of Path objects to chainloaded data directories. 
        :param names: Base name of the data file.
        :param reset: The raw data parsing can be forced with reset=True.
        
        :return:

        """
        #if len(paths) > 1:
        #    raise NotImplementedError('Received multiple data paths. Chainloading is not implemented.')
        self.paths = paths
        self.names = names

        # loop through the rest of the data files
        first = True
        for idx, apath in enumerate(paths):
            data_path = apath 

            # check that path and files exist
            loaded = False
            if not data_path.is_dir():
                raise ValueError("Invalid data_path in read data!")

            base_name = names[idx]

            if not reset:
                try:
                    # check if base_name has an event mode datafile and load it.
                    print('Trying to read parsed data', data_path, base_name)
                    data_dict, timing_data = read_binary_data(data_path, base_name, cfg=self.config, mode='event')
                    metadata = Metadata(None, self.num_ch)
                    try:
                        print('trying to read metadata')
                        metadata.load(data_path, base_name)
                    except ex.LimonadeMetadataError:
                        print('Could not find metadata in event mode load!')
                        raise
                    print('After metadata reading')
                    # self.t_cache.set(timing_data)
                    self._join(data_dict, timing_data, metadata)
                    loaded = True
                except ex.LimonadeDataNotFoundError:
                    print('Cannot find parsed data')
                except:
                    print('Event data load failed!')
                    raise

                if not loaded:
                    try:
                        # check if base_name has channel datafiles and load them. (Rerunning coincidence
                        # parsing can be done quickly by deleting the event file!)
                        # Otherwise set reset to True and proceed.
                        print('Trying to read channel data', data_path, base_name)
                        data_dict, timing_data = self._load_channel_data(data_path, base_name)
                        metadata = Metadata(None, self.num_ch)
                        metadata.load(data_path, base_name)
                        self._join(data_dict, timing_data, metadata)
                        loaded = True
                    except ex.LimonadeDataNotFoundError:
                        print('Cannot find channel data in Data.load_data!')
                        #metadata = Metadata(None, self.num_ch)
                        #metadata.load(data_path, base_name)
                        raise
                    except:
                        print('Channel data load failed in Data.load_data!')
                        raise



                if not loaded:
                    if self.data_type == 'standard':  # there is no raw data for standard data
                        raise FileNotFoundError('No files found for native format data')
                    reset = True  # Triggering raw data loader

            if reset:
                print('Data reset!')
                # Read raw data
                try:
                    print('Reading raw data')
                    # loader is responsible for converting raw data to channel data, parsing it and providing
                    # metadata if it is missing
                    data_dict, timing_data = self.data_model.loader(data_path, base_name)
                    metadata = Metadata(None, self.num_ch)
                    metadata.load(data_path, base_name)
                    self._join(data_dict, timing_data, metadata)
                    loaded = True
                except FileNotFoundError:
                    print('No raw data!')
                    print(data_path)
                    print('Exit!')
                    raise

            # Finally, if the load went well, the base name and path are added into config
            if first:
                self.config.path['paths'] = [data_path]
                self.config.path['names'] = [base_name]
                first = False
            else:
                self.config.path['paths'].append(data_path)
                self.config.path['names'].append(base_name)

    def get_data(self, data_type: str, idx1: int, idx2: Optional[int]=None):
        """
        Get a single entry or a slice of a single data_type from _data_store 
        """
        if idx2 is None:
            return self._data_store.get(idx1, data_type)
        else:
            return self._data_store.get_block(idx1, idx2)[data_type]


    def get_data_block(self, t_slice=None):
        """
        Get data and time vectors, but processed in chunks of self.block_size events to save memory. Optionally, define
        a slice in time. The method should be called in a loop to read everything. All data is returned.

        Last return value isdata indicates if there is more data to come. On a False the loop should be stopped, but
        the last data is still valid.

        :param t_slice: A tuple of start and stp times in nanoseconds. Full data is set to be read if this is None. The
                        time slice should never be changed while reading the data in a loop.

        :return:  A tuple of (data_dict, isdata) for current chunk.

        """

        # chunk_size = 1000000
        events = self._data_store.num_evt

        start, stop = self.t_cache.get_indices(t_slice)

        num_chunks = (stop - start) // self.chunk_size

        if self.chunk_idx < num_chunks:
            isdata = True  # data left
        else:  # self.chunk_idx == num_chunks - 1:  # last chunk
            isdata = False  # last chunk

        idx1 = int(start + self.chunk_idx * self.chunk_size)
        idx2 = min(stop, int(start + (self.chunk_idx + 1) * self.chunk_size), int(events))
        
        # Fetch the block from data_store. This is already a pure dict of numpy data - no memmaps
        block = self._data_store.get_block(idx1, idx2)
        if t_slice is not None:
            mask = np.logical_and(block[self.index_data] > t_slice[0],
                                  block[self.index_data] < t_slice[1])
        else:
            mask = np.ones((block[self.index_data].shape[0],), dtype='bool')

        #retdict = dict()
        for name, item in block.items():
            block[name] = item[mask, ...]

        if isdata:
            self.chunk_idx += 1
        else:
            self.chunk_idx = 0

        return (block, isdata)

    def get_dead_time(self, t_slice=None):
        """
        Get dead time for the data or a time_slice of data.

        :param t_slice: a tuple of start and stop times in nanoseconds. Full dead time is retrieved if this is set to
                        None.

        :return: The dead times in [s] for all channels as a vector of floats.

        """
        deltat = np.zeros((len(self.ch_list)))
        if t_slice is None:  # currently implemented
            timing = self.t_cache.timing
        else:  # not implemented
            timing = self.t_cache.get_timing(t_slice)
        for ch in range(len(self.ch_list)):
            deltat[ch] = timing['dt{}'.format(ch)].sum()

        return deltat

    def get_end_time(self):
        """ 
        The timestamp value of the last event. It is taken from data store directly. The t_chache should use this
        method to check its internal values are ok.
        """
        return self._data_store.max_t

    def _parse_on_load(self, data, path, basename):
        """
        For parsing events from channel mode files in batches to conserve memory.

        :param data: a tuple of (list of data_dicts, list of timing_datas).
        :param basename: The basename of the data.

        :return:
        """
        #batch_size = 100000
        batch_size = 10000
        data_list, timing_data = data

        if self.num_ch > 1:  # Go through the hoops only, if multi-channel data
            print('Allocating event file streamers!')
            # Chainloading changes the logic of this, as the data of each file is streamed to its own home directory.
            index_streamer = StreamData(path, basename, raw=False, data_name=self.index_data,
                                        method='data')
            timing_streamer = StreamData(path, basename, raw=False, data_name='timing',
                                         method='timing')

            # ugly fix for the stupid zero entries in the beginning of channel timing data
            # This does not seem to work though. There's a double line of zeroes in the beginning of timing data.
            for td_idx in range(len(timing_data)):
                if timing_data[td_idx]['idx'][0] == 0:  # if this fires, we are at the beginning of data. It should!
                    timing_data[td_idx] = timing_data[td_idx][1:]
            timing_streamer.write(np.zeros((1,), dtype=[('idx', 'u8'), ('t', 'u8')] +
                                                       [('dt{}'.format(x), 'f4') for x in range(len(timing_data))]))

            datas = self.config.det['datas']

            data_streamers = dict()

            for data in datas:
                data_streamers[data['name']] = StreamData(path, basename, raw=False, method='data', data_name=data['name'])

            # Time vector, or data_tuple[ch_idx][self.index_data], is used for parsing. The data is pushed to EventBuilder in
            # batches of constant time, but not exceeding max_datasize in length.
            chlist = np.array(range(self.num_ch), dtype='u1')  # used to retrieve indices through boolean indexing
            idx0_front = np.zeros((len(self.ch_list),), dtype='u8')  # start indices for batch
            idx1_front = np.zeros_like(idx0_front)  # stop indices for batch
            # set data_left for beginning
            idx_max = np.array([x[self.index_data].shape[0] for x in data_list], dtype='u8')  # the last indices of data
            data_left = idx0_front < idx_max

            # current timestamps
            # Empty channels must be handled separately or hilariousness ensues.
            t_front = np.zeros((self.num_ch,), dtype='u8')
            for live_ch in chlist[data_left]:
                t_front[data_left] = data_list[live_ch][self.index_data][idx1_front[live_ch]]

            # event builder is supposed to be an online function, so doing it posthumously is unnecessarily complicated...
            ev_bldr = EventBuilder(self.config, max_datasize=batch_size)

            # Loop through the data. Chop everything into equal time chunks by finding channel with highest rate and
            # selecting max_datasize events from that channel. Include other channels up to same time
            while np.any(data_left):
                try:
                    # next batch end idx in all channels
                    idx1_front[data_left] = [min(idx_max[x], idx0_front[x] + batch_size) for x in chlist[data_left]]
                    # corresponding timestamps, idx1_front points to one past the last index in the chunk
                    t_front[data_left] = [data_list[x][self.index_data][int(idx1_front[x]-1)] for x in chlist[data_left]]
                except:
                    print('exception in t_front calc')
                    raise

                events_left = idx_max - idx0_front
                print('left   :', events_left)

                mask = events_left > batch_size  # mask the channels which have more counts than the current batch
                if np.any(mask):
                    # pick the active channel with smallest timestamp at batch end. Here we have to take into account
                    # that some channels may already be done for. Hence the data_left tricks.
                    lead_ch = chlist[data_left][t_front[data_left].argmin()]
                else:
                    # when data is about to end we take one more step. We pick the channel with biggest timestamp
                    lead_ch = t_front.argmax()
                lead_t = t_front[lead_ch]

                full_data = [None for _x in range(len(self.ch_list))]
                ch_timing = [[] for _x in range(len(self.ch_list))]
                # Then find the same (or smaller) time for all active channels and cut the batch there
                for ch_idx in chlist:  # we go through empty channels too to provide empty data for event builder.
                    ch_data = dict()
                    if data_left[ch_idx]:

                        if ch_idx != lead_ch:
                            # easy way of finding the last timestamp under lead_t. Return value is number of events
                            # to include from the chunk, or the index +1
                            # of the last event in the chunk that passes the test <= lead_t.
                            # The test fails if all timestamps are smaller (0 returned, should not happen as lead_ch
                            # is smallest)
                            # or the last timestamps are equal (0 returned, unlikely but possible). Zero is returned
                            # also when all time stamps are more than lead_t. This is correct behaviour.

                            temp = np.argmin(
                                data_list[ch_idx][self.index_data][idx0_front[ch_idx]:idx1_front[ch_idx]] <= lead_t)
                            # debug
                            if temp == 0:

                                if data_list[ch_idx][self.index_data][idx0_front[ch_idx]] > lead_t:
                                    # the time of the first event in the chunk is bigger than the end time
                                    # of the chunk. Empty chunk so temp is correct!
                                    print('!"!"!"!"!"!"! correct temp 0')
                                    pass
                                elif data_list[ch_idx][self.index_data][int(idx1_front[ch_idx] - 1)] == lead_t:
                                    # last event in batch is shared between several channels
                                    temp = int(idx1_front[ch_idx] - idx0_front[ch_idx])
                                    print('oooooooo incorrect temp0')
                                elif data_list[ch_idx][self.index_data][int(idx1_front[ch_idx] - 1)] < lead_t:
                                    # last index is less than lead_t -> crash!
                                    temp = int(idx1_front[ch_idx] - idx0_front[ch_idx])
                                    if idx1_front[ch_idx] < idx_max[ch_idx]:  # Check if data left
                                        raise ex.LimonadeTimestampError('Last timestamp is less than lead_t but data is left!')
                                else:
                                    raise
                            # correct idx1 front
                            idx1_front[ch_idx] = idx0_front[ch_idx] + temp
                    else:
                        print('Empty channel!')
                        print('tfronts', idx0_front, idx1_front)
                        print('idx max', idx_max)
                        print('data left', data_left)
                        # correct idx1 front
                        #idx1_front[ch_idx] = idx0_front[ch_idx]
                        #raise

                    # timing data sliced by (idx)
                    timing_mask = np.logical_and(timing_data[ch_idx]['idx'] >= idx0_front[ch_idx],
                                                 timing_data[ch_idx]['idx'] < idx1_front[ch_idx])
                    temp_extra = []

                    # build batch.
                    for basename, value in data_list[ch_idx].items():
                        # ch_data[name] = value[idx0_front[ch_idx]:idx1_front[ch_idx]]
                        # testing sending full copies to the parser so that disc reads are not needed anymore.
                        # Might increase performance with USB disks
                        ch_data[basename] = value[idx0_front[ch_idx]:idx1_front[ch_idx]].copy()
                    full_data[ch_idx] = ch_data

                    ch_timing[ch_idx] = timing_data[ch_idx][timing_mask]

                ev_data_dict, ev_timing = ev_bldr.run_batch(full_data, ch_timing)

                # STOP to write the data. It is possible to have no events at all in the  data, so checking if idx
                # is None
                if not ev_data_dict is None:
                    index_streamer.write((ev_data_dict[self.index_data]))
                    for basename in data_streamers.keys():
                        data_streamers[basename].write(ev_data_dict[basename])
                    if len(ev_timing) > 0:
                        timing_streamer.write(ev_timing)

                    idx0_front[data_left] = idx1_front[data_left]
                    # recalculate data_left
                    data_left = idx0_front < idx_max

            # Close the event builder to flush rest of the data
            ev_data_dict, ev_timing = ev_bldr.run_batch(None, None, close=True)

            # STOP
            index_streamer.write((ev_data_dict[self.index_data]))
            for basename in data_streamers.keys():
                data_streamers[basename].write(ev_data_dict[basename])
            if len(ev_timing) > 0:
                timing_streamer.write(ev_timing)

            index_streamer.close()
            timing_streamer.close()
            for ds in data_streamers.values():
                ds.close()

        else:
            # copy original data to event data. Some of the original data may be omitted from parsed (copied) data.
            # In addition, having the debug flag False in the configuration triggers deletion of the original data.
            import shutil
            shutil.copy(path / (basename + '_timing_ch0.dat'.format(self.index_data)),
                        path / (basename + '_timing.dat'.format(self.index_data)))
            for adata in data_list[0].keys():
                shutil.copy(path / (basename + '_{}_ch0.dat'.format(adata)),
                            path / (basename + '_{}.dat'.format(adata)))


    def _load_channel_data(self, data_path: Path, name: str) -> tuple:
        """
        Used to read channel data and parse into events. Channel data for each
        channel can be just measurement or zero-suppressed strip detector data,
        with 1-d coordinates on a separate file.

        Coordinate data is aggregated into final coordinate information (forming
        an n-d coord-data) in the order of channel_cfg vector.

        :param data_path:   self evident
        :param name:        base name of the data file
        :param metadata:    If the data is just loaded from raw files, it needs its metadata set by the loader.
                            Otherwise the metadata is loaded from the data dir.

        :return:            A tuple of data_dict and timing data

        """
        # ch_list is a tuple of (list of ch_data_dicts, list of ch_timing_datas)
        ch_list = read_binary_data(data_path, name, mode='channel', cfg=self.config)
        self._parse_on_load(ch_list, data_path, name)
        del(ch_list)  # free the files. Important due to the possible deletion of channel data.
        data_dict, timing_data = read_binary_data(data_path, name, mode='event', cfg=self.config)

        # Get metadata from disk 
        # metadata = Metadata(None, self.num_ch)
        # metadata.load(data_path, name)

        # data_tuple is made of data_dict and timing data
        #self.data_dict = data_dict
        #self.t_cache.set(timing_data)

        try:
            delete_chfiles = not self.config.det['debug']
        except KeyError:
            delete_chfiles = True

        if delete_chfiles:
            ut.delete_channel_data(data_path, name, self.config)
        return data_dict, timing_data #, metadata


class HistoData(Data):
    def __init__(self, histo_file):
        """
        HistoData loads a csv histogram together with it's metadata. It is greatly simplified version of Data class
        but it still maintains metadata. Time_cache and DataStore are not needed. There is only one histogram,
        naturally, per csv file, but the class is built to handle arbitrary amount of them so that subclasses need only
        to implement the bare minimum of functionality.

        :param histo_file:      Path to the .csv histogram. Can be a string or a Path.
        """
        self.listmode = False  # not a  Data-class. Only partially functional and will be plotted differently.
        import csv
        self.data_list = list()

        # make sure we have Paths
        histo_file = Path(histo_file)

        # first load the metadata and make all the needed setups
        meta_file = histo_file.parent / (histo_file.stem + '.json')
        try:
            with meta_file.open('r') as fil:
                meta_dict = json.load(fil)
        except FileNotFoundError:
            raise ex.LimonadeDataNotFoundError('No metadata found!')
        # set config
        self.config = ut.old_config(meta_dict)
        self.num_ch = len(self.config.det['ch_list'])
        # set metadata
        self.metadata = Metadata(self)
        meta_in = meta_dict['metadata']
        #self.metadata.add(meta_dict)
        self.metadata.run_id = meta_in[0]['run_id']
        self.metadata.notes = meta_in[0]['notes']
        self.metadata.events = meta_in[0]['events']
        self.metadata.start = dt.datetime.fromisoformat(meta_in[0]['start'])
        self.metadata.stop = dt.datetime.fromisoformat(meta_in[0]['stop'])
        # due to stupid implementation of Metadata class, we need to save total data and dead time in the Data class
        # (no t_cache)
        self.total_time = dt.datetime.fromisoformat(meta_in[0]['stop'])

        # ch specific stuff
        input_counts = np.zeros((self.num_ch), dtype='uint64')
        counts = np.zeros((self.num_ch), dtype='uint64')
        dead_time = np.zeros((self.num_ch), dtype=float)
        for ch_idx, ch_meta in enumerate(meta_in):
            input_counts[ch_idx] = ch_meta['input_counts']
            counts[ch_idx] = ch_meta['counts']
            dead_time[ch_idx] = ch_meta['dead_time']

        self.metadata.input_counts =input_counts
        self.metadata.counts = input_counts
        self.dead_time = dead_time

        # extra data
        for key, value in meta_in[0].items():
            if key not in self.metadata.metadata_proto:
                self.set(key, value, -1)

        two_d = len(meta_dict['plot']['plot_cfg']['axes']) == 2

        # and then load the histogram
        try:
            data = []
            with histo_file.open('r', newline='') as fil:
                reader = csv.reader(fil)
                for line in reader:
                    row = [float(x) for x in line]
                    data.append(row)
        except FileNotFoundError:
            raise ex.LimonadeDataNotFoundError('No histogram found!')

        if two_d:
            # make a 2d histo out of bin indices
            x_start, x_stop = meta_dict['plot']['plot_cfg']['axes'][0]['range']
            y_start, y_stop = meta_dict['plot']['plot_cfg']['axes'][1]['range']
            bin_size_x = meta_dict['plot']['plot_cfg']['axes'][0]['bin_width']
            bin_size_y = meta_dict['plot']['plot_cfg']['axes'][1]['bin_width']
            x_start = x_start // bin_size_x * bin_size_x
            x_stop = x_stop // bin_size_x * bin_size_x + bin_size_y
            y_start = y_start // bin_size_y * bin_size_y
            y_stop = y_stop // bin_size_y * bin_size_y + bin_size_y
            histo = np.zeros(((x_stop - x_start)//bin_size_x, (y_stop - y_start)//bin_size_y), dtype=float)
            for entry in data:
                histo[int(entry[0]//bin_size_x-x_start), int(entry[1]//bin_size_y-y_start)] = entry[2]
            bins = (np.arange(x_start, x_stop, bin_size_x),
                    np.arange(y_start, y_stop, bin_size_y))
            self.data_list.append({'histo': np.array(histo), 'bins': bins, 'time_slice': [0, self.total_time]})
        else:
            x_start, x_stop = meta_dict['plot']['plot_cfg']['axes'][0]['range']
            bin_size_x = meta_dict['plot']['plot_cfg']['axes'][0]['bin_width']

            histo = np.zeros(((x_stop - x_start)//bin_size_x,), dtype=float)
            for entry in data:
                histo[int(entry[0]//bin_size_x-x_start)] = entry[1]
            bins = (np.arange(x_start, x_stop, bin_size_x),)
            self.data_list.append({'histo': np.array(histo), 'bins': bins, 'time_slice': [0, self.total_time]})

    def get_dead_time(self):
        return self.dead_time

    def get_end_time(self):
        return self.total_time

    def get_num_events(self):
        return self.metadata.events

    def load_data(self, paths, names):
        raise NotImplementedError()

    def get_data_block(self, t_slice=None):
        """
        Non- version of get data block returns a list of data_dicts. Each data_dict contains a histogram
        ('histo') and bins ('bins'9 for the axes. Time_slice ('time_slice') information is given too, for completeness.
        Time slice is always the full time range of the data.

        :param t_slice:
        :return:
        """

        return self.data_list

    def get_data(self, data_type, idx1, idx2=None):
        raise NotImplementedError()


def poly2(x, *p):
    """
    Model function for 2nd degree polynomial fit for energy calibration.

    :param x: A channel value or a numpy list of channel values.
    :param p: Calibration coefficients, starting from 0th degree coefficient.

    :return: Calibrated x.
    """

    a, b, c = p
    x = np.asarray(x)
    return a + b * x + c * x ** 2


def ipoly2(y, *p):
    """
    Estimates the inverse of 2nd degree polynomial above by dropping the 2nd degree term: returns ~x given y. Here the
    larger root is always returned.

    :param y: An energy value or a numpy list of energy values.
    :param p: Calibration coefficients, starting from 0th degree coefficient.
    :return: Channel values

    """
    y = np.asarray(y)  # cast single numbers to array if needed
    ylim = np.array((y.min(), y.max()))
    c, b, a = p

    if np.abs(a) > 1e-8:  # if it is 2nd deg
        disc = b**2 - 4*a*c
        xapex = -b/(2*a)
        if disc <= 0:

            # no intersection of axis. Only valid if a>0 and all y > xapex or all y < xapex
            if a > 0 and np.all(ylim >= xapex):
                branch = 1
            elif a > 0 and np.all(ylim < xapex):
                branch = -1
            else:
                raise ex.LimonadeCalibrationError('No real solution for inverse y calculation!')
        else:
            # Two roots case
            x0 = (-b - np.sqrt(disc))/(2 * a)
            x1 = (-b + np.sqrt(disc))/(2 * a)
            if a > 0:
                # Only valid if positive and all y over x1 or all y under x0
                if np.all(ylim > x1):
                    branch = 1
                elif np.all(ylim < x0):
                    branch = -1
                else:
                    raise ex.LimonadeCalibrationError('Inverse energy calibration is not unambiguous over the range!')
            else:
                # only valid if positive and between x0 to xapex or xapex to x1

                if np.all(np.logical_and(ylim >= x1, ylim < xapex)):
                    branch = 1
                elif np.all(np.logical_and(ylim >= xapex, ylim < x0)):
                    branch = -1
                else:
                    raise ex.LimonadeCalibrationError('No real solution for inverse y calculation!')

        x = (-b + branch*np.sqrt(b**2 - 4*a*(c-y)))/(2 * a)
    else:
        # linear case
        x = (y - c) / b

    return x


class EventBuilder:
    """
    Painful way of walking through the data and trying to build events
    by seeking coincidences between channel times.

    Ideally works on shortish arrays of data returned by the digitizer, but should manage big savefiles in chunks.

    """

    def __init__(self, cfg, max_datasize=8192):
        """

        :param cfg:          The detector configuration. It is used to set up data-types, coincidence information etc.
        :param max_datasize: size for the internal arrays during parsing, should be the size of the output buffer of the
                             digitizer.
        """
        self.index_var = cfg.det['index_variable']
        self.idx_name = self.index_var['name']
        self.datas = cfg.det['datas']
        self.coinc_win = cfg.det['coinc_win']  # coincidence window length in nanoseconds
        self.latency = np.array(cfg.det['latency'], dtype='int')  # per channel latencies

        # High latency value is needed for data that comes before others.
        # It is a delay for the data stream.
        self.maxwin = self.coinc_win - self.latency  # end of coincidence window in each channel

        self.num_ch = len(cfg.det['ch_list'])  # number of channels in the data
        self.chan_list = np.arange(self.num_ch, dtype='int32')
        self.bit_list = 2**self.chan_list

        self.chmax = np.zeros((self.num_ch,), dtype='uint64')  # max data idx per channel

        self.buffered = True  # cfg.det.get('buffered')  # Use buffering. Temporary - Will be the only way after testing
        if self.buffered is None:
            self.buffered = False
            multiplier = 1
        if self.buffered:
            self.num_buffers = cfg.det.get('num_buffers')
            if self.num_buffers is None:
                self.num_buffers = 2
            # The buffer itself. It holds data_dict, timing_list and channel index
            self.reserve = [[] for _x in range(self.num_ch)]
            multiplier = self.num_buffers

        # timing data
        # variables for individual channel timing arrays
        self.timing_chmax = np.zeros((self.num_ch,), dtype='uint64')  # index of last timing event (per ch)
        self.timing_front = np.zeros((self.num_ch,), dtype='uint64')  # indices to timing front
        # time values of the timing front
        self.timing0 = np.ones((self.num_ch,), dtype='uint64') * np.iinfo(self.index_var['type']).max
        timing_type_prefix = [('idx', '<u8'), ('t', self.index_var['type'])]
        self.ch_timing_type = timing_type_prefix + [('dt0', '<f4')]  # type-str of ch_timing
        # variables for output timing array
        self.timing_data_sz = 2000
        type_list = timing_type_prefix.copy()
        for x in range(self.num_ch):
            type_list.append(('dt{}'.format(x), '<f4'))
        self.timing_data = np.zeros((self.timing_data_sz,), dtype=type_list)

        # index data
        self.index_data = np.zeros((max_datasize * self.num_ch * multiplier,), dtype=self.index_var['type'])
        # create a prototype for a row of data.
        # Index variable and channel exist in every piece of datas though
        in_types = []
        in_names = []
        for adata in self.datas:
            # Filter out data that is created by the EventBuilder
            if adata['name'] not in ut.parsed_extras_list:
                in_types.append(adata['type'])
                in_names.append(adata['name'])
        self.in_type_list = [self.index_var['type'], '<u1'] + in_types
        self.in_name_list = [self.idx_name, 'ch'] + in_names
        # make it a type
        big_type = np.dtype({'names': self.in_name_list, 'formats': self.in_type_list})
        # and init array
        self.big_data = np.zeros((max_datasize * self.num_ch * multiplier,), dtype=big_type)
        # mask to select good data
        self.big_data_mask = np.zeros((max_datasize * self.num_ch * multiplier,), dtype='bool')
        # index in parsed output
        self.final_idx = np.zeros((self.big_data.shape[0],), dtype='int32')

        # Need to take into account that data may be missing on some channels.
        # create name list by channel so that missing data is not queried.
        self.names_by_channel = []
        for ch in range(self.num_ch):
            self.names_by_channel.append([])
            for adata in self.datas:
                if adata['name'] not in ut.parsed_extras_list:
                    if adata['ch_mask'][ch]:
                        self.names_by_channel[ch].append(adata['name'])
        self.t0 = np.zeros((self.num_ch,), dtype='uint64')
        #self.E0 = -1*np.ones((self.num_ch,), dtype='int16')

        self.ev_count = np.zeros((self.num_ch,), dtype='uint64')

        # output part
        self.proc_list = []
        self.out_data = []
        self.out_name_list = []
        self.defaults = []
        self.multihit = False
        self.combi_list = []

        # set output data format

        # out_data is just a list of matrices, one per data. Multihit and index_data are handled separately.
        self.out_name_list = [adata['name'] for adata in self.datas if adata['name'] != 'multihit']

        # init the processors for the data.
        for adata in self.datas:
            if adata['aggregate'] != 'multihit':
                self.proc_list.append(process_dict[adata['aggregate']](adata, max_datasize * self.num_ch * multiplier))
            else:
                self.multihit = True
                self.multihit_out = np.zeros((max_datasize * self.num_ch * multiplier,), dtype=adata['type'])

        # Combinator needs to be defined separately for each channel
        for ch in range(self.num_ch):
            self.combi_list.append([])
            for adata in self.datas:
                if adata['aggregate'] not in ut.parsed_extras_list:  # 'multihit':
                    if adata['ch_mask'][ch]:
                        self.combi_list[ch].append(
                            combinator_factory(adata['multi'], adata['name'], adata.get('other')))

        self.t_front = np.zeros((self.num_ch,), dtype='uint64')  # indices that are compared currently

        self.total_sum = 0  # total accumulated events
        self.ch_total_sum = np.zeros((self.num_ch,), dtype='uint64')  # total number of input counts

        if self.buffered:
            self.run_batch = self._run_batch_buffered
        else:
            self.run_batch = self._run_batch_orig

    def build_big_data(self, data_dict, count, t_front, close=False, force_write=None):
        """
        Setup the batch so that all hits are is rolled as one giant big_data array in rows first order. The big_data
        array, its mask and t0 are manipulated, all other class members are left untouched.

        The big_data should not get too big with small detector sizes: with a 4-channel
        detector with 2 coordinate data axes and 2 kinds of flag data we are running to 8+2+1+1+1 = 13 bytes of data per
        channel hit (need to reserve per maximum requirement) For chunk of 100000 hits (3 full buffers of 10000 for all
        other channels and one for the slowest) we need to reserve 5 700 000 bytes x 4 = 22 800 000 bytes.

        :param data_dict:   Current data
        :param count:       Current count in big_data (idx of the last hit)
        :param t_front:     Current count in each buffer in input.
        :param close:       True if iterating to the end of all data (old behavior) instead of stopping to the last
                            index of slowest channel. Input data is ignored when close=True.
        :param force_write: A list of channels that will be written to the end regardless of slow channels. This is
                            activated if buffer is filled for one or more channels.
        :return:            count, t_front, chan_mask. New count and t_fron values. Chan_mask indicates which channels
                            still have hits (channels with False are used up and new data should be pulled from the
                            reserve).
        """
        # force mask is True on channels that have force write enabled
        force_mask = np.zeros((self.num_ch,), dtype=bool)
        if not force_write is None:  # mark channels that will be run to the end.
            force_mask[force_write] = True

        ch_max = np.zeros((self.num_ch,), dtype='uint64')
        #t_front = np.zeros((self.num_ch), dtype='uint64')

        for ch in range(self.num_ch):
            if not data_dict[ch] is None:
                ch_max[ch] = data_dict[ch][self.idx_name].shape[0]

        chan_mask = t_front < ch_max  # data left
        oldt = 0
        running = True
        while running:
            # go through the hits one by one and insert earliest into big time.

            # Channels that can have data. Should be used every time a channel value is needed via bool indexing
            # (by using chan_mask)
            active_ch = self.chan_list[chan_mask]

            # go through active channels and record current values of time for each channel
            for ch in active_ch:
                self.t0[ch] = data_dict[ch][self.idx_name][t_front[ch]]

            # find channel with smallest t
            chan = active_ch[self.t0[active_ch].argmin()]

            # check for (Caen) timestamp errors. Should be ditched.
            if oldt > self.t0[chan]:
                print(oldt, self.t0[chan])
                print('Gotcha! Timestamp error!')
                raise ex.LimonadeTimestampError("Previous timestamp was bigger!")

            # insert into big list
            self.big_data[(self.in_name_list[:2] + self.names_by_channel[chan])][count] = \
                            tuple([self.t0[chan], chan] + [data_dict[chan][x][t_front[chan]] for x in
                                                                       self.names_by_channel[chan]])
            # Add the event as good data for the channel. The mask is used to select hits by channel.
            self.big_data_mask[count] = True

            oldt = self.t0[chan]
            t_front[chan] += 1
            chan_mask = t_front < ch_max
            count += 1
            if close:
                running = np.any(chan_mask)
            else:
                # run to the end of channels in force mask. If Force mask is empty, run to the last hit of the current
                # buffer of the slowest channel
                running = np.all(chan_mask) or np.any(chan_mask[force_mask])

        return count, t_front, chan_mask

    def process_output(self, evnt_num):
        """
        Run the data through the processors.

        :param evnt_num:
        :return:
        """
        # build output
        data_dict = dict()
        data_dict[self.idx_name] = self.index_data[:evnt_num]
        if self.multihit:
            data_dict['multihit'] = self.multihit_out[self.big_data_mask]
        for idx, proc in enumerate(self.proc_list):
            # proc.process(data_dict, self.out_list[idx][evnt_num, :], self.t_front, self.ev_count)
            data_dict[self.out_name_list[idx]] = proc.process(self.big_data[self.big_data_mask],
                                                              self.final_idx[self.big_data_mask])

        return data_dict

    '''
    def _run_batch_orig(self, data_dict, timing_list, close=False):
        """
        This is unbuffered version.
        The time front is a list of the lowest unbuilt indices for each channel.
        (The t0 is the times, E0 the energies)
        The channel which has lowest time in the front is put to an event
        and if other channels in the front have time within the window, then
        they are included. The front is incremented for all the channels that
        were included and the iteration is started again.

        :param data_dict: list of data_dicts for each channel
        :param timing_list: list holding timing information for each channel

        :return: data_dict, timing_data

        """

        # zero all data and indices in unbuffered
        coincsum = 0
        # self.data_mat.fill(-1)
        # self.final_idx.fill(0)
        self.index_data.fill(0)
        self.t_front.fill(0)
        self.timing_front.fill(0)
        self.timing_data.fill(0)
        self.timing_idx = 0
        self.big_data_mask.fill(0)

        tot_counts = 0

        # apply latency, update chmax and process timing lists
        for ch in range(self.num_ch):
            data_dict[ch][self.idx_name] = data_dict[ch][self.idx_name] + self.latency[ch]
            try:
                self.chmax[ch] = data_dict[ch][self.idx_name].shape[0]
            except IndexError:
                self.chmax[ch] = 0
            try:
                self.timing_chmax[ch] = timing_list[ch].shape[0]
                if self.timing_chmax[ch] == 0:
                    # very clumsy way around empty timing lists. If set to max value the write is never triggered.
                    self.timing0[ch] = np.iinfo('uint64').max
                else:
                    # otherwise we use the first index entry in timing_list
                    self.timing0[ch] = timing_list[ch][0]['idx']
            except IndexError:
                # Missing timing list
                self.timing0[ch] = np.iinfo('uint64').max
            except:
                raise

            tot_counts += int(self.chmax[ch])

        timing_chan_mask = self.timing_front < self.timing_chmax

        # build big data structure
        self.build_big_data(tot_counts, data_dict)

        #  Work part
        # reset t_front to loop through the data again
        self.t_front.fill(0)
        timing_idx = 0

        # find coincidences
        evnt_num = 0  # this is the most important number here. If wrong, the data is incorrectly cropped.
        big_idx = 0  # current idx in big_data-array
        self.multihit_out.fill(False)
        iterating = tot_counts > 0
        while iterating:  # through all events
            # Finding coincidences and marking all events to final_idx array.
            ev_sz = 0
            self.ev_count.fill(0)

            t_end = int(self.big_data[big_idx][self.idx_name] + self.coinc_win)

            # single event is looped always here, as first tstamp is guaranteed to be under.
            # final_idx is updated for all events
            while self.big_data[big_idx + ev_sz][self.idx_name] < t_end:
                # mark the channel to the event
                ch = self.big_data[big_idx + ev_sz][1]
                self.ev_count[ch] += 1
                # check multihit and kill the hit if true
                if self.ev_count[ch] > 1:
                    # run combinator on the additional hit. The latest hit is masked out and the first hit is updated
                    # according to the data_info['multi'] policy
                    self.big_data_mask[big_idx + ev_sz] = False
                    self.big_data[self.names_by_channel[ch]][big_idx] = tuple([combi_func(self.big_data[[big_idx,
                                                                                                         big_idx + ev_sz]]) for
                                              combi_func in self.combi_list[ch]])
                    if self.multihit:
                        self.multihit_out[evnt_num] += 2**ch
                # update final_idx
                self.final_idx[big_idx + ev_sz] = evnt_num
                # check if running out of data
                if big_idx + ev_sz + 1 == tot_counts:
                    iterating = False
                    break
                ev_sz += 1


            if ev_sz > 1:
                coincsum += 1


            # # set time of the event (time of first trigger modified by latencies)
            self.index_data[evnt_num] = self.big_data[big_idx][self.idx_name]

            # If the data block has any timing data left then
            # the current timing value is set according to the front
            changed = False
            for ch in self.chan_list[np.logical_and(self.ev_count > 0, timing_chan_mask)]:
                # Current index is equal or higher than the index of the timing event for the channel. 
                # Current index takes into account the overflow of timing event because of a multi-hit
                # event in the channel (reason for the -1 for ev_count. One hit per event is accounted for...)
                # The current channel timing data is written to the event timing and timing is flagged
                # as changed, so that also event index and event timestamp can be written after all
                # channels have been checked.

                if self.timing0[ch] <= int(self.t_front[ch] + self.ch_total_sum[ch] + (self.ev_count[ch]-1)):
                    self.timing_data['dt{}'.format(ch)][timing_idx] = timing_list[ch]['dt0'][self.timing_front[ch]]
                    self.timing_front[ch] += 1
                    changed = True
                    # calculate new timing0
                    if self.timing_chmax[ch] > self.timing_front[ch]:
                        self.timing0[ch] = timing_list[ch]['idx'][self.timing_front[ch]]
                    else:
                        timing_chan_mask[ch] = False

            if changed:
                # The event idx to write, on the other hand, is equal to already written events (self.total_sum)
                # plus event num of current event.
                self.timing_data['idx'][timing_idx] = evnt_num + self.total_sum  # evnt_num not incremented yet
                self.timing_data['t'][timing_idx] = self.big_data[big_idx][0]  # evnt_num not incremented yet
                timing_idx += 1  # increment output timing index if one or more channels were updated

            # update event
            self.t_front += self.ev_count
            evnt_num += 1
            big_idx += ev_sz

        # out of the big loop. Fill all output data
        #self.batch_out(big_idx, ev_sz, evnt_num, data_dict)  # done in process_output

        # update running values in the end of the processed chunk
        self.total_sum += evnt_num
        self.ch_total_sum += self.chmax

        # build output
        data_dict = self.process_output(evnt_num)

        return data_dict, self.timing_data[:timing_idx]
    '''

    def _get_ch_data(self, ch):
        data = []
        timing = []
        all_done = False
        # get oldest data, set all_done flag if there is none.
        if len(self.reserve[ch]) == 0:
            all_done = True
            data = None
            timing = None
            ch_idx = 0
        else:
            data, timing, ch_idx = self.reserve[ch][0]  # return first item in the reserve list

        return all_done, data, timing, ch_idx

    def _join_timing(self, ch, old_timing: Optional[np.array], new_timing: Optional[np.array]):
        """
        Just make sure that timing data exists and is concatenated in a sensible way. This method operates on each
        channel data and should be run on channel data load. Used timing data is stripped away.

        Only some buffers contain timing data, so mostly the timing lists are empty. Multiple buffers can have this
        data though, when loading several buffers ber run. This is why it has to be concatenated.

        This method updates self.timing_chmax, self.timing_front and self.timing0 directly

        :param old_timing:
        :param new_timing:
        :return: result_timing
        """
        no_old = False
        no_new = False

        # Check that old data exists
        if old_timing is None:
            no_old = True
        elif old_timing.shape[0] == 0:
            no_old = True

        # Check that new data exists
        if new_timing is None:
            no_new = True
        elif new_timing.shape[0] == 0:
            no_new = True

        # process all cases
        if no_old and no_new:
            # empty timing out
            self.timing_chmax[ch] = 0
            self.timing_front[ch] = 0
            self.timing0[ch] = np.iinfo(self.index_var['type']).max  # put to max so it'll never trigger
            out = np.zeros((0,), dtype=self.ch_timing_type)
        elif no_old:
            self.timing_chmax[ch] = new_timing.shape[0]
            self.timing_front[ch] = 0
            self.timing0[ch] = new_timing['t'][0]  # index variable value
            out = new_timing.copy()
        elif no_new:
            # it is possible to have timing data as input, but it is already spent. Check for that.
            out = old_timing[self.timing_front[ch]:].copy()
            self.timing_front[ch] = 0
            if out.shape[0] == 0:
                self.timing_chmax[ch] = 0
                self.timing0[ch] = np.iinfo(self.index_var['type']).max
                return np.zeros((0,), dtype=self.ch_timing_type)
            self.timing_chmax[ch] = out.shape[0]
            self.timing0[ch] = out['t'][0]
        else:
            out = np.concatenate((old_timing[self.timing_front[ch]:], new_timing), axis=0).copy()
            self.timing_front[ch] = 0
            self.timing_chmax[ch] = out.shape[0]
            self.timing0[ch] = out['t'][0]
        return out

    def _run_batch_buffered(self, data_dict, timing_list, close=False):
        """
        Buffered version of the run_batch.
        all data is appended into data reserve, a list (one per channel) where data_dict and timing_data are stored.

        The data is then inserted into big_data array in the order of the respective timestamps, getting more from the
        data_reserve as needed, until last event of the slowest channel is inserted (reserve is empty for that
        channel). Then the big_data array is processed and the
        produced event data is returned.

        All excess data is returned to its place in the data reserve, until run_batch is called again. The size of the
        data reserve can be set with the num_buffers option in config. If there are more than num_buffers items in
        data reserve the data is put to big_data array, ignoring slow channels, until the data fits.

        On next iteration the first items in data reserve are processed again until reserve is empty again.

        The time front is a list of the lowest unbuilt indices for each channel. It is used to fill in the big_data.
        (The t0 is the time at earliest channel in time_front)

        The channel which has earliest time in the front is put to an event
        and if other channels in the front have time within the window, then
        they are included (inclusion is set by setting the event number to the final_idx list). The front is
        incremented for all the channels that were included and the iteration is started again.

        Timing data is handled as in the old code and hence is a bit of a mess.

        :param data_dict: list of data_dicts for each channel
        :param timing_list: list holding timing information for each channel
        :param close:       Flush the reserve to record all the data left.

        :return: data_dict, timing_data

        """
        # zero all data and indices
        coincsum = 0
        # self.final_idx.fill(0)
        self.chmax.fill(0)              # maximum index in the batch
        self.index_data.fill(0)         # index data output
        self.t_front.fill(0)            # current idx in the batch
        self.timing_front.fill(0)
        self.timing_data.fill(0)
        timing_idx = 0
        self.big_data_mask.fill(False)
        self.final_idx.fill(0)
        if self.multihit:
            self.multihit_out.fill(False)
        #start = np.zeros((self.num_ch,), dtype='int64')
        ch_idx = np.zeros((self.num_ch,), dtype='int64')  # idx in the current buffer
        #buffmax = np.zeros((self.num_ch,), dtype='int64')  # max idx in the current buffer
        #all_done = False
        count = 0

        # push to FIFO and get oldest data
        curr_data = [[] for _x in range(self.num_ch)]
        curr_timing = [[] for _x in range(self.num_ch)]
        force_write_list = []
        data_left_mask = np.ones((self.num_ch,), dtype=bool)
        for ch in range(self.num_ch):
            if not close:  # No data if close=True
                # check if any data (length of index variable array, should be zero if empty list inserted here):
                if len(data_dict[ch][self.idx_name]) > 0:
                    # apply latency
                    data_dict[ch][self.idx_name] = data_dict[ch][self.idx_name] + self.latency[ch]
                    # check if reserve full
                    if len(self.reserve[ch]) >= self.num_buffers:
                        # throw out old data
                        # self.reserve[ch].pop(0)
                        # data should not be thrown away even if another channel stays silent - force the write
                        print('Forced a write!')
                        force_write_list.append(ch)  # add channel number into force write list
                    # append data, timing and index to first new hit into back of the reserve
                    self.reserve[ch].append([data_dict[ch], timing_list[ch], 0])

            # setting up the current data. The reserve is not modified by get_ch_data. Later the timing and index will
            # be updated.
            done, curr_data[ch], timing, ch_idx[ch] = self._get_ch_data(ch)
            data_left_mask[ch] = not done
            if data_left_mask[ch]:
                curr_timing[ch] = self._join_timing(ch, None, timing)  # used to set correct values for timing idx vars
            #all_done = all_done or done  # return True if any channel in the reserve is totally empty

        # return empty if even one of the channels is without data and no forced writes are defined.
        if np.all(data_left_mask):
            stop_iter = False  # go on iterating
        else:
            if close:
                print('Running close to iterate through all.', [len(x) for x in self.reserve], data_left_mask)
                stop_iter = False  # run through all data on close
            elif len(force_write_list) > 0:
                stop_iter = False
            else:
                return None, None

        # have data, go on. The big data array will be filled up until one channel has no events left, channels with
        # force_write set are fully processed or close is True
        while not stop_iter:
            # build big data structure. Here we add as much data as possible
            count, ch_idx, buffer_left_mask = self.build_big_data(curr_data, count, ch_idx, close=close,
                                                                force_write=force_write_list)

            # purge empty data from the reserve and get new in case the iteration continues
            for ch in np.arange(self.num_ch)[~buffer_left_mask]:
                if len(self.reserve[ch]) > 0:  # only pop if data (was emptied by build_big_index)
                    self.reserve[ch].pop(0)
                    if len(self.reserve[ch]) > 0:  # if data left in reserve
                        try:
                            done, curr_data[ch], ch_timing, ch_idx[ch] = self._get_ch_data(ch)  # done=True if no data
                        except:
                            print('Exception in get_ch_data after pop')
                            print('done: {}, curr data: {}, curr timing: {}, ch idx: {}'.format(done, curr_data[ch],
                                                                                                ch_timing, ch_idx[ch]))
                            raise
                        data_left_mask[ch] = not done  # should ALWAYS be True as data left is checked earlier
                        if data_left_mask[ch]:
                            # why this check? The timing stuff is done after all the data is put into big_data outside
                            # this loop, so we collect all timing data in the handled buffers into one timing list (per
                            # channel) The timing_chmax is updated.
                            # curr_timing[ch] = self._join_timing(ch, curr_timing[ch], ch_timing)
                            curr_timing[ch] = np.concatenate((curr_timing[ch], ch_timing), axis=0)
                            self.timing_chmax[ch] = curr_timing[ch].shape[0]

                    else:  # popped the last data
                        data_left_mask[ch] = False
                        #curr_timing[ch] = self._join_timing(ch, curr_timing[ch], None)  # Necessary?
                else:
                    data_left_mask[ch] = False  # If reserve was empty to begin with. Should not happen.

            if close:
                stop_iter = np.all(~data_left_mask)
            else:
                stop_iter = np.any(~data_left_mask)

        #  Work part. The event building is done once we have gone through the reserve (until stop_iter)
        timing_chan_mask = self.timing_front < self.timing_chmax
        # timing_idx = 0  # zeroed in the beginning

        # find coincidences
        # The outer loop goes
        evnt_num = 0  # this is the most important number here. If wrong, the data is incorrectly cropped.
        big_idx = 0  # current idx in big_data-array
        iterating = count > 0

        while iterating:  # through all events
            # Finding coincidences and marking all events to final_idx array.
            ev_sz = 0
            self.ev_count.fill(0)

            t_end = int(self.big_data[big_idx][self.idx_name] + self.coinc_win)

            # single event is looped always here, as first tstamp is guaranteed to be under.
            # final_idx is updated for all events
            while self.big_data[big_idx + ev_sz][self.idx_name] < t_end:
                # mark the channel to the event
                ch = self.big_data[big_idx + ev_sz][1]
                self.ev_count[ch] += 1
                # check multihit and kill the hit if true
                if self.ev_count[ch] > 1:
                    # run combinator on the additional hit. The latest hit is masked out and the first hit is updated
                    # according to the data_info['multi'] policy
                    self.big_data_mask[big_idx + ev_sz] = False
                    self.big_data[self.names_by_channel[ch]][big_idx] = tuple([combi_func(self.big_data[[big_idx,
                                                                                                         big_idx + ev_sz]])
                                                                               for combi_func in self.combi_list[ch]])
                    if self.multihit:
                        self.multihit_out[evnt_num] += 2 ** ch

                # update final_idx
                self.final_idx[big_idx + ev_sz] = evnt_num
                # check if running out of data
                if big_idx + ev_sz + 1 == count:
                    iterating = False
                    break
                ev_sz += 1

            if ev_sz > 1:
                coincsum += 1

            # # set time of the event (time of first trigger modified by latencies)
            self.index_data[evnt_num] = self.big_data[big_idx][self.idx_name]

            # If the data block has any timing data left then
            # the current timing value is set according to the front
            changed = False
            for ch in self.chan_list[np.logical_and(self.ev_count > 0, timing_chan_mask)]:
                # If current index is equal or higher than the index of the timing event for the channel.
                # Current index takes into account the overflow of timing event because of a multi-hit
                # event in the channel (reason for the -1 for ev_count. One hit per event is accounted for...)
                # The current channel timing data is written to the event timing and timing is flagged
                # as changed, so that also event index and event timestamp can be written after all
                # channels have been checked.

                if curr_timing[ch]['idx'][self.timing_front[ch]] <= int(self.t_front[ch] + self.ch_total_sum[ch] +
                                                                        (self.ev_count[ch] - 1)):
                    try:
                        self.timing_data['dt{}'.format(ch)][timing_idx] = curr_timing[ch]['dt0'][self.timing_front[ch]]
                    except:
                        print('Error in timing data in ch', ch)
                        print(self.timing0, self.timing_front, self.timing_chmax)
                        print([curr_timing[x].shape() for x in range(self.num_ch)], self.timing_data[:timing_idx+1])
                        raise
                    self.timing_front[ch] += 1
                    changed = True
                    # calculate new timing0
                    if self.timing_front[ch] < self.timing_chmax[ch]:
                        self.timing0[ch] = curr_timing[ch]['t'][self.timing_front[ch]]
                    else:
                        timing_chan_mask[ch] = False

            if changed:
                # The event idx to write, on the other hand, is equal to already written events (self.total_sum)
                # plus event num of current event.
                self.timing_data['idx'][timing_idx] = evnt_num + self.total_sum  # evnt_num not incremented yet
                self.timing_data['t'][timing_idx] = self.big_data[big_idx][0]  # evnt_num not incremented yet

                timing_idx += 1  # increment output timing index if one or more channels were updated

            # update event
            self.t_front += self.ev_count
            evnt_num += 1
            big_idx += ev_sz

        # out of the big loop. Fill all output data
        # update running values in the end of the processed chunk
        self.total_sum += evnt_num
        self.ch_total_sum += self.t_front

        # once events are built we save channel timing and index in reserve.
        for ch in range(self.num_ch):
            if len(self.reserve[ch]) > 0:
                # mark the current hit index to reserve
                # self.reserve[ch][0][1] = curr_timing[ch]
                self.reserve[ch][0][1] = self._join_timing(ch, curr_timing[ch], None)
                # mark the current hit index to reserve
                self.reserve[ch][0][2] = ch_idx[ch]

        # build output
        data_dict = self.process_output(evnt_num)

        print('Counts in eventbuilder', self.t_front, self.timing_chmax)
        print('Parsed', evnt_num, 'events with', coincsum, 'coincidences.')
        print('In total {} hits with {} events.'.format(self.ch_total_sum, self.total_sum))

        return data_dict, self.timing_data[:timing_idx]


def strip_cal(data_mat, coord, strip_cal, coord_ch):
    """
    Calculates strip calibration for coordinate data.

    :param data_mat: data
    :param coord: coordinates
    :param strip_cal: calibration matrix
    :param coord_ch: order of coordinate channels
    :return:
    """

    for idx, cc in enumerate(coord_ch):

        mask = data_mat[:, cc] > 0

        data_mat[mask, cc] = (strip_cal[idx, coord[mask, idx], 0] +
                              strip_cal[idx, coord[mask, idx], 1] * data_mat[mask, cc] +
                              strip_cal[idx, coord[mask, idx], 2] * data_mat[mask, cc] ** 2)


def generate_timing(chfile: Path, pulse_dead_time: int, t_vec):
    """
    Utility function to generate timing vector if it does not exist. Takes pathlib type
    filename, pulse dead time for the channel and t_vec.

    Returns nothing, just writes the data.
    """

    chunk_size = 100000
    count = t_vec.shape[0]
    if count % 100000 != 0:
        sz = int(count//chunk_size)
    else:
        sz = int(count//chunk_size-1)

    t_data = np.zeros((sz+2,), dtype=[('idx', '<u8'), ('t', '<u8'), ('dt0', '<f4')])
    # t_data[0] = (0, 0.)
    idx = 0
    for idx in range(sz):
        t_data[idx+1] = ((idx+1)*chunk_size, t_vec[(idx+1)*chunk_size], chunk_size*pulse_dead_time*1e-9)
    leftover = t_vec[(idx)*chunk_size:].shape[0]
    t_data[-1] = (t_vec.shape[0]-1, t_vec[-1], leftover*pulse_dead_time*1e-9)

    with chfile.open('wb') as f:
        f.write(t_data.tobytes())


def generate_metadata(data_list, timing_list, mod_time, path, base_name, cfg):
    """
    Metadata needs to be generated for data with no metadata files in the load directory. Note that events will
    not be updated, because the generation is done before parsing.

    Channels with zero counts are causing problems here and are handled separately.
    """
    metadata = Metadata(None, len(cfg.det['ch_list']))
    num_ch = len(cfg.det['ch_list'])
    input_counts = np.zeros((num_ch,), dtype='uint64')
    counts = np.zeros((num_ch,), dtype='uint64')
    dead_time = np.zeros((num_ch,), dtype='float32')
    total_time = 0
    primary = cfg.det['datas'][cfg.det['primary_data']]['name']
    for ch in range(num_ch):
        input_counts[ch] = np.count_nonzero(data_list[ch][primary] >= 0)
        counts[ch] = np.count_nonzero(data_list[ch][primary] > 0)
        if counts[ch] > 0:
            dead_time[ch] = timing_list[ch]['dt0'].sum()
        else:
            dead_time[ch] = 0

    metadata.input_counts = input_counts
    metadata.counts = counts
    metadata.total_time = total_time
    metadata.dead_time = dead_time
    metadata.start = dt.datetime.fromtimestamp(mod_time) - dt.timedelta(seconds=total_time*1e-9)
    metadata.stop = dt.datetime.fromtimestamp(mod_time)
    metadata.name = cfg.det['name']
    metadata.run_id = base_name
    metadata.notes = 'Metadata generated on first channel file load.'
    ut.write_channel_metadata(path, base_name, -1, metadata.dump())


class ColProcessor:
    """
    Simple class for setting the output data in event building.
    It is initialized with the data info. ;ulti-hits are processed separately.
    window.

    Each instance of a class is only updating its own
    part of the data (energy, timing, coord, etc.) and is supposed to be run in a pipeline
    for every event.
    """
    def __init__(self, info, max_buffer_size):
        """
        :param info: The data info dict containing information of the data:
                    "name": name of the output datafile: "basename_name.dat"
                    "type": datatype (u1, i2, u4 ..)
                    "num_col": number of columns in the output
                    "aggregate": aggregate type of the data. Accepted aggregate types are:
                            "col": each input channel is aggregated as a column to the
                                   output matrix
                            "bit": each input channel is cast to bool and added to a bitmask
                            "multihit": No inputs. Outputs a bitmask of multiple hits per event on a multi-
                                   channel detector.
                            "latency": No inputs. Outputs the time difference of coincident signals between a single
                                       main channel and all the others. Needs "main" parameter to be set.
                            In the future add:
                            "sum": Sum of the data defined by "type" and "channel" parameters where "type" denotes data
                                   type to sum and "channel" is a list of channels. This extra is associated to the
                                   first channel in the list.
                    "multi": What to do if multiple hits to a channel in single event:
                            "sum": sum all to a single value
                            "max": take the maximum value
                            "max_e": take value on the hit with maximum energy
                            "min": take the minimum value
                            "mean": calculate arithmetic mean and round to fit "type"
                            "kill": set to 0
                    "ch_mask": Some data is only valid for some channels. Boolean channel mask is used to define
                               valid channels for the data. Must be np array with shape[0]=num_ch
                    "main": Used by the "latency" aggregate to define which channel is compared against the others.
                    In the future add:
                    "type": Type of data to sum up as extra.
                    "channel": List of channels to sum up as extra.
        :param name_list: List of all data names.

        """
        # first check data types:
        self.info = info

        # Basic layout of the data
        self.ch_mask = np.array(self.info['ch_mask'], dtype='bool')
        self.ch_ind = np.arange(self.ch_mask.shape[0])  # used to map from data index to channel idx

        # channel map maps input channel index into output. It is used for data that can be missing from some
        # channels, such as coordinate data. The cumulative sum works because channel_mask masks the incorrect
        # indices - should not ever sample channel -1
        ch_map = self.ch_mask.cumsum() - 1
        #self.ch_map = np.expand_dims(ch_map, axis=0)
        self.ch_map = np.broadcast_to(ch_map, (max_buffer_size, ch_map.shape[0]))
        self.temp_idx = np.arange(max_buffer_size)

        # With the structured data input one needs to use the name of the data to index it from the input. This is also
        # true for 'energy'
        self.name = self.info['name']
        self.out = np.zeros((max_buffer_size, self.info['num_col']), dtype=self.info['type'])

    def process(self, in_array, final_idx):
        """
        :param in_list:     The big data array containing all data of the hits in the event
        :param final_idx:   The index of each hit in the output data, calculated by event builder
        :param out:         The output data as a matrix
        :return:
        """
        self.out.fill(self.info['empty_val'])
        data_len = len(in_array)
        self.out[final_idx, self.ch_map[self.temp_idx[:data_len], in_array['ch']]] = in_array[self.name]

        return self.out[:final_idx[-1] + 1, :]


class BitProcessor (ColProcessor):
    """
    Creates a bitmask from individual channel bits (for example, ones signalling pile-up events).
    """
    def __init__(self, info, max_buffer_size):
        super().__init__(info, max_buffer_size)
        bitvals = 2 ** np.array(range(self.ch_mask.shape[0]), dtype=self.info['type'])
        self.bitvals = np.broadcast_to(bitvals, (max_buffer_size, bitvals.shape[0]))
        # reinit output array storing the channel flags before summing
        self.out = np.zeros((max_buffer_size, self.ch_mask.sum()), dtype=self.info['type'])

    def process(self, in_array, final_idx):
        self.out.fill(0)
        data_len = len(in_array)
        ch_vec = self.ch_map[self.temp_idx[:data_len], in_array['ch']]

        self.out[final_idx, ch_vec] = self.bitvals[self.temp_idx[:data_len], ch_vec]
        return self.out[final_idx].sum(axis=1)


class LatencyProcessor (ColProcessor):
    """
    LatencyProcessor is a specialized processor used to visualize the timing properties of the input data. Each
    output column is equal to time difference between event in main channel and event in each other channel
    (so output of main channel is always zeros) calculated from latency corrected time data. Smallest value of type is
    returned if there was no coincidence between the channels. All channels should show zero-centered distributions
    in a properly tuned detector. Width of the distributions will show how big coincidence window is needed.
    """

    def __init__(self, info, max_buffer_size):
        super().__init__(info, max_buffer_size)
        self.main_ch = self.info['main']
        self.time = self.info['index']
        self.intermediate = np.zeros((max_buffer_size, self.ch_mask.sum()), dtype='int64')
        self.ch_mask[self.main_ch] = 0  # set to zero as self delta is constant 0
        self.temp = np.zeros((max_buffer_size,), dtype='int64')

    def process(self, in_array, final_idx):
        self.intermediate.fill(self.info['empty_val'])
        # mask of events that have a hit in the main channel
        main_mask = in_array['ch'] == self.main_ch
        # output indices of the hits
        out_idx = final_idx[main_mask]
        # mask of all hits in all channels coincident with main_ch
        full_mask = np.in1d(final_idx, out_idx, assume_unique=False, invert=False)
        # finally mask of other hits
        other_mask = np.logical_xor(full_mask, main_mask)

        # need some gymnastics with the types here... Latency should be calculated only on debug runs anyhow, so it is
        # not slowing down normal data taking. Intermediate data is handled as int64 but the timestamps can be up to
        # uint64 -> set 64th bit to zero, cast to int64 and subtract. Ignore the wrapping at the boundary,
        # a debug run does not take that long. In the end each event is guaranteed to be within
        # a very narrow time window, so we can safely cast the result to smaller type.

        # time vector
        self.temp[:in_array.shape[0]] = in_array[self.time] & 0x7fffffffffffffff
        # intermediate array with time values. Initialized to smallest value of the type and filled with
        # all the hits
        self.intermediate[final_idx[other_mask], in_array[other_mask]['ch']] = self.temp[:in_array.shape[0]][other_mask]
        #self.out[final_idx[in_mask], in_array[final_idx[in_mask]]['ch']] = in_array[final_idx[in_mask]][self.time]
        self.intermediate[final_idx[main_mask], in_array[main_mask]['ch']] -= self.temp[:in_array.shape[0]][main_mask]
        self.out[:in_array.shape[0], :] = self.intermediate[:in_array.shape[0], :].astype(self.info['type'])

        # return self.out[:final_idx[-1] + 1]
        return self.intermediate[:final_idx[-1] + 1, :]


def combinator_factory(combinator_type, name, other=None):
    afunc = multi_dict[combinator_type]
    if other is None:
        other = name
    if combinator_type in ('max'):
        def combi(in_array):
            return in_array[name][afunc(in_array[other]).argmax()]
    elif combinator_type in ('min'):
        def combi(in_array):
            return in_array[name][afunc(in_array[other]).argmin()]
    else:
        def combi(in_array):
            return afunc(in_array[name])
    return combi


class StreamData:
    """
    Stream_data is a manager that pushes list mode data into disk as it comes available. The index variable, data and
    timing data for Cache need their own streamers.

    Channel mode data is stored as raw binary files, with one file holding index variable, one file for each type of
    data recorded.
    Note: there is no reason to save data in channel mode after latency and coincidence window are set. Channel data
    should be automatically deleted when sure that the data is good.

    Event data is stored as raw binary with index (timestamps) and data matrix (num_cols columns).

    Timing data is a row of timing info (uint32 idx + 2xuint32 x num_ch). This will be changed later to work with any
    Cache type module, not just TimeCache.
    """

    def __init__(self, path, source_name, method='data', raw=False, channels=None, data_name=None):
        """
        Initialize the write method, coincidence window and number of channels.

        :param path: path to the data. String or a pathlib Path
        :param source_name: string, the base filename
        :param method:    * data: have any data, such as coordinates or tags as input, stream to 'data_name'
                          * timing: have index to event, event time plus dead time float (deprecated, should be
                          * streamed as normal data, with name 'timing'
        :param raw:       raw data is defined separately for each channel.
        :param channels:  Used if raw = True. This is a list of channel numbers that are saved. The time and energy
                          files will be appended with '_ch{channels[idx]}.dat'
        :param data_name: Used if mode is 'data'. This is a name of the data. Filename will be
                          'data_name_{extra_name}.dat'
        """
        self.raw = raw
        self.path = Path(path)
        self.source_name = source_name
        self.channels = channels
        self.method = method
        self.data_name = data_name

        if raw:
            if self.channels is None:
                raise ValueError('channels must be defined for raw stream mode!')
            if self.data_name is None:
                raise ValueError('Data_name must be defined for data mode!')
        else:
            if self.data_name is None:
                raise ValueError('Data_name must be defined for data mode!')
        #    raise ValueError('Invalid method for disk write')

        self.file_idx = 0  # the index of files in case the file size has exceeded 2GB and the data has been split
                           # Not in use at all
        self.new_files()

    def new_files(self):
        #self.index_files = []
        self.data_files = []

        if self.file_idx == 0:
            suffix = 'dat'
        else:
            suffix = 'b{:02}'.format(self.file_idx)

        if self.raw:
            for ch in self.channels:
                self.data_files.append((self.path / '{}_{}_ch{}.{}'.format(self.source_name,
                                                                               self.data_name,
                                                                               ch,
                                                                               suffix)).open('wb'))

        else:
            self.data_files.append((self.path / '{}_{}.{}'.format(self.source_name,
                                                                      self.data_name,
                                                                      suffix)).open('wb'))


    def write(self, data):
        """

        :param data: numpy matrix or list of matrices if raw == True
        :return:
        """
        if self.raw:
            for idx, ch in enumerate(self.channels):
                if len(data[ch]) > 0:
                    self.data_files[idx].write(data[ch].tobytes())
        else:
            self.data_files[0].write(data.tobytes())

    def close(self):
        for fil in self.data_files:
            fil.close()


def truncate_data(data_path, base_name, cfg):
    """
        :param data_path:   Path to the data directory
        :param base_name:   Base name of the data
        :param cfg:         The detector config dictionary

        :return:

        Discrepancy in data file size can happen if daq crashes before flushing all data into files. Fix data files by
        truncating to smallest common size.
        """
    event_info = cfg.det['datas'][cfg.det['primary_data']]
    primary = event_info['name']
    index_data = cfg.det['index_variable']['name']
    index_type = cfg.det['index_variable']['type']

    # Find the rest of the data and determine num_ch and ev_sz
    datas = [cfg.det['datas'][x] for x in range(len(cfg.det['datas']))]

    idxnames, dnames, tnames = ut.find_data_files(data_path, base_name, cfg, mode='channel')

    for fname in idxnames:  # not checking against timing data as sometimes it has to be generated afterwards
        if not fname.exists():
            raise ex.LimonadeDataNotFoundError('Could not find all data files')

    import pprint
    pp = pprint.PrettyPrinter(indent=2, sort_dicts=False)
    pp.pprint(dnames)

    for chnamelist in dnames:
        for fname in chnamelist:
            if (fname is not None) and (not fname.exists()):
                raise ex.LimonadeDataNotFoundError('Could not find all data files')

    for idx in range(len(idxnames)):
        idxname = idxnames[idx]
        ev_sz = idxname.stat().st_size // np.dtype(index_type).itemsize  # number of events
        print('Got idx file len of {} for ch {}'.format(ev_sz, idx))
        min_ev = ev_sz
        corrupt = False
        for d_idx, adata in enumerate(datas):
            # if this extra has channel info
            if adata['name'] not in ut.parsed_extras_list:  # if info for this channel exists
                xname = dnames[d_idx][idx]
                x_sz = xname.stat().st_size // np.dtype(adata['type']).itemsize  # number of events
                print('Got dat file len of {} for ch {}'.format(x_sz, idx))
                if x_sz != ev_sz:
                    min_ev = min(min_ev, x_sz)
                    corrupt = True

        if corrupt:
            # Discrepancy in file sizes, the data is truncated
            ev_sz = idxname.stat().st_size // np.dtype(index_type).itemsize  # number of events
            #curr_file = np.memmap(idxname, dtype=index_type, mode='r+', shape=(ev_sz,))
            #temp = curr_file[:min_ev]
            #del curr_file
            with idxname.open('a+b') as fil:
                #fil.write(temp.tobytes())
                fil.seek(np.dtype(index_type).itemsize*min_ev)
                #fil.truncate(size=np.dtype(index_type).itemsize*min_ev)
                fil.truncate()
                fil.flush()

            for d_idx, adata in enumerate(datas):
                # if this extra has channel info
                if adata['name'] not in ut.parsed_extras_list:  # if info for this channel exists
                    print('truncating ch {}'.format(idx))
                    xname = dnames[d_idx][idx]
                    x_sz = xname.stat().st_size // np.dtype(adata['type']).itemsize  # number of events
                    print('Size is {}, truncating to {}'.format(x_sz, min_ev))
                    #curr_file = np.memmap(xname, dtype=adata['type'], mode='r+', shape=(x_sz,)).resize(min_ev,
                    #                                                                                   refcheck=False)
                    with xname.open('a+b') as fil:
                        fil.seek(np.dtype(adata['type']).itemsize * min_ev)
                        # fil.truncate(size=np.dtype(index_type).itemsize*min_ev)
                        fil.truncate()
                        fil.flush()


def read_binary_data(data_path, base_name, cfg, mode='event'):
    """
    :param data_path:   Path to the data directory
    :param base_name:   Base name of the data
    :param cfg:         The detector config dictionary
    :param mode:        What mode of data to read: 'event' or 'channel'.

    :return:

    The detector configuration is needed for defining the data:
        List of dicts defining data files, type and number of columns.
        datas = {"name":'x',
                  "type":'t',
                  "num_col":'n'},
        where type is a numpy type string of the data. Several datas can be defined in
        det_cfg (coord, ch_flags). These are handled automatically if they are present.

    Some data, such as coord, need to have additional definitions in the
    config. For coord, it is the 'ch_mask' list which defines the number and channel of the coordinates. The order of
    the coordinates in x, y notation, is defined by the order of their respective channels.
    """
    event_info = cfg.det['datas'][cfg.det['primary_data']]
    primary = event_info['name']
    index_data = cfg.det['index_variable']['name']
    index_type = cfg.det['index_variable']['type']

    # Find the rest of the data and determine num_ch and ev_sz
    datas = [cfg.det['datas'][x] for x in range(len(cfg.det['datas']))]

    idxnames, dnames, tnames = ut.find_data_files(data_path, base_name, cfg, mode)

    for fname in idxnames:  # not checking against timing data as sometimes it has to be generated afterwards
        if not fname.exists():
            raise ex.LimonadeDataNotFoundError('Could not find all data files')

    import pprint
    pp = pprint.PrettyPrinter(indent=2, sort_dicts=False)
    pp.pprint(dnames)

    for chnamelist in dnames:
        for fname in chnamelist:
            if (fname is not None) and (not fname.exists()):
                raise ex.LimonadeDataNotFoundError('Could not find all data files')


    # Now all files in the name lists are loaded
    # For channel data this is one item per ch, for events there is only one item. Each item of full_data_list
    # is a ch_data_dict containing time, energy and extras. (Some extras are not included in channel mode read.)
    # with time vector, energy and individual extras as items
    full_data_list = []
    timing_list = []
    # build return tuple. Empty channels are given zeros vector instead of a memmap to prevent crashing the loader.

    print('Read binary', len(idxnames))
    for idx in range(len(idxnames)):
        idxname = Path(str(idxnames[idx]))
        ev_sz = idxname.stat().st_size // np.dtype(index_type).itemsize  # number of events


        if mode == 'channel':  # check if raw files are good
            print('Got file len of {} for ch {}'.format(ev_sz, idx))
            min_ev = ev_sz
            max_ev = ev_sz
            corrupt = False
            for d_idx, adata in enumerate(datas):
                # if this extra has channel info

                if adata['name'] not in ut.parsed_extras_list:  # if info for this channel exists
                    xname = Path(str(dnames[d_idx][idx]))
                    x_sz = xname.stat().st_size // np.dtype(adata['type']).itemsize  # number of events
                    print('Got file len of {} for ch {}'.format(x_sz, idx))
                    if x_sz != ev_sz:
                        min_ev = min(min_ev, x_sz)
                        max_ev = max(max_ev, x_sz)
                        corrupt = True

            if corrupt:
                # Discrepancy in file sizes, the data is truncated
                err_str = 'Mismatch in data file sizes for channel {}. Got data for {} to {} events. Fix datafiles!'.format(idx, min_ev, max_ev)
                raise ex.LimonadeDataError(err_str)
                # truncate_data(idxnames, datas, min_ev)

    for idx in range(len(idxnames)):
        ch_data_dict = dict()
        idxname = idxnames[idx]
        #ename = enames[idx]
        # First the timing
        ev_sz = idxname.stat().st_size // np.dtype(index_type).itemsize  # number of events
        print('Got file len of {} for ch {}'.format(ev_sz, idx))

        if ev_sz > 0:
            try:
                ch_data_dict[index_data] = np.memmap(idxname, dtype=index_type, mode='r', shape=(ev_sz,))

            except FileNotFoundError:
                print(idxname, 'not found!')
                raise ex.LimonadeDataNotFoundError
            except:
                print('Data load fails!')
                raise
        else:
            #num_ch = len(cfg.det['ch_cfg'])
            ch_data_dict[index_data] = np.zeros((0,), dtype=index_type)  # empty channel is just empty

        # now for events and extras
        if mode == 'channel':
            # First channel mode
            # all the datas that are defined, in channel mode
            try:
                for d_idx, adata in enumerate(datas):
                    # if this extra has channel info
                    if adata['name'] not in ut.parsed_extras_list:  # if info for this channel exists
                        xname = dnames[d_idx][idx]
                        x_sz = xname.stat().st_size // np.dtype(adata['type']).itemsize  # number of events
                        print('Got file len of {} for ch {}'.format(x_sz, idx))
                        if xname:  # an extra may be defined for a subset channels. Skip if empty.
                            # single channel extra always 1 column wide?
                            if ev_sz > 0:
                                ch_data_dict[adata['name']] = np.memmap(xname, dtype=adata['type'], mode='r',
                                                                        shape=(ev_sz,))
                            else:
                                ch_data_dict[adata['name']] = np.zeros((ev_sz,), dtype=adata['type'])
            except:
                print('Channel mode extras fail!')
                raise

            # for some data types the timing info is missing from channel data. Geant4 for example, but also
            # appended Caen files are dumped without timing.
            tname = tnames[idx]
            try:
                timing_sz = tname.stat().st_size // 20
                if ev_sz > 0:
                    print('Tying to load timing data', tname)
                    timing_list.append(np.memmap(tname, dtype=[('idx', '<u8'), ('t', '<u8'), ('dt0', '<f4')],
                                                 mode='r', shape=(timing_sz, 1)))

            except FileNotFoundError:
                print('No tdata for ch', idx)
                print('Generating timing data from datafiles.')
                if ev_sz > 0:
                    # need to generate timing data
                    generate_timing(tname, cfg.det['ch_cfg'][idx]['pdeadtime'], ch_data_dict[index_data])
                    timing_sz = tname.stat().st_size // 20
                    # Actually loading the data here
                    timing_list.append(np.memmap(tname, dtype=[('idx', '<u8'), ('t', '<u8'), ('dt0', '<f4')],
                                                 mode='r', shape=(timing_sz, 1)))
                else:
                    # no data
                    timing_list.append(np.zeros((1, 1), dtype=[('idx', '<u8'), ('t', '<u8'), ('dt0', '<f4')]))

        # event mode
        else:
            tname = tnames[0]
            num_ch = len(cfg.det['ch_list'])  # need num_ch to shape the data

            # loop through the datas
            for d_idx, adata in enumerate(datas):
                # if this extra has info
                dname = dnames[d_idx][idx]
                if ev_sz > 0:
                    try:
                        ch_data_dict[adata['name']] = np.memmap(dname, dtype=adata['type'],
                                                                mode='r', shape=(ev_sz, adata['num_col']))
                    except:
                        print('Loading extras fail!')
                        print('Loading', adata['name'])
                        raise
                else:
                    ch_data_dict[adata['name']] = np.zeros((0, adata['num_col']), dtype=adata['type'])

            timing_sz = tname.stat().st_size // (16 + num_ch*4)
            try:
                type_list = [('idx', '<u8'), ('t', '<u8')]
                for x in range(num_ch):
                    type_list.append(('dt{}'.format(x), '<f4'))
                timing_list.append(np.memmap(tname, dtype=type_list,
                                             mode='r', shape=(timing_sz,)))
            except:
                print('Fails on load of timing data!', tnames[idx])
                raise

        full_data_list.append(ch_data_dict)

    # timing data is returned as a copy, so that it can be directly appended to when chainloading.
    if mode == 'event':
        print('Read binary data in event mode')
        return full_data_list[0], timing_list[0].copy()
    else:
        # In the end of a channel load we check the existence of metadata and generate it if missing.
        # This is important as metadata must exist for all data, even if it was just a minimal start/stop and
        # event count info. Here we only check for the first file, as all should exist if one does.
        metaname = data_path / (base_name + '_metadata_ch00.json')
        if not metaname.exists():
            print('Metadata missing! Creating dummy values.')
            generate_metadata(full_data_list, timing_list, idxnames[0].stat().st_mtime, data_path, base_name, cfg)
        return full_data_list, timing_list.copy()


def data_info(info, ch_list):
    """
    Fills data_info dict with defaults for parts that are missing. Hardcoded settings for multihit and latency
    data will be overwritten if defined in config. A warning is printed if setup is overwritten.

    :param info: info dict
    :param ch_list: info dict
    :return: dict with missing keys filled with defaults.
    """
    # channel mask defines num_col -> it has to be checked and calculated first
    try:
        ch_mask = info['ch_mask']
    except KeyError:
        ch_mask = list(np.ones((len(ch_list)), dtype='u1'))
        info['ch_mask'] = ch_mask

    # hardcoded values for different datatypes.
    mh_hardcoded = {'type': 'u1',
                    'num_col': 1,
                    'aggregate': 'multihit',
                    'multi': 'max',
                    'empty_val': 0}
    lat_hardcoded = {'type': 'i2',
                    'aggregate': 'latency',
                    'multi': 'min',
                    'unit': 'ns',
                    'raw_unit': 'ns'}

    default = {'multi': 'max',
               'empty_val': 0}
    lat_default = {'main': 0}
    # hardcoded values are written over ones defined in info. num_col is calculated and defaults are applied.
    if info['name'] == 'multihit':
        for key in info:
            if key in mh_hardcoded:
                print('Warning, {} in multihit extra is incompatible and will be overwritten.!'.format(key))
        info.update(mh_hardcoded)

    elif info['name'] == 'latency':
        for key in info:
            if key in lat_hardcoded:
                print('Warning, {} in latency extra is incompatible and will be overwritten.!'.format(key))
        info.update(lat_hardcoded)
        default.update(lat_default)
        for key, value in default.items():
            if key not in info:
                info[key] = value
        info['num_col'] = sum(ch_mask)
        info['empty_val'] = -32768

    else:
        agg = info['aggregate']
        temp = process_dict[agg]
        if issubclass(temp, BitProcessor):
            info['num_col'] = 1
        else:
            info['num_col'] = sum(ch_mask)
        for key, value in default.items():
            if key not in info:
                info[key] = value
    return info


def load_calibration(config):
    """
    Loads calibration for the detector. Calibration gives the 2nd degree function coefficients for calibration for each
    channel and for each data type. The data is organized as a dictionary with data types as keys and each data as
    numpy arrays with channel in first axis and three coefficients (a, b and c) in second axis.

    Missing data is fixed with dummy calibration ([0,1,0] coefficients), but incompatible data (e.g. wrong number of
    channels) will raise an exception.

    :param config:  The detector config object. It is needed to find the calibration file for the data and to provide
                    defaults for missing calibration data.

    :return: The calibration dictionary. Missing data is fixed with dummy calibration.
    """

    cal_name = ut.find_path(config, config.det['cal_name'], suffix='ecal', from_global_conf=True)
    try:
        #with ut.find_path(config, cal_name, '_ecal.json').open('r') as fil:
        with cal_name.open('r') as fil:
            # Going back and forth with the 'cal' keyword as a fix for the desanitize-function. Now it works for
            # new style all dict config, but needs to be converted to a dict for the desanitation of actual cal file.
            temp = dict()
            temp['cal'] = json.load(fil)
            cal = misc.desanitize_json(temp)['cal']
    except FileNotFoundError:
        print('Calibration file not found!')
        raise ex.LimonadeConfigurationError('Calibration file not found!')

    for data in config.det['datas']:
        #('Extra cal', extra['name'])
        data_name = data['name']
        #if not issubclass(dat.process_dict[extra['aggregate']], dat.process_dict['bit']):  # bitmasks are not calibrated
        try:
            cal[data_name]
        except KeyError:  # missing calibration data is just generated here. Extra data calibration is not necessary
            temp = np.zeros((data['num_col'], 3))
            temp[:, 1] = 1
            cal[data_name] = temp
        if cal[data_name].shape[0] != data['num_col']:
            errstr = 'Incompatible calibration data for {} data!'.format(data_name)
            raise ex.LimonadeConfigurationError(errstr)

    return cal


def load_config(data_paths: Optional[Sequence], det_name: Optional[str]=None, from_global_conf: bool=False):
    """
    Detector configuration object is a namespace with (minimally):
    :path:  paths into configuration directories and data.
    :det:   Contents of the detector configuration file.
    :cal:   Calibration for the detector. Calibration gives the 2nd degree function coefficients for calibration for
            each channel and for each data type. The data is organized as a dictionary with data types as keys and
            each data as numpy arrays with channel in first axis and three coefficients (a, b and c) in second axis.
            Omitted calibration data is replaced with [0,1,0] coefficients.

    :param data_paths:      A list of paths (paths) to the data. The list of paths defines the chainloaded data
                            directories. First path is considered a home directory. If path is None, then 'data_dir' is
                            taken from local config.
    :param det_name:        Name of the detector configuration file without the _cfg.json. It is used if from_global_conf
                            bool is set.
    :param from_globa_conf: Load detector configuration from config dir even if local configuration exists.
    :return: detector configuration object

    """
    # setup path config with global configuration directory
    path_cfg = ut.get_limonade_config()

    # checking if loading a histogram file. In this case, the histogram metadata file is loaded.
    if det_name == 'histogram':
        det_cfg_path = Path(data_paths[0])
        with (det_cfg_path.parent / (det_cfg_path.stem + '.json')).open('r') as fil:
            print('Loading config from', det_cfg_path.parent / (det_cfg_path.stem + '.json'))
            det_cfg = json.load(fil)
        config = ut.old_config(det_cfg)
    else:
        # the first data directory is considered the home directory and configurations
        # in there are loaded preferably to ones in configuration directory, unless from_global_conf is set.
        if data_paths is None:
            path_cfg['home'] = path_cfg['data_dir']
        else:
            path_cfg['home'] = data_paths[0]

        # Detector config - Always loaded from data directory, unless from_global_config is True.
        det_cfg_path = ut.find_path(path_cfg, det_name, suffix=None, from_global_conf=from_global_conf)
        with det_cfg_path.open('r') as fil:
            det_cfg = json.load(fil)

        # detector config needs sensible values set for data. Data_info forces some mandatory configurations and fills in
        # some defaults if omitted from configuration file.
        # The first entry in det_cfg['datas'] is considered primary data and has to have data for each channel. This is
        # usually 'energy'.
        det_cfg['datas'] = [data_info(data, det_cfg['ch_list']) for data in det_cfg['datas']]

        # Fill in the basics for other configs
        config = types.SimpleNamespace(path=path_cfg, det=det_cfg, cal=None)

        # added calibrations. These will be loaded from the original global configuration.
        # cal_path = ut.find_path(config, config.det['cal_name'], 'ecal', from_global_conf=from_global_conf)
        config.cal = load_calibration(config)

    return config


multi_dict = {'max': np.max,
              'min': np.min,
              'mean': np.mean,
              'sum': np.sum}


process_dict = {'col': ColProcessor,
                'bit': BitProcessor,
                'multihit': BitProcessor,  # To fix type testing by Plot module. Multihits not processed by EventBuilder.
                'latency': LatencyProcessor}
