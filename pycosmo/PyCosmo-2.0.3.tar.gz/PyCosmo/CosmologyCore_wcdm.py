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

import sympy as sp

from sympy2c import (
    Alias,
    ERROR,
    Function,
    Globals,
    IfThenElse,
    Integral,
    InterpolationFunction1D,
    Min,
    Ode,
    OdeFast,
    PythonFunction,
    Symbol,
    Vector,
    isnan,
)

# definition of equation parameters
l_max = cosmology.equation_parameters.l_max
reorder = cosmology.equation_parameters.reorder
splits = cosmology.equation_parameters.splits
assert splits is None or (
    isinstance(splits, (list, tuple))
    and all(isinstance(s, int) for s in splits)
    and all(s0 < s1 for s0, s1 in zip(splits, splits[1:]))
), "splits must be none or a list of increasing numbers"

# definition of the SymPy symbols
# cosmological parameters
H0 = Symbol("H0")
Tcmb = Symbol("Tcmb")

a = Symbol("a")
k = Symbol("k")
lna = Symbol("lna")
lna_0 = Symbol("lna_0")
omega_b = Symbol("omega_b")
omega_dm = Symbol("omega_dm")
omega_gamma = Symbol("omega_gamma")
omega_l = Symbol("omega_l")
omega_m = Symbol("omega_m")
omega_neu = Symbol("omega_neu")
omega_r = Symbol("omega_r")
rh = Symbol("rh")
t = Symbol("t")
w0 = Symbol("w0")
wa = Symbol("wa")  # not implemented yet, assume w=w0=constant, and wa=0
cs_de2 = Symbol("cs_de2")
flat_universe = Symbol("flat_universe")

# fields
Phi = Symbol("Phi")
delta = Symbol("delta")
delta_b = Symbol("delta_b")
u = Symbol("u")
u_b = Symbol("u_b")
delta_de = Symbol("delta_de")
u_de = Symbol("u_de")
N = Vector("N", l_max + 1)
Theta = Vector("Theta", l_max + 1)
Theta_P = Vector("Theta_P", l_max + 1)

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
)

h = H0 / 100

neq = 5 + 2 + 3 * (l_max + 1)

# w_a is w(a), not to be confused with wa
w_a = w0

# check functions used to impose conditions
# on the parameters
def check_wa(params):
    if "wa" not in params:
        return "wa not set"
    wa = params.wa
    if wa != 0.0:
        return "wa != 0.0 not (yet) supported for this model"


def check_w0(params):
    if "w0" not in params:
        return "w0 not set"
    w0 = params.w0
    if w0 == -1.0:
        return "w0 must be > -1, I guess you want to use LCDM instead."
    if w0 <= -1:
        return "w0 must be > -1"


def check_cs_de2(params):
    if "cs_de2" not in params:
        return "cs_de2 not set"
    cs_de2 = params.cs_de2
    if cs_de2 < 0.0 or cs_de2 > 1.0:
        return "cs_de must be in the range [0.0, 1.0]"


def check_norm(params):
    if params.pk_norm == "A_s":
        if "k_pivot" not in params:
            return "Need to set k_pivot for A_s normalization"


def check_ini(params):
    if params.initial_conditions in ("class", "cosmics"):
        if params.lna_0 is not None:
            return (
                f"you must not set lna_0 for {params.initial_conditions} initial"
                " conditions"
            )
    elif params.initial_conditions == "camb":
        return (
            f"We discourage the use of {params.initial_conditions} initial"
            " conditions, they need checking"
        )


assert l_max > 2, "l_max must be at least 3"

# compute the energy density of dark energy
omega_l_a = IfThenElse(
    flat_universe,
    (1 - omega_m - omega_r),
    omega_l,
) * a ** (-3 * (1 + w0))
omega_k = 1 - omega_m - omega_r - omega_l_a.subs({a: 1})

# Friedmann equation
H = H0 * (omega_r * a**-4 + omega_m * a**-3 + omega_k * a**-2 + omega_l_a) ** (
    1 / 2
)

R = 3 / 4 * omega_b / omega_gamma * a

