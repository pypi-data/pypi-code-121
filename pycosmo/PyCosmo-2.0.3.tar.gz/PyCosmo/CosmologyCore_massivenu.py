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


import sympy as sp
import numpy as np
from PyCosmo.optimize_nq import gl_quadrature

from sympy2c import (
    ERROR,
    Alias,
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
l_max_mnu = cosmology.equation_parameters.l_max_mnu
mnu_relerr = cosmology.equation_parameters.mnu_relerr
splits = cosmology.equation_parameters.splits

# q sampling for massive neutrinos
qq, weights = gl_quadrature(mnu_relerr)
nq = len(qq)

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
flat_universe = Symbol("flat_universe")

Phi = Symbol("Phi")
delta = Symbol("delta")
delta_b = Symbol("delta_b")
u = Symbol("u")
u_b = Symbol("u_b")
Theta = Vector("Theta", l_max + 1)
Theta_P = Vector("Theta_P", l_max + 1)
N = Vector("N", l_max + 1)
# linear perturbation of massive neutrinos distribution function
M = Vector("M", (l_max_mnu + 1) * nq)

# massive neutrinos
q = Symbol("q")
N_massless_nu = Symbol("N_massless_nu")
N_massive_nu = Symbol("N_massive_nu")
N_eff = Symbol("N_eff")
massive_nu_total_mass = Symbol("massive_nu_total_mass")
T_mnu = Symbol("T_mnu")

# physical constants
c = Symbol("c")
kb = Symbol("kb")
evc2 = Symbol("evc2")
G = Symbol("G")
mpc = Symbol("mpc")
hbar = Symbol("hbar")

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
)

# check functions used to impose conditions
# on the parameters
def check_massive_nu_total_mass(params):
    if params.massive_nu_total_mass == 0.0:
        return "you must set massive_nu_total_mass > 0.0"


def check_N_massive_nu(params):
    if params.N_massive_nu == 0.0:
        return "you must set N_massive_nu > 0.0"


def check_wa(params):
    if "wa" not in params:
        return "wa not set"
    wa = params.wa
    if wa != 0:
        return "wa must be = 0 for mnuLCDM"


def check_w0(params):
    if "w0" not in params:
        return "w0 not set"
    w0 = params.w0
    if w0 != -1:
        return "w0 must be = -1 for LCDM"


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


assert l_max_mnu > 2, "l_max_mnu must be at least 3"
assert l_max > 2, "l_max must be at least 3"

c_ms = c * 1000  # speed of light in m/s
h = H0 / 100


neq = 5 + 3 * (l_max + 1) + nq * (l_max_mnu + 1)
T_0 = Tcmb * T_mnu

# critical density in eV^4
rho_ev = (
    3 * H0**2 * (hbar) ** 3 * c_ms**3 / (8 * sp.pi * G) / evc2 / (mpc / 1000) ** 2
) / (kb * T_0) ** 4


# define omega_nu_m
f = 1 / (sp.exp(q) + 1)
C_nu_bkg = N_massive_nu / (rho_ev * sp.pi**2)
amnu = a * massive_nu_total_mass / (N_massive_nu * kb * T_0)
integrand_om = f * q**2 * sp.sqrt(amnu**2 + q**2)
integrand_P = f * q**4 / sp.sqrt(amnu**2 + q**2)

omega_nu_m = C_nu_bkg * Integral(integrand_om, q, 0, sp.oo)
P_nu_m = C_nu_bkg / 3 * Integral(integrand_P, q, 0, sp.oo)

# compute the energy density of dark energy
omega_l_a = IfThenElse(
    flat_universe, (1 - omega_m - omega_r - omega_nu_m.subs({a: 1})), omega_l
)
omega_k = 1 - omega_m - omega_r - omega_nu_m.subs({a: 1}) - omega_l_a

