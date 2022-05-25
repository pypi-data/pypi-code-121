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

import os
from types import FunctionType

import numpy as np

from ..ini_handling import Bunch, load_ini

PYCOSMO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


INFO = {
    "cosmology": {
        "h": "Dimensionless hubble parameter [1]",
        "omega_b": "Baryon density [1]",
        "omega_m": "Matter density (DM+baryons) [1]",
        "omega_l": "Dark energy density [1]",
        "flat_universe": "Assume flat universe [1]",
        "n": "Scalar spectral index [1]",
        "Tcmb": "CMB Temperature [K]",
        "Yp": "Helim Fraction [1]",
        "N_massless_nu": "Number of massless neutrino species [1]",
        "N_massive_nu": "Number of massive neutrino species [1]",
        "massive_nu_total_mass": "Total mass of massive neutrinos [eV]",
        "wa": "Present DE of equation of state",
        "w0": "Time depenedent parameter of DE equation of state",
    },
    "recombination": {
        "recomb": "Recombination code",
        "recomb_dir": "",
        "recomb_filename": "",
        "F": "Fudge factor [1]",
        "fDM": "Annihilation efficiency [eV/s]",
    },
    "linear_perturbations": {
        "pk_type": "Linear powerspectrum type",
        "pk_norm_type": "Powerspectrum norm type",
        "pk_norm": "Powerspectrum norm value",
        "tabulation": "Use tabulated quantities",
    },
    "nonlinear_perturbations": {"pk_nonlin_type": "Nonlinear powerspectrum type"},
    "internal:boltzmann_solver": {
        "table_size": "Size of interpolation table for background quantities",
        "lna_0": "User defined initial lna",
        "y_0": "User defined initial values",
        "initial_conditions": "Initical conditions",
        "dt_0": "User defined initial steps size",
        "sec_factor": "Security factor for LU permutations",
        "boltzmann_atol": "Boltzmann solver atol",
        "boltzmann_rtol": "Boltzmann solver rtol",
        "boltzmann_max_bdf_order": "LSODA max bdf order",
        "boltzmann_max_iter": "LSODA max iter",
        "fast_solver": "Use fast LSODA solver",
    },
    "nonlinear_perturbations:mead": {
        "baryons": "",
        "multiplicity_fnct": "Multiplicity Function",
        "npoints_k": "Number of points for k grid",
        "A_mead": "",
        "eta0_mead_equation": "",
        "eta0_mead_equation_version": "",
        "eta0_mead": "",
    },
    "internal:observables": {
        "k_size": "Grid size k values",
        "a_size": "Grid size a values",
    },
    "internal:linear_perturbation_approx_growth_factor": {
        "ainit_growth": "Initial a for ODE",
        "rtol_growth": "Relative tolerance for ODE",
        "atol_growth": "Absolute tolerance for ODE",
        "h0_growth": "Initial step size for ODE",
    },
    "internal:comparison_modifications": {
        "omega_suppress": "",
        "suppress_rad": "",
        "cosmo_nudge": "",
    },
    "internal:physical_constants": {
        "c": "[km/s]",
        "kb": "[eV/K]",
        "evc2": "[kg]",
        "G": "[m^3/kg/s^2]",
        "hbar": "[eV s]",
        "mpc": "[m]",
        "mp": "[MeV/c^2]",
        "msun": "[kg]",
        "sigmat": "[m^2]",
    },
}


PARAM_INI_SPEC = {
    "cosmology": {
        "h": float,
        "omega_b": float,
        "omega_m": float,
        "omega_l": (None, float),
        "flat_universe": bool,
        "n": float,
        "Tcmb": float,
        "Yp": float,
        "N_massless_nu": float,
        "N_massive_nu": float,
        "massive_nu_total_mass": float,
        "wa": float,
        "w0": float,
    },
    "recombination": {
        "recomb": ["recfast++", "cosmics", "class"],
        "recomb_dir": (None, str),
        "recomb_filename": (None, str),
        "F": float,
        "fDM": float,
    },
    "linear_perturbations": {
        "pk_type": ["EH", "BBKS", "BBKS_CCL", "boltz"],
        "tabulation": bool,
        "pk_norm_type": ["sigma8", "deltah", "A_s"],
        "pk_norm": float,
        "k_pivot": (None, float),
    },
    "nonlinear_perturbations": {
        "pk_nonlin_type": ["halofit", "rev_halofit", "mead", None]
    },
    "nonlinear_perturbations:mead": {
        "baryons": ["DMonly", "REF", "AGN", "DBLIM"],
        "multiplicity_fnct": ["ST", "ST", "Ti"],
        "npoints_k": int,
        "A_mead": float,
        "eta0_mead_equation": bool,
        "eta0_mead_equation_version": [1],
        "eta0_mead": float,
    },
    "internal:boltzmann_solver": {
        "table_size": int,
        "lna_0": (None, float),
        "y_0": (None, np.ndarray),
        "initial_conditions": ["class", "cosmics", "camb"],
        "dt_0": (None, float),
        "sec_factor": lambda v: (
            isinstance(v, float) and v >= 1.0,
            "must be float >= 1.0",
        ),
        "boltzmann_atol": (float, np.ndarray),
        "boltzmann_rtol": (float, np.ndarray),
        "boltzmann_max_bdf_order": (1, 2, 3, 4, 5),
        "boltzmann_max_iter": int,
        "fast_solver": bool,
    },
    "internal:observables": {"k_size": int, "a_size": int},
    "internal:linear_perturbation_approx_growth_factor": {
        "ainit_growth": float,
        "rtol_growth": float,
        "atol_growth": float,
        "h0_growth": float,
    },
    "internal:comparison_modifications": {
        "omega_suppress": bool,
        "suppress_rad": bool,
        "cosmo_nudge": lambda n: (
            n is None
            or (
                isinstance(n, (list, tuple))
                and len(n) == 3
                and all(isinstance(ni, float) for ni in n)
            ),
            "must be None or tuple/list of 3 floats",
        ),
    },
    "internal:physical_constants": {
        "c": float,
        "kb": float,
        "evc2": float,
        "G": float,
        "hbar": float,
        "mpc": float,
        "mp": float,
        "msun": float,
        "sigmat": float,
    },
}


