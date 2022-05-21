#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

# import os
import sys

import scipy as sp

# from mud_examples.runner import setup_logging
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter


import numpy as np
from matplotlib import cm

# from mud import __version__ as __mud_version__
from mud.funs import map_sol, mud_sol, updated_cov
from mud.norm import full_functional, norm_data, norm_input, norm_predicted
from mud.util import transform_linear_setup, null_space

# from mud_examples import __version__
from mud_examples.utils import make_2d_unit_mesh
from mud_examples.parsers import parse_args

# maybe should segment out these examples at some point.
import mud_examples.linear.models as models
from mud_examples.utils import check_dir

plt.rcParams["figure.figsize"] = 10, 10
plt.rcParams["font.size"] = 24

__author__ = "Mathematical Michael"
__copyright__ = "Mathematical Michael"
__license__ = "mit"

_logger = logging.getLogger(__name__)  # TODO: make use of this instead of print


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def main_dim(args):
    """
    Main entrypoint for High-Dim Linear Dimension Example
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    np.random.seed(args.seed)
    #     example       = args.example
    #     num_trials   = args.num_trials
    #     fsize        = args.fsize
    #     linewidth    = args.linewidth
    #     seed         = args.seed
    # dim_input     = args.input_dim
    #     save         = args.save
    #     alt          = args.alt
    #     bayes        = args.bayes
    #     prefix       = args.prefix
    #     dist         = args.dist

    presentation = False
    save = True

    if not presentation:
        plt.rcParams["mathtext.fontset"] = "stix"
        plt.rcParams["font.family"] = "STIXGeneral"
    fdir = "figures/lin"
    check_dir(fdir)

    fsize = 42

    def numnonzero(x, tol=1e-4):
        return len(x[abs(x) < tol])

    # # Impact of Dimension for Various Choices of $\\Sigma_\text{init}$

    # dim_output = dim_input
    dim_input, dim_output = 100, 100
    seed = 12
    np.random.seed(seed)

    # from sklearn.datasets import make_spd_matrix as make_spd
    # from sklearn.datasets import make_sparse_spd_matrix as make_cov
    # cov = np.eye(dim_input)
    initial_cov = np.diag(np.sort(np.random.rand(dim_input))[::-1] + 0.5)

    plt.figure(figsize=(10, 10))
    initial_mean = np.zeros(dim_input).reshape(-1, 1)
    # initial_mean = np.random.randn(dim_input).reshape(-1,1)
    randA = models.randA_gauss  # choose which variety of generating map
    A, b = models.randP(dim_input, randA=randA)
    prefix = "lin-dim-cov"
    alpha_list = [10 ** (n) for n in np.linspace(-3, 4, 8)]

    # option to fix A and perturb lam_ref

    lam_ref = np.random.randn(dim_input).reshape(-1, 1)
    # d = A @ lam_ref + b

    # %%time
    sols = compare_linear_sols_dim(lam_ref, A, b, alpha_list, initial_mean, initial_cov)

    # c = np.linalg.cond(A)*np.linalg.norm(lam_ref)
    c = np.linalg.norm(lam_ref)
    # c = 1
    err_mud_list = [
        [np.linalg.norm(_m[0] - lam_ref) / c for _m in sols[alpha]]
        for alpha in alpha_list
    ]
    err_map_list = [
        [np.linalg.norm(_m[1] - lam_ref) / c for _m in sols[alpha]]
        for alpha in alpha_list
    ]
    err_pin_list = [
        [np.linalg.norm(_m[2] - lam_ref) / c for _m in sols[alpha]]
        for alpha in alpha_list
    ]

    # c = np.linalg.cond(A)
    c = np.linalg.norm(A)
    # err_Amud_list = [[np.linalg.norm(A @ (_m[0] - lam_ref)) / c for _m in sols[alpha]] for alpha in alpha_list]
    # err_Amap_list = [[np.linalg.norm(A @ (_m[1] - lam_ref)) / c for _m in sols[alpha]] for alpha in alpha_list]
    # err_Apin_list = [[np.linalg.norm(A @ (_m[2] - lam_ref)) / c for _m in sols[alpha]] for alpha in alpha_list]

    # measure # of components that agree
    # err_mud_list = [[numnonzero(_m[0] - lam_ref) for _m in sols[alpha]] for alpha in alpha_list]
    # err_map_list = [[numnonzero(_m[1] - lam_ref) for _m in sols[alpha]] for alpha in alpha_list]
    # err_pin_list = [[numnonzero(_m[2] - lam_ref) for _m in sols[alpha]] for alpha in alpha_list]

    x, y = np.arange(1, dim_output, 1), err_mud_list[0][0:-1]

    slope, intercept = (
        np.linalg.pinv(np.vander(x, 2)) @ np.array(y).reshape(-1, 1)
    ).ravel()
    regression = slope * x + intercept

    # ---

    # # Convergence Plot

    for idx, alpha in enumerate(alpha_list):
        if (1 + idx) % 2 and alpha <= 10:
            plt.annotate(
                f"$\\alpha$={alpha:1.2E}",
                (100, max(err_map_list[idx][-1], 0.01)),
                fontsize=24,
            )
        _err_mud = err_mud_list[idx]
        _err_map = err_map_list[idx]
        _err_pin = err_pin_list[idx]

        plt.plot(x, _err_mud[:-1], label="MUD", c="k", lw=10)
        plt.plot(x, _err_map[:-1], label="MAP", c="r", ls="--", lw=5)
        plt.plot(x, _err_pin[:-1], label="LSQ", c="xkcd:light blue", ls="-", lw=5)

    # plt.plot(x, regression, c='g', ls='-')
    # plt.xlim(0,dim_output)
    if "id" in prefix:
        plt.title(
            "Convergence for Various $\\Sigma_{init} = \\alpha I$",
            fontsize=1.25 * fsize,
        )
    else:
        plt.title(
            "Convergence for Various $\\Sigma_{init} = \\alpha \\Sigma$",
            fontsize=1.25 * fsize,
        )
        # plt.yscale('log')
    # plt.yscale('log')
    # plt.xscale('log')
    plt.ylim(0, 1.0)
    # plt.ylim(1E-4, 5E-2)
    # plt.ylabel("$\\frac{||\\lambda^\\dagger - \\lambda||}{||\\lambda^\\dagger||}$", fontsize=fsize*1.25)
    plt.ylabel("Relative Error", fontsize=fsize * 1.25)
    plt.xlabel("Dimension of Output Space", fontsize=fsize)
    plt.legend(["MUD", "MAP", "Least Squares"], fontsize=fsize)
    # plt.annotate(f'Slope={slope:1.4f}', (4,4/7), fontsize=32)
    plt.savefig(f"{fdir}/{prefix}-convergence.png", bbox_inches="tight")
    plt.close("all")
    # plt.show()

    # plt.imshow(initial_cov)

    # # ## Surface Plot

    # X, Y = np.meshgrid(x,alpha_list)
    # ZU = np.array(err_mud_list)[:,1:100]
    # ZA = np.array(err_map_list)[:,1:100]

    # # import matplotlib.pyplot as plt
    # from mpl_toolkits.mplot3d import Axes3D
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')
    # ax.plot_surface(X, np.log10(Y), ZU, alpha=0.3, color='xkcd:blue')
    # ax.plot_surface(X, np.log10(Y), ZA, alpha=0.7, color='xkcd:orange')
    # ax.set(ylabel='log10(Standard Deviation)', xlabel='Output Dimension', zlabel='Error')
    # # ax.set(yscale='log')
    # ax.view_init(15, 15)
    # plt.savefig(f'lin/{prefix}-surface-error.png', bbox_inches='tight')
    # plt.close('all')
    # # plt.show()

    # # # Convergence in Predictions

    # for idx, alpha in enumerate(alpha_list):
    #     _err_mud = err_Amud_list[idx]
    #     _err_map = err_Amap_list[idx]
    #     _err_pin = err_Apin_list[idx]

    #     plt.plot(np.arange(0, dim_output),_err_mud[:], label='mud', c='k', lw=10)
    #     plt.plot(np.arange(0, dim_output),_err_map[:], label='map', c='r', ls='--', lw=5)
    #     plt.plot(np.arange(0, dim_output),_err_pin[:], label='lsq', c='xkcd:light blue', ls='-', lw=5)
    # # plt.plot(x,regression, c='g', ls='-')
    # # plt.xlim(0,dim_output)
    # if 'id' in prefix:
    #     plt.title("Convergence for Various $\\Sigma_{init} = \\alpha I$", fontsize=1.25*fsize)
    # else:
    #     plt.title("Convergence for Various $\\Sigma_{init} = \\alpha \Sigma$", fontsize=1.25*fsize)# plt.yscale('log')
    # # plt.xscale('log')
    # # plt.ylim(0, 6)
    # # plt.ylim(1E-4, 5E-2)
    # plt.ylabel("Relative Error in $\mathcal{D}$", fontsize=fsize*1.25)
    # # plt.ylabel("$\\frac{||A (\\lambda^* - \\lambda) ||}{||A||}$", fontsize=fsize, fontsize=fsize*1.25)
    # plt.xlabel('Dimension of Output Space', fontsize=fsize)
    # plt.legend(['mud', 'map', 'least squares'], fontsize=fsize, loc='lower left')
    # # plt.annotate(f'Slope={slope:1.4f}', (4,4), fontsize=24)
    # plt.savefig(f'lin/{prefix}-convergence-dimension-out.png', bbox_inches='tight')
    # plt.close('all')
    # # plt.show()


def main_rank(args):
    """
    Main entrypoint for High-Dim Linear Rank Example
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    np.random.seed(args.seed)
    #     example       = args.example
    #     num_trials   = args.num_trials
    #     fsize        = args.fsize
    #     linewidth    = args.linewidth
    #     seed         = args.seed
    #     inputdim     = args.input_dim
    #     save         = args.save
    #     alt          = args.alt
    #     bayes        = args.bayes
    #     prefix       = args.prefix
    #     dist         = args.dist

    presentation = False
    save = True

    if not presentation:
        plt.rcParams["mathtext.fontset"] = "stix"
        plt.rcParams["font.family"] = "STIXGeneral"
    fdir = "figures/lin"
    check_dir(fdir)

    fsize = 42
    plt.figure(figsize=(10, 10))
    # ---

    # # Impact of Rank(A) for Various Choices of $\\Sigma_\text{init}$
    # We sequentially incorporate $D=1, \dots , P$ dimensions into our QoI map and study
    # the 2-norm between the true value that was used to generate
    # the data and the analytical MUD/MAP points.

    dim_input, dim_output = 100, 100
    seed = 12
    np.random.seed(seed)

    # from sklearn.datasets import make_spd_matrix as make_spd
    # from sklearn.datasets import make_sparse_spd_matrix as make_cov
    # cov = np.eye(dim_input)
    initial_cov = np.diag(np.sort(np.random.rand(dim_input))[::-1] + 0.5)

    initial_mean = np.zeros(dim_input).reshape(-1, 1)
    # initial_mean = np.random.randn(dim_input).reshape(-1,1)
    randA = models.randA_list_svd
    A_list, b = models.randP(dim_input, randA=randA)
    prefix = "lin-rank-cov"
    alpha_list = [10 ** (n) for n in np.linspace(-3, 4, 8)]

    # option to fix A and perturb lam_ref
    lam_ref = np.random.randn(dim_input).reshape(-1, 1)

    # d = A@lam_ref + b

    # %%time
    sols = compare_linear_sols_rank_list(
        lam_ref, A_list, b, alpha_list, initial_mean, initial_cov
    )

    # c = np.linalg.cond(A)*np.linalg.norm(lam_ref)
    c = np.linalg.norm(lam_ref)
    err_mud_list = [
        [np.linalg.norm(_m[0] - lam_ref) / c for _m in sols[alpha]]
        for alpha in alpha_list
    ]
    err_map_list = [
        [np.linalg.norm(_m[1] - lam_ref) / c for _m in sols[alpha]]
        for alpha in alpha_list
    ]
    err_pin_list = [
        [np.linalg.norm(_m[2] - lam_ref) / c for _m in sols[alpha]]
        for alpha in alpha_list
    ]

    err_Amud_list = [
        [
            np.linalg.norm(sum(A_list[0 : i + 1]) @ (_m[0] - lam_ref))
            / np.linalg.norm(sum(A_list[0 : i + 1]))
            for i, _m in enumerate(sols[alpha])
        ]
        for alpha in alpha_list
    ]  # noqa E551
    err_Amap_list = [
        [
            np.linalg.norm(sum(A_list[0 : i + 1]) @ (_m[1] - lam_ref))
            / np.linalg.norm(sum(A_list[0 : i + 1]))
            for i, _m in enumerate(sols[alpha])
        ]
        for alpha in alpha_list
    ]  # noqa E551
    err_Apin_list = [
        [
            np.linalg.norm(sum(A_list[0 : i + 1]) @ (_m[2] - lam_ref))
            / np.linalg.norm(sum(A_list[0 : i + 1]))
            for i, _m in enumerate(sols[alpha])
        ]
        for alpha in alpha_list
    ]  # noqa E551

    # measure # of components that agree
    # err_mud_list = [[numnonzero(_m[0] - lam_ref) for _m in sols[alpha]] for alpha in alpha_list]
    # err_map_list = [[numnonzero(_m[1] - lam_ref) for _m in sols[alpha]] for alpha in alpha_list]
    # err_pin_list = [[numnonzero(_m[2] - lam_ref) for _m in sols[alpha]] for alpha in alpha_list]

    # len(err_mud_list[0])
    x, y = np.arange(1, 1 + dim_output, 1), err_mud_list[0]

    slope, intercept = (
        np.linalg.pinv(np.vander(x, 2)) @ np.array(y).reshape(-1, 1)
    ).ravel()
    # regression = slope * x + intercept

    # # Convergence Plot

    for idx, alpha in enumerate(alpha_list):
        if (1 + idx) % 2 and alpha <= 10:
            plt.annotate(
                f"$\\alpha$={alpha:1.2E}",
                (100, max(err_map_list[idx][-1], 0.01)),
                fontsize=24,
            )
        _err_mud = err_mud_list[idx]
        _err_map = err_map_list[idx]
        _err_pin = err_pin_list[idx]

        plt.plot(x, _err_mud, label="MUD", c="k", lw=10)
        plt.plot(x, _err_map, label="MAP", c="r", ls="--", lw=5)
        plt.plot(x, _err_pin, label="LSQ", c="xkcd:light blue", ls="-", lw=5)

    # plt.plot(x, regression, c='g', ls='-')
    # plt.xlim(0,dim_output)
    if "id" in prefix:
        plt.title(
            "Convergence for Various $\\Sigma_{init} = \\alpha I$",
            fontsize=1.25 * fsize,
        )
    else:
        plt.title(
            "Convergence for Various $\\Sigma_{init} = \\alpha \\Sigma$",
            fontsize=1.25 * fsize,
        )
    # plt.yscale('log')
    # plt.xscale('log')
    plt.ylim(0, 1.0)
    # plt.ylim(1E-4, 5E-2)
    # plt.ylabel("$\\frac{||\\lambda^\\dagger - \\lambda||}{||\\lambda^\\dagger||}$", fontsize=fsize * 1.25)
    plt.ylabel("Relative Error", fontsize=fsize * 1.25)
    plt.xlabel("Rank(A)", fontsize=fsize)
    plt.legend(["MUD", "MAP", "Least Squares"], fontsize=fsize)
    # plt.annotate(f'Slope={slope:1.4f}', (4,4/7), fontsize=32)
    plt.savefig(f"{fdir}/{prefix}-convergence.png", bbox_inches="tight")
    plt.close("all")
    # plt.show()

    # plt.imshow(initial_cov)

    # ---

    # ## Surface Plot

    # X, Y = np.meshgrid(x,alpha_list)
    # ZU = np.array(err_mud_list)
    # ZA = np.array(err_map_list)
    # ZI = np.array(err_pin_list)

    # # import matplotlib.pyplot as plt
    # from mpl_toolkits.mplot3d import Axes3D
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')
    # ax.plot_surface(X, np.log10(Y), ZU, alpha=0.3, color='xkcd:blue')
    # ax.plot_surface(X, np.log10(Y), ZA, alpha=0.7, color='xkcd:orange')
    # ax.set(ylabel='log10(Standard Deviation)', xlabel='Output Dimension', zlabel='Error')
    # # ax.set(yscale='log')
    # ax.view_init(15, 15)
    # # plt.savefig(f'lin/{prefix}-surface-error.png', bbox_inches='tight')
    # plt.show()

    # # print(c, slope)

    # # # Convergence in Predictions

    # for idx, alpha in enumerate(alpha_list):
    #     _err_mud = err_Amud_list[idx]
    #     _err_map = err_Amap_list[idx]
    #     _err_pin = err_Apin_list[idx]

    #     plt.plot(np.arange(0, dim_output), _err_mud[:], label='mud', c='k', lw=10)
    #     plt.plot(np.arange(0, dim_output), _err_map[:], label='map', c='r', ls='--', lw=5)
    #     plt.plot(np.arange(0, dim_output), _err_pin[:], label='lsq', c='xkcd:light blue', ls='-', lw=5)
    # # plt.plot(x,regression, c='g', ls='-')
    # # plt.xlim(0,dim_output)
    # if 'id' in prefix:
    #     plt.title("Convergence for Various $\\Sigma_{init} = \\alpha I$", fontsize=1.25*fsize)
    # else:
    #     plt.title("Convergence for Various $\\Sigma_{init} = \\alpha \Sigma$", fontsize=1.25*fsize)# plt.yscale('log')
    # plt.xscale('log')
    # plt.yscale('log')
    # # plt.ylim(0, 6)
    # # plt.ylim(1E-4, 5E-2)
    # # plt.ylabel("$\\frac{||A (\\lambda^* - \\lambda) ||}{||A||}$", fontsize=fsize)
    # plt.ylabel("Relative Error in $\mathcal{D}$", fontsize=fsize*1.25)
    # plt.xlabel('Matrix Rank', fontsize=fsize)
    # plt.legend(['mud', 'map', 'least squares'], fontsize=fsize, loc='lower left')
    # # plt.annotate(f'Slope={slope:1.4f}', (4,4), fontsize=24)
    # # plt.savefig(f'lin/{prefix}-convergence-out.png', bbox_inches='tight')
    # plt.show()


