'''
Class for post-processing measurement data.
'''

from pdata._metadata import __version__

import os
import time
import numpy as np
import types
import re
import logging
import copy
import shutil
import gzip
import tarfile
import itertools
import json
import jsondiff
import datetime
import pytz
from dateutil import tz
from collections import OrderedDict

UNIX_EPOCH = datetime.datetime(1970, 1, 1, 0, 0, tzinfo = pytz.utc)

class PDataSingle():
    ''' Class for reading in the contents of a single pdata data directory.
        Almost always passed on to DataView for actual analysis. '''

    def __init__(self, path, convert_timestamps=True, parse_comments=False):
      '''Parse data stored in the specified directory path.

         convert_timestamps --> Convert values that look like time
         stamps into seconds since Unix epoch.

         parse_comments --> Parse comments placed between data
         rows. In the current implementation, parsing the comments
         requires a separate pass through the data.
      '''
      self._path = path

      def parse_initial_snapshot():
        self._snapshots = []
        if os.path.exists(os.path.join(path, 'snapshot.json')):
          with open(os.path.join(path, 'snapshot.json'), 'r') as f:
            self._snapshots.append((0, json.load(f)))
        else:
          with gzip.open(os.path.join(path, 'snapshot.json.gz'), 'r') as f:
            self._snapshots.append((0, json.load(f)))

      def add_snapshot_diff(row, f):
        # Deep copy the last snapshot -> VERY inefficient but easy & safe
        snap = json.loads(json.dumps(self._snapshots[-1][-1]))
        # Add the new copy with the changes
        self._snapshots.append((row, jsondiff.patch(snap, json.load(f))))

      def parse_snapshot_diff_names(fnames):
        """ Given a list of filenames, filter and sort the snapshot diffs. """
        diff_names = []

        for f in fnames:
          m = re.match(r'snapshot\.row-(\d+)\.diff(\d+)\.json', f)
          if m != None:
            diff_names.append((int(m.group(1)), int(m.group(2)), m.group(0)))
            continue
        diff_names.sort(key=lambda x: x[1]) # secondary sort on .diff<n>
        diff_names.sort(key=lambda x: x[0]) # primary sort on .row-<n>
        return diff_names

      def parse_tabular_data(f):
        # First read comments in the data file
        # and determine the number of data rows and columns
        self._comments = []
        converters = {}
        rowno = 0
        comment = ""
        while True:
          line = f.readline()
          if not isinstance(line, str): line = line.decode('utf-8')
          if len(line) == 0: break # EOF

          line = line.strip()
          if len(line) == 0: continue # empty line

          if line.startswith('#'):
            comment += line[1:].strip() + '\n'
            continue

          # Otherwise this is a data row
          comment = comment.strip()
          if len(comment) > 0:
            self._comments.append((rowno, comment))

          # The second to last comment row preceding the first data row is the table header
          # that defines the column names
          # Parse the columns
          if rowno==0: self._table_header = comment

          # Determine the number of columns from the first data row
          if rowno==0: ncols = len(line.split('\t'))

          # Determine, based on the first data row, whether any columns contain
          # time stamps. Convert them into seconds since Unix epoch.
          if rowno==0 and convert_timestamps:
            for i,c in enumerate(line.split('\t')):
              try:
                PDataSingle._parse_timestamp(c)
                converters[i] = lambda x: PDataSingle._parse_timestamp(x.decode('utf-8'))
                logging.info('Column %s appears to contain timestamps. Converting them to seconds since Unix epoch. (Disable by setting convert_timestamps=False.)', i)
              except ValueError:
                pass # Not a timestamp

          rowno += 1
          comment = ""

          # Done parsing the header. We can stop here if parsing comments is not needed.
          if not parse_comments: break

        if not hasattr(self, "_table_header"):
          logging.warn(f"No header found in tabular data of {self._path}")
          self._column_names, self._units = [], []
        else:
          self._column_names, self._units = PDataSingle._parse_columns_from_header(self._table_header)

        assert len(self._column_names) == ncols, "The number of columns in the header and data do not seem to match."

        self._column_name_to_index = dict((self._column_names[i], i) for i in range(len(self._column_names)) )

        # Parse the actual numerical data
        f.seek(0)
        self._data = np.genfromtxt(f,
                                   delimiter="\t",
                                   comments="#",
                                   converters=converters,
                                   dtype=float) # Assume all columns contain floats

        # If the data contains just a single point, genfromtxt returns a 1D vector instead of a 2D array, so convert it to 2D
        if len(self._data.shape) == 1: self._data = np.array([ self._data ])

        if parse_comments:
          # rowno should equal the number of data rows, if comments were parsed and
          # no new data was added between the two passes through the file.
          assert len(self._data) >= rowno, 'Unexcepted number of data rows: %s vs %s' % (len(self._data), rowno)

        if len(self._data) > 0:
          assert len(self._data[0]) == ncols, 'Unexcepted number of data columns: %s vs %s' % (len(self._data[0]), ncols)


      ###########################################################
      # Actually parse the data using the helper functions above
      ###########################################################

      # Parse main data file (possibly compressed)
      if os.path.exists(os.path.join(path, "tabular_data.dat")):
        with open(os.path.join(path, "tabular_data.dat"), 'r') as f:
          parse_tabular_data(f)

      elif os.path.exists(os.path.join(path, "tabular_data.dat.gz")):
        with gzip.open(os.path.join(path, "tabular_data.dat.gz"), 'rb') as f:
          parse_tabular_data(f)

      else:
        other_dat_files = [ pp for pp in os.scandir(path) if pp.name.endswith(".dat") ]
        if len(other_dat_files) == 0: assert False, f'No .dat file found in {os.path.abspath(path)}'
        logging.info(f"No tabular_data.dat(.gz) found in {path}. Using {other_dat_files[0].name} instead.")
        with open(other_dat_files[0].path, 'r') as f:
          parse_tabular_data(f)

      # Parse initial snapshot
      parse_initial_snapshot()

      # Parse snapshot diffs
      tar_fname = os.path.join(path, 'snapshot_diffs.tar.gz')
      if os.path.exists(tar_fname):
        with tarfile.open(tar_fname) as tar:
          for row,j,fname in parse_snapshot_diff_names(tar.getnames()):
            add_snapshot_diff(row, tar.extractfile(fname))

      else: # uncompressed snapshot diffs as separate files
        for row,j,fname in parse_snapshot_diff_names(os.listdir(path)):
          with open(os.path.join(path, fname)) as f:
            add_snapshot_diff(row, f)


    def name(self): return os.path.split(self._path)[-1]
    def filename(self): return self._path
    def dimension_names(self): return self._column_names
    def dimension_units(self): return self._units
    def npoints(self): return len(self._data)
    def data(self): return self._data

    def comments(self):
      return self._comments

    def settings(self):
      return self._snapshots

    def __getitem__(self, key):
      return self._data[:, self._column_name_to_index[key]]

    @staticmethod
    def _parse_timestamp(s):
      t = datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S.%f')
      return (t.astimezone() - UNIX_EPOCH).total_seconds()

    @staticmethod
    def _parse_columns_from_header(s):
      try:
        # Try assuming the "Column name (unit)\t" format in pdata
        cols = []
        units = []
        for c in s.split('\t'):
          m = re.match(r'([\w\d\s]+)\s+\(([\w\d\s]*)\)', c.strip())
          cols.append(m.group(1))
          units.append(m.group(2))

      except AttributeError:
        # Try assuming the legacy format used in QCoDeS (qcodes/data/gnuplot_format.py)
        s = s.split('\n')[-2] # Second to last header row contains the tab separated column names
        cols = [ c.strip().strip('"') for c in s.split('\t') ]
        units = [ '' for i in range(len(cols))]

      return cols, units

