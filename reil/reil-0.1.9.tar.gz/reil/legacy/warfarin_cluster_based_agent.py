# -*- coding: utf-8 -*-
# type: ignore
'''
WarfarinClusterAgent class
==========================

An agent that produces action based on similarity of the state with clusters.
'''


import os
from dill import HIGHEST_PROTOCOL, dump, load
from random import choice, random
from time import time
from scipy.stats import norm

from collections import deque
import numpy as np
import pandas as pd

from reil.agents import Agent
from reil.datatypes import ReilData


class WarfarinClusterAgent(Agent):
    '''
    An agent that produces action based on similarity of the state with clusters.

    Constructor Arguments
    ---------------------
        default_actions: list of default actions.

    Methods
    -------
        act: return an action based on the given state.
        learn: learn using either history or action, reward, and state.
        reset:
    '''

    def __init__(self, cluster_filename, type='smoothing', smoothing_dose_threshold=0.0, dose_step=0.5, **kwargs):
        '''
        Initialize a WarfarinClusterAgent.
        type:
            smoothed: `smoothing_dose_threshold` and `dose_step` can be set. 
            rule based: argument `rule_base_filename` should specify the file that contains rules.
            two phase: argument `phase_change_day` should specify the change day. During each phase, average dose for the cluster is applied.
        '''
        self._default_actions = {}
        self._cluster_filename=cluster_filename,
        self._type = 'smoothed'
        self._day=0
        self._max_day = 90
        self._previous_dose = 0.0
        self._max_dose = 15.0
        self._smoothing_dose_threshold = 0.0
        self._dose_step = 0.5
        self._rule_base_filename = None
        self._phase_change_day = 0

        self.set_params(**kwargs)
        super().__init__(**kwargs)

        try:
            self._cluster_data = pd.read_csv(self._cluster_filename, sep=',', index_col='Index')
        except FileNotFoundError:
            raise FileNotFoundError(f'{kwargs["cluster_filename"]} not found.')

    def learn(self, **kwargs):
        '''
        This agent does not learn using `learn` method. Instead use ????
        '''
        pass

    def _assign_to_cluster(self, age, CYP2C9, VKORC1):
        prob = {}
        prob['age'] = norm.pdf(age,
                               self._cluster_data.loc['age mean', :],
                               self._cluster_data.loc['age stdev', :])

        prob['CYP2C9'] = self._cluster_data.loc['*1/*1', :].values ** int(CYP2C9 == '*1/*1') \
                       * self._cluster_data.loc['*1/*2', :].values ** int(CYP2C9 == '*1/*2') \
                       * self._cluster_data.loc['*1/*3', :].values ** int(CYP2C9 == '*1/*3') \
                       * self._cluster_data.loc['*2/*2', :].values ** int(CYP2C9 == '*2/*2') \
                       * self._cluster_data.loc['*2/*3', :].values ** int(CYP2C9 == '*2/*3') \
                       / self._cluster_data.loc['CYP2C9 Total', :].values
                       #    * self._cluster_data.loc['*3/*3', :].values ** int(CYP2C9 == '*3/*3') \

        prob['VKORC1'] = self._cluster_data.loc['A/A', :].values ** int(CYP2C9 == 'A/A') \
                       * self._cluster_data.loc['G/A', :].values ** int(CYP2C9 == 'G/A') \
                       * self._cluster_data.loc['G/G', :].values ** int(CYP2C9 == 'G/G') \
                       / self._cluster_data.loc['VKORC1 Total', :].values

        label = np.argmax(prob['age'] * prob['CYP2C9'] * prob['VKORC1']
                        * self._cluster_data.loc['prob', :].values)

        return label

    def act(self, state, **kwargs):
        '''
        return the best action for a given state.

        Arguments
        ---------
            state: the state for which an action is chosen.
        '''
        if self._day >= self._max_day:
            self._day = 0
            self._previous_dose = 0.0

        if self._day == 0:
            self._cluster_label = self._assign_to_cluster(state.normalize().value[0][0], state.value['CYP2C9'], state.value['VKORC1'])

        if self._type == 'smoothed':
            try:
                dose = round(self._cluster_data.at[f'dose {self._day:02} mean', str(self._cluster_label)] / self._dose_step) * self._dose_step
            except ZeroDivisionError:
                dose = self._cluster_data.at[f'dose {self._day:02} mean', str(self._cluster_label)]

            if abs(dose - self._previous_dose) >= self._smoothing_dose_threshold:
                action = ReilData.single_numerical(name='dose', value=dose, lower=0.0, upper=15.0)
                self._previous_dose = dose
            else:
                action = ReilData.single_numerical(
                    name='dose', value=self._previous_dose, lower=0.0, upper=15.0)
        elif self._type == 'two phase':
            if self._day == 0:
                self._dose = np.average(self._cluster_data.loc[[f'dose {i:02} mean' for i in range(self._phase_change_day)],
                                                               str(self._cluster_label)])
            elif self._day == self._phase_change_day:
                self._dose = np.average(self._cluster_data.loc[[f'dose {i:02} mean' for i in range(self._phase_change_day, self._max_day)],
                                                               str(self._cluster_label)])

            action = ReilData.single_numerical(
                name='dose', value=self._dose, lower=0.0, upper=15.0)

        elif self._type == 'rule based':
            if self._day == 0:
                self._rule_base_filename = kwargs.get('rule_base_filename', self._rule_base_filename)
                self._rule_base_data = pd.read_csv(self._rule_base_filename, sep=',', index_col='Index')

        self._day += 1

        return action

    def __repr__(self):
        try:
            return f'WarfarinClusterAgent({self._cluster_filename})'
        except AttributeError:
            return 'WarfarinClusterAgent'

# c = WarfarinClusterAgent(cluster_filename='Weka output (4 clusters).csv')
# [[(age/15, CYP2C9, VKORC1, c._assign_to_cluster(age/15, CYP2C9, VKORC1))] for age in range(15) for CYP2C9 in ('*1/*1', '*1/*2', '*1/*3', '*2/*2', '*2/*3') for VKORC1 in ('G/G', 'G/A', 'A/A')]
