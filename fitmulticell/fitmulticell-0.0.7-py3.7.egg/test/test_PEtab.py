import os
import tempfile

import numpy as np
import pandas as pd
import petab_MS
from fitmulticell.sumstat import SummaryStatistics as ss
from fitmulticell.model import MorpheusModel
from fitmulticell.PEtab.base import PetabImporter


def test_PEtab_vs_noPEtab():
    """
    Check the the similarity between PEtab problem and regular problem
    in FitMultiCell.
    """

    # def simulation_prep(sumstat):
    #     new_sumstat = {}
    #     for key, _val in sumstat.items():
    #         if key == "loc":
    #             continue
    #         new_sumstat["condition1__" + key] = sumstat[key]
    #     return new_sumstat

    def eucl_dist(sim, obs):
        total = 0
        for key in sim:
            if key in ('loc', "time", "space.x"):
                continue
            if key == "condition1__a":
                y = obs["a"]
            else:
                y = obs["i"]
            x = sim[key]
            if x.size != y.size:
                return np.inf
            total += np.sum((x - y) ** 2)
        return total

    def obj_func_a(sumstat):
        new_sumstat = {}
        for key, _val in sumstat.items():
            if key in ["loc", "i", "time", "space.x"]:
                continue
            new_sumstat[key] = sumstat[key]
        return new_sumstat

    def obj_func_i(sumstat):
        new_sumstat = {}
        for key, _val in sumstat.items():
            if key in ["loc", "a", "time", "space.x"]:
                continue
            new_sumstat[key] = sumstat[key]
        return new_sumstat

    # Regular problem
    file = os.path.normpath(os.getcwd() + os.sep)
    par_map = {
        'rho_a': './Global/System/Constant[@symbol="rho_a"]',
        'mu_i': './Global/System/Constant[@symbol="mu_i"]',
        'mu_a': './Global/System/Constant[@symbol="mu_a"]',
    }
    obs_pars = {
        'rho_a': 0.01,
        'mu_i': 0.03,
        'mu_a': 0.02,
    }
    condition1_obs = str(file + '/doc/example/PEtab_problem_1' + '/Small.csv')
    model_file = str(
        file
        + '/doc/example/PEtab_problem_1'
        + '/ActivatorInhibitor_1D_seed.xml'
    )

    data = pd.read_csv(condition1_obs, sep='\t')
    tmp_dir = tempfile.TemporaryDirectory()
    dict_data = {}
    for col in data.columns:
        dict_data[col] = data[col].to_numpy()
    ss_dict = {"a": obj_func_a, "i": obj_func_i}
    sumstaat_func = ss(sum_stat_calculator=ss_dict)
    model = MorpheusModel(
        model_file,
        par_map=par_map,
        par_scale="lin",
        executable="morpheus",
        ignore_list=["time", "loc", "space.x"],
        dir=tmp_dir.name,
        sumstat=sumstaat_func,
        clean_simulation=False,
    )
    trajectory = model.sample(obs_pars)

    # PEtab problem
    tmp_dir = tempfile.TemporaryDirectory()
    petab_problem_path = str(
        file + '/doc/example/PEtab_problem_1' + '/ActivatorInhibitor_1D.yaml'
    )
    petab_problem = petab_MS.Problem.from_yaml(petab_problem_path)
    importer = PetabImporter(petab_problem)
    obs_pars_imported = petab_problem.get_x_nominal_dict(scaled=False)
    importer.petab_problem.model_file = (
        file
        + '/doc/example/PEtab_problem_1'
        + '/ActivatorInhibitor_1D_seed.xml'
    )
    petab_model = importer.create_model()
    petab_model.ignore_list = ["time", "loc", "space.x"]
    petab_model.executable = "morpheus"
    petab_model.clean_simulation = False
    petab_model.dir = tmp_dir.name
    petab_model.par_scale = "lin"
    petab_trajectory = petab_model.sample(obs_pars_imported)
    assert (eucl_dist(petab_trajectory, trajectory)) == 0