# symbolic integration of the integrand does not work in all cases, so we use numerical
# approximation here:
Ht = H.subs({a: t})  # H as function of t
integrand = 1.0 / Ht / t**2
chi = Integral(integrand, t, a, 1)
print("chi", integrand)

# the integrand contains a removable singularty, which is not
# removed by sympy. but we know that eta at 0 is 0, so:
eta = IfThenElse(a < 1e-100, 0, Integral(integrand, t, 0, a)) * H0 * rh


def initial_cosmics():
    """
    Initial conditions as defined in Cosmics
    """
    eta_0 = Min(1e-3 / k, 1e-1 * h)
    adotrad = sp.sqrt(omega_r)/rh

    a_0 = eta_0 * adotrad

    H_a0 = H.subs({a: a_0})  # H as function of t
    ha = H_a0 / H0 / rh

    # matter to radiation energy density (time-dependent)ratio [1]
    r_m = omega_m / omega_r * a_0

    psi_p = -1.0  # Psi - to match cosmics conventions
    H0_scaled = 1.0 / rh

    N_2 = (
        2.0
        / 45.0
        * (k / (a_0 * H0_scaled)) ** 2
        * psi_p
        * (1.0 + 7.0 / 36.0 * r_m)
        / (omega_m * a_0 ** (-3) + 4.0 / 3.0 * omega_r * a_0 ** (-4))
    )

    phi = -psi_p - 12.0 / (k * a_0 / H0_scaled) ** 2 * omega_neu * N_2

    delta = -3.0 / 2.0 * psi_p * (1.0 + r_m / 6.0)
    delta_b = delta
    theta_0 = delta / 3.0
    N_0 = delta / 3.0

    # u = 1./2. * k * eta_0 * psi_p
    u = (
        1.0
        / 3.0
        * k
        / (ha * a_0)
        * (
            -delta
            + 2.0
            / 3.0
            * (k / (a_0 * H0_scaled)) ** 2
            / (omega_m / a_0**3 + 4.0 / 3.0 * omega_r / a_0**4)
            * phi
        )
    )

    u_b = u
    theta_1 = u / 3.0
    N_1 = u / 3.0

    y_0 = [0 for _ in range(neq)]
    y_0[0] = phi
    y_0[1] = delta
    y_0[2] = u
    y_0[3] = delta_b
    y_0[4] = u_b
    y_0[7] = theta_0
    y_0[9] = N_0
    y_0[10] = theta_1
    y_0[12] = N_1
    y_0[15] = N_2

    return [a_0, eta_0] + y_0


"""
def initial_camb():
    # CAMB adiabatic initial conditions, currently not recommended, use at your own
    # risk!
    a_0 = sp.exp(lna_0)
    eta_0 = eta.subs({a: a_0})

    r_nu = omega_neu / (3.0 / 4.0 * omega_m * a_0 + omega_r)

    # matter to radiation energy density (time-dependent)ratio [1]
    r_m = omega_m / omega_r * a_0

    psi_p = -10.0 / (4.0 * r_nu + 15.0)
    y_0 = [0 for _ in range(neq)]

    # initial perturbations
    y_0[13] = (
        2.0
        / 45.0
        * (k * rh / a_0) ** 2
        * psi_p
        * (1.0 + 7.0 / 36.0 * r_m)
        / (omega_m * a_0 ** (-3) + 4.0 / 3.0 * omega_r * a_0 ** (-4))
    )  # N2 - cosmics version

    y_0[0] = -psi_p - 12.0 / (rh * k * a_0) ** 2 * omega_neu * y_0[13]  # Phi

    y_0[1] = -3 / 2 * psi_p * (1 + r_m / 6)
    y_0[3] = -3 / 2 * psi_p * (1 + r_m / 6)
    y_0[5] = -1 / 2 * psi_p * (1 + r_m / 6)
    y_0[7] = -1 / 2 * psi_p * (1 + r_m / 6)

    # y_0[[1, 3, 5, 7]] = (
    # np.array([-3. / 2., -3. / 2., -1. / 2., -1. / 2.]) * psi_p * (1. + r_m / 6.)
    # )  # delta,deltab,theta_0,N_0

    H_a0 = H.subs({a: a_0})  # H as function of t
    ha = H_a0 / H0 / rh

    u0 = (
        1.0
        / 3.0
        * k
        / ha
        / a_0
        * (
            -y_0[1]
            + 2.0
            / 3.0
            * (rh * k / a_0) ** 2
            / (omega_m / a_0 ** 3 + 4.0 / 3.0 * omega_r / a_0 ** 4)
            * y_0[0]
        )
    )
    y_0[2] = u0
    y_0[4] = u0
    y_0[10] = u0 / 3
    y_0[12] = u0 / 3

    # y_0[[2, 4, 8, 10]] = (
    # np.array([1., 1., 1. / 3., 1. / 3.]) * u0
    # )  # [u,ub,theta_1, N_1]
    return [a_0, eta_0] + y_0
    """


