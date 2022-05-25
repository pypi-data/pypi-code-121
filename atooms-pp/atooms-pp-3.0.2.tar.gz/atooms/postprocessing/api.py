"""Post processing API."""

import atooms.postprocessing as pp
from atooms.postprocessing.progress import progress
from atooms.postprocessing.partial import Partial
from atooms.trajectory import Trajectory
from atooms.trajectory.decorators import change_species, center
from atooms.system.particle import distinct_species

from .helpers import linear_grid, logx_grid

_func_db = {'linear_grid': linear_grid,
            'linear': linear_grid,
            'logx_grid': logx_grid,
            'logx': logx_grid}

def _get_trajectories(input_files, args):
    from atooms.trajectory import Sliced
    from atooms.core.utils import fractional_slice
    for input_file in input_files:
        with Trajectory(input_file, fmt=args['fmt']) as th:
            if args['center']:
                th.add_callback(center)
            # Caching is useful for systems with multiple species but
            # it will increase the memory footprint. Use --no-cache to
            # disable it
            if not args['no_cache']:
                th.cache = True
            if args['species_layout'] is not None:
                th.register_callback(change_species, args['species_layout'])
            sl = fractional_slice(args['first'], args['last'], args['skip'], len(th))
            if th.block_size > 1:
                sl_start = (sl.start // th.block_size) * th.block_size if sl.start is not None else sl.start
                sl_stop = (sl.stop // th.block_size) * th.block_size if sl.stop is not None else sl.stop
                sl = slice(sl_start, sl_stop, sl.step)
            if sl != slice(None, None, 1):
                ts = Sliced(th, sl)
            else:
                ts = th
            yield ts

def _compat(args):
    """Set default values of global arguments in `args` dictionary"""

    defaults = {
        'first': None,
        'last': None,
        'skip': None,
        'fmt': None,
        'center': False,
        'species_layout': None,
        'norigins': None,
        'fast': False,
        'legacy': False,
        'no_cache': False,
        'update': False,
        'filter': None,
        'no_partial': False,
    }
    for key in defaults:
        if key not in args:
            args[key] = defaults[key]

    # Implicit option rules
    if args['filter'] is not None:
        args['no_partial'] = True

    return args

def gr(input_file, dr=0.04, grandcanonical=False, ndim=-1, rmax=-1.0, *input_files, **global_args):
    """Radial distribution function"""
    global_args = _compat(global_args)
    if global_args['legacy']:
        backend = pp.RadialDistributionFunctionLegacy
    else:
        backend = pp.RadialDistributionFunction

    for th in _get_trajectories([input_file] + list(input_files), global_args):
        th._grandcanonical = grandcanonical
        cf = backend(th, dr=dr, rmax=rmax,
                     norigins=global_args['norigins'],
                     ndim=ndim)
        if global_args['filter'] is not None:
            cf = pp.Filter(cf, global_args['filter'])
        cf.do(update=global_args['update'])

        ids = distinct_species(th[0].particle)
        if len(ids) > 1 and not global_args['no_partial']:
            cf = Partial(backend, ids, th,
                         dr=dr, rmax=rmax, norigins=global_args['norigins'], ndim=ndim)
            cf.do(update=global_args['update'])

def sk(input_file, nk=20, dk=0.1, kmin=-1.0, kmax=15.0, ksamples=30,
       kgrid=None, weight=None, weight_trajectory=None,
       weight_fluctuations=False, *input_files, **global_args):
    """
    Structure factor
    """
    from atooms.trajectory import TrajectoryXYZ
    global_args = _compat(global_args)
    if global_args['fast']:
        backend = pp.StructureFactorFast
    else:
        backend = pp.StructureFactorLegacy
    if kgrid is not None:
        kgrid = [float(_) for _ in kgrid.split(',')]
    for th in _get_trajectories([input_file] + list(input_files), global_args):
        cf = backend(th, kgrid=kgrid,
                     norigins=global_args['norigins'], kmin=kmin,
                     kmax=kmax, nk=nk, dk=dk, ksamples=ksamples)
        if global_args['filter'] is not None:
            cf = pp.Filter(cf, global_args['filter'])
        if weight_trajectory is not None:
            weight_trajectory = TrajectoryXYZ(weight_trajectory)
        cf.add_weight(trajectory=weight_trajectory,
                      field=weight,
                      fluctuations=weight_fluctuations)
        cf.do(update=global_args['update'])

        ids = distinct_species(th[0].particle)
        if len(ids) > 1 and not global_args['no_partial']:
            cf = Partial(backend, ids, th, kgrid=kgrid,
                         norigins=global_args['norigins'],
                         kmin=kmin, kmax=kmax, nk=nk, dk=dk,
                         ksamples=ksamples)
            cf.add_weight(trajectory=weight_trajectory,
                          field=weight,
                          fluctuations=weight_fluctuations)
            cf.do(update=global_args['update'])

def ik(input_file, trajectory_radius=None, nk=20, dk=0.1, kmin=-1.0,
       kmax=15.0, kgrid=None, ksamples=30, *input_files,
       **global_args):
    """Spectral density"""
    global_args = _compat(global_args)
    if kgrid is not None:
        kgrid = [float(_) for _ in kgrid.split(',')]
    for th in _get_trajectories([input_file] + list(input_files), global_args):
        if trajectory_radius is None:
            trajectory_radius = input_file
            pp.SpectralDensity(th, trajectory_radius,
                               kgrid=kgrid, norigins=global_args['norigins'],
                               kmin=kmin, kmax=kmax, nk=nk, dk=dk,
                               ksamples=ksamples).do(update=global_args['update'])

def msd(input_file, tmax=-1.0, tmax_fraction=0.75, tsamples=30,
        sigma=1.0, func='linear', rmsd_max=-1.0, fix_cm=False,
        no_offset=False, *input_files, **global_args):
    """Mean square displacement"""
    func = _func_db[func]
    global_args = _compat(global_args)
    for th in _get_trajectories([input_file] + list(input_files), global_args):
        dt = th.timestep
        if tmax > 0:
            t_grid = [0.0] + func(dt, min(th.total_time, tmax), tsamples)
        elif tmax_fraction > 0:
            t_grid = [0.0] + func(dt, tmax_fraction*th.total_time, tsamples)
        else:
            t_grid = None
        ids = distinct_species(th[0].particle)
        pp.MeanSquareDisplacement(th, tgrid=t_grid,
                                  norigins=global_args['norigins'],
                                  sigma=sigma, rmax=rmsd_max, no_offset=no_offset,
                                  fix_cm=fix_cm).do(update=global_args['update'])
        if len(ids) > 1 and not global_args['no_partial']:
            Partial(pp.MeanSquareDisplacement, ids, th, tgrid=t_grid,
                    norigins=global_args['norigins'], sigma=sigma,
                    rmax=rmsd_max, no_offset=no_offset).do(update=global_args['update'])

def vacf(input_file, tmax=-1.0, tmax_fraction=0.10,
         tsamples=30, func='linear', *input_files, **global_args):
    """Velocity autocorrelation function"""
    global_args = _compat(global_args)
    func = _func_db[func]
    for th in _get_trajectories([input_file] + list(input_files), global_args):
        if tmax > 0:
            t_grid = [0.0] + func(th.timestep, min(th.total_time, tmax), tsamples)
        elif tmax_fraction > 0:
            t_grid = [0.0] + func(th.timestep, tmax_fraction*th.total_time, tsamples)
        else:
            t_grid = None
        pp.VelocityAutocorrelation(th, t_grid, norigins=global_args['norigins']).do(update=global_args['update'])
        ids = distinct_species(th[0].particle)
        if len(ids) > 1 and not global_args['no_partial']:
            Partial(pp.VelocityAutocorrelation, ids, th,
                    t_grid, norigins=global_args['norigins']).do(update=global_args['update'])

def fkt(input_file, tmax=-1.0, tmax_fraction=0.75,
        tsamples=60, kmin=7.0, kmax=7.0, ksamples=1, dk=0.1, nk=100,
        kgrid=None, func='logx', fix_cm=False, total=False, *input_files,
        **global_args):
    """Total intermediate scattering function"""
    global_args = _compat(global_args)
    func = _func_db[func]
    files = [input_file] + list(input_files)
    traj = _get_trajectories(files, global_args)
    bar = progress(active=True, total=len(files))
    for i, th in enumerate(traj):
        bar.update(i)
        if tmax > 0:
            t_grid = [0.0] + func(th.timestep, tmax, tsamples)
        elif tmax_fraction > 0:
            t_grid = [0.0] + func(th.timestep, tmax_fraction*th.total_time, tsamples)
        else:
            t_grid = None
        if kgrid is not None:
            k_grid = [float(_) for _ in kgrid.split(',')]
        else:
            k_grid = linear_grid(kmin, kmax, ksamples)
        ids = distinct_species(th[0].particle)
        if total or len(ids) == 1:
            pp.IntermediateScattering(th, k_grid, t_grid,
                                      norigins=global_args['norigins'],
                                      nk=nk, dk=dk, fix_cm=fix_cm).do(update=global_args['update'])
        if len(ids) > 1 and not global_args['no_partial']:
            Partial(pp.IntermediateScattering, ids, th, k_grid, t_grid,
                    norigins=global_args['norigins'],
                    nk=nk, dk=dk, fix_cm=fix_cm).do(update=global_args['update'])

def fskt(input_file, tmax=-1.0, tmax_fraction=0.75, tsamples=60,
         kmin=7.0, kmax=8.0, ksamples=1, dk=0.1, nk=8, kgrid=None,
         func='logx', total=False, fix_cm=False, lookup_mb=64.0,
         *input_files, **global_args):
    """Self intermediate scattering function"""
    global_args = _compat(global_args)
    func = _func_db[func]
    if global_args['legacy']:
        backend = pp.SelfIntermediateScatteringLegacy
    else:
        backend = pp.SelfIntermediateScattering
    for th in _get_trajectories([input_file] + list(input_files), global_args):
        if tmax > 0:
            t_grid = [0.0] + func(th.timestep, tmax, tsamples)
        elif tmax_fraction > 0:
            t_grid = [0.0] + func(th.timestep, tmax_fraction*th.total_time, tsamples)
        else:
            t_grid = None
        if kgrid is not None:
            k_grid = [float(_) for _ in kgrid.split(',')]
        else:
            k_grid = linear_grid(kmin, kmax, ksamples)
        ids = distinct_species(th[0].particle)
        if total or len(ids) == 1:
            backend(th, k_grid, t_grid, nk, dk=dk,
                    norigins=global_args['norigins'], fix_cm=fix_cm,
                    lookup_mb=lookup_mb).do(update=global_args['update'])
        if len(ids) > 1 and not global_args['no_partial']:
            Partial(backend, ids, th, k_grid, t_grid, nk, dk=dk,
                    norigins=global_args['norigins'], fix_cm=fix_cm,
                    lookup_mb=lookup_mb).do(update=global_args['update'])

def chi4qs(input_file, tsamples=60, a=0.3, tmax=-1.0, func='logx',
           tmax_fraction=0.75, total=False, *input_files,
           **global_args):
    """Dynamic susceptibility of self overlap"""
    global_args = _compat(global_args)
    func = _func_db[func]
    if global_args['fast']:
        backend = pp.Chi4SelfOverlapOpti
    else:
        backend = pp.Chi4SelfOverlap

    for th in _get_trajectories([input_file] + list(input_files), global_args):
        if tmax > 0:
            t_grid = [0.0] + func(th.timestep, min(th.total_time, tmax), tsamples)
        elif tmax_fraction > 0:
            t_grid = [0.0] + func(th.timestep, tmax_fraction*th.total_time, tsamples)
        else:
            t_grid = None
        if total:
            backend(th, t_grid, a=a, norigins=global_args['norigins']).do(update=global_args['update'])
        ids = distinct_species(th[0].particle)
        if not total and len(ids) > 1:
            Partial(backend, ids, th, t_grid, a=a,
                    norigins=global_args['norigins']).do(update=global_args['update'])

def alpha2(input_file, tmax=-1.0, tmax_fraction=0.75,
           tsamples=60, func='logx', *input_files, **global_args):
    """Non-Gaussian parameter"""
    global_args = _compat(global_args)
    func = _func_db[func]
    for th in _get_trajectories([input_file] + list(input_files), global_args):
        if tmax > 0:
            t_grid = [0.0] + func(th.timestep, tmax, tsamples)
        elif tmax_fraction > 0:
            t_grid = [0.0] + func(th.timestep, tmax_fraction*th.total_time, tsamples)
        else:
            t_grid = None
        pp.NonGaussianParameter(th, t_grid, norigins=global_args['norigins']).do(update=global_args['update'])
        ids = distinct_species(th[0].particle)
        if len(ids) > 1 and not global_args['no_partial']:
            Partial(pp.NonGaussianParameter, ids, th, t_grid,
                    norigins=global_args['norigins']).do(update=global_args['update'])

def qst(input_file, tmax=-1.0, tmax_fraction=0.75,
        tsamples=60, func='logx', *input_files, **global_args):
    """Self overlap correlation function"""
    global_args = _compat(global_args)
    func = _func_db[func]
    for th in _get_trajectories([input_file] + list(input_files), global_args):
        if tmax > 0:
            t_grid = [0.0] + func(th.timestep, tmax, tsamples)
        elif tmax_fraction > 0:
            t_grid = [0.0] + func(th.timestep, tmax_fraction*th.total_time, tsamples)
        else:
            t_grid = None
        pp.SelfOverlap(th, t_grid, norigins=global_args['norigins']).do(update=global_args['update'])
        ids = distinct_species(th[0].particle)
        if len(ids) > 1 and not global_args['no_partial']:
            Partial(pp.SelfOverlap, ids, th, t_grid,
                    norigins=global_args['norigins']).do(update=global_args['update'])

def qt(input_file, tmax=-1.0, tmax_fraction=0.75,
        tsamples=60, func='logx', *input_files, **global_args):
    """Collective overlap correlation function"""
    global_args = _compat(global_args)
    func = _func_db[func]
    for th in _get_trajectories([input_file] + list(input_files), global_args):
        if tmax > 0:
            t_grid = [0.0] + func(th.timestep, tmax, tsamples)
        elif tmax_fraction > 0:
            t_grid = [0.0] + func(th.timestep, tmax_fraction*th.total_time, tsamples)
        else:
            t_grid = None
        pp.CollectiveOverlap(th, t_grid, norigins=global_args['norigins']).do(update=global_args['update'])
        ids = distinct_species(th[0].particle)
        if len(ids) > 1 and not global_args['no_partial']:
            Partial(pp.CollectiveOverlap, ids, th, t_grid,
                    norigins=global_args['norigins']).do(update=global_args['update'])

def ba(input_file, dtheta=4.0, grandcanonical=False, *input_files, **global_args):
    """Bond-angle distribution"""
    global_args = _compat(global_args)
    for th in _get_trajectories([input_file] + list(input_files), global_args):
        th._grandcanonical = grandcanonical

        cf = pp.BondAngleDistribution(th, dtheta=dtheta, norigins=global_args['norigins'])
        if global_args['filter'] is not None:
            cf = pp.Filter(cf, global_args['filter'])
        cf.do(update=global_args['update'])

        # ids = distinct_species(th[0].particle)
        # if len(ids) > 1 and not global_args['no_partial']:
        #     cf = Partial(pp.BondAngleDistribution, ids, th, dtheta=dtheta, norigins=global_args['norigins'])
        #     cf.do(update=global_args['update'])
