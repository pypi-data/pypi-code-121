# This file is part of PyCosmo, a multipurpose cosmology calculation tool in Python.
#
# Copyright (C) 2013-2021 ETH Zurich, Institute for Particle and Astrophysics and SIS
# ID.
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.

from sympy2c import OdeCombined
from CosmologyCore_massivenu import *

# definition of the SymPy symbols
rsa_trigger_k_eta = Symbol("rsa_trigger_k_eta")
rsa_trigger_taudot_eta = Symbol("rsa_trigger_taudot_eta")

# definition of global variables
globals_ = Globals(
    omega_r,
    omega_m,
    omega_l,
    flat_universe,
    H0,
    omega_b,
    omega_dm,
    omega_gamma,
    omega_neu,
    rh,
    Tcmb,
    lna_0,
    k,
    mpc,
    hbar,
    c,
    kb,
    G,
    evc2,
    N_massless_nu,
    N_massive_nu,
    N_eff,
    massive_nu_total_mass,
    T_mnu,
    rsa_trigger_k_eta,
    rsa_trigger_taudot_eta,
)

# import the full ODE system (without RSA)
ode_full = OdeFast(
    "ode_full",
    lna,
    lhs(),
    rhs(),
    splits=cosmology.equation_parameters.splits,
    reorder=cosmology.equation_parameters.reorder,
)


def lhs_rsa():
    # lhs of the ODE system
    # no radiation fields in RSA
    y = [Phi, delta, u, delta_b, u_b]
    for j in range((l_max_mnu + 1) * nq):
        y.append(M[j])
    return tuple(y)


def rhs_rsa(H=H_Mpc, H0=H0_Mpc, R=R, amnu=amnu, l_max=2):
    """
    rhs of the ODE system containing the equations
    in d(lna), order needs to be the same as in lhs.
    l_max = 2 because of RSA
    """
    k_H = k / (a * H)

    # empty symbols for the radiation hierarchies
    Theta_interp = [sp.S.Zero for _ in range(l_max + 1)]
    Theta_P_interp = [sp.S.Zero for _ in range(l_max + 1)]
    N_interp = [sp.S.Zero for _ in range(l_max + 1)]
    dM_dlan = [sp.S.Zero for _ in range(nq * (l_max_mnu + 1))]

    # Einstein equations
    N_interp[0] = Phi
    Theta_interp[0] = Phi + u_b * taudot_interp(a) / k
    Psi = -Phi - 12 * (H0 / (k * a)) ** 2 * (
        omega_gamma * Theta_interp[2] + omega_neu * N_interp[2] + C_nu * sum_M2
    )
    Pi = Theta_interp[2] + Theta_P_interp[0] + Theta_P_interp[2]
    dPhi_dlan = (
        Psi
        - k_H**2 / 3 * Phi
        + (H0 / H) ** 2
        / 2
        * (
            (omega_dm * delta + omega_b * delta_b) * a**-3
            + 4
            * (omega_gamma * Theta_interp[0] + omega_neu * N_interp[0] + C_nu * sum_M0)
            * a**-4
        )
    )

    # Boltzmann equations for the various components
    # N_interp[1] = -2 * a * H / k * dPhi_dlan
    Theta_interp[1] = -2 * a * H / k * dPhi_dlan + a * H * taudot_interp(a) / k**2 * (
        u_b - k_H * c_s_interp(a) ** 2 * delta_b + k_H * Phi
    )  # Theta_1 RSA
    ddelta_dlan = -k_H * u - 3 * dPhi_dlan  # dark matter density
    du_dlan = -u + k_H * Psi  # dark matter velocity
    ddelta_b_dlan = -k_H * u_b - 3 * dPhi_dlan  # baryonic matter density
    du_b_dlan = (
        -u_b
        + k_H * Psi
        + taudot_interp(a) / (R * a * H) * (u_b - 3 * Theta_interp[1])
        + k_H * c_s_interp(a) ** 2 * delta_b
    )  # baryonic matter velocity

    for j in range(nq):
        # Massive neutrinos: the first nq values of the array are the 0th multipole
        dM_dlan[j] = -qq[j] * k_H / sp.sqrt(amnu**2 + qq[j] ** 2) * M[
            nq + j
        ] - dPhi_dlan * qq[j] / (sp.exp(-qq[j]) + 1)
        # Massive neutrinos: the second nq values of the array are the 1st multipole
        dM_dlan[nq + j] = (
            1
            / (a * H)
            * (
                qq[j]
                * k
                / (3 * sp.sqrt(amnu**2 + qq[j] ** 2))
                * (M[j] - 2 * M[2 * nq + j])
                + sp.sqrt(amnu**2 + qq[j] ** 2) * k / 3 * Psi / (sp.exp(-qq[j]) + 1)
            )
        )
    # lth multipoles massive neutrinos
    for m in range(2, l_max_mnu):
        for j in range(nq):

            dM_dlan[m * nq + j] = (
                qq[j]
                * k
                / (a * H * sp.sqrt(amnu**2 + qq[j] ** 2) * (2 * m + 1))
                * (m * M[(m - 1) * nq + j] - (m + 1) * M[(m + 1) * nq + j])
            )
    # hierarchy truncation massive neutrinos
    for j in range(nq):
        dM_dlan[l_max_mnu * nq + j] = (
            1
            / (a * H)
            * (
                qq[j]
                * k
                / sp.sqrt(amnu**2 + qq[j] ** 2)
                * M[(l_max_mnu - 1) * nq + j]
                - (l_max_mnu + 1) / eta_interp(a) * M[l_max_mnu * nq + j]
            )
        )

    # returns the rhs in the right order
    ret = [dPhi_dlan, ddelta_dlan, du_dlan, ddelta_b_dlan, du_b_dlan]
    ret += dM_dlan
    ret = [r.subs({a: sp.exp(lna)}) for r in ret]
    return ret


