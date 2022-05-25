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


import functools
import hashlib
import os
import sys
import textwrap
import types
import warnings

import dill
import numpy as np
from PyCosmo import core_file_handling
from PyCosmo.Background import Background, _call
from PyCosmo.BoltzmannSolver.LinearPerturbationBoltzmann import (
    LinearPerturbationBoltzmann,
)
from PyCosmo.LinearPerturbationApprox import LinearPerturbationApprox

from sympy2c import __version__ as sympy2c_version
from sympy2c.compiler import base_cache_folder, load_module
from sympy2c.utils import get_platform

from ._Util import get_active_branch_name
from .config import INFO, check_flattened, load_parameters_ini
from .ini_handling import Bunch
from .LinearPerturbationTable import LinearPerturbationTable
from .NonLinearPerturbationHaloFit import NonLinearPerturbationHaloFit
from .NonLinearPerturbationMead import NonLinearPerturbationMead
from .NonLinearPerturbationTable import NonLinearPerturbationTable
from .Projection import Projection

HERE = os.path.dirname(os.path.abspath(__file__))


def make_pickable(checks):
    detached_checks = [
        types.FunctionType(check.__code__, __builtins__) for check in checks
    ]
    return detached_checks


class Cosmo(object):
    """
    All of main functionalities of PyCosmo are managed by the main (Cosmo) class,
    which links to the other classes where the bulk of the calculations is
    performed.
    """

    _DEFAULT_PARAM_FILE = os.path.join(HERE, "config", "default.ini")

    def __init__(self, *, model_config=None):
        """Initiates the cosmo class
        :param paramfile:
        """

        if model_config is None:
            raise ValueError(
                "please use PyCosmo.build to create an instance of {}".format(
                    self.__class__
                )
            )

        self.model_config = model_config
        core_equations_files = model_config.main.core_equations_files

        key_0 = "_".join(map(str, sympy2c_version))
        key_1 = ""
        for i, core_equations_file in enumerate(core_equations_files):
            if not core_equations_file.startswith(
                "."
            ) and not core_equations_file.startswith("/"):
                core_equations_file = os.path.join(HERE, core_equations_file)
                core_equations_files[i] = core_equations_file

            key_1 += hashlib.md5(
                open(core_equations_file, "rb").read() + str(self.model_config).encode()
            ).hexdigest()[:6]

        self.core_equations_files = core_equations_files

        print(self.model_config)
        self.params = Bunch({})

        self._cache_file_name = "{}__{}.pkl".format(key_0, key_1)
        self._load_wrapper()
        self.load_params()

    def _load_wrapper(self):

        from . import version

        branch = get_active_branch_name() or ""

        platform = get_platform()

        folder = os.path.join(
            base_cache_folder(), "PyCosmo", platform, branch, version.replace(".", "_")
        )
        if not os.path.exists(folder):
            try:
                os.makedirs(folder)
            except IOError:
                # might be triggered due to race condition when run in parallel
                assert os.path.exists(folder), "this must not happen"

        cache_file = os.path.join(folder, self._cache_file_name)

        wrapper_loaded = False
        if os.path.exists(cache_file):
            print("cache hit at", cache_file)

            data = dill.load(open(cache_file, "rb"))

            folder = data["folder"]
            checks = data["checks"]
            enrich_params = data["enrich_params"]

            try:
                print("load wrapper from", folder)
                wrapper = load_module(folder)
                wrapper_loaded = True
            except ImportError:
                wrapper = None

        if not wrapper_loaded:
            module, checks, enrich_params = core_file_handling.load_core_files(
                self.core_equations_files, self.model_config
            )
            compilation_flags = self.model_config.main.compilation_flags.split(" ")
            wrapper = module.compile_and_load(compilation_flags=compilation_flags)

            data = {
                "folder": wrapper._folder,
                "module": module,
                "model_config": self.model_config,
                "checks": make_pickable(checks),
                "enrich_params": enrich_params and make_pickable([enrich_params])[0],
            }

            with open(cache_file, "wb") as fh:
                dill.dump(data, fh)
            print("new cache entry at", cache_file)

        self.model_parameter_checks = checks
        self.model_enrich_params = enrich_params
        self._wrapper = wrapper
        self._cache_file = cache_file

    @staticmethod
    def recompile_from_cli():
        assert len(sys.argv) == 2, "need name to pkl file"
        cache_file = sys.argv[1]
        try:
            data = dill.load(open(cache_file, "rb"))
        except Exception as e:
            print("could not read {}: {}".format(cache_file, e))
            sys.exit(1)

        model_config = data["model_config"]
        compilation_flags = model_config.main.compilation_flags.split(" ")
        module = data["module"]

        wrapper = module.recompile_and_load(
            compilation_flags=compilation_flags, force=True
        )

        data = {
            "folder": wrapper._folder,
            "module": module,
            "model_config": model_config,
            "checks": data["checks"],
            "enrich_params": data["enrich_params"],
        }

        with open(cache_file, "wb") as fh:
            dill.dump(data, fh)
        print("new cache entry at", cache_file)

    def load_params(self, paramfile=None):
        r"""
        Loads parameter file and additional user-defined parameters
        to initialize the Cosmo object

        :param paramfile: path to parameter file
        """

        if paramfile is None:
            paramfile = self.model_config.main.default_ini_file

        user_parameters, model_specific_parameters = load_parameters_ini(paramfile)
        check_flattened(user_parameters)
        self.user_parameters = user_parameters
        self.model_specific_parameters = model_specific_parameters
        self.paramfile = paramfile
        self._reset()

    def set(self, **kwargs):
        """
        Changes the configuration parameters of the PyCosmo instance. This will also
        recalculate the derived quantities.

        :param kwargs: keyword arguments for the input parameters to change.

        .. Warning ::
            Always change parameters of an instance of PyCosmo using the set function.
            Do not change variables directly!

        :return: If no keywords are passed then a list of options is printed

        Example:

        .. code-block:: python

            cosmo.set(omega_m=0.23)

        """

        model_specific_params = {
            k: v for (k, v) in kwargs.items() if k in self.model_specific_parameters
        }
        self.model_specific_parameters.update(model_specific_params)

        general_user_params = {
            k: v for (k, v) in kwargs.items() if k not in self.model_specific_parameters
        }

        check_flattened(general_user_params)
        self.user_parameters.update(general_user_params)
        self._reset()
        if len(general_user_params) == 0:
            print("Current status:")
            self.print_params(inc_derived=False)
            print("")
        else:
            print("Parameters updated")

    def __getstate__(self):
        dd = self.__dict__.copy()
        dd["model_parameter_checks"] = dill.dumps(dd["model_parameter_checks"])
        dd["model_enrich_params"] = dill.dumps(dd["model_enrich_params"])
        return dd

    def __setstate__(self, dd):
        dd["model_parameter_checks"] = dill.loads(dd["model_parameter_checks"])
        dd["model_enrich_params"] = dill.loads(dd["model_enrich_params"])
        self.__dict__.update(dd)
        self._reset()

    def _reset(self):
        """
        Resets the internal data in the instance

        :param paramfile: (optional) the name of the param file to use.
        """

        # check_flattened(self.user_parameters)
        self.derived_parameters = derived_parameters = self._enrich_params_pre(
            self.user_parameters
        )

        merged = self.user_parameters.copy()
        merged.update(derived_parameters)
        merged.update(self.model_specific_parameters)
        self.params.clear()
        self.params.update(merged)

        params = self.params
        messages = []
        for check in self.model_parameter_checks:
            msg = check(params)
            if msg:
                messages.append(msg)
        if messages:
            raise ValueError(
                "the model did not accept the given parameters: {}".format(
                    ", ".join(messages)
                )
            )

        self.reset_wrapper_globals()

        self.derived_parameters = derived_parameters = self._enrich_params_post(
            self.params
        )

        merged = self.params.copy()
        merged.update(derived_parameters)
        self.params.clear()
        self.params.update(merged)
        self.reset_wrapper_globals()

        params = self.params

        recomb = params.recomb
        if recomb == "recfast++":
            print("Recombination set to Recfast++")
            from PyCosmo._Recombination import Recombination

            self.rec = Recombination(params)
        elif recomb == "class":
            print("Recombination set to CLASS")
            from PyCosmo._RecombinationClass import RecombinationClass

            self.rec = RecombinationClass(params)
        elif recomb == "cosmics":
            print("Recombination set to COSMICS")
            from PyCosmo._RecombinationCosmics import RecombinationCosmics

            self.rec = RecombinationCosmics(params, self)
        elif recomb is None:
            print("Ignoring recombination.")
            self.rec = None
        else:
            raise ValueError("invalid value '{}' for recombination".format(recomb))

        self.background = background = Background(self, params, self.rec, self._wrapper)

        if params.pk_type == "boltz":
            a_table = 10 ** np.linspace(-15, 0, params.table_size)
            wrapper = self._wrapper
            wrapper.set_c_s_interp_values(a_table, background.cs(a_table))
            wrapper.set_taudot_interp_values(a_table, background.taudot(a_table))
            wrapper.set_eta_interp_values(a_table, background.eta(a_table))

        if params.pk_type in ("EH", "BBKS", "BBKS_CCL"):
            if params.pk_norm == "A_s":
                raise ValueError(
                    "A_s normalization not available for fitting functions"
                )
            self.lin_pert = LinearPerturbationApprox(self)
        elif params.pk_type == "boltz":
            self.lin_pert = LinearPerturbationBoltzmann(self)
            if params.pk_nonlin_type is not None:
                params.pk_nonlin_type = None
                warnings.warn(
                    "disabled non-linear perturbations which are not working "
                    "with the Boltzmann solver yet",
                )
        else:
            # Todo raise an error
            raise ValueError("unknown pk_type value {} used".format(params.pk_type))
            self.lin_pert = None

        # TODO: remove duplicate ?
        self.lin_pert_tab = LinearPerturbationTable(self.lin_pert)

        if params.pk_nonlin_type == "halofit" or params.pk_nonlin_type == "rev_halofit":
            assert (
                params.pk_type != "boltz"
            ), "Halofit model not supported by the Boltzmann solver yet!"
            self.nonlin_pert = NonLinearPerturbationHaloFit(self)

        elif params.pk_nonlin_type == "mead":
            assert (
                params.pk_type != "boltz"
            ), "Mead model not supported by the Boltzmann solver yet!"
            self.nonlin_pert = NonLinearPerturbationMead(self)

        elif params.pk_nonlin_type is None:
            self.nonlin_pert = None

        else:
            raise ValueError(
                'unknown pk_nonlin_type "{}"'.format(params.pk_nonlin_type)
            )

        self.lin_pert_tab = LinearPerturbationTable(self.lin_pert)

        if self.nonlin_pert is None:
            self.projection = FakeProjection()
            return

        self.nonlin_pert_tab = NonLinearPerturbationTable(self.nonlin_pert, params)
        if params.tabulation:
            self.projection = Projection(
                params, self.background, self.lin_pert_tab, self.nonlin_pert_tab
            )
        else:
            self.projection = Projection(
                params, self.background, self.lin_pert, self.nonlin_pert
            )

    def reset_wrapper_globals(self):
        params = self.params
        g = {}
        for name in self._wrapper.get_globals().keys():
            if hasattr(params, name):
                g[name] = getattr(params, name)

        self._wrapper.set_globals(**g)

    def _enrich_params_pre(self, params):
        """
        Setting basic constants and some derived quantities
        Initialising the basic cosmological parameters
        """

        derived_parameters = Bunch()

        if "cosmo_nudge" not in params.keys():
            nudge = [1.0, 1.0, 1.0]  # no nudge
        else:
            nudge = list(params.cosmo_nudge)

        if nudge != [1.0, 1.0, 1.0]:
            print(
                "Warning: nudges to H0, omega_gamma, omega_neu introduced "
                "- for debugging purposes only"
            )

        derived_parameters.H0 = (
            100.0 * params.h * nudge[0]
        )  # Hubble constant [km/s/Mpc]
        derived_parameters.rh = (
            params.c / derived_parameters.H0 * params.h
        )  # Hubble radius (=c/H0) at z=0 [h^-1 Mpc]
        # critical density at z=0 [h^2 M_sun Mpc^-3]
        derived_parameters.rho_crit = (
            3.0
            * derived_parameters.H0 ** 2
            / (8.0 * np.pi * params.G)
            * 1e6
            * params.mpc
            / params.msun
            / params.h ** 2
        )
        # TODO: check omega_gamma and omega_neu expressions
        # omega_photon (see Dodelson eq. 2.70) ** express in terms of H0? **)
        # params.omega_gamma = 2.470109245e-5 * (params.Tcmb / 2.725)**4 / params.h**2 *
        # nudge[1]

        # Uwe: put this into core file(s)? depends om model_specific_parameters
        if params.N_massive_nu != 0:
            derived_parameters.N_eff = (
                params.N_massless_nu
                + self.model_specific_parameters.T_mnu ** 4
                * (4 / 11) ** -(4 / 3)
                * params.N_massive_nu
            )

        derived_parameters.rho_gamma_eV = (
            (3 * 100 ** 2 / (8 * np.pi * params.G))
            * params.hbar ** 3
            * (1 / (params.mpc * 1e-3)) ** 2
            * (1 / (params.evc2))
            * (params.c * 1e3) ** 3
        )

        derived_parameters.T_0 = params.Tcmb * ((4 / 11) ** (1 / 3))
        derived_parameters.rho_mnu_eV = (
            3.0
            * derived_parameters.H0 ** 2
            * (params.hbar) ** 3
            * (params.c * 1e3) ** 3
            / (8 * np.pi * params.G)
            * (1 / (params.evc2))
            * (1 / (params.mpc * 1e-3)) ** 2
            / (params.kb * derived_parameters.T_0) ** 4
        )

        derived_parameters.omega_gamma_prefactor = (
            np.pi ** 2
            / 15
            * (2.725 * params.kb) ** 4
            / (derived_parameters.rho_gamma_eV)
        )
        derived_parameters.omega_gamma = (
            derived_parameters.omega_gamma_prefactor
            * (params.Tcmb / 2.725) ** 4
            / params.h ** 2
            * nudge[1]
        )
        derived_parameters.omega_neu = (
            params.N_massless_nu
            * 7.0
            / 8.0
            * (4.0 / 11.0) ** (4.0 / 3.0)
            * derived_parameters.omega_gamma
            * nudge[2]
        )  # omega for massless neutrino
        derived_parameters.omega_r = (
            derived_parameters.omega_gamma + derived_parameters.omega_neu
        )  # omega_radiation

        # suppress_rad
        if params.suppress_rad:
            derived_parameters.omega_r = 0.0

        if params.omega_suppress:
            # this ignores curvature - wrong but used by some codes which does not
            # account for omega_r in omega
            derived_parameters.omega = 1.0
            derived_parameters.omega_k = 0.0
            derived_parameters.omega_r = 0.0
            print(
                "Cosmo_add_constants: Warning: curvature suppressed - "
                "for testing purposes only"
            )
            # TODO: curvature suppression perhaps needs to be removed at some point
            if params.pk_type == "boltz":
                raise ValueError(
                    "Behaviour of the Boltzmann solver undetermined for suppressed"
                    " radiation!"
                )

        if self.model_enrich_params is not None:
            self.model_enrich_params(params, derived_parameters)

        return derived_parameters

    def _enrich_params_post(self, params):
        """
        Setting basic constants and some derived quantities
        Initialising the basic cosmological parameters
        """
        derived_parameters = Bunch()

        derived_parameters.omega_nu_m = getattr(self._wrapper, "omega_nu_m")(1.0)
        derived_parameters.omega_k = _call(self._wrapper, "omega_k")

        if params.flat_universe:
            derived_parameters.omega_l = _call(self._wrapper, "omega_l_a", 1.0)
        else:
            if params.omega_l is None:
                raise ValueError(
                    "for a non-float universe you also must provide a value for omega_l"
                )
            derived_parameters.omega_l = params.omega_l
            if params.pk_type == "boltz":
                raise NotImplementedError(
                    "Boltzmann solver only implemented for flat cosmologies"
                )
            derived_parameters.omega = (
                params.omega_m
                + params.omega_r
                + params.omega_l
                + derived_parameters.omega_nu_m
                + derived_parameters.omega_k
            )  # correct expression

        derived_parameters.omega_dm = (
            params.omega_m - params.omega_b
        )  # DM density (z=0)
        if derived_parameters.omega_k == 0.0:
            derived_parameters.sqrtk = 1.0
        else:
            derived_parameters.sqrtk = np.sqrt(abs(derived_parameters.omega_k))

        if params.omega_r > 0.0:
            derived_parameters.a_eq = (
                params.omega_r / params.omega_m
            )  # matter-radiation equality
            derived_parameters.z_eq = 1.0 / derived_parameters.a_eq - 1.0
        else:
            derived_parameters.a_eq = np.nan
            derived_parameters.z_eq = np.nan

        # derived_parameters.H_0 = 100 * params.h

        omh2 = params.omega_m * params.h ** 2

        derived_parameters._sigma_27 = params.Tcmb / 2.7  # Normalised CMB temperature

        # Wave vector values
        derived_parameters._k_eq = (
            7.46e-2 * omh2 * derived_parameters._sigma_27 ** -2
        )  # Eq. (3), units: Mpc^-1

        # Redshift values
        # TODO: this differs from z_eq in the cosmo class. should probably rename
        # it to avoid confusion
        # Redshift at matter-radiation equality, Eq. (2)
        derived_parameters._z_equality = (
            2.5e4 * omh2 * derived_parameters._sigma_27 ** -4
        )
        b_1 = 0.313 * omh2 ** -0.419 * (1.0 + 0.607 * omh2 ** 0.674)
        b_2 = 0.238 * omh2 ** 0.223
        derived_parameters._z_drag = (
            1291.0
            * (omh2 ** 0.251)
            / (1.0 + 0.659 * omh2 ** 0.828)
            * (1.0 + b_1 * (params.omega_b * params.h ** 2) ** b_2)
        )  # Redshift at drag epoch, Eq. (4)

        # Comoving distance values
        derived_parameters._R_drag = self._photon2baryon_dens(
            params, derived_parameters, derived_parameters._z_drag
        )
        derived_parameters._R_eq = self._photon2baryon_dens(
            params, derived_parameters, derived_parameters._z_equality
        )
        if derived_parameters._R_eq == 0:
            derived_parameters._sound_horiz = np.nan
        else:
            derived_parameters._sound_horiz = (
                2
                / (3 * derived_parameters._k_eq)
                * np.sqrt(6 / derived_parameters._R_eq)
                * np.log(
                    (
                        np.sqrt(1.0 + derived_parameters._R_drag)
                        + np.sqrt(derived_parameters._R_drag + derived_parameters._R_eq)
                    )
                    / (1.0 + np.sqrt(derived_parameters._R_eq))
                )
            )  # Eq. (6)

        if derived_parameters.omega_l > 0 and params.wa == 0.0:

            derived_parameters.a_eq2 = (
                params.omega_m / derived_parameters.omega_l
            ) ** (1 / 3.0)
            derived_parameters.z_eq2 = 1.0 / derived_parameters.a_eq2 - 1.0
        else:
            derived_parameters.a_eq2 = np.nan
            derived_parameters.z_eq2 = np.nan

        if self.model_enrich_params is not None:
            self.model_enrich_params(params, derived_parameters)

        return derived_parameters

    def _photon2baryon_dens(self, params, derived_parameters, z):
        """Returns the ratio of the baryon to photon momentum density R
        as defined in Eisenstein & Hu, 1998, ApJ, 511, 5, Equation (5)
        for redshift z
        R = 31.5 omega_b h^2 sigma_27^-4 (z/10^3)^-1"""

        R = (
            31.5
            * params.omega_b
            * params.h ** 2
            * derived_parameters._sigma_27 ** (-4)
            * (z / 10 ** 3) ** (-1.0)
        )

        return R

    def print_params(self, inc_derived=True, inc_internal=True, file=None):
        """
        Prints the parameters of PyCosmo instance.

        :param inc_derived: prints derived parameters [True or False]
        :param inc_internal:  prints internal parameterss (e.g. for lin_pert)
                              [True or False]
        """

        print_ = functools.partial(print, file=file)
        INDENT = "  "

        for section, parameters in INFO.items():

            if section.startswith("nonlinear_perturbations:"):
                if section != "nonlinear_perturbations:{}".format(
                    self.params.pk_nonlin_type
                ):
                    continue

            if section.startswith("internal:") and not inc_internal:
                continue

            print_("----", (section + " ").ljust(70, "-"))
            print_()
            for name, extra_text in parameters.items():
                full_text = name
                if extra_text:
                    full_text += " ({})".format(extra_text)
                lines = textwrap.wrap(full_text, 45)
                for line in lines[:-1]:
                    print_(INDENT + line)
                value = self.params[name]
                if value is None:
                    value = "not set"
                print_(INDENT + "{:45s}: {}".format(lines[-1], value))
            print_()

        # Uwe: review if this output is still up to date:

        DERIVED_INFO = dict(
            _sigma_27="Dimensionless CMB temperature [1]",
            _z_equality="Redshift of matter-radiation equlity [1]",
            _z_drag="Redshift of drag epoch [1]",
            _k_eq="Particle horizon at equality epoch [Mpc-1]",
            _sound_horiz="Sound horizon [Mpc-1]",
            H0="Hubble constant (H0) [km/s/Mpc]",
            rh="Hubble radius (rh) [Mpc/h]",
            rho_crit="Critical Density (rho_crit) [h^2 M_sun/Mpc^3]",
            omega_dm="Dark Matter density (omega_dm) [1]",
            omega_gamma="Photon density (omega_gamma) [1]",
            omega_neu="Neutrino density (omega_neu) [1]",
            omega_nu_m="Massive neutrino density (Omega_m_nu) [1]",
            omega_k="Curvature density (omega_k) [1]",
            omega="Total density (omega) [1]",
            a_eq="Dark energy-matter equality [1]",
            z_eq="Dark energy-matter equality as redshift [1]",
            a_eq2="Dark energy-radiation equality [1]",
            z_eq2="Dark energy-radiation equality as redshift [1]",
        )

        if inc_derived:
            print_("----", ("Derived quantities").ljust(70, "-"))
            print_()
            for key, value in self.derived_parameters.items():
                extra_text = DERIVED_INFO.get(key)
                if extra_text:
                    key += " ({})".format(extra_text)

                lines = textwrap.wrap(key, 45)
                for line in lines[:-1]:
                    print_(INDENT + line)

                if value is None:
                    value = "not set"
                print_(INDENT + "{:45s}: {}".format(lines[-1], value))
            print_()

        if self.model_specific_parameters:

            model_name = self.model_config.main.model
            print_(
                "----",
                ("Model {} specific quantities".format(model_name)).ljust(70, "-"),
            )
            print_()
            for key, value in self.model_specific_parameters.items():
                if value is None:
                    value = "not set"
                print_(INDENT + "{:45s}: {}".format(key, value))
        print_()

        if hasattr(self, "lin_pert"):
            if hasattr(self.lin_pert, "print_params"):
                self.lin_pert.print_params()


class FakeProjection:
    def __getattr__(self, *a):
        raise ValueError("you must set pk_nonlin_type to access projections")

    def __str__(self):
        return "None"

    def __getstate__(self):
        return None

    def __setstate__(self, dd):
        pass
