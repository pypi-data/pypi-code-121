# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 20:45:14 2020

@author: msmsa
"""
import pandas as pd
import matplotlib.pyplot as plt
from .MC import MC
import ast
from pathlib import Path


class InputData(MC):
    """
    ``InputData`` class reads the input data from the csv file and load them as class attributes. This class is inherited from the ``MC`` class.

    Main functionalities include:
    loading data, updating data and generating random number for data based on the defined probabiliy distributions.

    :param input_data_path: absolute path to the input data file
    :type input_data_path: str
    :param eval_parameter: If the parameters are tuple instead of str, it will evalute their real value.
    :type eval_parameter: bool, optional

    """
    def __init__(self, input_data_path, eval_parameter=False):
        """Initialize ``InputData`` class
        """
        self.input_data_path = input_data_path
        self.Data = pd.read_csv(self.input_data_path, dtype={'amount': float, 'uncertainty_type': pd.Int64Dtype(), 'loc': float,
                                                             'scale': float, 'shape': float, 'minimum': float, 'maximum': float})

        self.Data['Comment'] = self.Data['Comment'].fillna('')
        self.Data['Reference'] = self.Data['Reference'].fillna('')

        if eval_parameter:
            self.Data['Parameter Name'] = self.Data['Parameter Name'].apply(ast.literal_eval)

        # Setting uncertainty type to 0 : Undefined ; when it is not defined
        self.Data['uncertainty_type'].fillna(0, inplace=True)
        # self.Data=self.Data.where((pd.notnull(self.Data)),None)
        self.Input_dict = {}
        self.keys = self.Data.columns[3:]
        for i in range(len(self.Data)):
            if self.Data.Category[i] not in self.Input_dict.keys():
                exec("self.%s = {}" % self.Data.Dictionary_Name[i])
                exec("self.Input_dict[self.Data.Category[i]] = self.%s" % self.Data.Dictionary_Name[i])
                exec("self.%s[self.Data['Parameter Name'][i]] = dict(zip(self.keys,self.Data.loc[i,'Parameter Description':]))" %
                     self.Data.Dictionary_Name[i])
            else:
                exec("self.%s[self.Data['Parameter Name'][i]] = dict(zip(self.keys,self.Data.loc[i,'Parameter Description':]))" %
                     self.Data.Dictionary_Name[i])

        # References
        self._references = pd.read_csv(Path(__file__).parent / 'Data/References.csv',
                                       index_col=0)

    def Update_input(self, NewData):
        """ Get a new DataFrame and update the ``data`` in ``InputData`` class.

        :param NewData:
        :type NewData: 'pandas.DataFrame'
        """
        for i in NewData.index:
            exec("self.%s[NewData['Parameter Name'][i]] = dict(zip(self.keys,NewData.loc[i,'Parameter Description':]))" % NewData.Dictionary_Name[i])
            self.Data.loc[i] = NewData.loc[i]

    def setup_MC(self, seed=None, **kwargs):
        """ Initialize the parent class (``MC``) and create ``MCRandomNumberGenerator`` based on the data for uncertainty distributions via
        calling ``MC.setupMC()`` method.

        :param seed: seed for random number generation
        :type seed: int, optional

        .. seealso:: Class_MC_
        """
        super().__init__(self.Input_dict)
        super().setup_MC(seed, **kwargs)

    def reset_static_vals(self):
        for i in self.Data.index:
            exec("self.%s[self.Data['Parameter Name'][i]]['amount'] = self.Data.loc[i,'amount']" % self.Data.Dictionary_Name[i])

    def stats(self):
        plt.rcParams["font.family"] = "Times New Roman"
        plt.rcParams["font.size"] = "14"
        stats = pd.DataFrame(index=['n_param', 'Uncertain_dist?', 'Reference?'], columns=['value'])
        stats.loc['n_param', 'value'] = len(self.Data.index)
        stats.loc['Uncertain_dist?', 'value'] = sum(self.Data['uncertainty_type'] > 1)
        stats.loc['Reference?', 'value'] = sum(self.Data['Reference'] != '')

        fig, ax = plt.subplots(1, figsize=(6, 3))
        stats.plot.bar(ax=ax)
        ax.tick_params(axis='x', rotation=0)
        ax.set_title(self.__module__.split('.')[-1])

        return stats

    def report_references(self, df=None):
        if df is None:
            df = self.Data
        included_ref = set()
        for i in df['Reference']:
            if len(i) > 1:
                i = eval(i)
                for r in i:
                    included_ref.add(r)
        ref = self._references.loc[included_ref, :]
        ref.sort_values(by='ID', inplace=True)
        return ref
