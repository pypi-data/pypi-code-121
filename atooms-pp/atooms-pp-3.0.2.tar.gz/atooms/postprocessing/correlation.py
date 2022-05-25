# This file is part of atooms
# Copyright 2010-2018, Daniele Coslovich

"""Base correlation function."""

import os
import logging
from collections import defaultdict

import numpy
from atooms.trajectory import Trajectory
from atooms.trajectory.decorators import Unfolded, fold
from atooms.trajectory.decorators import change_species
from atooms.system.particle import distinct_species
from atooms.core.utils import Timer
try:
    from medepy.metadata import dump as _dump
except ImportError:
    from .helpers import _dump

from . import core
from .helpers import adjust_skip
from .progress import progress

__all__ = ['acf', 'gcf', 'gcf_offset', 'Correlation']

_log = logging.getLogger(__name__)


def acf(grid, skip, t, x):
    """
    Auto correlation function.

    Calculate the correlation between time t(i0) and t(i0+i)
    for all possible pairs (i0,i) provided by grid.
    """
    cf = defaultdict(float)
    cnt = defaultdict(int)
    xave = numpy.average(x)
    for i in grid:
        for i0 in range(0, len(x)-i, skip):
            # Get the actual time difference
            dt = t[i0+i] - t[i0]
            cf[dt] += (x[i0+i]-xave) * (x[i0]-xave)
            cnt[dt] += 1

    # Return the ACF with the time differences sorted
    dt = sorted(cf.keys())
    return dt, [cf[ti] / cnt[ti] for ti in dt], cnt


def gcf(f, grid, skip, t, x):
    """
    Generalized auto-correlation function <f(x[i], x[i0])>

    Pass a function `f` to apply to the data at each frame.

    Exemple: mean square displacement.
    """
    # Calculate the correlation between time t(i0) and t(i0+i)
    # for all possible pairs (i0,i) provided by grid
    cf = defaultdict(float)
    cnt = defaultdict(int)
    for i in grid:
        # Note: len(x) gives x.shape[0]
        for i0 in progress(range(0, len(x)-i-1, skip)):
            # Get the actual time difference
            dt = t[i0+i] - t[i0]
            cf[dt] += f(x[i0+i], x[i0])
            cnt[dt] += 1

    # Return the ACF with the time differences sorted
    dt = sorted(cf.keys())
    return dt, [cf[ti] / cnt[ti] for ti in dt], [cnt[ti] for ti in dt]


def gcf_offset(f, grid, skip, t, x):
    """
    Generalized auto-correlation function <f(x[i], x[i0])> using a grid with offsets

    Pass a function `f` to apply to the data `x` at each frame.

    Exemple: mean square displacement.
    """
    # Calculate the correlation between time t(i0) and t(i0+i)
    # for all possible pairs (i0,i) provided by grid
    cf = defaultdict(float)
    cnt = defaultdict(int)
    # Standard calculation
    for off, i in progress(grid, total=len(grid)):
        for i0 in range(off, len(x)-i, skip):
            # Get the actual time difference
            dt = t[i0+i] - t[i0]
            cf[dt] += f(x[i0+i], x[i0])
            cnt[dt] += 1

    # Return the ACF with the time differences sorted
    dt = sorted(cf.keys())
    return dt, [cf[ti] / cnt[ti] for ti in dt]


def _subtract_mean(weight):
    mean = 0
    for current_field in weight:
        mean += current_field.mean()
    mean /= len(weight)
    for current_field in weight:
        current_field -= mean
    return weight


