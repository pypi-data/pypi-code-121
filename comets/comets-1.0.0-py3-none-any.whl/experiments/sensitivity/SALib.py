# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from .sensitivityanalyzer import (
    BaseSensitivityAnalyzer,
    SensitivityAnalyzerRegistry,
)
from SALib.sample import saltelli, fast_sampler, latin
from SALib.analyze import sobol, fast, rbd_fast
from ...utilities.registry import partialclass
import numpy as np


class SALib(BaseSensitivityAnalyzer):
    """
    SALib sensitivity analyzer (prototype, only uniform or normal continuous distributions, only few methods)
    """

    def __init__(self, distribution, method='FAST'):

        self.parameter_names = [parameter['name'] for parameter in distribution]
        self.distribution = distribution
        self.method = method
        self.problem = {
            "num_vars": len(distribution),
            "names": self.parameter_names,
            "bounds": [
                list(parameter["parameters"].values()) for parameter in distribution
            ],
            "dists": [
                self.map_distribution_name(parameter["distribution"])
                for parameter in distribution
            ],
        }
        if self.method == 'Sobol':
            self.samplermethod = saltelli.sample
            self.analyzermethod = sobol.analyze
        elif self.method == 'FAST':
            self.samplermethod = fast_sampler.sample
            self.analyzermethod = fast.analyze
        elif self.method == 'RBD-FAST':
            self.samplermethod = latin.sample
            self.analyzermethod = rbd_fast.analyze

    def map_distribution_name(self, dist_name):
        if dist_name == "uniform":
            return "unif"
        elif dist_name == "normal":
            return "norm"
        else:
            raise ValueError("Unsupported distribution: {}".format(dist_name))

    def get_samples(self, number_of_samples):
        samples = self.samplermethod(self.problem, number_of_samples)
        self.X = samples  # Storing samples for some analysis methods
        return self.decoder(samples)

    def sensitivity_analysis(self, list_of_results):
        results = {}
        for kpi_num, kpi in enumerate(list(list_of_results[0].keys())):
            # Transform results from a list of dictionaries into an array
            Y = np.array([list(i.values())[kpi_num] for i in list_of_results])

            if self.method == 'RBD-FAST':
                Si = self.analyzermethod(self.problem, self.X, Y)

                results[kpi] = {
                    "Sobol main effects": dict(zip(self.parameter_names, Si["S1"])),
                }

            else:
                Si = self.analyzermethod(self.problem, Y)

                results[kpi] = {
                    "Sobol main effects": dict(zip(self.parameter_names, Si["S1"])),
                    "Sobol total effects": dict(zip(self.parameter_names, Si["ST"])),
                }

        return results

    def decoder(self, samples):
        # Change format to construct a list of dict of the form {'name of param1' : value1, 'name of param2' : value2}
        sample_inputs = []
        for j in range(len(samples[:, 0])):
            one_sample = samples[j, :]
            sample_inputs.append(
                {key: value for key, value in zip(self.parameter_names, one_sample)}
            )
        return sample_inputs


# Register different SALib methods
for method_name in ['Sobol', 'FAST', 'RBD-FAST']:
    SensitivityAnalyzerRegistry[method_name] = partialclass(SALib, method=method_name)
