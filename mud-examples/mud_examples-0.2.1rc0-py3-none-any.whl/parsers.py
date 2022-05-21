#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging

from mud import __version__ as __mud_version__
from mud_examples import __version__

__author__ = "Mathematical Michael"
__copyright__ = "Mathematical Michael"
__license__ = "mit"

_logger = logging.getLogger(__name__)


def parse_args(args):
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """

    desc = """
        Examples
        """

    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"mud_examples {__version__}, mud {__mud_version__}",
    )
    parser.add_argument(
        "-e",
        "--example",
        help="Which example to run (ode, pde, lin).",
        default="ode",
        type=str,
        metavar="STR",
    )
    parser.add_argument(
        "-m",
        "--num-measure",
        help="Dimension of input space (default=2).",
        default=[25, 50, 100, 200, 400],
        type=int,
        nargs="+",
    )
    parser.add_argument(
        "-r",
        "--ratio-measure",
        help="Dimension of input space (default=2).",
        default=[0.125, 0.25, 0.5, 1],
        type=float,
        nargs="+",
    )
    parser.add_argument(
        "--num-trials",
        help="Dimension of input space (default=2).",
        default=20,
        type=int,
    )
    parser.add_argument(
        "-t",
        "--sample-tolerance",
        help="Dimension of input space (default=2).",
        default=0.95,
        dest="tolerance",
        type=float,
    )
    parser.add_argument(
        "-p",
        "--sensor-precision",
        help="Dimension of input space (default=2).",
        default=[0.1],
        dest="precision",
        metavar="FLOAT",
        type=float,
        nargs="+",
    )

    #     parser.add_argument('-n', '--num_samples',
    #         dest="num",
    #         help="Number of samples",
    #         default=100,
    #         type=int,
    #         metavar="INT")
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
        "-d",
        "--distribution",
        dest="dist",
        help="Distribution. `n` (normal), `u` (uniform, default)",
        default="u",
        type=str,
        metavar="STR",
    )
    #     parser.add_argument('-b', '--beta-params',
    #         dest="beta_params",
    #         help="Parameters for beta distribution. Overrides --distribution. (default = 1 1 )",
    #         default=None,
    #         nargs='+',
    #         type=float,
    #         metavar="FLOAT FLOAT")
    parser.add_argument(
        "--loc",
        dest="loc",
        help="Prior/Initial Distribution `loc` parameter (scipy.stats.distributions).",
        default=[-4.0, -4.0],
        type=float,
        nargs="+",
        metavar="FLOAT",
    )
    parser.add_argument(
        "--scale",
        dest="scale",
        help="Prior/Initial Distribution `scale` parameter (scipy.stats.distributions).",
        default=[4.0, 4.0],
        type=float,
        nargs="+",
        metavar="FLOAT",
    )
    parser.add_argument(
        "--sample-dist",
        dest="sample_dist",
        help="Sample distribution (used for loading file) for evaluations of poisson model. default=`u`",
        default="u",
        type=str,
        metavar="STR",
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

    parser.add_argument(
        "-s",
        "--seed",
        help="Dimension of input space (default=2).",
        default=21,
        type=int,
    )
    parser.add_argument(
        "-lw",
        "--linewidth",
        help="Dimension of input space (default=2).",
        default=5,
    )
    parser.add_argument(
        "--fsize",
        help="Dimension of input space (default=2).",
        default=32,
        type=int,
        metavar="INT",
    )
    parser.add_argument(
        "--bayes",
        action="store_true",
        help="Run comparison against Bayesian Maximum A-Posteriori (MAP) estimate.",
    )
    parser.add_argument(
        "--alt",
        action="store_true",
        help="""
        Run comparison with alternative experimental design in 1-D,
        alternative QoI map in N-D for MUD estimate.
        """,
    )
    parser.add_argument(
        "--save",
        "--save-results",
        action="store_true",
        help="Save all results (including) `mud` objects to `./results.pkl`.",
    )

    return parser.parse_args(args)