class Correlation(object):
    """
    Base class for correlation functions.

    The correlation function is calculated for the trajectory `trj`. This can be:

    - an object implementing the atooms `Trajectory` interface
    - the path to a trajectory file in a format recognized by atooms

    A correlation function A(x) is defined over a grid of real
    entries {x_i} given by the list `grid`. To each entry of the grid,
    the correlation function has a corresponding value A_i=A(x_i). The
    latter values are stored in the `value` list.

    Correlation functions that depend on several variables, A(x,y,...)
    must provide a list of grids, one for each variable. The order is
    one specified by the `symbol` class variable, see below.

    The correlation function A is calculated as a statistical average
    over several time origins in the trajectory `trj`. The `norigins`
    variable can be used to tune the number of time origins used to
    carry out the average. `norigins` can take the following values:

    - `norigins=-1`: all origins are used
    - an integer >= 1: use only `n_origins` time origins
    - a float in the interval (0,1): use only a fraction `norigins` of frames as time origins
    - `None`: a heuristics is used to keep the product of steps times particles constant

    Subclasses must provide a symbolic expression of the correlation
    function through the `symbol` class variable. The following
    convention is used: if a correlation function A depends on
    variables x and y, then `symbol = 'A(x,y)'`.

    The `phasespace` variable allow subclasses to access a list of 2d
    numpy arrays with particles coordinates via the following private
    variables:

    - if `nbodies` is 1: `self._pos` for positions, `self._vel` for
    velocities, `self._unf_pos` for PBC-unfolded positions

    - if `nbodies` is 2, an additional suffix that take values 0 or 1
    is added to distinguish the two sets of particles,
    e.g. `self._pos_0` and `self._pos_1`
    """

    nbodies = 1
    """
    Class variable that controls the number of bodies, i.e. particles,
    associated to the correlation function. This variable controls the
    internal arrays used to compute the correlation, see `phasespace`.
    """
    static = False
    """
    Turn this to `True` is the correlation function is static,
    i.e. not time-dependent. This may enable some optimizations.
    """
    symbol = ''
    """Example: fskt"""
    short_name = ''
    """Example: F_s(k,t)"""
    long_name = ''
    """Example: Self intermediate scattering function"""
    phasespace = ['pos', 'pos-unf', 'vel']
    """
    List of strings or string among ['pos', 'pos-unf', 'vel']. It
    indicates which variables should be read from the trajectory file.
    They will be available as self._pos, self._pos_unf, self._vel.
    """

    def __init__(self, trj, grid, output_path=None, norigins=None, fix_cm=False):
        # Accept a trajectory-like instance or a path to a trajectory
        if isinstance(trj, str):
            self.trajectory = Trajectory(trj, mode='r', fmt=core.pp_trajectory_format)
        else:
            self.trajectory = trj
        self._fix_cm = fix_cm
        self._unfolded = None
        self.grid = grid
        self.value = []
        self.analysis = {}
        self.comments = None  # can be modified by user at run time
        self.tag = ''
        self.tag_description = 'the whole system'
        self.output_path = output_path if output_path is not None else core.pp_output_path
        self.skip = adjust_skip(self.trajectory, norigins)

        # Callbacks
        self._cbk = []
        self._cbk_args = []
        self._cbk_kwargs = []

        # Lists for one body correlations
        self._pos = []
        self._vel = []
        self._ids = []
        self._pos_unf = []

        # Lists for two-body correlations
        self._pos_0, self._pos_1 = [], []
        self._vel_0, self._vel_1 = [], []
        self._ids_0, self._ids_1 = [], []
        self._pos_unf_0, self._pos_unf_1 = [], []

        # Weights
        self._weight = None
        self._weight_0, self._weight_1 = None, None
        self._weight_field = None
        self._weight_fluctuations = False

    def __str__(self):
        return '{} at <{}>'.format(self.long_name, id(self))

    def add_weight(self, trajectory=None, field=None, fluctuations=False):
        """
        Add weight from the given `field` in `trajectory`

        If `trajectory` is `None`, `self.trajectory` will be used and
        `field` must be a particle property.

        If `field` is `None`, `trajectory` is assumed to be a path an
        xyz trajectory and we use the data in last column as a weight.

        If both `field` and `trajectory` are `None` the function
        returns immediately and the weight is not set.

        The optional `fluctuations` option subtracts the mean,
        calculated from the ensemble average, from the weight.
        """
        if trajectory is None and field is None:
            return

        self._weight = []
        self._weight_fluctuations = fluctuations

        # Guessing the field from the last column of an xyz file is
        # not supported anymore
        if field is None:
            raise ValueError('provide field to use as weight')
        else:
            self._weight_field = field

        # By default we use the same trajectory as for the phasespace
        if trajectory is None:
            self._weight_trajectory = self.trajectory
        else:
            self._weight_trajectory = trajectory
            # Copy over the field
            from .helpers import copy_field
            self.trajectory.add_callback(copy_field, self._weight_field, self._weight_trajectory)

        # Make sure the steps are consistent
        if self._weight_trajectory.steps != self.trajectory.steps:
            raise ValueError('inconsistency between weight trajectory and trajectory')

        # Modify tag
        fluct = 'fluctuations' if self._weight_fluctuations else ''
        self.tag_description += ' with {} {} field'.format(self._weight_field.replace('_', ' '), fluct)
        self.tag_description = self.tag_description.replace('  ', ' ')
        self.tag += '.{}_{}'.format(self._weight_field, fluct)
        self.tag.strip('_.')

    def add_filter(self, cbk, *args, **kwargs):
        """Add filter callback `cbk` along with positional and keyword arguments"""
        if len(self._cbk) > self.nbodies:
            raise ValueError('number of filters cannot exceed n. of bodies')
        self._cbk.append(cbk)
        self._cbk_args.append(args)
        self._cbk_kwargs.append(kwargs)

    def need_update(self):
        """Check if the trajectory file is newer than the output file"""
        need = True
        if os.path.exists(self._output_file) and self._output_file != '/dev/stdout':
            if os.path.getmtime(self.trajectory.filename) < \
               os.path.getmtime(self._output_file):
                need = False
        return need

    def _setup_arrays(self):
        """
        Dump positions and/or velocities at different time frames as a
        list of numpy array.
        """
        # TODO: what happens if we call compute twice?? Shouldnt we reset the arrays?
        # Ensure phasespace is a list.
        # It may not be a class variable anymore after this
        if not isinstance(self.phasespace, list) and \
           not isinstance(self.phasespace, tuple):
            self.phasespace = [self.phasespace]

        # Setup arrays
        if self.nbodies == 1:
            self._setup_arrays_onebody()
            self._setup_weight_onebody()
        elif self.nbodies == 2:
            self._setup_arrays_twobody()
            self._setup_weight_twobody()

    def _setup_arrays_onebody(self):
        """
        Setup list of numpy arrays for one-body correlations.

        We also take care of dumping the weight if needed, see
        `add_weight()`.
        """
        # Local shortcut
        th = self.trajectory

        # We unfold the trajectory if phasespace requests it and
        # unfolded positions are not available in the trajectory, or
        # if we request folded positions with fixed center of mass
        if ('pos-unf' in self.phasespace and not hasattr(th[0].particle[0], 'position_unfolded')) or \
           ('pos' in self.phasespace and self._fix_cm):
            # We unfold the positions, caching the trajectory
            if self._unfolded is None:
                self._unfolded = Unfolded(self.trajectory, fixed_cm=self._fix_cm)
                # We must fold positions back in this case
                if 'pos' in self.phasespace:
                    self._unfolded.add_callback(fold)
            # Change the local shortcut to the unfolded trajectory
            th = self._unfolded

        # Read everything except unfolded trajectories
        if 'pos' in self.phasespace or 'vel' in self.phasespace or 'ids' in self.phasespace:
            ids = distinct_species(th[0].particle)
            for s in progress(th):
                # Apply filter if there is one
                if len(self._cbk) > 0:
                    s = self._cbk[0](s, *self._cbk_args[0], **self._cbk_kwargs[0])
                if 'pos' in self.phasespace:
                    self._pos.append(s.dump('pos'))
                if 'vel' in self.phasespace:
                    self._vel.append(s.dump('vel'))
                if 'ids' in self.phasespace:
                    _ids = s.dump('species')
                    _ids = numpy.array([ids.index(_) for _ in _ids], dtype=numpy.int32)
                    self._ids.append(_ids)

        # Read unfolded positions if requested
        if 'pos-unf' in self.phasespace:
            if hasattr(th[0].particle[0], 'position_unfolded'):
                # Unfolded positions are present in the trajectory
                for s in progress(th):
                    # Apply filter if there is one
                    if len(self._cbk) > 0:
                        s = self._cbk[0](s, *self._cbk_args[0], **self._cbk_kwargs[0])
                    # Fixing the CM must be done explicitly using
                    # particle.position_unfolded because atooms.system
                    # methods work with particle.position
                    # TODO: can be revised with atooms 3.4.0
                    if self._fix_cm:
                        # Compute CM using unfolded positions, which is safe
                        cm = numpy.zeros_like(s.particle[0].position_unfolded)
                        mtot = 0.0
                        for p in s.particle:
                            cm += p.position_unfolded * p.mass
                            mtot += p.mass
                        cm /= mtot
                        # Subtract it
                        for p in s.particle:
                            p.position_unfolded -= cm
                    self._pos_unf.append(s.dump('particle.position_unfolded'))
            else:
                for s in progress(th):
                    # Apply filter if there is one
                    if len(self._cbk) > 0:
                        s = self._cbk[0](s, *self._cbk_args[0], **self._cbk_kwargs[0])
                    self._pos_unf.append(s.dump('pos'))

    def _setup_weight_onebody(self):
        """
        Setup list of numpy arrays for the weight, see `add_weight()`
        """
        if self._weight is None:
            return

        # Dump arrays of weights
        for s in progress(self.trajectory):
            # Apply filter if there is one
            # TODO: fix when weight trajectory does not contain actual particle info
            # It should be possible to link the weight trajectory to the trajectory
            # and return the trajectory particles with the weight
            if len(self._cbk) > 0:
                s = self._cbk[0](s, *self._cbk_args[0], **self._cbk_kwargs[0])
            current_weight = s.dump('particle.%s' % self._weight_field)
            self._weight.append(current_weight)

        # Subtract global mean
        if self._weight_fluctuations:
            _subtract_mean(self._weight)

    def _setup_weight_twobody(self):
        """
        Setup list of numpy arrays for the weight, see `add_weight()`
        """
        if self._weight is None:
            return

        self._weight = []
        self._weight_0 = []
        self._weight_1 = []

        # TODO: add checks on number of filters
        if len(self._cbk) <= 1:
            self._setup_weight_onebody()
            self._weight_0 = self._weight
            self._weight_1 = self._weight
            return

        # Dump arrays of weights
        for s in progress(self.trajectory):
            # Apply filters
            if len(self._cbk) == 2:
                s0 = self._cbk[0](s, *self._cbk_args[0], **self._cbk_kwargs[0])
                s1 = self._cbk[1](s, *self._cbk_args[1], **self._cbk_kwargs[1])
            self._weight_0.append(s0.dump('particle.%s' % self._weight_field))
            self._weight_1.append(s1.dump('particle.%s' % self._weight_field))

        # Subtract global mean
        if self._weight_fluctuations:
            _subtract_mean(self._weight_0)
            _subtract_mean(self._weight_1)

    def _setup_arrays_twobody(self):
        """Setup list of numpy arrays for two-body correlations."""
        if len(self._cbk) <= 1:
            self._setup_arrays_onebody()
            self._pos_0 = self._pos
            self._pos_1 = self._pos
            self._vel_0 = self._vel
            self._vel_1 = self._vel
            self._ids_0 = self._ids
            self._ids_1 = self._ids
            return

        if 'pos' in self.phasespace or 'vel' in self.phasespace or 'ids' in self.phasespace:
            ids = distinct_species(self.trajectory[0].particle)
            for s in progress(self.trajectory):
                s0 = self._cbk[0](s, *self._cbk_args[0], **self._cbk_kwargs[0])
                s1 = self._cbk[1](s, *self._cbk_args[1], **self._cbk_kwargs[1])
                if 'pos' in self.phasespace:
                    self._pos_0.append(s0.dump('pos'))
                    self._pos_1.append(s1.dump('pos'))
                if 'vel' in self.phasespace:
                    self._vel_0.append(s0.dump('vel'))
                    self._vel_1.append(s1.dump('vel'))
                if 'ids' in self.phasespace:
                    _ids_0 = s0.dump('species')
                    _ids_1 = s1.dump('species')
                    _ids_0 = numpy.array([ids.index(_) for _ in _ids_0], dtype=numpy.int32)
                    _ids_1 = numpy.array([ids.index(_) for _ in _ids_1], dtype=numpy.int32)
                    self._ids_0.append(_ids_0)
                    self._ids_1.append(_ids_1)

        # Dump unfolded positions if requested
        if 'pos-unf' in self.phasespace:
            for s in progress(Unfolded(self.trajectory)):
                s0 = self._cbk[0](s, *self._cbk_args[0], **self._cbk_kwargs[0])
                s1 = self._cbk[1](s, *self._cbk_args[1], **self._cbk_kwargs[1])
                self._pos_unf_0.append(s0.dump('pos'))
                self._pos_unf_1.append(s1.dump('pos'))

    def compute(self):
        """
        Compute the correlation function.

        It wraps the _compute() method implemented by subclasses.
        This method sets the `self.grid` and `self.value` variables,
        which are also returned.
        """
        _log.info('setup arrays for %s', self.tag_description)
        t = [Timer(), Timer()]
        t[0].start()
        self._setup_arrays()
        t[0].stop()

        _log.info('computing %s for %s', self.long_name, self.tag_description)
        _log.info('using %s time origins out of %s',
                  len(range(0, len(self.trajectory), self.skip)),
                  len(self.trajectory))
        t[1].start()
        self._compute()
        t[1].stop()

        _log.info('output file %s', self._output_file)
        _log.info('done %s for %s in %.1f sec [setup:%.0f%%, compute: %.0f%%]',
                  self.long_name,
                  self.tag_description, t[0].wall_time + t[1].wall_time,
                  t[0].wall_time / (t[0].wall_time + t[1].wall_time) * 100,
                  t[1].wall_time / (t[0].wall_time + t[1].wall_time) * 100)
        _log.info('')

        return self.grid, self.value

    def _compute(self):
        """Subclasses must implement this"""
        pass

    def analyze(self):
        """
        Subclasses may implement this and store the results in the
        self.analysis dictonary
        """
        pass

    @property
    def _output_file(self):
        """Returns path of output file"""
        # Interpolate the output path string
        if self.output_path is None:
            filename = None
        else:
            filename = self.output_path.format(symbol=self.symbol,
                                               short_name=self.short_name,
                                               long_name=self.long_name.replace(' ', '_'),
                                               tag=self.tag,
                                               tag_description=self.tag_description.replace(' ', '_'),
                                               trajectory=self.trajectory)
            # Strip unpleasant punctuation from basename path
            for punct in ['.', '_', '-']:
                subpaths = filename.split('/')
                subpaths[-1] = subpaths[-1].replace(punct * 2, punct)
                subpaths[-1] = subpaths[-1].strip(punct)
                filename = '/'.join(subpaths)
        return filename

    def read(self):
        """Read correlation function from existing file"""
        with open(self._output_file, 'r') as inp:
            x = numpy.loadtxt(inp, unpack=True)
            if len(x) == 3:
                _log.warn("cannot read 3-columns files yet in %s", self._output_file)
            elif len(x) == 2:
                self.grid, self.value = x
            else:
                self.grid, self.value = x[0: 2]
                _log.warn("Ignoring some columns in %s", self._output_file)

    @property
    def grid_name(self):
        """
        Return the name of the grid variables

        Example:
        -------
        If `self.name` is `F_s(k,t)`, the function returns `['k', 't']`
        """
        variables = self.short_name.split('(')[1][:-1]
        return variables.split(',')

    def write(self):
        """
        Write the correlation function and the analysis data to file

        The `output_path` instance variable is used to define the
        output files by interpolating the following variables:

        - symbol
        - short_name
        - long_name
        - tag
        - tag_description
        - trajectory

        The default is defined by core.pp_output_path, which currently
        looks like '{trajectory.filename}.pp.{symbol}.{tag}'
        """
        def is_iterable(maybe_iterable):
            try:
                iter(maybe_iterable)
            except TypeError:
                return False
            else:
                return True

        # Pack grid and value into arrays to dump
        if is_iterable(self.grid[0]) and len(self.grid) == 2:
            x = numpy.array(self.grid[0]).repeat(len(self.value[0]))
            y = numpy.array(self.grid[1] * len(self.grid[0]))
            z = numpy.array(self.value).flatten()
            dump = numpy.transpose(numpy.array([x, y, z]))
        else:
            dump = numpy.transpose(numpy.array([self.grid, self.value]))

        # Comment line
        # Extract variables from parenthesis in symbol
        variables = self.short_name.split('(')[1][:-1]
        variables = variables.split(',')
        columns = variables + [self.short_name]  # [self.symbol]
        if len(self.tag_description) > 0:
            conj = 'of'
        else:
            conj = ''
        comments = _dump(title='%s %s %s %s' % (self.long_name, self.short_name, conj, self.tag_description),
                         columns=columns,
                         command='atooms-pp', version=core.__version__,
                         description=None, note=None,
                         parents=self.trajectory.filename,
                         inline=False)
        if self.comments is not None:
            comments += self.comments

        # Results of analysis
        analysis = ""
        for x, f in self.analysis.items():
            if f is not None:
                analysis += '# %s: %s\n' % (x, f)

        # Put it all together
        # and make sure the path to the output file exists
        import os
        from atooms.core.utils import mkdir
        mkdir(os.path.dirname(self._output_file))
        with open(self._output_file, 'w') as fh:
            fh.write(comments)
            if len(analysis) > 0:
                fh.write(analysis)
            numpy.savetxt(fh, dump, fmt="%g")
            fh.flush()

    def do(self, update=False):
        """
        Do the full template pattern: compute, analyze and write the
        correlation function.
        """
        if update and not self.need_update():
            self.read()
            return

        self.compute()

        try:
            self.analyze()
        except ImportError as e:
            _log.warn('Could not analyze due to missing modules, continuing...')
            _log.warn(e)

        self.write()

    def __call__(self):
        self.do()