# Friedmann equation
H = H0 * (
    (omega_r + omega_nu_m) * a**-4 + omega_m * a**-3 + omega_k * a**-2 + omega_l_a
) ** (1.0 / 2.0)

R = (3.0 / 4.0) * omega_b / omega_gamma * a

# symbolic integration of the integrand does not work in all cases, so we use numerical
# approximation here:d
Ht = H.subs({a: t})  # H as function of t
integrand = 1.0 / Ht / t**2
chi = Integral(integrand, t, a, 1)

# the integrand contains a removable singularty, which is not
# removed by sympy. but we know that eta at 0 is 0, so:
eta = IfThenElse(a < 1e-100, 0, Integral(integrand, t, 0, a)) * H0 * rh
# constant fro massive neutrino linear perturbations
C_nu = N_massive_nu / (2 * np.pi) ** 2 / rho_ev


def initial_cosmics():
    """
    Initial conditions as defined in Cosmics
    """
    eta_0 = Min(1e-3 / k, 1e-1 * h)

    _omega_nu_m_a0 = (
        7.0
        / 8.0 * N_eff
        * (4.0 / 11.0) ** (4.0 / 3.0)
        * omega_gamma
    )  # omega_nu_m.subs({a: a_0})
    omega_allr = omega_r + _omega_nu_m_a0

    adotrad = sp.sqrt(omega_allr)/rh

    a_0 = eta_0 * adotrad

    H_a0 = H.subs({a: a_0})  # H as function of t
    
    P_nu_m_a0 = 1 / 3 * _omega_nu_m_a0  # P_nu_m.subs({a: a_0})
    ha = H_a0 / H0 / rh
    amnu_0 = a_0 * massive_nu_total_mass / (N_massive_nu * kb * T_0)

    r_nu = (omega_neu + _omega_nu_m_a0) / (
        3.0 / 4.0 * omega_m * a_0 + omega_r + _omega_nu_m_a0
    )

    # matter to radiation energy density (time-dependent)ratio [1]
    r_m = omega_m / (omega_r + _omega_nu_m_a0) * a_0

    psi_p = -1.0  # Psi - to match cosmics conventions

    N_2 = (
        2.0
        / 45.0
        * (k * rh / a_0) ** 2
        * psi_p
        * (1.0 + 7.0 / 36.0 * r_m)
        / (
            omega_m * a_0 ** (-3)
            + (4.0 / 3.0 * omega_r + _omega_nu_m_a0 + P_nu_m_a0) * a_0 ** (-4)
        )
    )

    M_2 = q / (sp.exp(-q) + 1)
    M2_a0 = [sp.S.Zero for _ in range(nq)]
    for i in range(nq):
        M2_a0[i] = M_2.subs(q, qq[i]) * N_2

    phi = -psi_p - 12.0 / (k * a_0 * rh) ** 2 * (
        omega_neu * N_2
        + C_nu
        * sum(
            weights[i]
            * sp.exp(qq[i])
            * qq[i] ** 4
            / sp.sqrt(amnu_0**2 + qq[i] ** 2)
            * M2_a0[i]
            / (sp.exp(qq[i]) + 1)
            for i in range(nq)
        )
    )

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
            * (k * rh / a_0) ** 2
            / (
                omega_m * a_0 ** (-3)
                + (4.0 / 3.0 * omega_r + _omega_nu_m_a0 + P_nu_m_a0) * a_0 ** (-4)
            )
            * phi
        )
    )

    u_b = u
    theta_1 = u / 3.0
    N_1 = u / 3.0

    M_0 = q / (sp.exp(-q) + 1)
    M_1 = sp.sqrt(amnu_0**2 + q**2) / (sp.exp(-q) + 1)
    M0_a0 = [sp.S.Zero for _ in range(nq)]
    M1_a0 = [sp.S.Zero for _ in range(nq)]
    for i in range(nq):
        M0_a0[i] = M_0.subs(q, qq[i]) * N_0
        M1_a0[i] = M_1.subs(q, qq[i]) * N_1

    y_0 = [0 for _ in range(neq)]
    y_0[0] = phi
    y_0[1] = delta
    y_0[2] = u
    y_0[3] = delta_b
    y_0[4] = u_b
    y_0[5] = theta_0
    y_0[7] = N_0
    y_0[8] = theta_1
    y_0[10] = N_1
    y_0[13] = N_2
    l_nu = 5 + 3 * (l_max + 1)  # first massive_nu multipole
    y_0[l_nu : (l_nu + nq)] = M0_a0
    y_0[(l_nu + nq) : (l_nu + 2 * nq)] = M1_a0
    y_0[(l_nu + 2 * nq) : (l_nu + 3 * nq)] = M2_a0

    return [a_0, eta_0] + y_0