def main_contours(args):
    """
    Main entrypoint for 2D Linear Rank-Deficient Example (Contour Plots)
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    np.random.seed(args.seed)
    #     example       = args.example
    #     num_trials   = args.num_trials
    #     fsize        = args.fsize
    #     linewidth    = args.linewidth
    #     seed         = args.seed
    #     inputdim     = args.input_dim
    #     save         = args.save
    #     alt          = args.alt
    #     bayes        = args.bayes
    #     prefix       = args.prefix
    #     dist         = args.dist

    presentation = False
    save = True

    if not presentation:
        plt.rcParams["mathtext.fontset"] = "stix"
        plt.rcParams["font.family"] = "STIXGeneral"
    fdir = "figures/contours"
    check_dir(fdir)
    lam_true = np.array([0.7, 0.3])
    initial_mean = np.array([0.25, 0.25])
    A = np.array([[1, 1]])
    b = np.zeros((1, 1))

    experiments = {}

    # data mismatch
    experiments["data_mismatch"] = {}
    experiments["data_mismatch"]["out_file"] = f"{fdir}/data_mismatch_contour.png"
    experiments["data_mismatch"]["data_check"] = True
    experiments["data_mismatch"]["full_check"] = False
    experiments["data_mismatch"]["tk_reg"] = 0
    experiments["data_mismatch"]["pr_reg"] = 0

    # tikonov regularization
    experiments["tikonov"] = {}
    experiments["tikonov"]["out_file"] = f"{fdir}/tikonov_contour.png"
    experiments["tikonov"]["tk_reg"] = 1
    experiments["tikonov"]["pr_reg"] = 0
    experiments["tikonov"]["data_check"] = False
    experiments["tikonov"]["full_check"] = False

    # modified regularization
    experiments["modified"] = {}
    experiments["modified"]["out_file"] = f"{fdir}/consistent_contour.png"
    experiments["modified"]["tk_reg"] = 1
    experiments["modified"]["pr_reg"] = 1
    experiments["modified"]["data_check"] = False
    experiments["modified"]["full_check"] = False

    # map point
    experiments["classical"] = {}
    experiments["classical"]["out_file"] = f"{fdir}/classical_solution.png"
    experiments["classical"]["tk_reg"] = 1
    experiments["classical"]["pr_reg"] = 0
    experiments["classical"]["data_check"] = True
    experiments["classical"]["full_check"] = True

    # mud point
    experiments["consistent"] = {}
    experiments["consistent"]["out_file"] = f"{fdir}/consistent_solution.png"
    experiments["consistent"]["tk_reg"] = 1
    experiments["consistent"]["pr_reg"] = 1
    experiments["consistent"]["data_check"] = True
    experiments["consistent"]["full_check"] = True

    # comparison
    experiments["compare"] = {}
    experiments["compare"]["out_file"] = f"{fdir}/map_compare_contour.png"
    experiments["compare"]["data_check"] = True
    experiments["compare"]["full_check"] = True
    experiments["compare"]["tk_reg"] = 1
    experiments["compare"]["pr_reg"] = 0
    experiments["compare"]["comparison"] = True
    experiments["compare"]["cov_01"] = -0.5

    for ex in experiments:
        _logger.info(f"Running {ex}")
        config = experiments[ex]
        out_file = config.get("out_file", "latest_figure.png")
        tk_reg = config.get("tk_reg", 1)
        pr_reg = config.get("pr_reg", 1)
        cov_01 = config.get("cov_01", -0.25)
        cov_11 = config.get("cov_11", 0.5)
        obs_std = config.get("obs_std", 0.5)
        full_check = config.get("full_check", True)
        data_check = config.get("data_check", True)
        numr_check = config.get("numr_check", False)
        comparison = config.get("comparison", False)

        contour_example(
            A=A,
            b=b,
            save=save,
            param_ref=lam_true,
            compare=comparison,
            cov_01=cov_01,
            cov_11=cov_11,
            initial_mean=initial_mean,
            alpha=tk_reg,
            omega=pr_reg,
            show_full=full_check,
            show_data=data_check,
            show_est=numr_check,
            obs_std=obs_std,
            figname=out_file,
        )


def main_meas(args):
    """
    Main entrypoint for High-Dim Linear Measurement Example
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    np.random.seed(args.seed)
    #     example       = args.example
    #     num_trials   = args.num_trials
    #     fsize        = args.fsize
    #     linewidth    = args.linewidth
    #     seed         = args.seed
    # dim_input     = args.input_dim
    # save         = args.save
    #     alt          = args.alt
    #     bayes        = args.bayes
    #     prefix       = args.prefix
    #     dist         = args.dist

    presentation = False
    save = True

    if not presentation:
        plt.rcParams["mathtext.fontset"] = "stix"
        plt.rcParams["font.family"] = "STIXGeneral"
    fdir = "figures/lin"
    check_dir(fdir)

    fsize = 42

    def numnonzero(x, tol=1e-4):
        return len(x[abs(x) < tol])

    # # Impact of Number of Measurements for Various Choices of $\\Sigma_\text{init}$

    # dim_output = dim_input
    dim_input, dim_output = 20, 5
    # seed = 12
    # np.random.seed(seed)

    initial_cov = np.diag(np.sort(np.random.rand(dim_input))[::-1] + 0.5)
    # initial_cov = np.eye(dim_input)  # will cause spectrum of updated covariance to contain repeated eigenvalues

    plt.figure(figsize=(10, 10))
    # initial_mean = np.zeros(dim_input).reshape(-1, 1)
    # initial_mean = np.random.randn(dim_input).reshape(-1,1)
    # num_obs_list = np.arange(1, 101).tolist()

    lam_ref = np.random.randn(dim_input).reshape(-1, 1)

    prefix = "lin-meas-cov"

    # Ns = [10, 50, 100, 500, 1000]

    sigma = 1e-1
    # np.random.seed(21)
    # Ns = np.arange(10, 2001, 50).tolist()
    Ns = [10, 100, 1000, 10000]

    # for _ in range(num_trials):

    operator_list, data_list, _ = models.createRandomLinearProblem(
        lam_ref,
        dim_output,
        [max(Ns)] * dim_output,  # want to iterate over increasing measurements
        [0] * dim_output,  # noiseless data bc we want to simulate multiple trials
        dist="norm",
        repeated=True,
    )

    MUD = np.zeros((dim_input, len(Ns)))
    UP = np.zeros((dim_input, len(Ns)))
    noise_draw = np.random.randn(dim_output, max(Ns)) * sigma

    for j, N in enumerate(Ns):
        A, b, _ = transform_measurements(operator_list, data_list, N, sigma, noise_draw)
        MUD[:, j] = mud_sol(A, b, cov=initial_cov)
        up_cov = updated_cov(A, initial_cov)
        up_sdvals = sp.linalg.svdvals(up_cov)
        # print(up_sdvals.shape, dim_input, up_cov.shape)
        UP[:, j] = up_sdvals

    # mud_var = MUD.var(axis=2)
    lines = ["solid", "dashed", "dashdot", "dotted"]

    for p in range(dim_input):
        plt.plot(
            Ns,
            UP[p, :],
            label=f"SV {p}",
            alpha=0.4,
            lw=5,
            ls=lines[p % len(lines)],
        )

    # plt.plot(Ns, mud_var, label='MUD', c='k', lw=10)
    # plt.title("Precision of MUD Estimates", fontsize=1.25 * fsize)
    plt.yscale("log")
    plt.xscale("log")
    plt.ylabel("Eigenvalues of $\\Sigma_{up}$", fontsize=fsize * 1.25)
    plt.xlabel("Number of Measurements", fontsize=fsize)
    # plt.legend()
    if save:
        plt.savefig(f"{fdir}/{prefix}-convergence.png", bbox_inches="tight")
        plt.close("all")
    else:
        plt.show()
        plt.close("all")

    fig, ax = plt.subplots(figsize=(15, 10))
    ax.set_yscale("log")
    index_values = np.arange(dim_input) + 1

    for i, N in enumerate(Ns):
        ax.scatter(
            index_values,
            UP[:, i],
            marker="o",
            s=200,
            facecolors="none",
            edgecolors="k",
        )

        ax.plot(
            index_values,
            UP[:, i],
            label=f"$N={N:1.0E}$",
            alpha=1,
            lw=3,
            ls=lines[i % len(lines)],
            c="k",
        )
    ax.set_xticks(index_values)
    ax.set_xticklabels(ax.get_xticks(), rotation=0)
    ax.set_xlabel("Index", fontsize=fsize)
    ax.set_ylabel("Eigenvalue", fontsize=fsize)

    ax.xaxis.set_major_formatter(FormatStrFormatter("%2d"))
    ax.legend(loc="lower left", fontsize=fsize * 0.75)

    if save:
        plt.savefig(f"{fdir}/{prefix}-sd-convergence.png", bbox_inches="tight")
        plt.close("all")
    else:
        plt.show()
        plt.close("all")