def switch_time(lna):  # pragma: no cover
    # use trigger parameters to determine a
    # at which RSA kicks in (as a function of k)
    a = np.logspace(-3, 0, 50)
    eta = eta_ufunc(a)
    a_tau = np.where(
        (-1 / (taudot_interp_ufunc(a) * eta) > get_globals()["rsa_trigger_taudot_eta"]),
        a,
        1.0,
    )
    lim = get_globals()["k"] * eta > get_globals()["rsa_trigger_k_eta"]
    a_keta = np.where(lim, a, 1.0)
    lna_cut = np.log(max(min(a_keta), min(a_tau)))
    return lna_cut


# functions to use l_max and mnu_relerr within merge
get_l_max = Function("get_l_max", l_max)
get_mnu_relerr = Function("get_mnu_relerr", mnu_relerr)


def switch(t, y):  # pragma: no cover
    # initial conditions for RSA ODE system
    l_max = int(get_l_max())
    return np.hstack((y[-1, :5], y[-1, 5 + 3 * (l_max + 1) :]))


def merge(t_0, t_switch, t_1, y_0, y_1):  # pragma: no cover
    """
    combine the non-RSA and RSA solutions
    and recompute the approximated radiation
    fields at output times
    """

    if len(t_1) == 0:
        return y_0

    from PyCosmo.optimize_nq import gl_quadrature

    # redefine needed params
    glob = get_globals()
    k = glob["k"]
    H0 = glob["H0"]
    rh = glob["rh"]
    massive_nu_total_mass = glob["massive_nu_total_mass"]
    N_massive_nu = glob["N_massive_nu"]
    kb = glob["kb"]
    Tcmb = glob["Tcmb"]
    T_mnu = glob["T_mnu"]
    hbar = glob["hbar"]
    c_ms = glob["c"] * 1000
    G = glob["G"]
    evc2 = glob["evc2"]
    mpc = glob["mpc"]
    a = np.exp(t_1)

    # and derived params
    T_0 = Tcmb * T_mnu
    amnu = a * massive_nu_total_mass / (N_massive_nu * kb * T_0)
    rho_ev = (
        3
        * H0**2
        * (hbar) ** 3
        * c_ms**3
        / (8 * np.pi * G)
        / evc2
        / (mpc / 1000) ** 2
    ) / (kb * T_0) ** 4
    C_nu = N_massive_nu / (2 * np.pi) ** 2 / rho_ev

    Phi = y_1[:, 0]
    delta = y_1[:, 1]
    delta_b = y_1[:, 3]
    u_b = y_1[:, 4]
    M = y_1[:, 5:]

    mnu_relerr = float(get_mnu_relerr())
    qq, weights = gl_quadrature(mnu_relerr)
    nq = len(qq)
    sum_M0 = sum(
        (
            weights[i]
            * np.exp(float(qq[i]))
            * qq[i] ** 2
            * np.sqrt(np.array(amnu) ** 2 + float(qq[i]) ** 2)
            * M[:, i]
            / (np.exp(float(qq[i])) + 1)
        )
        for i in range(nq)
    )
    sum_M2 = sum(
        (
            weights[i]
            * np.exp(float(qq[i]))
            * qq[i] ** 4
            * np.sqrt(np.array(amnu) ** 2 + float(qq[i]) ** 2)
            * M[:, 2 * nq + i]
            / (np.exp(float(qq[i])) + 1)
        )
        for i in range(nq)
    )

    omega_gamma = glob["omega_gamma"]
    omega_neu = glob["omega_neu"]
    omega_dm = glob["omega_dm"]
    omega_b = glob["omega_b"]

    H = H_ufunc(a)
    H_Mpc = H / H0 / rh

    # recompute fields with RSA
    N0_interp = Phi
    Theta0_interp = Phi + u_b * taudot_interp_ufunc(a) / k

    Psi = -Phi - 12 * (1 / (rh * k * a)) ** 2 * (C_nu * sum_M2)
    dPhi_dlan = (
        Psi
        - (k / (a * H_Mpc)) ** 2 / 3 * Phi
        + (1 / (rh * H_Mpc)) ** 2
        / 2
        * (
            (omega_dm * delta + omega_b * delta_b) * a**-3
            + 4
            * (omega_gamma * Theta0_interp + omega_neu * N0_interp + C_nu * sum_M0)
            * a**-4
        )
    )

    N1_interp = -2 * a * H_Mpc / k * dPhi_dlan
    Theta1_interp = -2 * a * H_Mpc / k * dPhi_dlan + a * H_Mpc * taudot_interp_ufunc(
        a
    ) / k**2 * (
        u_b
        - k / (a * H_Mpc) * c_s_interp_ufunc(a) ** 2 * delta_b
        + k / (a * H_Mpc) * Phi
    )

    # reshape and stack perturbations
    N0_interp = np.reshape(N0_interp, (len(y_1[:, 0]), 1))
    Theta0_interp = np.reshape(Theta0_interp, (len(y_1[:, 0]), 1))
    N1_interp = np.reshape(N1_interp, (len(y_1[:, 0]), 1))
    Theta1_interp = np.reshape(Theta1_interp, (len(y_1[:, 0]), 1))
    ThetaP0_interp = np.zeros((len(y_1[:, 0]), 1))
    ThetaP1_interp = np.zeros((len(y_1[:, 0]), 1))

    y1_stacked = np.hstack(
        (
            y_1[:, :5],
            Theta0_interp,
            ThetaP0_interp,
            N0_interp,
            Theta1_interp,
            ThetaP1_interp,
            N1_interp,
        )
    )
    y_1_complete = np.zeros((len(t_1), len(y_0[0, :])))
    y_1_complete[:, :11] = y1_stacked
    y_1_complete[:, -len(y_1[0, 5:]) :] = y_1[:, 5:]

    y = np.vstack((y_0, y_1_complete))

    return y


# remove imported declarations to avoid name overlap
del ode
del ode_fast

ode_rsa = OdeFast("rsa", lna, lhs_rsa(), rhs_rsa())
ode_final = OdeCombined(
    "linear_perturbation", ode_full, ode_rsa, switch_time, switch, merge
)
