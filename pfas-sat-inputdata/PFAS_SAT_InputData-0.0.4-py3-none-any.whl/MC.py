# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 15:49:46 2019

@author: msardar2
"""
from stats_arrays import MCRandomNumberGenerator, UncertaintyBase
import numpy as np


class MC():
    """
    .. _Class_MC:

    :param input_dict: list of dictionaries that include input data (see the example)
    :type input_dict: list

    This class generates random number for Monte-Carlo simulations. This class is the interface to
    `stats_arrays <https://pypi.org/project/stats-arrays/>`_ package.

    The example below is showing the usage of ``stats_arrays``.

    :Example:

    >>> from stats_arrays import *
    >>> my_variables = UncertaintyBase.from_dicts(
    ...     {'loc': 2, 'scale': 0.5, 'uncertainty_type': NormalUncertainty.id},
    ...     {'loc': 1.5, 'minimum': 0, 'maximum': 10, 'uncertainty_type': TriangularUncertainty.id}
    ... )
    >>> my_variables
    array([(2.0, 0.5, nan, nan, nan, False, 3),
           (1.5, nan, nan, 0.0, 10.0, False, 5)],
        dtype=[('loc', '<f8'), ('scale', '<f8'), ('shape', '<f8'),
               ('minimum', '<f8'), ('maximum', '<f8'), ('negative', '?'),
               ('uncertainty_type', 'u1')])
    >>> my_rng = MCRandomNumberGenerator(my_variables)
    >>> my_rng.next()
    array([ 2.74414022,  3.54748507])

    >>> from PFAS_SAT import MC
    >>> input_dict={'Cat1': {'Par1': {'Name': 'Name1','amount': 1.0,'unit': 'Unit1',
    ...                                 'uncertainty_type': 3,'loc': 1,'scale':0.2 ,'shape': None,
    ...                                 'minimum': None,'maximum': None,
    ...                                 'Reference': None,'Comment': None},
    ...                     'Par2': {'Name': 'Name2','amount': 1.5,'unit': 'Unit2',
    ...                                 'uncertainty_type': 3,'loc': 1.5,'scale': 0.4,'shape': None,
    ...                                 'minimum': None,'maximum': None,
    ...                                 'Reference': None,'Comment': None}}}
    >>> test_MC = MC(input_dict)
    >>> test_MC.setup_MC()
    >>> test_MC.gen_MC()
    [(('Cat1', 'Par1'), 1.0554408376879747),
     (('Cat1', 'Par2'), 1.9366617123732333)]

    """
    def __init__(self, input_dict):
        """ Initialize ``MC`` class
        """
        self.input_dict = input_dict

    def setup_MC(self, seed=None, flow_full_name=None, concentration=True):
        """ Creates `MCRandomNumberGenerator` and store it in ``MC.rand`` attribute

        :param seed: seed for random number generation
        :type seed: int, optional
        """
        self.list_var = list()
        self.sens_analysis = {}
        self.run_index = 0
        self.max_run = 10000000
        k = 0
        if flow_full_name is None:
            for x in self.input_dict.values():
                for y in x:
                    self.list_var.append(x[y])
                    if 'list' in x[y].keys():
                        self.sens_analysis[k] = x[y]['list']
                        self.max_run = min(self.max_run, len(x[y]['list']))
                    k += 1
        if flow_full_name:
            self.input_dict_mc = {}
            self.input_dict_mc[flow_full_name] = self.input_dict[flow_full_name]
            if concentration:
                self.input_dict_mc[flow_full_name + ' PFAS Concentration'] = (
                    self.input_dict[flow_full_name + ' PFAS Concentration'])
            for x in self.input_dict_mc.values():
                for y in x:
                    self.list_var.append(x[y])
                    if 'list' in x[y].keys():
                        self.sens_analysis[k] = x[y]['list']
                        self.max_run = min(self.max_run, len(x[y]['list']))
                    k += 1

        self.Vars = UncertaintyBase.from_dicts(*self.list_var)
        self.rand = MCRandomNumberGenerator(self.Vars, seed=seed)

    def gen_MC(self):
        """Generate random numbers and update data. It also returns a list of tuples include the name of parameter and generted number.

        :return: List of tuples include the name of parameter and generted number: ``[((parameter_category,parameter),generated_number)]``
        :rtype: list
        """
        data = self.rand.next()
        if len(self.sens_analysis) > 0:
            for x in self.sens_analysis.keys():
                data[x] = self.sens_analysis[x][self.run_index]
            self.run_index += 1
            if self.run_index > self.max_run:
                raise ValueError('Number of runs are more than the number of defined inputs')
        i = 0
        variables = []
        if hasattr(self, 'input_dict_mc'):
            for x in self.input_dict_mc.keys():
                for y in self.input_dict_mc[x]:
                    if self.input_dict_mc[x][y]['uncertainty_type'] > 1:
                        if np.isnan(data[i]):
                            raise ValueError(f"Generate value for  ({x}, {y}) is invalide! (nan)")
                        self.input_dict_mc[x][y]['amount'] = data[i]
                        variables.append(((x, y), data[i]))
                    i += 1
        else:
            for x in self.input_dict.keys():
                for y in self.input_dict[x]:
                    if self.input_dict[x][y]['uncertainty_type'] > 1:
                        if np.isnan(data[i]):
                            raise ValueError(f"Generate value for  ({x}, {y}) is invalide! (nan)")
                        self.input_dict[x][y]['amount'] = data[i]
                        variables.append(((x, y), data[i]))
                    i += 1
        return variables