def main_meas_var(args):
    """
    Main entrypoint for High-Dim Linear Measurement Example
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    np.random.seed(args.seed)
    #     example       = args.example
    #     num_trials   = args.num_trials
    #     fsize        = args.fsize
    #     linewidth    = args.linewidth
    #     seed         = args.seed
    # dim_input     = args.input_dim
    # save         = args.save
    #     alt          = args.alt
    #     bayes        = args.bayes
    #     prefix       = args.prefix
    #     dist         = args.dist

    presentation = False
    save = True

    if not presentation:
        plt.rcParams["mathtext.fontset"] = "stix"
        plt.rcParams["font.family"] = "STIXGeneral"
    fdir = "figures/lin"
    check_dir(fdir)

    fsize = 42

    def numnonzero(x, tol=1e-4):
        return len(x[abs(x) < tol])

    # # Impact of Number of Measurements for Various Choices of $\\Sigma_\text{init}$

    # dim_output = dim_input
    dim_input, dim_output = 4, 2
    # seed = 12
    # np.random.seed(seed)

    # initial_cov = np.diag(np.sort(np.random.rand(dim_input))[::-1] + 0.5)
    initial_cov = np.eye(dim_input)

    plt.figure(figsize=(10, 10))
    # initial_mean = np.zeros(dim_input).reshape(-1, 1)
    # initial_mean = np.random.randn(dim_input).reshape(-1,1)
    # num_obs_list = np.arange(1, 101).tolist()

    lam_ref = np.random.randn(dim_input).reshape(-1, 1)

    prefix = "lin-meas-cov"

    # Ns = [10, 50, 100, 500, 1000]

    sigma = 1e-1
    # np.random.seed(21)
    Ns = np.arange(10, 2001, 50).tolist()
    # Ns = [10, 50, 100, 500, 1000, 5000, 10000]

    num_trials = 50
    # for _ in range(num_trials):

    def A_N(M, N, sigma):
        A = np.sqrt(N) / sigma * M
        return A

    def d_N(M, lam, n):
        d = M @ lam + n
        assert len(d.ravel()) == len(
            n.ravel()
        ), f"Shape mismatch noise={n.shape}, data={d.shape}"
        return d

    def b_N(N, d, sigma):
        b = -1 / np.sqrt(N) * np.sum(np.divide(d, sigma), axis=1)
        return b

    # M = np.random.normal(size=(dim_output, dim_input))
    operator_list, data_list, _ = models.createRandomLinearProblem(
        lam_ref,
        dim_output,
        [max(Ns)] * dim_output,  # want to iterate over increasing measurements
        [0] * dim_output,  # noiseless data bc we want to simulate multiple trials
        dist="norm",
        repeated=True,
    )

    # operator list has dim_output 1xdim_input matrices
    MUD = np.zeros((dim_input, len(Ns), num_trials))
    # M = np.array(operator_list).reshape(dim_output, dim_input)
    noise_draw = [
        np.random.randn(dim_output, max(Ns)) * sigma for _ in range(num_trials)
    ]
    for j, N in enumerate(Ns):
        # _A = A_N(M, N, sigma)
        for i in range(num_trials):
            # _b = b_N(N, d_N(M, lam_ref, noise_draw[i][:, 0:N]), sigma)
            # A, b = transform_linear_setup(operator_list, data_list, sigma)
            A, b, _ = transform_measurements(
                operator_list, data_list, N, sigma, noise_draw[i]
            )
            MUD[:, j, i] = mud_sol(A, b, cov=initial_cov)

    mud_var = MUD.var(axis=2).mean(axis=0)
    plt.plot(Ns, mud_var, label="MUD", c="k", lw=10)

    # plt.title("Precision of MUD Estimates", fontsize=1.25 * fsize)
    plt.yscale("log")
    plt.xscale("log")
    plt.ylabel("Mean Variance of MUD Estimates", fontsize=fsize * 1.25)
    plt.xlabel("Number of Measurements", fontsize=fsize)
    plt.legend()
    # plt.legend(['MUD', 'Least Squares'], fontsize=fsize)
    if save:
        plt.savefig(f"{fdir}/{prefix}-convergence.png", bbox_inches="tight")
        plt.close("all")
    else:
        plt.show()
        plt.close("all")


def main(args):
    """
    Main entrypoint for example-generation
    """
    main_contours(args)
    main_rank(args)
    main_dim(args)
    main_meas(args)


def run():
    """Entry point for console_scripts"""
    main(sys.argv[1:])


def run_meas():
    """Entry point for console_scripts"""
    main_meas(sys.argv[1:])


def run_meas_var():
    """Entry point for console_scripts"""
    main_meas_var(sys.argv[1:])


############################################################


def contour_example(
    A=np.array([[1, 1]]),
    b=np.zeros([1, 1]),  # noqa: C901
    cov_11=0.5,
    cov_01=-0.25,
    initial_mean=np.array([0.25, 0.25]),
    alpha=1,
    omega=1,
    obs_std=1,
    show_full=True,
    show_data=True,
    show_est=False,
    param_ref=None,
    compare=False,
    fsize=42,
    figname="latest_figure.png",
    save=False,
):
    """
    alpha: float in [0, 1], weight of Tikhonov regularization
    omega: float in [0, 1], weight of Modified regularization
    """
    # mesh for plotting
    N, r = 250, 1
    X, Y, XX = make_2d_unit_mesh(N, r)
    inputs = XX

    std_of_data = [obs_std]
    obs_cov = np.diag(std_of_data)
    observed_data_mean = np.array([[1]])
    initial_cov = np.array([[1, cov_01], [cov_01, cov_11]])

    assert np.all(np.linalg.eigvals(initial_cov) > 0)

    z = full_functional(
        A, XX, b, initial_mean, initial_cov, observed_data_mean, observed_cov=obs_cov
    )
    zp = norm_predicted(A, XX, initial_mean, initial_cov)
    zi = norm_input(XX, initial_mean, initial_cov)
    zd = norm_data(A, XX, b, observed_data_mean, observed_cov=obs_cov)
    # sanity check that all arguments passed correctly:
    assert np.linalg.norm(z - zi - zd + zp) < 1e-8

    # plotting contours
    z = alpha * zi + zd - omega * zp
    mud_a = np.argmin(z)
    map_a = np.argmin(alpha * zi + zd)

    # get mud/map points from minimal values on mesh
    mud_pt = inputs[mud_a, :]
    map_pt = inputs[map_a, :]

    msize = 500
    ls = (np.linalg.pinv(A) @ observed_data_mean.T).ravel()
    if show_data:
        plt.contour(
            inputs[:, 0].reshape(N, N),
            inputs[:, 1].reshape(N, N),
            (zd).reshape(N, N),
            25,
            cmap=cm.viridis,
            alpha=0.5,
            vmin=0,
            vmax=4,
        )
        plt.axis("equal")

        s = np.linspace(-2 * r, 2 * r, 10)

        if A.shape[0] < A.shape[1]:
            # nullspace through least-squares
            null_line = null_space(A) * s + ls.reshape(-1, 1)
            plt.plot(
                null_line[0, :],
                null_line[1, :],
                label="Solution Contour",
                lw=2,
                color="xkcd:red",
            )
            if not show_full:
                plt.annotate(
                    "Solution Contour", (0.1, 0.9), fontsize=fsize, backgroundcolor="w"
                )

    if show_full:
        plt.contour(
            inputs[:, 0].reshape(N, N),
            inputs[:, 1].reshape(N, N),
            z.reshape(N, N),
            50,
            cmap=cm.viridis,
            alpha=1.0,
        )
    elif alpha + omega > 0:
        plt.contour(
            inputs[:, 0].reshape(N, N),
            inputs[:, 1].reshape(N, N),
            (alpha * zi - omega * zp).reshape(N, N),
            100,
            cmap=cm.viridis,
            alpha=0.25,
        )
    plt.axis("equal")

    if alpha + omega > 0:
        plt.scatter(
            initial_mean[0], initial_mean[1], label="Initial Mean", color="k", s=msize
        )
        if not show_full:
            plt.annotate(
                "Initial Mean",
                (initial_mean[0] + 0.001 * fsize, initial_mean[1] - 0.001 * fsize),
                fontsize=fsize,
                backgroundcolor="w",
            )
        else:
            if compare:
                plt.scatter(
                    param_ref[0],
                    param_ref[1],
                    label="$\\lambda^\\dagger$",
                    color="k",
                    s=msize,
                    marker="s",
                )

                plt.annotate(
                    "Truth",
                    (param_ref[0] + 0.00075 * fsize, param_ref[1] + 0.00075 * fsize),
                    fontsize=fsize,
                    backgroundcolor="w",
                )

        show_mud = omega > 0 or compare

        if show_full:
            # scatter and line from origin to least squares
            plt.scatter(
                ls[0],
                ls[1],
                label="Least Squares",
                color="xkcd:blue",
                marker="d",
                s=msize,
                zorder=10,
            )
            plt.plot(
                [0, ls[0]], [0, ls[1]], color="xkcd:blue", marker="d", lw=1, zorder=10
            )
            plt.annotate(
                "Least Squares",
                (ls[0] - 0.001 * fsize, ls[1] + 0.001 * fsize),
                fontsize=fsize,
                backgroundcolor="w",
            )

            if show_est:  # numerical solutions
                if omega > 0:
                    plt.scatter(
                        mud_pt[0],
                        mud_pt[1],
                        label="min: Tk - Un",
                        color="xkcd:sky blue",
                        marker="o",
                        s=3 * msize,
                        zorder=10,
                    )
                if alpha > 0 and omega != 1:
                    plt.scatter(
                        map_pt[0],
                        map_pt[1],
                        label="min: Tk",
                        color="xkcd:blue",
                        marker="o",
                        s=3 * msize,
                        zorder=10,
                    )

            if alpha > 0 and omega != 1:  # analytical MAP point
                map_pt_eq = map_sol(
                    A,
                    b,
                    observed_data_mean,
                    initial_mean,
                    initial_cov,
                    data_cov=obs_cov,
                    w=alpha,
                )
                plt.scatter(
                    map_pt_eq[0],
                    map_pt_eq[1],
                    label="MAP",
                    color="xkcd:orange",
                    marker="x",
                    s=msize,
                    lw=10,
                    zorder=10,
                )

                if compare:  # second map point has half the regularization strength
                    plt.annotate(
                        "MAP$_{\\alpha}$",
                        (map_pt_eq[0] - 0.004 * fsize, map_pt_eq[1] - 0.002 * fsize),
                        fontsize=fsize,
                        backgroundcolor="w",
                    )

                else:
                    plt.annotate(
                        "MAP$_{\\alpha}$",
                        (map_pt_eq[0] + 0.0001 * fsize, map_pt_eq[1] - 0.002 * fsize),
                        fontsize=fsize,
                        backgroundcolor="w",
                    )

            if show_mud:  # analytical MUD point
                mud_pt_eq = mud_sol(A, b, observed_data_mean, initial_mean, initial_cov)
                plt.scatter(
                    mud_pt_eq[0],
                    mud_pt_eq[1],
                    label="MUD",
                    color="xkcd:brown",
                    marker="*",
                    s=2 * msize,
                    lw=5,
                    zorder=10,
                )
                plt.annotate(
                    "MUD",
                    (mud_pt_eq[0] + 0.001 * fsize, mud_pt_eq[1] - 0.001 * fsize),
                    fontsize=fsize,
                    backgroundcolor="w",
                )

        if A.shape[0] < A.shape[1]:
            # want orthogonal nullspace, function gives one that is already normalized
            v = null_space(A @ initial_cov)
            v = v[
                ::-1
            ]  # in 2D, we can just swap entries and put a negative sign in front of one
            v[0] = -v[0]

            if show_full and show_mud:
                # grid search to find upper/lower bounds of line being drawn.
                # importance is the direction, image is nicer with a proper origin/termination
                s = np.linspace(-1, 1, 1000)
                new_line = (v.reshape(-1, 1) * s) + initial_mean.reshape(-1, 1)
                mx = np.argmin(
                    np.linalg.norm(new_line - initial_mean.reshape(-1, 1), axis=0)
                )
                mn = np.argmin(
                    np.linalg.norm(new_line - mud_pt_eq.reshape(-1, 1), axis=0)
                )
                plt.plot(
                    new_line[0, mn:mx],
                    new_line[1, mn:mx],
                    lw=1,
                    label="projection line",
                    c="k",
                )
        elif show_full:
            plt.plot(
                [initial_mean[0], ls[0]],
                [initial_mean[1], ls[1]],
                lw=1,
                label="Projection Line",
                c="k",
            )

    #     print(p)

    plt.axis("square")
    plt.axis([0, r, 0, r])
    #     plt.legend(fontsize=fsize)
    plt.xticks(fontsize=0.75 * fsize)
    plt.yticks(fontsize=0.75 * fsize)
    plt.tight_layout()
    if save:
        if "/" in figname:
            fdir = "/".join(figname.split("/")[:-1])
            check_dir(fdir)
        plt.savefig(figname, dpi=300)
        plt.close("all")


#     plt.title('Predicted Covariance: {}'.format((A@initial_cov@A.T).ravel() ))
# plt.show()


def compare_mud_map_pin(A, b, y, mean, cov):
    mud_pt = mud_sol(A, b, y, mean, cov)
    map_pt = map_sol(A, b, y, mean, cov)
    pin_pt = (np.linalg.pinv(A) @ (y - b)).reshape(-1, 1)
    return mud_pt, map_pt, pin_pt


def transform_rank_list(lam_ref, A, b, rank):
    """
    A is a list here. We sum the first `rank` elements of it
    to return a matrix with the desired rank.
    """
    _A = sum(A[0:rank])
    _b = b
    _d = _A @ lam_ref + _b
    assert np.linalg.matrix_rank(_A) == rank, "Unexpected rank mismatch"
    return _A, _b, _d


def transform_dim_out(lam_ref, A, b, dim):
    if isinstance(A, list) or isinstance(A, tuple):
        raise AttributeError("A must be a matrix, not a list or tuple.")

    _A = A[:dim, :]
    _b = b[:dim, :]
    _d = _A @ lam_ref + _b
    return _A, _b, _d


def transform_measurements(operator_list, data_list, measurements, std_list, noise):
    dim_output = len(operator_list)
    N = measurements
    _oper_list = [M[0:N, :] for M in operator_list]
    _d = np.array([y[0:N] for y in data_list]) + noise[:, 0:N]
    _data_list = _d.tolist()
    A, b = transform_linear_setup(_oper_list, _data_list, std_list)
    d = np.zeros(dim_output).reshape(-1, 1)
    return A, b, d


def compare_linear_sols_rank_list(lam_ref, A, b, alpha=1, mean=None, cov=None):
    """
    Input and output dimensions fixed, varying rank 1..dim_output.
    """

    return compare_linear_sols(transform_rank_list, lam_ref, A, b, alpha, mean, cov)


def compare_linear_sols_dim(lam_ref, A, b, alpha=1, mean=None, cov=None):
    """
    Input dimension fixed, varying output dimension.
    """
    return compare_linear_sols(transform_dim_out, lam_ref, A, b, alpha, mean, cov)


def compare_linear_sols(transform, lam_ref, A, b, alpha=1, mean=None, cov=None):
    """
    Input dimension fixed, varying according to the output
    of the anonymous function `transform`'s return.
    """
    sols = {}
    if isinstance(alpha, (list, tuple)):
        alpha_list = alpha
    else:
        alpha_list = [alpha]

    if isinstance(A, np.ndarray):
        dim_in = A.shape[1]
    else:
        dim_in = len(A)

    if mean is None:
        mean = np.zeros(dim_in)

    if cov is None:
        cov = np.eye(dim_in)

    _logger.info("alpha = {}".format(alpha_list))
    if isinstance(
        A, list
    ):  # svd approach returns list (max dim output), so does measurement study (max meas)
        max_iteration = A[0].shape[0]
        if max_iteration == 1:
            max_iteration = (
                100  # repeated measurement map is 1xp, this is a dirty override.
            )
    else:
        max_iteration = A.shape[0]

    for alpha in alpha_list:
        sols[alpha] = []
        for _out in range(1, max_iteration + 1, 1):
            _A, _b, _y = transform(lam_ref, A, b, _out)
            _mud, _map, _pin = compare_mud_map_pin(_A, _b, _y, mean, alpha * cov)
            sols[alpha].append((_mud, _map, _pin))

    return sols


if __name__ == "__main__":
    run()