def initial_class():
    """
    Adiabatic initial conditions as in CLASS,
    defined in synchronous gauge and then transformed
    to Newtonian conformal gauge
    """
    # the initial time is same as in Cosmics,
    # we do not set it iteratively as in CLASS
    eta_0_approx = Min(1e-3 / k, 1e-1 * h)
    adotrad = sp.sqrt(omega_r)/rh

    a_0 = eta_0_approx * adotrad

    H_a0 = H.subs({a: a_0})  # H as function of t
    ha = H_a0 / H0 / rh

    # initial conformal time [h^-1 Mpc] - warning: this is in MB95 notation and thus not
    # the optical depth
    eta_0 = eta.subs({a: a_0})
    # da/d(eta)/a [h Mpc^-1]
    a_prime_over_a = a_0 * ha
    # om=H0*Omega_m/sqrt(Omega_r) [h Mpc^-1]
    om = omega_m / omega_r**0.5 / rh
    # neutrino/radiation (constant) ratio [1]
    fracnu = omega_neu / omega_r
    # dark matter/matter (constant) ratio[1]
    fraccdm = omega_dm / omega_m
    # baryon/matter (constant) ratio [1]
    fracb = 1.0 - fraccdm
    # photon/radiation (constant) ratio [1]
    fracg = 1.0 - fracnu
    # matter to radiation energy density (time-dependent)ratio [1]
    rho_m_over_rho_r = omega_m / omega_r * a_0
    ktau = k * eta_0
    ktau_two = ktau**2
    ktau_three = ktau**3

    # initial perturbations in synchronous gauge and in Ma&Bertschinger95 notation
    delta_g = -ktau_two / 3.0 * (1.0 - om * eta_0 / 5.0)  # photon density
    theta_g = (
        -k
        * ktau_three
        / 36.0
        * (
            1.0
            - 3.0 * (1.0 + 5.0 * fracb - fracnu) / 20.0 / (1.0 - fracnu) * om * eta_0
        )
    )  # photon velocity
    delta_b = 3.0 / 4.0 * delta_g  # baryon density
    theta_b = theta_g  # baryon velocit

    delta_c = (
        3.0 / 4.0 * delta_g
    )  # dm density - note: dm velocity=0 in synchronous gauge
    delta_ur = delta_g  # neutrino (massless) density
    # neutrino velocity
    theta_ur = (
        -k
        * ktau_three
        / 36.0
        / (4.0 * fracnu + 15.0)
        * (
            4.0 * fracnu
            + 11.0
            + 12.0
            - 3.0
            * (8.0 * fracnu * fracnu + 50.0 * fracnu + 275.0)
            / 20.0
            / (2.0 * fracnu + 15.0)
            * eta_0
            * om
        )
    )
    # neutrino shear
    shear_ur = (
        ktau_two
        / (45.0 + 12.0 * fracnu)
        * (3.0 - 1.0)
        * (1.0 + (4.0 * fracnu - 5.0) / 4.0 / (2.0 * fracnu + 15.0) * eta_0 * om)
    )
    l3_ur = ktau_three * 2.0 / 7.0 / (12.0 * fracnu + 45.0)  # l=3 neutrino moment - TBC
    # metric perturbation in synchronous gauge
    eta_sync = 1.0 - ktau_two / 12.0 / (15.0 + 4.0 * fracnu) * (
        5.0
        + 4.0 * fracnu
        - (16.0 * fracnu**2 + 280.0 * fracnu + 325.0)
        / 10.0
        / (2.0 * fracnu + 15.0)
        * eta_0
        * om
    )

    # Christiane: DE fluid initial conditions, as described in arXiv:1004.5509
    delta_de = (
        -ktau_two
        / 4.0
        * (1.0 + w0)
        * (4.0 - 3.0 * cs_de2)
        / (4.0 - 6.0 * w0 + 3.0 * cs_de2)
    )
    theta_de = -k * ktau_three / 4.0 * cs_de2 / (4.0 - 6.0 * w0 + 3.0 * cs_de2)

    # compute factor alpha to convert from synchronous to newtonian gauge
    delta_tot = (
        fracg * delta_g
        + fracnu * delta_ur
        + rho_m_over_rho_r * (fracb * delta_b + fraccdm * delta_c)
    ) / (1.0 + rho_m_over_rho_r)
    velocity_tot = (
        (4.0 / 3.0) * (fracg * theta_g + fracnu * theta_ur)
        + rho_m_over_rho_r * fracb * theta_b
    ) / (1.0 + rho_m_over_rho_r)
    alpha = (
        eta_sync
        + 3.0
        / 2.0
        * a_prime_over_a
        * a_prime_over_a
        / k
        / k
        * (delta_tot + 3.0 * a_prime_over_a / k / k * velocity_tot)
    ) / a_prime_over_a

    # convert to newtonian gauge
    # newtonian potential perturbation (differs by minus sign in MB95)
    phi_mb95 = eta_sync - a_prime_over_a * alpha
    delta_g = delta_g - 4.0 * a_prime_over_a * alpha
    theta_g = theta_g + k * k * alpha
    delta_b = delta_b - 3.0 * a_prime_over_a * alpha
    theta_b = theta_b + k * k * alpha
    delta_c = delta_c - 3.0 * a_prime_over_a * alpha
    theta_c = k * k * alpha
    delta_de = delta_de - 3.0 * (1.0 + w0) * a_prime_over_a * alpha
    theta_de = theta_de + k * k * alpha
    delta_ur = delta_ur - 4.0 * a_prime_over_a * alpha
    theta_ur = theta_ur + k * k * alpha
    # shear_ur and l3_ur are gauge invariant

    # convert to initial condition vector
    y_0 = [0 for _ in range(neq)]
    y_0[0] = -phi_mb95  # Phi
    y_0[1] = delta_c  # delta
    y_0[2] = theta_c / k  # u
    y_0[3] = delta_b  # deltab
    y_0[4] = theta_b / k  # ub
    y_0[5] = delta_de  # delta_de
    y_0[6] = theta_de / k  # u_de
    y_0[7] = delta_g / 4.0  # theta_0
    y_0[9] = delta_ur / 4.0  # N_0
    y_0[10] = theta_g / k / 3.0  # theta_1

    y_0[12] = theta_ur / k / 3.0  # N_1
    y_0[15] = shear_ur / 2.0  # N_2
    y_0[18] = (
        l3_ur / 4.0
    )  # N_3    l3_ur=F_nu,3 in MB95 notation = N_3*4 in Dodelson notation
    return [a_0, eta_0] + y_0


