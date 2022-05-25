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


def model_config(model_name, extra_settings):

    configs = {
        "lcdm": _model_lcdm,
        "wcdm": _model_wcdm,
        "mnulcdm": _model_mnulcdm,
    }

    if model_name not in configs:
        raise ValueError(
            "model {} not known, avaiable models: {}".format(
                model_name, sorted(configs.keys())
            )
        )

    return configs[model_name](extra_settings)


def _model_lcdm(extra_settings):
    rsa = extra_settings.pop("rsa", False)

    if rsa:
        main_defaults = dict(
            model="RSA",
            core_equations_files=["CosmologyCore.py", "CosmologyCore_rsa.py"],
            compilation_flags="-O3",
            default_ini_file="config/default_lcdm_rsa.ini",
        )
    else:
        main_defaults = dict(
            model="LCDM",
            core_equations_files=["CosmologyCore.py"],
            compilation_flags="-O3",
            default_ini_file="config/default_lcdm.ini",
        )

    main = {}
    for key, default_value in main_defaults.items():
        main[key] = extra_settings.pop(key, default_value)

    equation_parameters = dict(
        l_max=20,
        splits=None,
        reorder=True,
    )
    equation_parameters.update(extra_settings)

    return dict(
        main=main,
        equation_parameters=equation_parameters,
    )


def _model_wcdm(extra_settings):

    rsa = extra_settings.pop("rsa", False)

    if rsa:
        main_defaults = dict(
            model="WCDM_RSA",
            core_equations_files=["CosmologyCore_wcdm.py", "CosmologyCore_wcdm_rsa.py"],
            compilation_flags="-O3",
            default_ini_file="config/default_wcdm_rsa.ini",
        )
    else:
        main_defaults = dict(
            model="WCDM",
            core_equations_files=["CosmologyCore_wcdm.py"],
            compilation_flags="-O3",
            default_ini_file="config/default_wcdm.ini",
        )

    main = {}
    for key, default_value in main_defaults.items():
        main[key] = extra_settings.pop(key, default_value)

    equation_parameters = dict(
        l_max=20,
        splits=None,
        reorder=True,
    )
    equation_parameters.update(extra_settings)

    return dict(
        main=main,
        equation_parameters=equation_parameters,
    )


def _model_mnulcdm(extra_settings):
    rsa = extra_settings.pop("rsa", False)
    hierarchy = extra_settings.pop("hierarchy", "degenerate")

    variants = dict(
        degenerate=_model_mnu_degenerate,
    )

    if hierarchy not in variants:
        raise ValueError(
            "invalid value {} for hierarchy. supported: {}".format(
                hierarchy, list(variants)
            )
        )

    return variants[hierarchy](extra_settings, rsa)


def _model_mnu_degenerate(extra_settings, rsa):

    equation_parameters = dict(
        l_max=20,
        l_max_mnu=20,
        mnu_relerr=1e-5,
        splits=None,
        reorder=True,
    )
    equation_parameters.update(extra_settings)

    if rsa:
        return dict(
            main=dict(
                model="mnuLCDM_rsa",
                core_equations_files=[
                    "CosmologyCore_massivenu.py",
                    "CosmologyCore_massivenu_rsa.py",
                ],
                compilation_flags="-O3",
                default_ini_file="config/default_mnulcdm_rsa.ini",
            ),
            equation_parameters=equation_parameters,
        )

    return dict(
        main=dict(
            model="mnuLCDM",
            core_equations_files=["CosmologyCore_massivenu.py"],
            compilation_flags="-O3",
            default_ini_file="config/default_mnulcdm.ini",
        ),
        equation_parameters=equation_parameters,
    )
