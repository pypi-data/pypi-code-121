"""AlgoSquare Dataset API."""
import io
import time
import numpy as np
import pandas as pd
import requests
import json

from ..base.tabular import is_input_metatype
from ..base.types import Metatype, is_target_metatype, is_classification_metatype, string_to_metatype
from ..metrics import get_metric

from .api import ApiObject, api_get, api_post, api_put
from .task import Task
from .common import upload_dataframe

def get_datasets():
    """fetches all datasets."""
    return [Dataset.load(x) for x in api_get('api/datasets')]

class Dataset(ApiObject):
    """Base class for all datasets."""
    def __init__(self, entry):
        if type(self) == Dataset:
            raise RuntimeError('base class should not be instantiated')
        super().__init__(entry)

    @staticmethod
    def get(dataset_id):
        """
        Gets specific dataset.
        
        Args:
            dataset_id: string.

        Returns:
            Dataset subclass.
        """
        return Dataset.load(api_get(f'api/datasets/{dataset_id}'))

    @staticmethod
    def load(entry):
        if entry['data_format'] == 'tabular':
            return TabularData(entry)
        else:
            raise ValueError('unknown data_format')

    def refresh(self):
        """reloads dataset."""
        self.update(api_get(f'api/datasets/{self.dataset_id}'))

    def get_tasks(self):
        """
        Gets tasks for dataset.
        
        Returns:
            List of Tasks.
        """
        return [Task(x) for x in api_get(f'api/datasets/{self.dataset_id}/tasks')]

class TabularData(Dataset):
    """Tabular data class."""
    @classmethod
    def from_csv(cls, title, input_file, target_file, input_metatypes = None, target_metatypes = None):
        """
        Creates tabular data from csv files.
        
        Args:
            title: title of dataset.
            input_file: path to input data.
            target_file: path to target data.
            input_metatypes: list of Metatype or path to csv file.
            target_metatypes: list of Metatype or path to csv file.

        Returns:
            TabularData.
        """
        input_df = pd.read_csv(input_file, dtype=str)
        target_df = pd.read_csv(target_file, dtype=str)
        return cls.from_df(title, input_df, target_df, input_metatypes, target_metatypes)

    @classmethod
    def from_df(cls, title, input_df, target_df, input_metatypes = None, target_metatypes = None):
        """
        Creates tabular data from DataFrames.
        
        Args:
            title: title of dataset.
            input_df: DataFrame with input data.
            target_df: DataFrame with target data.
            input_metatypes: list of Metatype or path to csv file.
            target_metatypes: list of Metatype or path to csv file.

        Returns:
            TabularData.

        Raises:
            TypeError, ValueError
        """
        if not isinstance(title, str):
            raise TypeError('title must be a string')
        if len(title) > 1024:
            raise ValueError('title must be maximum 1024 characters')

        if not isinstance(input_df, pd.DataFrame):
            raise TypeError('input_df must be a DataFrame')
        if not isinstance(target_df, pd.DataFrame):
            raise TypeError('target_df must be a DataFrame')

        metatypes = []

        if input_metatypes is not None:
            prepared_metatypes = _prepare_metatypes(input_df, input_metatypes)
            for metatype in prepared_metatypes.values():
                if not is_input_metatype(metatype):
                    raise ValueError(f'invalid input metatype: {metatype}')
            metatypes.append(dict(namespace = 'inputs', metadata = [dict(name = name, metatype = prepared_metatypes.get(name, Metatype.VOID).name.lower()) for name in input_df]))

        if target_metatypes is not None:
            prepared_metatypes = _prepare_metatypes(target_df, target_metatypes)
            for metatype in prepared_metatypes.values():
                if not is_target_metatype(metatype):
                    raise ValueError(f'invalid target metatype: {metatype}')
            metatypes.append(dict(namespace = 'targets', metadata = [dict(name = name, metatype = prepared_metatypes.get(name, Metatype.VOID).name.lower()) for name in target_df]))

        files = [dict(namespace = namespace, key = upload_dataframe(namespace, df)) for namespace, df in [('inputs', input_df), ('targets', target_df)]]
        entry = api_post('api/datasets', json=dict(settings = dict(title = title, data_format = 'tabular'), files = files, metatypes = metatypes))
        return cls(entry)

    def create_task(self, title, metric_name = None, pos_label = None, holdout = 25, input_columns = None, target_columns = None):
        """
        Creates a task for dataset.
        
        Args:
            title: title of task.
            metric_name: name used for get_metric.
            pos_label: positive label for binary metrics.
            holdout: size of test set as a proportion of dataset.
            input_columns: list of columns in inputs.
            target_columns: list of columns in targets.

        Returns:
            Task.

        Raises:
            RuntimeError, ValueError
        """
        if self.status != 'ok':
            raise RuntimeError('status must be ok')

        holdout = int(holdout)
        if holdout < 5 or holdout > 30:
            raise ValueError('holdout outside of range 5-30')

        if input_columns is None:
            input_columns = [x['name'] for x in self.metadata['inputs']]

        if target_columns is None:
            target_columns = [self.metadata['targets'][0]['name']]

        if len(target_columns) != 1:
            raise ValueError('only one target column is currently allowed')

        features = dict(inputs = [x for x in self.metadata['inputs'] if x['name'] in input_columns], targets = [x for x in self.metadata['targets'] if x['name'] in target_columns])

        if len(features['inputs']) == 0:
            raise ValueError('no X features selected')

        if len(features['targets']) != 1:
            raise ValueError('only one y feature must be selected')

        target_metatype = string_to_metatype(features['targets'][0]['metatype'])
        if not is_target_metatype(target_metatype):
            raise ValueError('invalid target_metatype')

        if metric_name is None:
            metric_name = 'accuracy' if is_classification_metatype(target_metatype) else 'mean_squared_error'
        else:
            metric = get_metric(metric_name)
            if metric['metatypes'] == ['binary'] and pos_label is None:
                raise ValueError('pos_label is missing')

        settings = dict(title = title, metric = metric_name, holdout = holdout)
        if pos_label is not None:
            if target_metatype != Metatype.BINARY:
                raise ValueError('pos_label only expected for binary metatypes')

            categories = features['targets'][0]['stats']['categories']
            if pos_label not in categories:
                raise RuntimeError(f'{pos_label} not in {categories}')
            settings['pos_label'] = pos_label

        payload = dict()
        payload['settings'] = settings
        payload['selections'] = [dict(namespace = namespace, features = [x['feature_id'] for x in v]) for namespace, v in features.items()]

        return Task(api_post(f'api/datasets/{self.dataset_id}/tasks', json=payload))

def _prepare_metatypes(data_df, metatypes):
    if isinstance(metatypes, str):
        mt_df = pd.read_csv(metatypes, dtype = str, index_col = 0)
        if mt_df.shape[1] != 1:
            raise ValueError(f'{metatypes} must have exactly two columns')
        mt_dict = mt_df.squeeze().to_dict()
        if set(mt_dict.keys()).difference(data_df):
            raise ValueError(f'{metatypes} have invalid names')

        return {k : string_to_metatype(v) for k, v in mt_dict.items()}
    else:
        return dict(zip(data_df, metatypes))

def _sizeof_fmt(num, suffix="B"):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi']:
        if abs(num) < 1024.0 or unit == 'Pi':
            break
        num /= 1024.0
    return f'{num:3.1f} {unit}{suffix}'