def lhs():
    # lhs of the ODE system, containing the variables
    # in the desired order
    y = [Phi, delta, u, delta_b, u_b, delta_de, u_de]
    for i in range(l_max + 1):
        y.append(Theta[i])
        y.append(Theta_P[i])
        y.append(N[i])
    return tuple(y)


# interpolation of thermodynamical quantities
taudot_interp = InterpolationFunction1D("taudot_interp")
c_s_interp = InterpolationFunction1D("c_s_interp")
eta_interp = InterpolationFunction1D("eta_interp")

# change of units, be careful with the h factors!
H_Mpc = H / (H0 * rh)  # [h Mpc^-1]
H0_Mpc = 1 / rh  # [h Mpc^-1]

courant_0 = a * H_Mpc / k
courant_1 = a * H_Mpc * eta_interp(a)

# econ is a parameter quantifyng the consistency of the Einstein equations
# that can be used to control numerical errors
econ = (
    (-2 / 3 * (k / (a * H0_Mpc)) ** 2 * Phi)
    + (
        (omega_dm * delta + omega_b * delta_b) / a**3
        + 4 * (omega_gamma * Theta[0] + omega_neu * N[0]) / a**4
    )
    + (3 * a * H_Mpc / k)
    * (
        (omega_dm * u + omega_b * u_b) / a**3
        + 4 * (omega_gamma * Theta[1] + omega_neu * N[1]) / a**4
    )
) / ((omega_dm + omega_b) / a**3 + (omega_gamma + omega_neu) / a**4)


