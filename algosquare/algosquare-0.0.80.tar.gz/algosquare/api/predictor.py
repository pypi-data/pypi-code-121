"""AlgoSquare Predictor API."""
import os
import io
import json
import uuid
import pandas as pd

from ..base.types import Metatype
from ..base.tabular import TabularClassifier, TabularRegressor
from ..base.metric import Metric
from ..metrics import get_metric

from .common import upload_file
from .api import ApiObject, api_post, api_get, api_delete
from .model import Model

def get_predictors():
    """
    Gets all predictors.
    
    Returns:
        List of Predictors.
    """
    return [Predictor(x) for x in api_get('api/predictors')]

def add_model(predictor, output_dir, tag = None, metric = None, metric_stats = None, predictor_id = None):
    """
    Add model to latest or specific Predictor.
    
    Args:
        predictor: TabularClassifier or TabularRegressor.
        output_dir: path for temp files.   
        tag: model tag.
        metric: Metric.
        metric_stats: output from tools.analytics.calculate_metric_stats.
        predictor_id: string.

    Returns:
        Model.

    Raises:
        TypeError, ValueError
    """
    if not _is_valid_predictor(predictor):
        raise TypeError('invalid predictor')  

    if predictor_id is not None and not isinstance(predictor_id, str):
        raise TypeError('invalid predictor_id')

    settings = dict()
    if tag is not None:
        if len(str(tag)) > 64:
            raise ValueError('tag must not be longer than 64')
        settings['tag'] = str(tag)

    if metric is not None:
        if not isinstance(metric, Metric):
            raise TypeError('metric should be a Metric')

        metric_dict = metric.to_dict()

        if metric_stats is not None:
            metric_dict['stats'] = metric_stats

        settings['metric'] = metric_dict

    filename = uuid.uuid4().hex + '.mdl'
    model_path = os.path.join(output_dir, filename)
    predictor.save(model_path)

    payload = dict(settings = settings, class_name = type(predictor).__name__)
    payload['file'] = dict(filename = filename, key = upload_file(model_path))
    if predictor_id is not None:
        payload['predictor_id'] = predictor_id

    os.remove(model_path)
    return Model.load(api_post('api/predictors', json=payload))

class Predictor(ApiObject):
    def add_model(predictor, output_dir, tag = None, metric = None, metric_stats = None):
        """
        Add model to specific Predictor.
        
        Args:
            predictor: TabularClassifier or TabularRegressor.
            output_dir: path for temp files.   
            tag: model tag.
            metric: Metric.
            metric_stats: output from tools.analytics.calculate_metric_stats.

        Returns:
            Model.

        Raises:
            TypeError, ValueError
        """
        if self.status == 'disabled':
            raise RuntimeError('predictor is disabled')

        return add_model(predictor, output_dir, tag, metric, metric_stats, self.predictor_id)

    @classmethod
    def get(cls, predictor_id):
        """
        Gets specific predictor.
        
        Args:
            predictor_id: string.

        Returns:
            Predictor.
        """
        return cls(api_get(f'api/predictors/{predictor_id}'))

    def get_models(self):
        """
        Gets models for predictor.
        
        Returns:
            List of Models.
        """
        return [Model.load(x) for x in api_get(f'api/predictors/{self.predictor_id}/models')]

def _is_classifier(predictor):
    for base_class in [TabularClassifier]:
        if isinstance(predictor, base_class):
            return True
    return False

def _is_valid_predictor(predictor):
    for base_class in [TabularClassifier, TabularRegressor]:
        if isinstance(predictor, base_class):
            return True
    return False