"""
def initial_camb():
    # CAMB adiabatic initial conditions, currently not recommended, use at your own
    # risk!
    a_0 = sp.exp(lna_0)
    eta_0 = eta.subs({a: a_0})
    C_nu = N_massive_nu / (2 * np.pi) ** 2 / rho_ev
    _omega_nu_m_a0 = (
        7.0
        / 8.0
        * (4.0 / 11.0) ** (4.0 / 3.0)
        * omega_r
        / (1 + 7.0 / 8.0 * N_eff * (4.0 / 11.0) ** (4.0 / 3.0))
    )
    P_nu_m_a0 = 1 / 3 * _omega_nu_m_a0  # P_nu_m.subs({a: a_0})
    amnu_0 = a_0 * massive_nu_total_mass / (N_massive_nu * kb * T_0)

    r_nu = (omega_neu + _omega_nu_m_a0) / (
        3.0 / 4.0 * omega_m * a_0 + omega_r + _omega_nu_m_a0
    )

    # matter to radiation energy density (time-dependent)ratio [1]
    r_m = omega_m / (omega_r + _omega_nu_m_a0) * a_0

    psi_p = -10.0 / (4.0 * r_nu + 15.0)
    y_0 = [0 for _ in range(neq)]

    # initial perturbations
    y_0[13] = (
        2.0
        / 45.0
        * (k * rh / a_0) ** 2
        * psi_p
        * (1.0 + 7.0 / 36.0 * r_m)
        / (
            omega_m * a_0 ** (-3)
            + (4.0 / 3.0 * omega_r + _omega_nu_m_a0 + P_nu_m_a0) * a_0 ** (-4)
        )
    )  # N2 - cosmics version

    l_nu = 5 + 3 * (l_max + 1)  # first massive_nu multipole
    M_2 = q / (sp.exp(-q) + 1)

    for i in range(nq):
        y_0[l_nu + 2 * nq + i] = M_2.subs(q, qq[i]) * y_0[13]

    y_0[0] = -psi_p - 12.0 / (rh * k * a_0) ** 2 * (
        omega_neu * y_0[13]
        + C_nu
        * sum(
            weights[i]
            * sp.exp(qq[i])
            * qq[i] ** 4
            / sp.sqrt(amnu_0 ** 2 + qq[i] ** 2)
            * y_0[3 * l_max + 6]
            / (sp.exp(qq[i]) + 1)
            for i in range(nq)
        )
    )  # Phi

    y_0[1] = -3 / 2 * psi_p * (1 + r_m / 6)
    y_0[3] = -3 / 2 * psi_p * (1 + r_m / 6)
    y_0[5] = -1 / 2 * psi_p * (1 + r_m / 6)
    y_0[7] = -1 / 2 * psi_p * (1 + r_m / 6)
    # delta,deltab,theta_0,N_0

    H_a0 = H.subs({a: a_0})  # H as function of t
    ha = H_a0 / H0 / rh

    u0 = (
        1
        / 3
        * k
        / ha
        / a_0
        * (
            -y_0[1]
            + 2
            / 3
            * (rh * k / a_0) ** 2
            / (
                omega_m * a_0 ** (-3)
                + (4.0 / 3.0 * omega_r + _omega_nu_m_a0 + P_nu_m_a0) * a_0 ** (-4)
            )
            * y_0[0]
        )
    )

    y_0[2] = u0
    y_0[4] = u0
    y_0[8] = u0 / 3
    y_0[10] = u0 / 3
    # [u,ub,theta_1, N_1]

    M_0 = q / (sp.exp(-q) + 1)
    M_1 = sp.sqrt(amnu_0 ** 2 + q ** 2) / (sp.exp(-q) + 1)

    for i in range(nq):
        y_0[l_nu + i] = M_0.subs(q, qq[i]) * y_0[7]
        y_0[l_nu + nq + i] = M_1.subs(q, qq[i]) * y_0[10]

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

    omega_nu_tot = (
        7.0
        / 8.0 * N_eff
        * (4.0 / 11.0) ** (4.0 / 3.0)
        * omega_gamma
    )  # omega_nu_m.subs({a: a_0})
    omega_allr = omega_gamma + omega_nu_tot

    adotrad = sp.sqrt(omega_allr)/rh

    a_0 = eta_0_approx * adotrad
    amnu_0 = a_0 * massive_nu_total_mass / (N_massive_nu * kb * T_0)

    H_a0 = H.subs({a: a_0})  # H as function of t
    ha = H_a0 / H0 / rh

    # initial conformal time [h^-1 Mpc] - warning: this is in MB95 notation and thus not
    # the optical depth
    eta_0 = eta.subs({a: a_0})
    # da/d(eta)/a [h Mpc^-1]
    a_prime_over_a = a_0 * ha
    # om=H0*Omega_m/sqrt(Omega_r) [h Mpc^-1]
    om = omega_m / sp.sqrt(omega_allr) / rh
    # neutrino/radiation (constant) ratio [1]
    fracnu = omega_nu_tot / omega_allr
    # dark matter/matter (constant) ratio[1]
    fraccdm = omega_dm / omega_m
    # baryon/matter (constant) ratio [1]
    fracb = 1.0 - fraccdm
    # photon/radiation (constant) ratio [1]
    fracg = 1.0 - fracnu
    # matter to radiation energy density (time-dependent)ratio [1]
    rho_m_over_rho_r = omega_m / omega_allr * a_0
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
    delta_ur = delta_ur - 4.0 * a_prime_over_a * alpha
    theta_ur = theta_ur + k * k * alpha
    # shear_ur and l3_ur are gauge invariant

    # create initial condition vector
    y_0 = [0 for _ in range(neq)]

    # after transforming the gauge introduce massive neutrinos initial conditions
    l_nu = 5 + 3 * (l_max + 1)  # first massive_nu multipole
    M_0 = q / (sp.exp(-q) + 1)
    M_1 = sp.sqrt(amnu_0**2 + q**2) / (sp.exp(-q) + 1)
    M_2 = q / (sp.exp(-q) + 1)
    M_3 = q / (sp.exp(-q) + 1)

    for i in range(nq):
        y_0[l_nu + i] = M_0.subs(q, qq[i]) * delta_ur / 4.0
        y_0[l_nu + nq + i] = M_1.subs(q, qq[i]) * theta_ur / (3.0 * k)
        y_0[l_nu + 2 * nq + i] = M_2.subs(q, qq[i]) * shear_ur / 2.0
        y_0[l_nu + 3 * nq + i] = M_3.subs(q, qq[i]) * l3_ur / 4.0

    y_0[0] = -phi_mb95  # Phi
    y_0[1] = delta_c  # delta
    y_0[2] = theta_c / k  # u
    y_0[3] = delta_b  # deltab

    y_0[4] = theta_b / k  # ub
    y_0[5] = delta_g / 4.0  # theta_0
    y_0[7] = delta_ur / 4.0  # N_0
    y_0[8] = theta_g / k / 3.0  # theta_1

    y_0[10] = theta_ur / k / 3.0  # N_1
    y_0[13] = shear_ur / 2.0  # N_2
    y_0[16] = (
        l3_ur / 4.0
    )  # N_3    l3_ur=F_nu,3 in MB95 notation = N_3*4 in Dodelson notation

    return [a_0, eta_0] + y_0


def lhs():
    # lhs of the ODE system, containing the variables
    # in the desired order
    y = [Phi, delta, u, delta_b, u_b]
    for i in range(l_max + 1):
        y.append(Theta[i])
        y.append(Theta_P[i])
        y.append(N[i])
    for j in range((l_max_mnu + 1) * nq):
        y.append(M[j])
    return y


# interpolation of thermodynamical quantities
c_s_interp = InterpolationFunction1D("c_s_interp")
eta_interp = InterpolationFunction1D("eta_interp")
taudot_interp = InterpolationFunction1D("taudot_interp")

# ode equations
# massive neutrinos
sum_M0 = sum(
    (
        weights[i]
        * sp.exp(qq[i])
        * qq[i] ** 2
        * sp.sqrt(amnu**2 + qq[i] ** 2)
        * M[i]
        / (sp.exp(qq[i]) + 1)
    )
    for i in range(nq)
)

sum_M1 = sum(
    (weights[i] * sp.exp(qq[i]) * qq[i] ** 3 * M[nq + i] / (sp.exp(qq[i]) + 1))
    for i in range(nq)
)

sum_M2 = sum(
    (
        weights[i]
        * sp.exp(qq[i])
        * qq[i] ** 4
        / (sp.sqrt(amnu**2 + qq[i] ** 2))
        / (sp.exp(qq[i]) + 1)
        * M[2 * nq + i]
    )
    for i in range(nq)
)

sum_0 = sum(
    (
        weights[i]
        * sp.exp(qq[i])
        * qq[i] ** 2
        * sp.sqrt(qq[i] ** 2 + amnu**2)
        / (sp.exp(qq[i]) + 1)
    )
    for i in range(nq)
)

sum_1 = sum(
    (
        weights[i]
        * sp.exp(qq[i])
        * qq[i] ** 4
        / (sp.sqrt(amnu**2 + qq[i] ** 2) * (sp.exp(qq[i]) + 1))
    )
    for i in range(nq)
)

# Massive neutrino fields
delta_nu_m = sum_M0 / sum_0
u_nu_m = sum_M1 / (sum_0 + sum_1 / 3)
sigma_nu_m = 2 / 3 * sum_M2 / (sum_0 + sum_1 / 3)

# change of units, be careful with the h factors!
H_Mpc = H / (H0 * rh)  # [h Mpc^-1]
H0_Mpc = 1 / rh  # [h Mpc^-1]

courant_0 = a * H / k
courant_1 = a * H * eta_interp(a)

# econ is a parameter quantifyng the consistency of the Einstein equations
# that can be used to control numerical errors
econ = (
    (-2 / 3 * (k / (a * H0_Mpc)) ** 2 * Phi)
    + (omega_dm * delta + omega_b * delta_b) / a**3
    + 4 * (omega_gamma * Theta[0] + omega_neu * N[0] + C_nu * sum_M0) / a**4
    + 3
    * a
    * H_Mpc
    / k
    * (
        (omega_dm * u + omega_b * u_b) / a**3
        + 4 * (omega_gamma * Theta[1] + omega_neu * N[1] + C_nu * sum_M1) / a**4
    )
) / (
    (omega_dm + omega_b) / a**3
    + (omega_gamma + omega_neu + omega_nu_m) / a**4
    + omega_l_a
)


def rhs(H=H_Mpc, H0=H0_Mpc, amnu=amnu):
    """
    rhs of the ODE system containing the equations
    in d(lna), order needs to be the same as in lhs
    """

    k_H = k / (a * H)

    # empty symbols for the radiation hierarchies
    dTheta_dlan = [sp.S.Zero for _ in range(l_max + 1)]
    dTheta_P_dlan = [sp.S.Zero for _ in range(l_max + 1)]
    dN_dlan = [sp.S.Zero for _ in range(l_max + 1)]
    dM_dlan = [sp.S.Zero for _ in range(nq * (l_max_mnu + 1))]

    # Einstein equations
    Psi = -Phi - 12 * (H0 / (k * a)) ** 2 * (
        omega_gamma * Theta[2] + omega_neu * N[2] + C_nu * sum_M2
    )
    Pi = Theta[2] + Theta_P[0] + Theta_P[2]
    dPhi_dlan = (
        Psi
        - (k_H**2) * Phi / 3
        + (H0 / H) ** 2
        / 2
        * (
            (omega_dm * delta + omega_b * delta_b) * a**-3
            + 4 * (omega_gamma * Theta[0] + omega_neu * N[0] + C_nu * sum_M0) * a**-4
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

    # lth multipoles massless and massive neutrinos
    for l in range(2, l_max):
        dN_dlan[l] = k_H / (2 * l + 1) * (l * N[l - 1] - (l + 1) * N[l + 1])

    for m in range(2, l_max_mnu):
        for j in range(nq):

            dM_dlan[m * nq + j] = (
                qq[j]
                * k
                / (a * H * sp.sqrt(amnu**2 + qq[j] ** 2) * (2 * m + 1))
                * (m * M[(m - 1) * nq + j] - (m + 1) * M[(m + 1) * nq + j])
            )

    # hierarchy truncation
    dN_dlan[l_max] = (
        1 / (a * H) * (k * N[l_max - 1] - (l_max + 1) / eta_interp(a) * N[l_max])
    )
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
    for dTheta, dTheta_P, dN in zip(dTheta_dlan, dTheta_P_dlan, dN_dlan):
        ret += [dTheta, dTheta_P, dN]
    ret += dM_dlan
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
fun_econ = Function("econ", econ, a, y)

ddy = sp.Matrix(rhs()).jacobian(lhs())
fun_linear_perturbation_jac = Function(
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
fun_omega_nu_m = Function("omega_nu_m", omega_nu_m, a)
fun_P_nu_m = Function("P_nu_m", P_nu_m, a)


fun_taudot_interp = Function("taudot_interp", taudot_interp(a), a)
fun_c_s_interp = Function("c_s_interp", c_s_interp(a), a)
fun_eta_interp = Function("eta_interp", eta_interp(a), a)

fun_delta_nu_m = Function("delta_nu_m", delta_nu_m, a, y)
fun_u_nu_m = Function("u_nu_m", u_nu_m, a, y)
fun_sigma_nu_m = Function("sigma_nu_m", sigma_nu_m, a, y)


def fields(lna, y, cosmology):
    # put together the fields, can be functions of
    # the result of solving the ODE
    lhs = ["Phi", "delta", "u", "delta_b", "u_b"]
    l_max = cosmology.model_config.equation_parameters.l_max
    neq = y.shape[1]
    for i in range(l_max + 1):
        lhs.append(f"Theta[{i}]")
        lhs.append(f"Theta_P[{i}]")
        lhs.append(f"N[{i}]")
    for i in range(neq - 5 - 3 * l_max):
        lhs.append(f"M[{i}]")

    fields = dict(zip(lhs, y.T))

    a = np.exp(lna)
    fields["econ"] = econ_ufunc(a, y)
    fields["delta_nu_m"] = delta_nu_m_ufunc(a, y)
    fields["u_nu_m"] = u_nu_m_ufunc(a, y)
    fields["sigma_nu_m"] = sigma_nu_m_ufunc(a, y)
    return fields


fields = PythonFunction(fields)