def rhs(H=H_Mpc, H0=H0_Mpc, R=R):
    """
    rhs of the ODE system containing the equations
    in d(lna), order needs to be the same as in lhs
    """

    k_H = k / (a * H)

    # empty symbols for the radiation hierarchies
    dTheta_dlan = [sp.S.Zero for _ in range(l_max + 1)]
    dTheta_P_dlan = [sp.S.Zero for _ in range(l_max + 1)]
    dN_dlan = [sp.S.Zero for _ in range(l_max + 1)]

    # Einstein equations
    Psi = -Phi - 12 * (H0 / (k * a)) ** 2 * (omega_gamma * Theta[2] + omega_neu * N[2])
    Pi = Theta[2] + Theta_P[0] + Theta_P[2]
    dPhi_dlan = (
        Psi
        - k_H**2 * Phi / 3.0
        + (H0 / H) ** 2
        / 2
        * (
            (omega_dm * delta + omega_b * delta_b) * a**-3
            + omega_l_a * delta_de
            + 4 * (omega_gamma * Theta[0] + omega_neu * N[0]) * a**-4
        )
    )

    # Boltzmann equations for the various components
    ddelta_dlan = -k_H * u - 3 * dPhi_dlan  # dark matter density
    du_dlan = -u + k_H * Psi  # dark matter velocity
    ddelta_b_dlan = -k_H * u_b - 3 * dPhi_dlan  # baryonic matter density
    du_b_dlan = (
        -u_b
        + k_H * Psi
        + taudot_interp(a) / (R * a * H) * (u_b - 3 * Theta[1])
        + k_H * c_s_interp(a) ** 2 * delta_b
    )  # baryonic matter velocity
    ddelta_de_dlan = (
        -(1 + w0) * (k_H * u_de + 3 * dPhi_dlan)
        - 3 * (cs_de2 - w0) * delta_de
        - 9 * (1 + w0) * (cs_de2 - w0) * (a * H) / k * u_de
    )  # dark energy density
    du_de_dlan = (
        -(1 - 3 * cs_de2) * u_de + cs_de2 / (1 + w0) * delta_de * k_H + k_H * Psi
    )  # dar energy velocity
    dTheta_dlan[0] = -k_H * Theta[1] - dPhi_dlan  # 0th photon multipole
    dTheta_dlan[1] = k_H / 3 * (Theta[0] - 2 * Theta[2] + Psi) + taudot_interp(a) / (
        a * H
    ) * (
        Theta[1] - u_b / 3
    )  # 1st photon multipole
    dTheta_dlan[2] = k_H / 5 * (2 * Theta[1] - 3 * Theta[3]) + taudot_interp(a) / (
        a * H
    ) * (
        Theta[2] - Pi / 10
    )  # 2nd photon multipole

    dTheta_P_dlan[0] = k_H / 1 * -Theta_P[1] + taudot_interp(a) / (a * H) * (
        Theta_P[0] - Pi / 2
    )  # 0th photon polarization multipole
    dTheta_P_dlan[1] = (
        k_H / 3 * (Theta_P[0] - 2 * Theta_P[2])
        + taudot_interp(a) / (a * H) * Theta_P[1]
    )  # 1st photon polarization multipole
    dTheta_P_dlan[2] = k_H / 5 * (2 * Theta_P[1] - 3 * Theta_P[3]) + taudot_interp(
        a
    ) / (a * H) * (
        Theta_P[2] - Pi / 10
    )  # 2nd photon polarization multipole

    for l in range(3, l_max):  # lth photons multipoles
        dTheta_dlan[l] = (
            k_H / (2 * l + 1) * (l * Theta[l - 1] - (l + 1) * Theta[l + 1])
            + taudot_interp(a) / (a * H) * Theta[l]
        )
        dTheta_P_dlan[l] = (
            k_H / (2 * l + 1) * (l * Theta_P[l - 1] - (l + 1) * Theta_P[l + 1])
            + taudot_interp(a) / (a * H) * Theta_P[l]
        )

    # truncate hierarchy
    dTheta_dlan[l_max] = (
        1
        / (a * H)
        * (
            k * Theta[l_max - 1]
            - ((l_max + 1) / eta_interp(a) - taudot_interp(a)) * Theta[l_max]
        )
    )
    dTheta_P_dlan[l_max] = (
        1
        / (a * H)
        * (
            k * Theta_P[l_max - 1]
            - ((l_max + 1) / eta_interp(a) - taudot_interp(a)) * Theta_P[l_max]
        )
    )

    # 0th, 1st and lth multipoles for massless neutrinos
    dN_dlan[0] = -k_H * N[1] - dPhi_dlan
    dN_dlan[1] = k_H / 3 * (N[0] - 2 * N[2] + Psi)
    for l in range(2, l_max):
        dN_dlan[l] = k_H / (2 * l + 1) * (l * N[l - 1] - (l + 1) * N[l + 1])

    # truncate hierarchy
    dN_dlan[l_max] = (
        1 / (a * H) * (k * N[l_max - 1] - (l_max + 1) / eta_interp(a) * N[l_max])
    )

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
    for dTheta, dTheta_P, dN in zip(dTheta_dlan, dTheta_P_dlan, dN_dlan):
        ret += [dTheta, dTheta_P, dN]
    ret = [r.subs({a: sp.exp(lna)}) for r in ret]

    return ret


