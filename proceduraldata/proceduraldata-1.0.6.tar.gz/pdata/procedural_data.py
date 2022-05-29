"""
Class for storing measurement data.
"""

from pdata._metadata import __version__

import os
import numpy as np
import time
import datetime
import logging
import shutil
import gzip
import tarfile
import contextlib
import json
import jsondiff
import tempfile
import random

from pdata.helpers import NumpyJSONEncoder, filter_timestamps
import pdata.jupyter_helpers

@contextlib.contextmanager
def run_measurement(get_snapshot,
                    columns, name,
                    data_base_dir='.',
                    dir_name_generator=lambda n: datetime.datetime.now().strftime(f"%Y-%m-%d_%H-%M-%S_{int(1e3*random.random())}") + f"_{n}",
                    autosnap=True, snap_diff_filter=filter_timestamps,
                    compress=True):
  '''
  A simple context manager that runs begin() and end()
  automatically, and gets an updated snapshot of instrument parameters
  each time data is added, using get_snapshot().

  columns defines the tabular data columns, see Measurement class.

  The directory name for storing the data set is:
    <data_base_dir>/<dir_name_generator(name)>

  By default, we filter out timestamps added by QCoDeS from snapshot diffs.

  If you're using QCoDeS, your get_snapshot funciton would typically look like this::

    import qcodes.station
    with run_measurement(lambda s=qcodes.station.Station.default: s.snapshot(update=True), ...) as m:
      ...
  
  '''
  target_dir = os.path.join(data_base_dir, dir_name_generator(name))

  m = Measurement(columns,
                  target_dir=target_dir,
                  get_snapshot=get_snapshot,
                  snap_diff_filter=snap_diff_filter,
                  autosnap=autosnap, compress=compress)

  m.begin()
  try:     yield m
  finally: m.end()



