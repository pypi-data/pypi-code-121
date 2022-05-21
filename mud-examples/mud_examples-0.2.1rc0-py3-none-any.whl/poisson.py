#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import os
import pickle
import pkgutil
import sys
from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt  # move when migrating plotting code (maybe)
import numpy as np  # only needed for band_qoi + sample generation for main method
from mud import __version__ as __mud_version__
from mud.funs import map_problem, mud_problem

# used for convenience in setting Normal distribution
from mud.util import std_from_equipment

from mud_examples import __version__
from mud_examples.utils import LazyLoader, check_dir
from mud_examples.models import generate_spatial_measurements as generate_sensors_pde

ds = LazyLoader("scipy.stats.distributions")
# from mpi4py import MPI
# comm = MPI.COMM_WORLD
# rank = comm.Get_rank()


__author__ = "Mathematical Michael"
__copyright__ = "Mathematical Michael"
__license__ = "mit"

_logger = logging.getLogger(__name__)

try:
    fin = LazyLoader("dolfin")
except ModuleNotFoundError:
    _logger.error("Could not load fenics.")


def parse_args(args):
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(description="Poisson Problem")
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"mud_examples {__version__}, mud {__mud_version__}",
    )
    parser.add_argument(
        "-s",
        "--num_samples",
        dest="num",
        help="Number of samples",
        default=1,
        type=int,
        metavar="INT",
    )
    parser.add_argument(
        "-d",
        "--distribution",
        dest="dist",
        help="Distribution. `n` (normal), `u` (uniform, default)",
        default="u",
        type=str,
        metavar="STR",
    )
    parser.add_argument(
        "-m",
        "--mean",
        dest="mean",
        help="Sets mean for normal distribution.",
        default=-2.0,
        type=float,
        metavar="FLOAT",
    )
    parser.add_argument(
        "-t",
        "--sample-tolerance",
        dest="tolerance",
        help="Sets std dev for normal distribution. Proportion of samples (default: 0.95) that fall within +/- 2 of the mean.",
        default=0.95,
        type=float,
        metavar="FLOAT",
    )
    parser.add_argument(
        "-i",
        "--input_dim",
        dest="input_dim",
        help="Dimension of input space (default=2).",
        default=2,
        type=int,
        metavar="INT",
    )
    parser.add_argument(
        "-b",
        "--beta-params",
        dest="beta_params",
        help="Parameters for beta distribution. (default = 1 1 )",
        default=None,
        nargs="+",
        type=float,
        metavar="FLOAT FLOAT",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def main(args):
    """Main entry point allowing external calls.
    Generates PDE data (requires fenics to be installed)

    Args:
      args ([str]): command line parameter list
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    _logger.debug("poisson.py data generation")

    num_samples = args.num
    sample_dist = args.dist
    mean = args.mean
    dim_input = args.input_dim
    beta_params = args.beta_params  # signals to use beta (first preference)
    tol = (
        args.tolerance
    )  # signals to use normal (beta must be empty), overrides uniform
    if sample_dist == "n":
        if tol < 0 or tol >= 1:
            raise ValueError("tolerance must be in (0, 1)")
    elif sample_dist == "u":
        tol = 1.0
    else:
        raise ValueError("Unsupported value for sample_dist.")
    # perform random sampling according to command-line arguments
    if beta_params is None:
        if (
            sample_dist == "n"
        ):  # N(-mean, sd), sd chosen so 100*tol % samples are +/- 2 around mean
            _logger.info(
                f"Generating samples from N(-2, sd), sd s.t. {100*tol}% are in a ball of radius 2 around mean."
            )
            sd = std_from_equipment(2, tol)
            randsamples = np.random.randn(num_samples, dim_input) * sd + mean
        elif sample_dist == "u":  # U(-4, 0)
            _logger.info("Generating samples from U(-4, 0).")
            tol = 1.0
            randsamples = -4 * np.random.rand(num_samples, dim_input)
        else:
            raise ValueError(
                "Improper distribution choice, use `n` (normal) or `u` (uniform)."
            )

    else:
        _logger.info("Using beta distribution since `beta_params` were passed.")
        beta_params = tuple(beta_params)
        sample_dist = "b" + str(beta_params).replace(", ", "_").replace(
            "(", ""
        ).replace(")", "")

        if len(beta_params) != 2:
            raise ValueError("Beta distribution requires only two parameters.")

        randsamples = -4 * np.random.beta(*beta_params, size=(num_samples, dim_input))

    # indexed list of samples we will evaluate through our poisson model
    sample_seed_list = list(zip(range(num_samples), randsamples))

    outfile = str(round(np.floor(tol * 1000))) + "_" + str(dim_input) + str(sample_dist)
    results = []
    for sample in sample_seed_list:
        r = evaluate_and_save_poisson(sample, outfile)
        results.append(r)
        _logger.debug(r)

    pickle.dump(results, open(f"{outfile}.pkl", "wb"))
    _logger.info(f"Data generation completed, saved to {outfile}.pkl.")


def run():
    """Entry point for console_scripts"""
    main(sys.argv[1:])


############################################################


def poissonModel(gamma=-3, mesh=None, width=1, nx=36, ny=36):
    """
    `gamma` is scaling parameter for left boundary condition
    `n_x` and `n_y` are the number of elements for the horizontal/vertical axes of the mesh
    """
    # Create mesh and define function space
    if mesh is None:
        mesh = fin.RectangleMesh(fin.Point(0, 0), fin.Point(width, 1), nx, ny)

    V = fin.FunctionSpace(mesh, "Lagrange", 1)
    u = fin.TrialFunction(V)
    v = fin.TestFunction(V)

    # Define the left boundary condition, parameterized by gamma
    left_bc = gamma_boundary_condition(gamma)

    # Define the rest of the boundary condition
    dirichlet_bc = fin.Constant(0.0)  # top and bottom
    right_bc = fin.Constant(0)

    # Define integrand
    boundary_markers = get_boundary_markers_for_rect(mesh, width)
    ds = fin.Measure("ds", domain=mesh, subdomain_data=boundary_markers)

    # Define variational problem
    f = fin.Expression(
        "10*exp(-(pow(x[0] - 0.5, 2) + pow(x[1] - 0.5, 2)) / 0.02)", degree=2
    )
    a = fin.inner(fin.grad(u), fin.grad(v)) * fin.dx
    L = f * v * fin.dx + right_bc * v * ds(1) + left_bc * v * ds(3)  # sum(integrals_N)

    # Define Dirichlet boundary (x = 0 or x = 1)
    def top_bottom_boundary(x):
        return x[1] < fin.DOLFIN_EPS or x[1] > 1.0 - fin.DOLFIN_EPS

    bc = fin.DirichletBC(
        V, dirichlet_bc, top_bottom_boundary
    )  # this is required for correct solutions

    # Compute solution
    u = fin.Function(V)
    fin.solve(a == L, u, bc)
    return u


def gamma_boundary_condition(gamma=-3):
    """
    Defines boundary condition parameterized by either a scalar or list/iterable.
    In the latter case, piecewise-interpolation on an equispaced grid over
    the interior of (0, 1). In the former, the scalar defines the minimum displacement
    value of the boundary condition.
    """
    if isinstance(gamma, int) or isinstance(gamma, float):  # 1-D case
        # the function below will have a min at (2/7, gamma) by design
        # (scaling factor chosen via calculus)
        lam = gamma * 823543 / 12500
        expr = fin.Expression(f"pow(x[1], 2) * pow(1 - x[1], 5) * {lam}", degree=3)
    else:  # Higher-D case
        expr = fin.Expression(piecewise_eval_from_vector(gamma, d=1), degree=1)
    return expr


def poisson_sensor_model(sensors, gamma, nx, ny, mesh=None):
    """
    Convenience function wrapper to just return a qoi given a parameter.
    """
    assert sensors.shape[1] == 2, "pass with shape (num_sensors, 2)"
    u = poissonModel(gamma=gamma, mesh=mesh, nx=nx, ny=ny)
    return [u(xi, yi) for xi, yi in sensors]


def eval_boundary_piecewise(u, n, d=1):
    """
    Takes an Expression `u` (on unit domain) and returns the string
    for another expression based on evaluating a piecewise-linear approximation.
    The mesh is equispaced into n intervals.
    """
    dx = 1 / (n + 1)
    intervals = [i * dx for i in range(n + 2)]
    node_values = [u(0, i) for i in intervals]
    return piecewise_eval(intervals, node_values, d)


def piecewise_eval_from_vector(u, d=1):
    """
    Takes an iterable `u` with y-values (on interior of equispaced unit domain)
    and returns the string for an expression
    based on evaluating a piecewise-linear approximation through these points.
    """
    n = len(u)
    dx = 1 / (n + 1)
    intervals = [i * dx for i in range(n + 2)]
    node_values = [0] + list(u) + [1]
    return piecewise_eval(intervals, node_values, d)


def piecewise_eval(xvals, yvals, d=1):
    s = ""
    for i in range(1, len(xvals)):
        start = xvals[i - 1]
        end = xvals[i]
        diff = start - end
        s += f" ((x[{d}] >= {start}) && (x[{d}] < {end}))*"
        s += f"({yvals[i-1]}*((x[{d}]-{end})/{diff}) + (1 - ((x[{d}]-{end})/{diff}))*{yvals[i]} ) +"
    return s[1:-1]


def eval_boundary(u, n):
    dx = 1 / (n + 1)
    invals = [i * dx for i in range(n + 2)]
    outvals = [u(0, i) for i in invals][1:-1]
    return invals[1:-1], outvals


def expressionNorm(u, v, n=100):
    u = eval_boundary(u, n)[1]
    v = eval_boundary(v, n)[1]
    return np.linalg.norm(np.array(u) - np.array(v)) / n


def copy_expression(expression):
    u = expression
    return fin.Expression(
        u._cppcode, **u._user_parameters, degree=u.ufl_element().degree()
    )


def get_boundary_markers_for_rect(mesh, width=1):
    class BoundaryX0(fin.SubDomain):
        def inside(self, x, on_boundary):
            return on_boundary and fin.near(x[0], 0, 1e-14)

    class BoundaryX1(fin.SubDomain):
        def inside(self, x, on_boundary):
            return on_boundary and fin.near(x[0], width, 1e-14)

    class BoundaryY0(fin.SubDomain):
        def inside(self, x, on_boundary):
            return on_boundary and fin.near(x[1], 0, 1e-14)

    class BoundaryY1(fin.SubDomain):
        def inside(self, x, on_boundary):
            return on_boundary and fin.near(x[1], 1, 1e-14)

    # not sure what the first argument here does.
    boundary_markers = fin.MeshFunction("size_t", mesh, mesh.topology().dim() - 1, 0)

    # starting from top of square, going clockwise
    # we have to instantiate a class for each boundary portion in order to mark them.
    # each operation changes the state of `boundary_markers`
    BoundaryY1().mark(boundary_markers, 0)
    BoundaryX1().mark(boundary_markers, 1)
    BoundaryY0().mark(boundary_markers, 2)
    BoundaryX0().mark(boundary_markers, 3)

    return boundary_markers


def make_reproducible_without_fenics(
    example="mud",
    lam_true=-3,
    input_dim=2,
    sample_dist="u",
    sample_tol=0.95,
    num_samples=None,
    num_measure=100,
):
    """
    (Currently) requires XML data to be on disk, simulates sensors
    and saves everything required to one pickle file.
    """
    if sample_dist == "u":
        sample_tol = 1.0
    elif sample_dist == "n":
        if sample_tol < 0 or sample_tol >= 1:
            raise ValueError(
                "Sample tolerance must be in (0, 1) when using normal distributions."
            )
    else:
        raise ValueError("Unsupported argument for `sample_dist`.")

    if lam_true < -4 or lam_true > 0:
        raise ValueError("True value must be in (-4, 0).")
    prefix = str(round(np.floor(sample_tol * 1000)))
    _logger.info("Running make_reproducible without fenics")
    # Either load or generate the data.
    try:  # TODO: generalize this path here... take as argument
        model_list = pickle.load(open(f"{prefix}_{input_dim}{sample_dist}.pkl", "rb"))
        if num_samples is None or num_samples > len(model_list):
            num_samples = len(model_list)

    except FileNotFoundError as e:
        if num_samples is None:
            num_samples = 50
        _logger.error(f"make_reproducible: {e}")
        _logger.warning("Attempting data generation with system call.")
        # below has to match where we expected our git-controlled file to be... TODO: generalize to data/
        # curdir = os.getcwd().split('/')[-1]
        os.system(
            f"generate_poisson_data -v -s {num_samples} -i {input_dim} -d {sample_dist} -t {sample_tol}"
        )
        try:
            model_list = pickle.load(
                open(f"{prefix}_{input_dim}{sample_dist}.pkl", "rb")
            )
            if num_samples is None or num_samples > len(model_list):
                num_samples = len(model_list)
        except TypeError:
            raise ModuleNotFoundError("Try `conda install -c conda forge fenics`")

    fdir = f"pde_{input_dim}D"
    check_dir(fdir)

    if (
        input_dim == 1 and "alt" in example
    ):  # alternative measurement locations for more sensitivity / precision
        sensors = generate_sensors_pde(num_measure, ymax=0.95, xmax=0.25)
        fname = f"{fdir}/ref_alt_{prefix}_{input_dim}{sample_dist}.pkl"
    else:
        sensors = generate_sensors_pde(num_measure, ymax=0.95, xmax=0.95)
        fname = f"{fdir}/ref_{prefix}_{input_dim}{sample_dist}.pkl"

    lam, qoi = load_poisson_from_fenics_run(
        sensors, model_list[0:num_samples], nx=36, ny=36
    )
    qoi_ref = poisson_sensor_model(sensors, gamma=lam_true, nx=36, ny=36)

    pn = poissonModel(gamma=lam_true)
    c = pn.function_space().mesh().coordinates()
    v = [pn(c[i, 0], c[i, 1]) for i in range(len(c))]

    g = gamma_boundary_condition(lam_true)
    g_mesh = np.linspace(0, 1, 1000)
    g_plot = [g(0, y) for y in g_mesh]
    ref = {
        "sensors": sensors,
        "lam": lam,
        "qoi": qoi,
        "truth": lam_true,
        "data": qoi_ref,
        "plot_u": (c, v),
        "plot_g": (g_mesh, g_plot),
    }

    with open(fname, "wb") as f:
        pickle.dump(ref, f)
    _logger.info(fname + " saved: " + str(Path(fname).stat().st_size // 1000) + "KB")

    return fname


def plot_without_fenics(
    fname, num_sensors=None, num_qoi=2, mode="sca", fsize=36, example=None
):
    plt.figure(figsize=(10, 10))
    mode = mode.lower()
    colors = ["xkcd:red", "xkcd:black", "xkcd:orange", "xkcd:blue", "xkcd:green"]

    if "data" in fname:  # TODO turn into function.
        _logger.info(f"Loading {fname} from package")
        data = pkgutil.get_data(__package__, fname)
        data = BytesIO(data)
    else:
        _logger.info("Loading from disk")
        data = open(fname, "rb")
    ref = pickle.load(data)

    sensors = ref["sensors"]
    # qoi_ref = ref['data']
    coords, vals = ref["plot_u"]
    #     try:
    #         import fenics as fin
    #         from poisson import poissonModel
    #         pn = poissonModel()
    #         fin.plot(pn, vmin=-0.5, vmax=0)
    #     except:
    plt.tricontourf(coords[:, 0], coords[:, 1], vals, levels=20, vmin=-0.5, vmax=0)

    # input_dim = ref['lam'].shape[1]

    plt.title("Response Surface", fontsize=1.25 * fsize)
    if num_sensors is not None:  # plot sensors
        intervals = np.linspace(0, 1, num_qoi + 2)[1:-1]
        if mode == "sca":
            qoi_indices = band_qoi(sensors, 1, axis=1)
            _intervals = (
                np.array(intervals[1:])
                + (np.array(intervals[:-1]) - np.array(intervals[1:])) / 2
            )

        elif mode == "hor":
            qoi_indices = band_qoi(sensors, num_qoi, axis=1)
            # partitions equidistant between sensors
            _intervals = (
                np.array(intervals[1:])
                + (np.array(intervals[:-1]) - np.array(intervals[1:])) / 2
            )

        elif mode == "ver":
            qoi_indices = band_qoi(sensors, num_qoi, axis=0)
            # partitions equidistant on x_1 = (0, 1)
            _intervals = np.linspace(0, 1, num_qoi + 1)[1:]
        else:
            raise ValueError(
                "Unsupported mode type. Select from ('sca', 'ver', 'hor'). "
            )
        for i in range(0, len(qoi_indices)):
            _q = qoi_indices[i][qoi_indices[i] < num_sensors]
            plt.scatter(sensors[_q, 0], sensors[_q, 1], s=100, color=colors[i % 2])
            if i < num_qoi - 1:
                if mode == "hor":
                    plt.axhline(_intervals[i], lw=3, c="k")
                elif mode == "ver":
                    plt.axvline(_intervals[i], lw=3, c="k")

        plt.scatter([0] * num_qoi, intervals, s=500, marker="^", c="w")
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    #     plt.xticks([])
    #     plt.yticks([])
    plt.xlabel("$x_1$", fontsize=fsize)
    plt.ylabel("$x_2$", fontsize=fsize)

    if example:
        # if 'data' in fname:  # TODO: clean this up
        #     fdir= '/'.join(fname.split('/')[1:-1])
        # else:
        #     fdir= '/'.join(fname.split('/')[:-1])
        fdir = "figures/" + fname.replace(".pkl", "")
        # print(fdir)
        check_dir(fdir)
        fname = f"{fdir}/{example}_surface.png"
        plt.savefig(fname, bbox_inches="tight")
        _logger.info(f"Saved {fname}")


# from scipy.stats import gaussian_kde as gkde
# from scipy.stats import distributions as dist

# def ratio_dci_sing(qoi):
#     kde = gkde(qoi.T)
#     ratio_eval = dist.norm.pdf(qoi)/kde.pdf(qoi.T).ravel()
#     return ratio_eval


# def ratio_dci_mult(qois):
#     nq = np.array(qois)
#     kde = gkde(nq)
#     obs = dist.norm.pdf(nq)
#     obs_eval = np.product(obs, axis=0)
#     pre_eval = kde.pdf(nq)
#     ratio_eval = np.divide(obs_eval, pre_eval)
#     return ratio_eval


def make_mud_wrapper(
    domain, lam, qoi, qoi_true, indices=None, sample_dist="u", dist=ds.norm, **kwargs
):
    """
    Anonymous function
    """
    if not isinstance(sample_dist, str):
        raise ValueError("`sample_dist` must be of type `str`.")

    def mud_wrapper(num_obs, sd):
        d = mud_problem(
            domain=domain,
            lam=lam,
            qoi=qoi,
            qoi_true=qoi_true,
            sd=sd,
            num_obs=num_obs,
            split=indices,
        )
        d.set_initial(dist(**kwargs))
        if sample_dist == "u":
            _logger.debug("Using weighted KDE for MUD solution.")
            d.set_predicted(weights=d._in)
        return d

    return mud_wrapper


def make_map_wrapper(domain, lam, qoi, qoi_true, log=False, dist=ds.norm, **kwargs):
    """
    Anonymous function
    """

    def map_wrapper(num_obs, sd):
        b = map_problem(
            domain=domain,
            lam=lam,
            qoi=qoi,
            qoi_true=qoi_true,
            sd=sd,
            num_obs=num_obs,
            log=log,
        )
        b.set_prior(dist(**kwargs))
        return b

    return map_wrapper


# probably move to helpers or utils
def band_qoi(sensors, num_qoi=1, axis=1):
    intervals = np.linspace(0, 1, num_qoi + 2)[1:-1]
    if axis == 1:
        _intervals = (
            np.array(intervals[1:])
            + (np.array(intervals[:-1]) - np.array(intervals[1:])) / 2
        )
    elif axis == 0:
        _intervals = np.linspace(0, 1, num_qoi + 1)[1:]
    else:
        raise ValueError("axis must be 0 or 1 since the example is in 2D")
    _intervals = [0] + list(_intervals) + [1]
    qoi_indices = [
        np.where(
            np.logical_and(
                sensors[:, axis] > _intervals[i], sensors[:, axis] < _intervals[i + 1]
            )
        )[0]
        for i in range(num_qoi)
    ]
    return qoi_indices


def dist_from_fname(fname):
    """
    Function that infers distribution used to generate samples from the filename
    It looks for a letter before `.pkl`, i.e. `..n.pkl` -> normal distribution.
    """
    dist_from_fname = fname.strip("results").strip("res").strip(".pkl")
    dist_from_fname = dist_from_fname.split("/")[-1][
        -1
    ]  # attempting to infer distribution from filename
    _logger.info(f"Inferring distribution from file name with {dist_from_fname}")
    return dist_from_fname


class pdeProblem(object):
    def __init__(self, fname=None):
        self.fname = fname
        self._lam = None
        self._lam_ref = None
        self._qoi = None
        self._qoi_ref = None
        self._sensors = None
        self._domain = None
        self._u = None
        self._g = None
        self._dist = None
        self._sample_dist = None

    @property
    def lam(self):
        return self._lam

    @lam.setter
    def lam(self, lam):
        self._lam = lam

    @property
    def lam_ref(self):
        return self._lam_ref

    @lam_ref.setter
    def lam_ref(self, lam_ref):
        if self.domain is None:
            raise AttributeError("domain not yet set.")
        min_val, max_val = -4, 0  # problem-specific
        if (lam_ref < min_val) or (lam_ref > max_val):
            raise ValueError("lam_ref must be inside domain (-4, 0).")
        self._lam_ref = lam_ref

    @property
    def qoi(self):
        return self._qoi

    @qoi.setter
    def qoi(self, qoi):
        self._qoi = qoi

    @property
    def qoi_ref(self):
        return self._qoi_ref

    @qoi_ref.setter
    def qoi_ref(self, qoi_ref):
        self._qoi_ref = qoi_ref

    @property
    def sensors(self):
        return self._sensors

    @sensors.setter
    def sensors(self, sensors):
        self._sensors = sensors

    @property
    def domain(self):
        return self._domain

    @domain.setter
    def domain(self, domain):
        self._domain = domain

    @property
    def g(self):
        return self._g

    @g.setter
    def g(self, g):
        self._g = g

    @property
    def u(self):
        return self._u

    @u.setter
    def u(self, u):
        self._u = u

    @property
    def dist(self):
        return self._dist

    @dist.setter
    def dist(self, dist):
        self._dist = dist

    @property
    def sample_dist(self):
        return self._sample_dist

    @sample_dist.setter
    def sample_dist(self, dist):
        if dist not in ["u", "n"]:
            raise ValueError(
                "distribution could not be inferred. Must be from ('u', 'n')"
            )
        self._sample_dist = dist

    def load(self, fname=None):
        """
        Loads from filename, e.g., "data/pde_2D/ref_1000_2u.pkl"
        """
        if fname:
            self.fname = fname
            _logger.info(f"PDE problem loading from {fname}.")
        else:
            fname = self.fname
            _logger.info(f"PDE problem loading from default {fname}.")

        self.sample_dist = dist_from_fname(fname)

        domain, sensors, lam, qoi, qoi_ref, lam_ref, u, g = load_poisson_from_disk(
            fname
        )
        self.domain = domain
        self.sensors = sensors
        self.lam = lam
        self.lam_ref = lam_ref
        self.qoi = qoi
        self.qoi_ref = qoi_ref
        self.u = u
        self.g = g

        _logger.info(
            f"lam: {self.lam.shape}, qoi: {self.qoi.shape}, dist: {self.sample_dist}"
        )

    def map_scalar(self, log=True, **kwargs):
        _logger.info("Solving with MAP estimates.")
        return make_map_wrapper(
            self.domain,
            self.lam,
            self.qoi,
            self.qoi_ref,
            dist=self.dist,
            log=log,
            **kwargs,
        )

    def mud_scalar(self, **kwargs):
        _logger.info("Solving with scalar-valued MUD estimates.")
        return make_mud_wrapper(
            self.domain,
            self.lam,
            self.qoi,
            self.qoi_ref,
            dist=self.dist,
            sample_dist=self.sample_dist,
            **kwargs,
        )

    def mud_vector_horizontal(self, num_qoi=None, **kwargs):
        if num_qoi is None:  # set output dimension = input dimension
            num_qoi = self.lam.shape[1]
        indices = band_qoi(self.sensors, num_qoi=num_qoi, axis=1)
        _logger.info("Solving with horizontal-split vector-valued MUD estimates.")
        return make_mud_wrapper(
            self.domain,
            self.lam,
            self.qoi,
            self.qoi_ref,
            indices,
            dist=self.dist,
            sample_dist=self.sample_dist,
            **kwargs,
        )

    def mud_vector_vertical(self, num_qoi=None, **kwargs):
        if num_qoi is None:  # set output dimension = input dimension
            num_qoi = self.lam.shape[1]
        indices = band_qoi(self.sensors, num_qoi=num_qoi, axis=0)
        _logger.info("Solving with vertical-split vector-valued MUD estimates.")
        return make_mud_wrapper(
            self.domain,
            self.lam,
            self.qoi,
            self.qoi_ref,
            indices,
            dist=self.dist,
            sample_dist=self.sample_dist,
            **kwargs,
        )

    def plot_initial(self, save=True, **kwargs):
        self.plot(save=save, **kwargs)

    def plot_solutions(self, sols, num, save=True, **kwargs):
        self.plot(sols=sols, num_measurements=num, save=save, **kwargs)

    def plot(
        self,
        sols=None,
        num_measurements=20,
        example="mud",
        fsize=36,
        ftype="png",
        save=False,
    ):
        lam = self.lam
        qoi = self.qoi
        qoi_ref = self.qoi_ref
        # dist = self.dist
        g = self.g
        fname = self.fname.replace(".pkl", "")
        # fname = fname.replace('data/', '')
        fname = "figures/" + fname
        check_dir(fname)
        closest_fit_index_out = np.argmin(
            np.linalg.norm(qoi - np.array(qoi_ref), axis=1)
        )
        g_projected = list(lam[closest_fit_index_out, :])
        plt.figure(figsize=(10, 10))

        g_mesh, g_plot = g
        intervals = list(np.linspace(0, 1, lam.shape[1] + 2)[1:-1])
        # fin.plot(u_plot, mesh=mesh, lw=5, c='k', label="$g$")
        plt.plot(g_mesh, g_plot, lw=5, c="k", label="$g$")
        plt.plot(
            [0] + intervals + [1],
            [0] + g_projected + [0],
            lw=5,
            c="green",
            alpha=0.6,
            ls="--",
            label="$\\hat{g}$",
            zorder=5,
        )

        if sols is not None:
            if sols.get(num_measurements, None) is None:
                raise AttributeError(
                    f"Solutions `sols` missing requested N={num_measurements}. `sols`={sols!r}"
                )
            else:
                prefix = f"{fname}/{example}_solutions_N{num_measurements}"
                plot_lam = np.array(sols[num_measurements])
                if example == "mud-alt":
                    qmap = "$Q_{%dD}^\\prime$" % lam.shape[1]
                    soltype = "MUD"
                elif example == "mud":
                    qmap = "$Q_{%dD}$" % lam.shape[1]
                    soltype = "MUD"
                elif example == "map":
                    qmap = "$Q_{1D}$"
                    soltype = "MAP"
                else:
                    raise ValueError("Unsupported example type.")
                plt.title(
                    f"{soltype} Estimates for {qmap}, $N={num_measurements}$",
                    fontsize=1.25 * fsize,
                )
        else:  # initial plot, first 100
            # prefix = f'pde_{lam.shape[1]}{dist}/initial'
            prefix = f"{fname}/{example}_initial_S{lam.shape[0]}"
            plot_lam = lam[0:100, :]
            plt.title("Samples from Initial Density", fontsize=1.25 * fsize)

        for _lam in plot_lam:
            plt.plot(
                [0] + intervals + [1],
                [0] + list(_lam) + [0],
                lw=1,
                c="purple",
                alpha=0.2,
            )

        plt.xlabel("$x_2$", fontsize=fsize)
        plt.ylabel("$g(x, \\lambda)$", fontsize=fsize)

        # label min(g)
        # plt.axvline(2/7, alpha=0.4, ls=':')
        # plt.axhline(-lam_true, alpha=0.4, ls=':')
        plt.ylim(-4, 0)
        plt.xlim(0, 1)
        plt.legend()
        if save:
            _fname = f"{prefix}.{ftype}"
            plt.savefig(_fname, bbox_inches="tight")
            _logger.info(f"Saved {_fname}")
            plt.close("all")

    #     plt.show()


def evaluate_and_save_poisson(sample, save_prefix):
    """
    sample is a tuple (index, gamma)
    """
    prefix = save_prefix.replace(".pkl", "")
    g = sample[1]

    # define fixed mesh to avoid re-instantiation on each call to model (how it handles mesh=None)
    nx, ny = 36, 36
    mesh = fin.RectangleMesh(fin.Point(0, 0), fin.Point(1, 1), nx, ny)
    u = poissonModel(gamma=g, mesh=mesh, nx=nx, ny=ny)

    # Save solution as XML mesh
    fname = f"{prefix}-data/poisson-{int(sample[0]):06d}.xml"
    fin.File(fname, "w") << u
    # tells you where to find the saved file and what the input was to generate it.
    return {int(sample[0]): {"u": fname, "gamma": sample[1]}}


def load_poisson_from_fenics_run(sensors, file_list, nx=36, ny=36):
    num_samples = len(file_list)
    _logger.info(
        f"load_poisson_from_fenics_run - Loading {num_samples} evaluations of parameter space."
    )

    mesh = fin.RectangleMesh(fin.Point(0, 0), fin.Point(1, 1), nx, ny)
    V = fin.FunctionSpace(mesh, "Lagrange", 1)

    qoi = []
    lam = []
    # go through all the files and load them into an array
    for i in range(num_samples):
        fname = file_list[i][i]["u"]
        _logger.debug(f"Loading {fname}")
        u = fin.Function(V, fname)
        q = [u(xi, yi) for xi, yi in sensors]  # sensors
        qoi.append(np.array(q))
        lam.append(file_list[i][i]["gamma"])  # TODO: change name of this
    qoi = np.array(qoi)
    lam = np.array(lam)

    _logger.info(f"qoi: {qoi.shape}, lam: {lam.shape}, sensors: {sensors.shape}")

    return lam, qoi


def load_poisson_from_disk(fname):
    _logger.info(f"Attempting to load {fname} from disk")
    try:
        if "data" in fname:
            _logger.info(f"Loading {fname} from package")
            data = pkgutil.get_data(__package__, fname)
            data = BytesIO(data)
        else:
            _logger.info("Loading from disk")
            data = open(fname, "rb")
        ref = pickle.load(data)
    except FileNotFoundError:
        _logger.info(f"load_poisson_from_disk - Failed to load {fname} from disk")
        raise FileNotFoundError(
            f"load_poisson_from_disk: File {fname} missing. Run `make_reproducible_without_fenics` first."
        )
    lam = ref["lam"]
    input_dim = lam.shape[1]
    domain = np.array([[-4, 0]] * input_dim)
    _logger.info(f"Domain set by default as [-4, 0] for each dimension.")
    qoi = ref["qoi"]
    qoi_ref = ref["data"]
    lam_ref = ref["truth"]
    u = ref["plot_u"]
    g = ref["plot_g"]
    sensors = ref["sensors"]
    return domain, sensors, lam, qoi, qoi_ref, lam_ref, u, g


if __name__ == "__main__":
    run()