# OdeFast object from sympy2c holding the ODE system
ode_fast = OdeFast(
    "linear_perturbation",
    lna,
    lhs(),
    rhs(),
    splits=splits,
    reorder=reorder,
)

ode = Ode(
    "linear_perturbation",
    lna,
    lhs(),
    rhs(),
)


y = Alias("y", *lhs())
fun_econ = Function("econ", econ, a, y)  # export econ as a function
fun_courant_0 = Function("courant_0", courant_0, a)
fun_courant_1 = Function("courant_1", courant_1, a)

# jacobian, can be used for scipy ODE solvers, currently not implemented
ddy = sp.Matrix(rhs()).jacobian(lhs())
linear_perturbation_jac = Function(
    "linear_perturbation_jac", ddy.reshape(1, ddy.rows * ddy.cols), lna, y
)

# export initial condition functions
fun_initial_values_cosmics = Function("initial_values_cosmics", initial_cosmics())
# fun_initial_values_camb = Function("initial_values_camb", initial_camb())
fun_initial_values_class = Function("initial_values_class", initial_class())

# export other useful functions, can be called from python
# using getattr(self._background._wrapper, "fun_name")(param)
fun_neq = Function("neq", neq)

fun_H = Function("H", H, a)
fun_R = Function("R", R, a)
fun_chi = Function("chi", chi, a)
fun_eta = Function("eta", eta, a)
fun_etai = Function("etai", integrand, t)
fun_omega_l_a = Function("omega_l_a", omega_l_a, a)
fun_omega_k = Function("omega_k", omega_k)
fun_omega_nu_m = Function("omega_nu_m", 0, a)


fun_taudot_interp = Function("taudot_interp", taudot_interp(a), a)
fun_c_s_interp = Function("c_s_interp", c_s_interp(a), a)
fun_eta_interp = Function("eta_interp", eta_interp(a), a)


def fields(lna, y, cosmology):
    # put together the fields, can be functions of
    # the result of solving the ODE
    lhs = ["Phi", "delta", "u", "delta_b", "u_b", "delta_de", "u_de"]
    l_max = cosmology.model_config.equation_parameters.l_max
    for i in range(l_max + 1):
        lhs.append(f"Theta[{i}]")
        lhs.append(f"Theta_P[{i}]")
        lhs.append(f"N[{i}]")
    fields = dict(zip(lhs, y.T))
    fields["econ"] = econ_ufunc(np.exp(lna), y)
    return fields


fields = PythonFunction(fields)