class Measurement():
  '''
  Writes data to a data table with fixed columns defined during __init__().

  The data directory contains the following:

    * :file:`tabular_data.dat` -- Data table with rows added using :code:`add_points`, and columns defined as arguments of :code:`run_measurement`.
    * :file:`snapshot.json` -- Instrument parameter snapshot when :code:`run_measurement` started.
    * :file:`snapshot.row-<n>.diff<m>.json` -- `jsondiff <https://pypi.org/project/jsondiff/>`_ of parameter changes, recorded when the there were <n> data rows in tabular_data.dat. <m> is a simple counter, in case multiple diffs are created for the same row.
    * :file:`log.txt` -- copy of messages from the logging module.
    * A copy of the Jupyter notebook (.ipynb) or other measurement script, if possible.

  Optionally, the files may be compressed (.gz or .tar.gz).

  Although the format is human readable in the simplest cases, it is
  meant to be parsed programmatically, i.e., by the dataview module
  (analysis/dataview.py).

  For more information, see https://pdata.readthedocs.io/en/latest/
  '''

  def __init__(self, columns, target_dir=None, get_snapshot=None,
               autosnap=True, snap_diff_filter=None, omit_readme=False,
               compress=True):
    '''
    Args:

      columns: a list of strings (column names) or tuples
               (<column name>, <units> [optional], <formatter> [optional]).
               Formatter should be a function that takes in a data point
               and turns it into a str written to the data file.

      target_dir: full path to where the data directory is to be created.

      get_snapshot: function that returns a dict of instrument settings.

      autosnap: create snapshot diffs automatically each time add_points()
                is called.

      snap_diff_filter: function applied to the snapshot before computing diffs;
                        useful for filtering things out (e.g. timestamps).

      omit_readme: don't create a README file in the data directory.

      compress: compress data files when measurement ends
    '''
    self._target_dir = target_dir
    self._get_snapshot = get_snapshot
    self._autosnap = True
    self._snap_diff_filter = snap_diff_filter
    self._omit_readme = omit_readme
    self._compress = compress

    self._npoints_total = 0
    self._last_snapshot = None


    self._columns = list()
    self._units = list()
    self._formatters = list()

    self._check_for_manual_abort()

    # Parse columns and units.
    # Units are optional.
    # The formatter is an optional function used for conversion to str.
    for x in columns:
      u = ""
      f = None
      if isinstance(x, str):
        c = x
      elif len(x) == 2:
        c,u = x
      elif len(x) == 3:
        c,u,f = x
      else:
        raise Exception('Did not understand column specification: %s' % x)

      self._columns.append(c)
      self._units.append(u)
      self._formatters.append(f)

      assert len(self._columns) == len(self._units)
      assert len(self._columns) == len(self._formatters)

  def path(self): return self._target_dir

  def begin(self):
    '''Creates the data directory, initial snapshot, etc.  Must be called
        before add_points(). The run_measurement() context manager
        calls this automatically.
    '''
    if self._target_dir == None:
      self._target_dir = str(datetime.datetime.now()).replace(".", "_").replace(":", "-").replace(" ", "_")

    parent_dir, target = os.path.split(self._target_dir)

    target = Measurement._path_friendly_str(target)

    # Append a number to target dir name if the dir already exists
    i = 2
    self._target_dir = os.path.join(parent_dir, target)
    while os.path.exists(self._target_dir):
      self._target_dir = os.path.join(parent_dir, '%s_%d' % (target, i))
      i += 1

    self._check_for_manual_abort()

    os.makedirs(self._target_dir)

    self._write_readme()
    self._open_log_file()
    self._copy_jupyter_notebook()
    self.write_snapshot()

    self._dat_file = open(os.path.join(self._target_dir, 'tabular_data.dat'), 'w')

    # Write a header, to some extent compatible with the "legacy" QCoDeS format.
    self._dat_file.write("#\n")
    self._dat_file.write("# " + "\t".join("%s (%s)" % (c,u) for c,u in zip(self._columns, self._units)) + "\n")
    self._dat_file.write("#\n")

  def end(self):
    '''Ends the measurement, i.e. closes and compresses the data set
        files. The run_measurement() context manager calls this
        automatically.
    '''
    self._close_dat_file()
    self._close_log_file()

  def add_points(self, data, snap=None):
    '''Add rows to the data table.

        The values for the columns are given
        as a dicitonary of the form::

            { 'column name 1': <array of values>,
              'column name 2': ... }.

       snap=True/False can override the "autosnap" option
       specified in __init__.
    '''

    for k in data.keys(): assert k in self._columns, '"%s" is not a column in the data table.' % k

    for k in self._columns: assert k in data.keys(), 'You need to pass "%s" as a keyword argument to append_data.' % k

    npts = len(data[self._columns[0]])
    assert all(len(data[k]) == npts for k in data.keys()), 'All appended data columns must be vectors of the same length.'

    if self._npoints_total == 0 and npts>0: self._guess_missing_formatters(data)

    if snap or (snap == None and self._autosnap): self.write_snapshot()

    for i in range(npts):
      self._dat_file.write("\t".join(f(data[c][i]) for c,f in zip(self._columns, self._formatters)))
      self._dat_file.write("\n")

    self._dat_file.flush()
    self._npoints_total += npts

    self._check_for_manual_abort()

  def add_point(self, data, snap=None):
    ''' Same as add_points but takes scalar inputs for the column values. '''
    self.add_points(dict( (k, [ data[k] ]) for k in data.keys() ),
                    snap=snap)

  def write_snapshot(self, snap=None):
    '''Add a snapshot (delta) file to the data directory. This is called
automatically whenever you call add_points(), unless you disabled
autosnapping.'''
    if snap==None:
      snap = self._get_snapshot()

    if self._last_snapshot == None:
      with open(os.path.join(self._target_dir, 'snapshot.json'), 'w') as fsnap:
        Measurement._dump_json(snap, fsnap)

      # Filter _after_ writing initial snapshot.
      if self._snap_diff_filter != None: snap = self._snap_diff_filter(snap)

    else:

      if self._snap_diff_filter != None: snap = self._snap_diff_filter(snap)
      d = jsondiff.diff(self._last_snapshot, snap)

      if len(d.keys()) == 0: return

      i = 0
      while True:
        fname = os.path.join(self._target_dir,
                             'snapshot.row-%u.diff%u.json' % (self._npoints_total, i))
        if not os.path.exists(fname): break

      with open(fname, 'w') as fsnap: Measurement._dump_json(d, fsnap, is_diff=True)

    self._last_snapshot = snap

  def _guess_missing_formatters(self, data):
    '''Given the first points added to the data file, assign reasonable
        formatters for columns that didn't have one manually specified.
    '''

    for i,c in enumerate(self._columns):
      if self._formatters[i] != None: continue

      if isinstance(data[c][0], float):
        self._formatters[i] = lambda x: "%.12e" % x
      else:
        self._formatters[i] = str

  def _open_log_file(self):
    ''' Open a secondary log file in the data directory. '''
    fn = os.path.join(self._target_dir, 'log.txt')
    if len(logging.getLogger().handlers) > 0:
      formatter = logging.getLogger().handlers[0].formatter
    else:
      formatter = None

    self._log_file_handler = logging.FileHandler(fn)
    self._log_file_handler.setLevel(logging.getLogger().level)
    self._log_file_handler.setFormatter(formatter)

    logging.getLogger().addHandler(self._log_file_handler)
    logging.debug('Added log_file_handler. path="%s", formatter="%s"' % (fn, str(formatter)))

  def _close_dat_file(self):
    self._dat_file.close()

    if self._compress:

      def gzip_file(fname):
        with open(fname, 'rb') as f_in:
          with gzip.open(fname + '.gz', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
        os.remove(fname) # Remove original

      def tar_files(data_files, tar_name):
        with tarfile.open(os.path.join(self._target_dir, tar_name + '.tar.gz'),
                          'w:gz') as tar:
          for f in data_files:
            tar.add(f, arcname=os.path.split(f)[-1])
        for f in data_files: os.remove(f) # Remove originals

      # Compress tabular_data.dat
      gzip_file( os.path.join(self._target_dir, 'tabular_data.dat') )

      # Compress snapshot.json
      gzip_file( os.path.join(self._target_dir, 'snapshot.json') )

      # Add snapshot diffs to a compressed tar file.
      tar_files([ os.path.join(self._target_dir, f)
                  for f in os.listdir(self._target_dir)
                  if f.startswith('snapshot.row-') ],
                'snapshot_diffs')


  def _close_log_file(self):
    logging.getLogger().removeHandler(self._log_file_handler)
    self._log_file_handler.close()
    self._log_file_handler = None

  def _copy_jupyter_notebook(self):
    ''' Saves the current notebook (if any) and copies it to the data directory. '''
    try:
      fname = pdata.jupyter_helpers.get_notebook_name()
      if fname == None: return # Not running within Jupyter

      pdata.jupyter_helpers.save_notebook()
      shutil.copyfile(fname, os.path.join(self._target_dir, os.path.split(fname)[1]))
    except:
      logging.exception(f"Failed to copy measurement Jupyter notebook to {self.path()}. Starting experiment anyway.")

  def _write_readme(self):
    '''
    Creates a README file the the data directory with a brief
    description of the data format.
    '''
    if self._omit_readme: return

    with open(os.path.join(self._target_dir, 'README'), 'w') as f:
      f.write('This data directory was created by the '
              'pdata.procedural_data module at\n'
              '%s.\n\n' % datetime.datetime.now())

      f.write('The docsctring of the main Measurement class '
              'describes the data format:\n\n')

      f.write(Measurement.__doc__)

  def _check_for_manual_abort(self):
    try:
      t = os.path.getmtime(abort_signal_file)
    except FileNotFoundError:
      t = None

    if not hasattr(self, '_abort_signal_initial_mtime'):
      self._abort_signal_initial_mtime = t
      return

    if t != self._abort_signal_initial_mtime: raise Exception('Measurement aborted manually.')

  @staticmethod
  def _dump_json(snap, fhandle, is_diff=False):
    json.dump(snap, fhandle, sort_keys=False,
              indent=2, ensure_ascii=False, cls=NumpyJSONEncoder)

  @staticmethod
  def _path_friendly_str(s):
    def acceptable_char(x): return x.isalnum() or x in ['#', '-', '=']
    return "".join(x if acceptable_char(x) else '_' for x in s)


# A bit of a hack allowing controllably aborting a measurement
# from another process on the same machine.
abort_signal_file = os.path.join(tempfile.gettempdir(),
                                 'pdata.abort-measurements.signal')
def abort_measurements():
  '''Abort all measurements running on this machine after their next
  call to add_points(), which is presumably a safe time to abort. Can
  be called from an independent process running on the same machine.
  '''
  with open(abort_signal_file, 'w') as f:
    f.write('Manual abort called for at %s\n' % datetime.datetime.now())
