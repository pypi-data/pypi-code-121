"""AlgoSquare Model API."""
import io
import json
import pandas as pd

from .api import ApiObject, api_post, api_get, api_delete
from .common import upload_dataframe

def get_deployed():
    """
    Gets all deployed models.
    
    Returns:
        List of Models.
    """
    return [Model.load(x) for x in api_get('api/models/deployments')]

class Model(ApiObject):
    """Base class for all models."""
    def __init__(self, entry):
        if type(self) == Model:
            raise RuntimeError('base class should not be instantiated')
        super().__init__(entry)

    @staticmethod
    def get(model_id):
        """
        Gets specific model.
        
        Args:
            model_id: string.

        Returns:
            Model.
        """
        return Model.load(api_get(f'api/models/{model_id}'))

    @staticmethod
    def load(entry):
        base_class = entry['base_class']
        if base_class in ('TabularClassifier', 'TabularClassificationAutoML'):
            return TabularClassifier(entry)
        elif base_class in ('TabularRegressor', 'TabularRegressionAutoML'):
            return TabularRegressor(entry)
        else:
            raise ValueError('unknown base_class')

    def refresh(self):
        """reloads model."""
        self.update(api_get(f'api/models/{self.model_id}'))

    def deploy(self):
        """
        Deploys model.
        
        Raises:
            RuntimeError.
        """
        if self.status != 'stopped':
            raise RuntimeError('status must be stopped')

        self.update(api_post(f'api/models/{self.model_id}/deployment'))

    def discharge(self):
        """discharges model."""
        if self.status != 'running':
            raise RuntimeError('status must be running')
        self.update(api_delete(f'api/models/{self.model_id}/deployment'))

    def prediction_update(self, prediction_id, actual):
        """
        Updating model.
        
        Args:
            prediction_id: output from model.predict.
            actual: observed target.

        Raises:
            RuntimeError.
        """
        if self.status != 'running':
            raise RuntimeError('status must be running')

        return api_post(f'api/models/{self.model_id}/prediction/update', data = json.dumps(dict(prediction_id = prediction_id, actual = actual)))

    def _predict(self, data, prediction_method):
        if self.status != 'running':
            raise RuntimeError('status must be running')

        if prediction_method not in self.prediction_methods:
            raise NotImplementedError(f'{prediction_method} not implemented in model')

        return api_post(f'api/models/{self.model_id}/prediction', data = json.dumps(dict(data = data, prediction_method = prediction_method)))

    def _predict_batch(self, data, prediction_method, upload_func):
        if self.status != 'running':
            raise RuntimeError('status must be running')

        if prediction_method not in self.prediction_methods:
            raise NotImplementedError(f'{prediction_method} not implemented in model')

        files = upload_func(data)
        payload = dict(prediction_method = prediction_method, files = files)

        return api_post(f'api/models/{self.model_id}/batch', data = json.dumps(payload))


class TabularClassifier(Model):
    """Tabular classifier class."""
    def predict(self, data):
        """
        Using deployed model to make single prediction.
        
        Args:
            data: dict

        Returns:
            dict.

        Raises:
            NotImplementedError, RuntimeError, TypeError.
        """
        if not isinstance(data, dict):
            raise TypeError('data must be a dict')

        return self._predict(data, 'predict')

    def predict_batch(self, data):
        """
        Using deployed model to make batch prediction.
        
        Args:
            data: DataFrame

        Returns:
            DataFrame.

        Raises:
            NotImplementedError, RuntimeError, TypeError.
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError('data must be a dataframe')

        return _batch_to_df(self._predict_batch(data, 'predict', _upload_tabular_inputs))

    def predict_proba(self, data):
        """
        Using deployed model to output class probabilities.
        
        Args:
            data: dict

        Returns:
            dict.

        Raises:
            NotImplementedError, RuntimeError, TypeError.
        """
        if not isinstance(data, dict):
            raise TypeError('data must be a dict')

        return self._predict(data, 'predict_proba')

    def predict_proba_batch(self, data):
        """
        Using deployed model to output class probabilities for batch.
        
        Args:
            data: DataFrame

        Returns:
            DataFrame.

        Raises:
            NotImplementedError, RuntimeError, TypeError.
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError('data must be a dataframe')

        return _batch_to_df(self._predict_batch(data, 'predict_proba', _upload_tabular_inputs))

    def decision_function(self, data):
        """
        Using deployed model to output decision function.
        
        Args:
            data: dict

        Returns:
            dict.

        Raises:
            NotImplementedError, RuntimeError, TypeError.
        """
        if not isinstance(data, dict):
            raise TypeError('data must be a dict')

        return self._predict(data, 'decision_function')

    def decision_function_batch(self, data):
        """
        Using deployed model to output decision function for batch.

        Args:
            data: DataFrame

        Returns:
            DataFrame.

        Raises:
            NotImplementedError, RuntimeError, TypeError.
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError('data must be a dataframe')

        return _batch_to_df(self._predict_batch(data, 'decision_function', _upload_tabular_inputs))

class TabularRegressor(Model):
    """Tabular regressor class."""
    def predict(self, data):
        """
        Using deployed model to make single prediction.
        
        Args:
            data: dict

        Returns:
            dict.

        Raises:
            NotImplementedError, RuntimeError, TypeError.
        """
        if not isinstance(data, dict):
            raise TypeError('data must be a dict')

        return self._predict(data, 'predict')

    def predict_batch(self, data):
        """
        Using deployed model to make batch prediction.
        
        Args:
            data: DataFrame

        Returns:
            DataFrame.

        Raises:
            NotImplementedError, RuntimeError, TypeError.
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError('data must be a dataframe')

        return _batch_to_df(self._predict_batch(data, 'predict', _upload_tabular_inputs))

def _batch_to_df(response):
    with io.StringIO(response['data']) as buffer:
        return pd.read_csv(buffer, index_col = 0)

def _upload_tabular_inputs(data):
    return [dict(namespace = 'inputs', key = upload_dataframe('inputs', data))]