class DataView():
    '''
    Class for post-processing measurement data. Main features are:
      * Concatenating multiple separate data objects
      * Creating "virtual" columns by parsing comments or snapshot files
        or by applying arbitrary functions to the data
      * Dividing the rows into "sweeps" based on various criteria.

    See docs/examples/Procedural Data and DataView.ipynb for example use.
    '''

    def __init__(self, data, deep_copy=False, source_column_name='data_source', fill_value=None, **kwargs):
        '''
        Create a new view of existing data objects for post-processing.
        The original data objects will not be modified.

        args:
          data -- Data object(s). Each data object needs to provide the following methods:
                     * name()     # Arbitrary string identifier for the data object
                     * filename() # Specifies the path to the main datafile
                                      # (for identification/debugging purpose only)
                     * dimension_names() # List of all data column names
                     * dimension_units() # List of all data column units
                     * npoints()  # Number of data points/rows.
                     * data()     # 2D ndarray containing all data rows and columns.
                     * comments()  # List of tuples (data_row_no, comment string),
                                      #   where data_row_no indicated the index of
                                      #   the data point that the comment precedes.
                     * settings()  # List of tuples (data_row_no, settings dict),
                                      #   where data_row_no indicated the index of
                                      #   the data point that the settings apply to.

        kwargs input:
          deep_copy          -- specifies whether the underlying data is copied or 
                                only referenced (more error prone, but memory efficient)
          source_column_name -- specifies the name of the (virtual) column that tells which
                                data object the row originates from. Specify None, if
                                you don't want this column to be added.
          fill_value         -- fill value for columns that do not exist in all data objects.
                                Default is None, in which case the column is omitted entirely.
        '''

        self._virtual_dims = {}

        if isinstance(data, DataView): # clone
          # these private variables should be immutable so no need to deep copy
          self._dimensions = data._dimensions
          self._units = data._units
          self._dimension_indices = data._dimension_indices
          self._source_col = data._source_col
          self._comments = data._comments
          self._settings = data._settings
          
          if deep_copy:
            self._data = data._data.copy()
          else:
            self._data = data._data

          # Always deep copy the mask
          self._mask = data._mask.copy()

          for name, fn in data._virtual_dims.items():
              self._virtual_dims[name] = fn

          return

        try: # see if a single Data object
          self._dimensions = data.dimension_names()
          self._units = dict(zip(data.dimension_names(), data.dimension_units()))
          unmasked = data.data().copy() if deep_copy else data.data()
          
          if source_column_name != None:
            n = data.name()
            self._source_col = [n for i in range(data.npoints())]
          else:
            self._source_col = None

          self._comments = data.comments()

          try:
            self._settings = data.settings()
          except:
            logging.exception("Could not parse the instrument settings file. Doesn't matter if you were not planning to add virtual columns based on values in the snapshot files.")
            self._settings = None

        except MemoryError as e:
          raise

        except Exception as e: # probably a sequence of Data objects then
          self._dimensions = set(itertools.chain( *(dd.dimension_names() for dd in data) ))
          
          unmasked = {}
          for dim in self._dimensions:
            unmasked[dim] = []
            for dat in data:
              if len(dat.dimension_names()) == 0:
                logging.warn("Data object '%s' seems to contain zero columns. Skipping it..." % (str(dat)))
                break

              n_rows = dat.npoints()
              if n_rows == 0:
                logging.warn("Data object '%s' seems to contain zero rows. Skipping it..." % (str(dat)))
                break

              try:
                unmasked[dim].append(dat[dim])
              except:
                msg = "Dimension '%s' does not exist in Data object '%s'. " % (dim, str(dat))
                if fill_value == None:
                  # ignore dimensions that don't exist in all data objects
                  del unmasked[dim]
                  msg += ' Omitting the dimension.'
                  logging.warn(msg)
                  break
                else:
                  unmasked[dim].append(fill_value + np.zeros(n_rows, dtype=type(fill_value)))
                  msg += ' Using fill_value = %s (for %d rows)' % (str(fill_value), len(unmasked[dim][-1]))
                  logging.warn(msg)

            # concatenate rows from all files
            if dim in unmasked.keys():
              unmasked[dim] = np.concatenate(unmasked[dim])
          
          # add a column that specifies the source data file
          lens = [ dat.npoints() for dat in data ]
          if source_column_name != None:
            names = [ '%s_(%s)' % (dat.name(), dat.filename().strip('.dat')) for dat in data ]
            self._source_col = [ [n for jj in range(l)] for n,l in zip(names,lens) ]
            #self._source_col = [ jj for jj in itertools.chain.from_iterable(self._source_col) ] # flatten
            self._source_col = list(itertools.chain.from_iterable(self._source_col)) # flatten
          else:
            self._source_col = None
          
          # keep only dimensions that could be parsed from all files
          self._dimensions = unmasked.keys()
          unmasked = np.array([unmasked[k] for k in self._dimensions]).T

          # take units from first data set
          self._units = dict(zip(data[0].dimension_names(), data[0].dimension_units()))

          # concatenate comments, adjusting row numbers from Data object rows to the corresponding dataview rows
          lens = np.array(lens)

          self._comments = [ dat.comments() for dat in data ]
          all_comments = []
          for jj,comments in enumerate(self._comments):
              all_comments.append([ (rowno + lens[:jj].sum(), commentstr) for rowno,commentstr in comments ])
          self._comments = list(itertools.chain.from_iterable(all_comments)) # flatten by one level

          # concatenate settings (snapshot) files in the same way
          self._settings = [ dat.settings() for dat in data ]
          all_settings = []
          for jj,settings in enumerate(self._settings):
              all_settings.append([ (rowno + lens[:jj].sum(), sett) for rowno,sett in settings ])
          self._settings = list(itertools.chain.from_iterable(all_settings)) # flatten by one level

        self._data = unmasked
        self._mask = np.zeros(len(unmasked), dtype=bool)
        self._mask_stack = []

        self._dimension_indices = dict([(n,i) for i,n in enumerate(self._dimensions)])
        self.set_mask(False)

        if source_column_name != None:
          self.add_virtual_dimension(source_column_name, arr=np.array(self._source_col))

    def __getitem__(self, index):
        '''
        Access the data.

        index may be a slice or a string, in which case it is interpreted
        as a dimension name.
        '''
        if isinstance(index, str):
            return self.column(index)
        else:
            return self.data()[index]

    def copy(self, copy_data=False):
        '''
        Make a copy of the view. The returned copy will always have an independent mask.
        
        copy_data -- whether the underlying data is also deep copied.
        '''
        return DataView(self, deep_copy=copy_data)

    def data_source(self):
        '''
        Returns a list of strings that tell which Data object each of the unmasked rows originated from.
        '''
        return [ i for i in itertools.compress(self._source_col, ~(self._mask)) ]

    def clear_mask(self):
        '''
        Unmask all data (i.e. make all data in the initially
        provided Data object visible again).
        '''
        self._mask[:] = False
        self._mask_stack = []

    def mask(self):
        '''
        Get a vector of booleans indicating which rows are masked.
        '''
        return self._mask.copy()

    def dimensions(self):
        '''
        Returns a list of all dimensions, both real and virtual.
        '''
        return list(itertools.chain(self._dimension_indices.keys(), self._virtual_dims.keys()))

    def units(self, d):
        '''
        Returns the units for dimension d
        '''
        return self._units[d]

    def comments(self):
        '''
        Return the comments parsed from the data files.

        Returns tuples where the first item is an index to the
        first datarow that the comment applies to.
        '''
        return self._comments

    def settings(self):
        '''
        Return the settings parsed from the settings files.

        Returns tuples where the first item is an index to the
        first datarow that the settings apply to.
        '''
        return self._settings

    def continuous_ranges(self, masked_ranges=False):
        '''
        Returns a list of (start,stop) tuples that indicate continuous ranges of (un)masked data.
        '''
        m = self.mask() * (-1 if masked_ranges else 1)
        
        dm = m[1:] - m[:-1]
        starts = 1+np.where(dm < 0)[0]
        stops = 1+np.where(dm > 0)[0]

        if not m[0]:
            starts = np.concatenate(( [0], starts ))
        if not m[-1]:
            stops = np.concatenate(( stops, [len(m)] ))

        return zip(starts, stops)

    def set_mask(self, mask):
        '''
        Set an arbitrary mask for the data. Should be a vector of booleans of
        the same length as the number of data points.
        Alternatively, simply True/False masks/unmasks all data.

        See also mask_rows().
        '''
        try:
          if mask:
            self._mask[:] = True
          else:
            self._mask[:] = False
        except:
          m = np.zeros(len(self._mask), dtype=bool)
          m[mask] = True
          self._mask = m

    def mask_rows(self, row_mask, unmask_instead = False):
        '''
        Mask rows in the data. row_mask can be a slice or a boolean vector with
        length equal to the number of previously unmasked rows.

        The old mask is determined from the mask of the first column.

        Example:
          d = DataView(...)
          # ignore points where source current exceeds 1 uA.
          d.mask_rows(np.abs(d['I_source']) > 1e-6)
        '''
        old_mask = self._mask
        n = (~old_mask).astype(int).sum() # no. of previously unmasked entries
        #logging.debug("previously unmasked rows = %d" % n)

        # new mask for the previously unmasked rows
        new_mask = np.empty(n, dtype=bool); new_mask[:] = unmask_instead
        new_mask[row_mask] = (not unmask_instead)
        #logging.debug("new_mask.sum() = %d" % new_mask.sum())

        # combine the old and new masks
        full_mask = old_mask.copy()
        full_mask[~old_mask] = new_mask

        logging.debug("# of masked/unmasked rows = %d/%d" % (full_mask.astype(int).sum(), (~full_mask).astype(int).sum()))
        self.set_mask(full_mask)

    def push_mask(self, mask, unmask_instead = False):
        '''
        Same as mask_rows(), but also pushes the mask to a 'mask stack'.
        Handy for temporary masks e.g. inside loops.
        See also pop_mask().
        '''
        self._mask_stack.append(self.mask())
        self.mask_rows(mask, unmask_instead = unmask_instead)

    def pop_mask(self):
        '''
        Pop the topmost mask from the mask stack,
        set previous mask in the stack as current one
        and return the popped mask.
        Raises an exception if trying to pop an empty stack.
        '''
        try:
          previous_mask = self._mask_stack.pop()
        except IndexError as e:
          raise Exception("Trying to pop empty mask stack: %s" % e)

        self.set_mask(previous_mask)
        return previous_mask

    def remove_masked_rows_permanently(self):
        '''
        Removes the currently masked rows permanently.

        This is typically unnecessary, but may be useful
        before adding (cached) virtual columns to
        huge data sets where most rows are masked (because
        the cached virtual columns are computed for
        masked rows as well.)
        '''
        # Removing the real data rows themselves is easy.
        self._data = self._data[~(self._mask),:]
        
        # but we have to also adjust the comment & settings line numbers
        s = np.cumsum(self._mask.astype(int))
        def n_masked_before_line(lineno): return s[max(0, min(len(s)-1, lineno-1))]
        self._comments = [ (max(0,lineno-n_masked_before_line(lineno)), comment) for lineno,comment in self._comments ]
        self._settings = [ (max(0,lineno-n_masked_before_line(lineno)), setting) for lineno,setting in self._settings ]

        # as well as remove the masked rows from cached virtual columns.
        # However, _virtual_dims is assumed to be immutable in copy() so
        # we must copy it here!
        old_dims = self._virtual_dims
        self._virtual_dims = {}
        for name, dim in old_dims.iteritems():
          cached_arr = dim['cached_array']
          if isinstance(cached_arr, np.ndarray):
            cached_arr = cached_arr[~(self._mask)]
          elif cached_arr != None:
            cached_arr = [ val for i,val in enumerate(cached_arr) if not self._mask[i] ]
          self._virtual_dims[name] = { 'fn': dim['fn'], 'cached_array': cached_arr }

        # finally remove the obsolete mask(s)
        self._mask = np.zeros(len(self._data), dtype=bool)
        self._mask_stack = []

    def single_valued_parameter(self, param):
        ''' If all values in the (virtual) dimension "param" are the same, return that value. '''
        assert len(np.unique(self[param])) == 1 or (all(np.isnan(self[param])) and len(self[param]) > 0), \
            '%s is not single valued for the current unmasked rows: %s' % (param, np.unique(self[param]))
        return self[param][0]

    def all_single_valued_parameters(self):
        params = OrderedDict()
        for p in self.dimensions():
          try: params[p] = self.single_valued_parameter(p)
          except: pass
        return params

    def divide_into_sweeps(self, sweep_dimension, use_sweep_direction = None):
        '''Divide the rows into "sweeps" based on a monotonously increasing
        or decreasing value of column "sweep_dimension", if use_sweep_direction==True.

        If use_sweep_direction==False, sequences of points where
        "sweep_dimension" stays constant are considered sweeps. This
        is useful for splitting the data into sweeps based on a slowly
        varying parameter, e.g. a gate voltage set point that is
        changed between IV curve sweeps.

        If use_sweep_direction is None, this function tries to figure
        out which one is more reasonable.

        Returns a sequence of slices indicating the start and end of
        each sweep.

        Note that the indices are relative to the currently _unmasked_
        rows only.

        '''
        sdim = self[sweep_dimension]

        if isinstance(sdim[0], str):
          use_sweep_direction = False
          dx = np.array([ sdim[i+1] != sdim[i] for i in range(len(sdim)-1) ])
        else:
          dx = np.sign(sdim[1:] - sdim[:-1])

        if use_sweep_direction == None:
          use_sweep_direction = ( np.abs(dx).astype(int).sum() > len(dx)/4. )

        if use_sweep_direction:
          logging.info("Assuming '%s' is swept." % sweep_dimension)
        else:
          logging.info("Assuming '%s' stays constant within a sweep." % sweep_dimension)

        if use_sweep_direction:
          for i in range(1,len(dx)):
              if i+1 < len(dx) and dx[i] == 0: dx[i]=dx[i+1] # this is necessary to detect changes in direction, when the end point is repeated
          change_in_sign = (2 + np.array(np.where(dx[1:] * dx[:-1] < 0),dtype=int).reshape((-1))).tolist()

          # the direction changing twice in a row means that sweeps are being done repeatedly
          # in the same direction.
          for i in range(len(change_in_sign)-1, 0, -1):
            if change_in_sign[i]-change_in_sign[i-1] == 1: del change_in_sign[i]

          if len(change_in_sign) == 0: return [ slice(0, len(sdim)) ]

          start_indices = np.concatenate(([0], change_in_sign))
          stop_indices  = np.concatenate((change_in_sign, [len(sdim)]))

          sweeps = np.concatenate((start_indices, stop_indices)).reshape((2,-1)).T
        else:
          change_in_sdim = 1 + np.array(np.where(dx != 0)).reshape((-1))
          if len(change_in_sdim) == 0: return [ slice(0, len(sdim)) ]

          start_indices = np.concatenate(([0], change_in_sdim))
          stop_indices  = np.concatenate((change_in_sdim, [len(sdim)]))
        
          sweeps = np.concatenate((start_indices, stop_indices)).reshape((2,-1)).T

        return [ slice(max(s, 0), min(e, len(sdim))) for s,e in sweeps ]

    def mask_sweeps(self, sweep_dimension, sl, unmask_instead=False):
        '''
        Mask entire sweeps (see divide_into_sweeps()).

        sl can be a single integer or any slice object compatible with a 1D numpy.ndarray (list of sweeps).

        unmask_instead -- unmask the specified sweeps instead, mask everything else
        '''
        sweeps = self.divide_into_sweeps(sweep_dimension)
        row_mask = np.zeros(len(self[sweep_dimension]), dtype=bool)
        for start,stop in ([sweeps[sl]] if isinstance(sl, int) else sweeps[sl]):
            logging.debug("%smasking start: %d, stop %d" % ('un' if unmask_instead else '',start, stop))
            row_mask[start:stop] = True
        self.mask_rows(~row_mask if unmask_instead else row_mask)


    def unmask_sweeps(self, sweep_dimension, sl):
        '''
        Mask all rows except the specified sweeps (see divide_into_sweeps()).

        sl can be a single integer or any slice object compatible with a 1D numpy.ndarray (list of sweeps).
        '''
        self.mask_sweeps(sweep_dimension, sl, unmask_instead=True)


    def data(self, deep_copy=False):
        '''
        Get the non-masked data as a 2D ndarray.

        kwargs:
          deep_copy -- copy the returned data so that it is safe to modify it.
        '''
        d = self._data[~(self._mask)]
        if deep_copy: d = d.copy()
        return d

    def column(self, name, deep_copy=False):
        '''
        Get the non-masked entries of dimension 'name' as a 1D ndarray.
        name is the dimension name.

        kwargs:
          deep_copy -- copy the returned data so that it is safe to modify it.
        '''
        if name in self._virtual_dims.keys():
            d = self._virtual_dims[name]['cached_array']
            if d is None: d = self._virtual_dims[name]['fn'](self)
            if len(d) == len(self._mask): # The function may return masked or unmasked data...
              # The function returned unmasked data so apply the mask
              try:
                d = d[~(self._mask)] # This works for ndarrays
              except:
                # workaround to mask native python arrays
                d = [ x for i,x in enumerate(d) if not self._mask[i] ]
            return d
        else:
            d = self._data[~(self._mask),self._dimension_indices[name]]
        
        if deep_copy: d = d.copy()
        return d

    non_numpy_array_warning_given = []
    def add_virtual_dimension(self, name, units="", fn=None, arr=None, comment_regex=None, from_set=None, dtype=float, preparser=None, cache_fn_values=True, return_result=False):
        '''
        Makes a computed vector accessible as self[name].
        The computed vector depends on whether fn, arr or comment_regex is specified.

        It is advisable that the computed vector is of the same length as
        the real data columns.
        
        kwargs:

          Arguments for specifying how to parse the value:

          fn            -- the function applied to the DataView object, i.e self[name] returns fn(self)
          arr           -- specify the column directly as an array, i.e. self[name] returns arr
          comment_regex -- for each row, take the value from the last match in a comment, otherwise np.NaN. Should be a regex string.
          from_set      -- for each row, take the value from the corresponding snapshot file. Specify as a tuple that indexes the settings dict ("instrument_name", "parameter_name", ...).

          Other options:

          dtype           -- data type (default: float)
          preparser       -- optional preparser function that massages the value before it is passed to dtype
          cache_fn_values -- evaluate fn(self) immediately for the entire (unmasked) array and cache the result
          return_result   -- return the result directly as an (nd)array instead of adding it as a virtual dimension
        '''
        logging.debug('adding virtual dimension "%s"' % name)

        assert (fn != None) + (arr is not None) + (comment_regex != None) + (from_set != None) == 1, 'You must specify exactly one of "fn", "arr", or "comment_regex".'

        if arr is not None:
          assert len(arr) == len(self._mask), '"arr" must be a vector of the same length as the real data columns. If you want to do something fancier, specify your own fn.'

        if from_set != None:
            assert self._settings != None, 'snapshot files were not successfully parsed during dataview initialization.'

        if comment_regex != None or from_set != None:
            # construct the column by parsing the comments or snapshots
            use_set = (from_set != None) # shorthand for convenience

            # pre-allocate an array for the values
            try:
              if issubclass(dtype, str):
                raise Exception('Do not store strings in numpy arrays (because it "works" but the behavior is unintuitive, i.e. only the first character is stored if you just specify dtype=str).')
              vals = np.zeros(len(self._mask), dtype=dtype)
              if dtype == float: vals += np.nan # initialize to NaN instead of zeros
            except:
              if not name in self.non_numpy_array_warning_given:
                logging.info("%s does not seem to be a numpy data type. The virtual column '%s' will be a native python array instead, which may be slow." % (str(dtype), name))
                self.non_numpy_array_warning_given.append(name)
              vals = [None for jjj in range(len(self._mask))]

            def set_vals(up_to_row, new_val):
              """
              Helper that sets values up to the specified row, starting from where we last left off.

              This is a little trickier than might seem at first because when we parse a new value,
              we don't yet know the row up to which it applies. Instead, we always set the previous value
              up to row where the new value appeared (and remember the new value for the next call).
              """
              if up_to_row > set_vals.prev_match_on_row:

                # Apply preparser() and dtype(() to the previously parsed value.
                #
                # It's good to do it only here because occasionally there may be multiple definitions for the 
                # same column and same row, usually on row zero.
                # These might not all have valid syntax for preparser/dtype()
                # so it's best to only parse the one that matters (the last one).
                v = set_vals.prev_val
                try:
                  if preparser != None: v = preparser(v)
                  v = dtype(v)
                except:
                  #logging.exception('Could not convert the parsed value (%s) to the specifed data type (%s).'
                  #                  % (v, dtype))
                  raise

                if isinstance(vals, np.ndarray): vals[set_vals.prev_match_on_row:up_to_row] = v
                else: vals[set_vals.prev_match_on_row:up_to_row] = ( v for jjj in range(up_to_row-set_vals.prev_match_on_row) )
                logging.debug('Setting value for rows %d:%d = %s' % (set_vals.prev_match_on_row, up_to_row, v))

              set_vals.prev_match_on_row = up_to_row
              set_vals.prev_val = new_val

            set_vals.prev_match_on_row = 0

            #logging.debug(self._comments)

            for rowno,commentstr in (self._settings if use_set else self._comments):
              if use_set:
                # simply use the value from the snapshot file
                assert from_set[0] in commentstr.keys(), '"%s" not found in settings.' % from_set[0]
                new_val = commentstr
                for k in from_set: new_val = new_val[k]
              else:
                # see if the comment matches the specified regex
                m = re.search(comment_regex, commentstr)
                if m == None: continue
                #logging.debug('Match on row %d: "%s"' % (rowno, commentstr))

                if len(m.groups()) != 1:
                  logging.warn('Did not get a unique match (%s) in comment (%d): %s'
                               % (str(groups), rowno, commentstr))
                new_val = m.group(1)

              set_vals(up_to_row=rowno, new_val=new_val)

            logging.debug('Setting value for (remaining) rows %d: = %s' % (set_vals.prev_match_on_row, set_vals.prev_val))
            set_vals(up_to_row=len(vals), new_val=None)
            

            return self.add_virtual_dimension(name, units=units, arr=vals, return_result=return_result)

        if cache_fn_values and arr is None:
            old_mask = self.mask().copy() # backup the mask
            self.clear_mask()
            vals = fn(self)
            self.mask_rows(old_mask) # restore the mask

            return self.add_virtual_dimension(name, units=units, arr=vals, cache_fn_values=False, return_result=return_result)

        if return_result:
          return arr
        else:
          self._virtual_dims[name] = {'fn': fn, 'cached_array': arr}
          self._units[name] = units

    def remove_virtual_dimension(self, name):
        if name in self._virtual_dims.keys():
            del self._virtual_dims[name]
        else:
            logging.warn('Virtual dimension "%s" does not exist.' % name)

    def remove_virtual_dimensions(self):
        self._virtual_dims = {}
