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

# pragma: no cover

from sympy2c import OdeCombined
from CosmologyCore_wcdm import *

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
    w0,
    wa,
    rh,
    Tcmb,
    lna_0,
    k,
    cs_de2,
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
    y = [Phi, delta, u, delta_b, u_b, delta_de, u_de]
    return tuple(y)


def rhs_rsa(H=H_Mpc, H0=H0_Mpc, R=R, l_max=2):
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

    # Einstein equations
    N_interp[0] = Phi
    Theta_interp[0] = Phi + u_b * taudot_interp(a) / k
    Psi = -Phi - 12 * (H0 / (k * a)) ** 2 * (
        omega_gamma * Theta_interp[2] + omega_neu * N_interp[2]
    )
    Pi = Theta_interp[2] + Theta_P_interp[0] + Theta_P_interp[2]
    dPhi_dlan = (
        Psi
        - k_H**2 / 3 * Phi
        + (H0 / H) ** 2
        / 2
        * (
            (omega_dm * delta + omega_b * delta_b) * a**-3
            + omega_l_a * delta_de
            + 4 * (omega_gamma * Theta_interp[0] + omega_neu * N_interp[0]) * a**-4
        )
    )
    ddelta_de_dlan = (
        -(1 + w0) * (k_H * u_de + 3 * dPhi_dlan)
        - 3 * (cs_de2 - w0) * delta_de
        - 9 * (1 + w0) * (cs_de2 - w0) * (a * H) / k * u_de
    )
    du_de_dlan = (
        -(1 - 3 * cs_de2) * u_de
        + cs_de2 / (1 + w0) * k * delta_de / (a * H)
        + k_H * Psi
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

    # returns the rhs in the right order
    ret = [
        dPhi_dlan,
        ddelta_dlan,
        du_dlan,
        ddelta_b_dlan,
        du_b_dlan,
        ddelta_de_dlan,
        du_de_dlan,
    ]
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


# function to use l_max within merge
get_l_max = Function("get_l_max", l_max)


def switch(t, y):  # pragma: no cover
    # initial conditions for RSA ODE system
    return y[-1, :7]


def merge(t_0, t_switch, t_1, y_0, y_1):  # pragma: no cover
    """
    combine the non-RSA and RSA solutions
    and recompute the approximated radiation
    fields at output times
    """

    if len(t_1) == 0:
        return y_0

    # redefine needed params
    glob = get_globals()
    k = glob["k"]
    H0 = glob["H0"]
    rh = glob["rh"]
    w0 = glob["w0"]
    a = np.exp(t_1)

    Phi = y_1[:, 0]
    delta = y_1[:, 1]
    delta_b = y_1[:, 3]
    u_b = y_1[:, 4]
    delta_de = y_1[:, 5]

    omega_gamma = glob["omega_gamma"]
    omega_neu = glob["omega_neu"]
    omega_dm = glob["omega_dm"]
    omega_b = glob["omega_b"]
    omega_m = glob["omega_m"]
    omega_r = glob["omega_r"]
    omega_l_a = omega_l_a_ufunc(a)

    H = H_ufunc(a)
    H_Mpc = H / H0 / rh  # [h Mpc^-1]

    # recompute fields with RSA
    N0_interp = Phi
    Theta0_interp = Phi + u_b * taudot_interp_ufunc(a) / k

    Psi = -Phi
    dPhi_dlan = (
        Psi
        - (k / (a * H_Mpc)) ** 2 / 3 * Phi
        + (1 / (rh * H_Mpc)) ** 2
        / 2
        * (
            (omega_dm * delta + omega_b * delta_b) * a**-3
            + omega_l_a * delta_de
            + 4 * (omega_gamma * Theta0_interp + omega_neu * N0_interp) * a**-4
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
            y_1,
            Theta0_interp,
            ThetaP0_interp,
            N0_interp,
            Theta1_interp,
            ThetaP1_interp,
            N1_interp,
        )
    )
    y_1_complete = np.zeros((len(t_1), len(y_0[0, :])))
    y_1_complete[:, :13] = y1_stacked

    y = np.vstack((y_0, y_1_complete))

    return y


# remove imported declarations to avoid name overlap
del ode
del ode_fast

ode_rsa = OdeFast("rsa", lna, lhs_rsa(), rhs_rsa())
ode_final = OdeCombined(
    "linear_perturbation", ode_full, ode_rsa, switch_time, switch, merge
)
