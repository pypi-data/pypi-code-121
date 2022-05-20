#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classe Scikit-Learn like pour analyser les biais d'une modélisation.

Created on Sun Feb 13 14:52:34 2022

@author: Cyrile Delestre
"""

from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict
from itertools import combinations
from collections import OrderedDict
from inspect import signature

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.metrics import (roc_auc_score, accuracy_score, f1_score,
                             matthews_corrcoef)
from joblib import Parallel, delayed
from tqdm import tqdm

from dstk.utils import RollingWindow

@dataclass
class DataTypeInterface:

    def fit(self, data: pd.DataFrame):
        pass


@dataclass
class Categorical(DataTypeInterface):
    column: str

    def fit(self, data: pd.DataFrame):
        self.mode = data.loc[:, self.column].unique().tolist()
        self.cardinality = [f'{self.column} == {ii}' for ii in self.mode]


@dataclass
class OneHot(DataTypeInterface):
    columns: List[str]

    def fit(self, data: pd.DataFrame):
        self.mode = self.columns
        self.filter = [f'{ii} == 1' for ii in self.columns]


@dataclass
class Continous(DataTypeInterface):
    column: str
    quantile: List[float] = field(default_factory = lambda: [0.25, 0.5, 0.75])

    def fit(self, data: pd.DataFrame):
        self.mode = self.quantile
        quantile = data[:, self.column].quantile(q=self.quantile).value
        quant = RollingWindow(quantile, window=2, position='left')
        self.filter = [
            f'{self.column} > {quant[ii][0]} '
            f'and {self.column} <= {quant[ii][1]}'
            for ii in range(len(quant-1))
        ]


@dataclass
class Discret(DataTypeInterface):
    column: str

    def fit(self, data: pd.DataFrame):
        self.mode = data.loc[:, self.column].unique().tolist()
        self.filter = [f'{self.column} == {ii}' for ii in self.mode]

    def query(self):
        return ...


class BiasAnalyser(BaseEstimator, TransformerMixin):
    def __init__(
        self,
        data_type: Dict[str, DataTypeInterface],
        *,
        score: Dict[str, callable]=dict(acc=accuracy_score, f1=f1_score),
        degre: int=1
    ):
        self.data_type = data_type
        self.score = score
        self.degre = degre

    def fit(
        self,
        X: pd.DataFrame,
        y: Union[np.ndarray, pd.DataFrame]=None,
        labels: Optional[List[str]]=None
    ):
        self.mode = list()
        return self

    def transform(
    ):
        ...