PARAM_INI_SPEC_FLAT = {
    k: v for section in PARAM_INI_SPEC.values() for k, v in section.items()
}


def fix_package_internal_path(path):
    if not path.startswith("/") and not path.startswith("./"):
        path = os.path.join(PYCOSMO_ROOT, path)
    return path


def load_parameters_ini(path, **kw):

    if path is not None and kw:
        raise ValueError(
            "either provide path_to_ini_file or kw arguments, but not both"
        )

    if path:
        bunch = load_ini(fix_package_internal_path(path))
    else:
        bunch = Bunch(kw)

    model_specific_parameters = bunch.pop("model_specific_parameters", {})
    check_bunch(bunch)

    flattened = {
        name: value
        for section, settings in bunch.items()
        for name, value in settings.items()
    }

    parameters = Bunch(flattened)
    return parameters, model_specific_parameters


def check_flattened(user_parameters, specification=PARAM_INI_SPEC_FLAT):
    unknown = set(user_parameters) - set(specification)
    if unknown:
        msg = "unknown parameter(s): {}".format(", ".join(sorted(unknown)))
        raise ValueError(msg)

    for key, value in user_parameters.items():
        spec = specification[key]
        _check(key, value, spec)


def _check(key, value, spec):
    if spec is None:
        return

    if isinstance(spec, (tuple, list)):
        for si in spec:
            if si == value:
                return
            if si in (float, int, str, bool, np.ndarray):
                if isinstance(value, si):
                    return
        raise ValueError(
            "{} has invalid value {}, allowed are {}.".format(key, value, spec)
        )
    elif spec is float:
        if not isinstance(value, (int, float)):
            raise ValueError(
                "{} has invalid value {}, expected {}.".format(key, value, spec)
            )

    elif spec in (int, str, bool, np.ndarray, list):
        if not isinstance(value, spec):
            raise ValueError(
                "{} has invalid value {}, expected {}.".format(key, value, spec)
            )

    elif isinstance(spec, FunctionType):
        ok, msg = spec(value)
        if not ok:
            raise ValueError(msg)

    elif spec == "existing_file":
        value = fix_package_internal_path(value)
        if not isinstance(value, str) or not os.path.exists(value):
            raise ValueError(
                "value {} for {} is not an existing file".format(value, key)
            )

    else:
        raise ValueError("spec check for {} not implemented".format(spec))


def check_bunch(bunch, specification=PARAM_INI_SPEC):

    missing, unknown = match(bunch, specification)

    if missing:
        raise ValueError("setting(s) {} missing".format(missing))
    if unknown:
        raise ValueError("setting(s) {} is/are unknown".format(unknown))

    for section_name, section_specification in specification.items():
        section = bunch[section_name]
        if section_specification is None:
            continue
        for option_name, option_specification in section_specification.items():
            missing, unknown = match(section, section_specification)
            if missing:
                raise ValueError(
                    "setting(s) {} missing in section {}".format(missing, section_name)
                )
            if unknown:
                raise ValueError(
                    "setting(s) {} in secion {} unknown".format(unknown, section_name)
                )

            value = section[option_name]
            _check(
                "{}.{}".format(section_name, option_name), value, option_specification
            )


def match(to_check, specification):
    to_check_keys = to_check.keys()
    specification_keys = specification.keys()

    missing = specification_keys - to_check_keys
    unknown = to_check_keys - specification_keys

    return ", ".join(missing), ", ".join(unknown)
