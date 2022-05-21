#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import argparse
import logging

# import os
import sys

import matplotlib.pyplot as plt
import numpy as np

# from matplotlib import cm
# from mud import __version__ as __mud_version__
from scipy.stats import gaussian_kde as kde  # A standard kernel density estimator
from scipy.stats import norm, uniform  # The standard Normal distribution

# from mud_examples import __version__
from mud_examples.parsers import parse_args
from mud_examples.utils import check_dir

plt.rcParams["figure.figsize"] = 10, 10
plt.rcParams["font.size"] = 24

__author__ = "Mathematical Michael"
__copyright__ = "Mathematical Michael"
__license__ = "mit"

_logger = logging.getLogger(__name__)  # TODO: use this


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
    """
    Main entrypoint for example-generation
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
    fdir = "figures/comparison"
    check_dir(fdir)
    presentation = False
    save = True

    if not presentation:
        plt.rcParams["mathtext.fontset"] = "stix"
        plt.rcParams["font.family"] = "STIXGeneral"

    # number of samples from initial and observed mean (mu) and st. dev (sigma)
    N, mu, sigma = int(1e3), 0.25, 0.1
    lam = np.random.uniform(low=-1, high=1, size=N)

    # Evaluate the QoI map on this initial sample set to form a predicted data
    qvals_predict = QoI(lam, 5)  # Evaluate lam^5 samples

    # Estimate the push-forward density for the QoI
    pi_predict = kde(qvals_predict)

    # Compute more observations for use in BIP
    tick_fsize = 28
    legend_fsize = 24
    for num_data in [1, 5, 10, 20]:
        np.random.seed(
            123456
        )  # Just for reproducibility, you can comment out if you want.
        data = norm.rvs(loc=mu, scale=sigma ** 2, size=num_data)

        # We will estimate the observed distribution using a parametric estimate to keep
        # the assumptions involved as similar as possible between the BIP and the SIP
        # So, we will assume the sigma is known but that the mean mu is unknown and estimated
        # from data to fit a Gaussian distribution
        mu_est = np.mean(data)

        r_approx = np.divide(
            norm.pdf(qvals_predict, loc=mu_est, scale=sigma), pi_predict(qvals_predict)
        )

        # Use r to compute weighted KDE approximating the updated density
        update_kde = kde(lam, weights=r_approx)

        # Construct estimated push-forward of this updated density
        pf_update_kde = kde(qvals_predict, weights=r_approx)

        likelihood_vals = np.zeros(N)
        for i in range(N):
            likelihood_vals[i] = data_likelihood(
                qvals_predict[i], data, num_data, sigma
            )

        # compute normalizing constants
        C_nonlinear = np.mean(likelihood_vals)
        data_like_normalized = likelihood_vals / C_nonlinear

        posterior_kde = kde(lam, weights=data_like_normalized)

        # Construct push-forward of statistical Bayesian posterior
        pf_posterior_kde = kde(qvals_predict, weights=data_like_normalized)

        # Plot the initial, updated, and posterior densities
        fig, ax = plt.subplots(figsize=(10, 10))
        lam_plot = np.linspace(-1, 1, num=1000)
        ax.plot(
            lam_plot,
            uniform.pdf(lam_plot, loc=-1, scale=2),
            "b--",
            linewidth=4,
            label="Initial/Prior",
        )
        ax.plot(lam_plot, update_kde(lam_plot), "k-.", linewidth=4, label="Update")
        ax.plot(lam_plot, posterior_kde(lam_plot), "g:", linewidth=4, label="Posterior")
        ax.set_xlim([-1, 1])
        if num_data > 1:
            plt.annotate(f"$N={num_data}$", (-0.75, 5), fontsize=legend_fsize * 1.5)
            ax.set_ylim([0, 28])  # fix axis height for comparisons
        #         else:
        #             ax.set_ylim([0, 5])
        ax.tick_params(axis="x", labelsize=tick_fsize)
        ax.tick_params(axis="y", labelsize=tick_fsize)
        ax.set_xlabel("$\\Lambda$", fontsize=1.25 * tick_fsize)
        ax.legend(fontsize=legend_fsize, loc="upper left")
        if save:
            fig.savefig(f"{fdir}/bip-vs-sip-{num_data}.png", bbox_inches="tight")
            plt.close(fig)
        # plt.show()

        # Plot the push-forward of the initial, observed density,
        # and push-forward of pullback and stats posterior
        fig, ax = plt.subplots(figsize=(10, 10))
        qplot = np.linspace(-1, 1, num=1000)
        ax.plot(
            qplot,
            norm.pdf(qplot, loc=mu, scale=sigma),
            "r-",
            linewidth=6,
            label="$N(0.25, 0.1^2)$",
        )
        ax.plot(qplot, pi_predict(qplot), "b-.", linewidth=4, label="PF of Initial")
        ax.plot(qplot, pf_update_kde(qplot), "k--", linewidth=4, label="PF of Update")
        ax.plot(
            qplot, pf_posterior_kde(qplot), "g:", linewidth=4, label="PF of Posterior"
        )

        ax.set_xlim([-1, 1])
        if num_data > 1:
            plt.annotate(f"$N={num_data}$", (-0.75, 5), fontsize=legend_fsize * 1.5)
            ax.set_ylim([0, 28])  # fix axis height for comparisons
        #         else:
        #             ax.set_ylim([0, 5])
        ax.tick_params(axis="x", labelsize=tick_fsize)
        ax.tick_params(axis="y", labelsize=tick_fsize)
        ax.set_xlabel("$\\mathcal{D}$", fontsize=1.25 * tick_fsize)
        ax.legend(fontsize=legend_fsize, loc="upper left")
        if save:
            fig.savefig(f"{fdir}/bip-vs-sip-pf-{num_data}.png", bbox_inches="tight")
            plt.close(fig)
        # plt.show()


def run():
    main(sys.argv[1:])


############################################################


def QoI(lam, p):
    """
    Defines a QoI mapping function as monomials to some power p
    """
    q = lam ** p
    return q


def data_likelihood(qvals, data, num_data, sigma):
    v = 1.0
    for i in range(num_data):
        v *= norm.pdf(qvals - data[i], loc=0, scale=sigma)
    return v


if __name__ == "__main__":
    run()
