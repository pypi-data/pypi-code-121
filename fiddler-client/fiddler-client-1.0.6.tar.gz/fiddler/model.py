import os
import tarfile
import tempfile
from collections import namedtuple
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Union

import pandas as pd
import requests

from fiddler.connection import Connection
from fiddler.core_objects import (
    AttributionExplanation,
    ModelInfo,
    MulticlassAttributionExplanation,
)
from fiddler.utils import cast_input_data
from fiddler.utils.general_checks import type_enforce
from fiddler.utils.pandas import df_to_dict


class Model:
    def __init__(self, connection: Connection, project_id: str, model_id):
        self.connection = connection
        self.project_id = project_id
        self.model_id = model_id

    def get_info(self) -> ModelInfo:
        """Get ModelInfo for a model in a certain project.

        :returns: A fiddler.ModelInfo object describing the model.
        """
        # Type enforcement
        project_id = type_enforce('project_id', self.project_id, str)
        model_id = type_enforce('model_id', self.model_id, str)

        path = ['model_info', self.connection.org_id, project_id, model_id]
        res = self.connection.call(path, is_get_request=True)
        return ModelInfo.from_dict(res)

    def delete(self, delete_prod=False, delete_pred=True):
        """Permanently delete a model.

        :param delete_prod: Boolean value to delete the production table.
            By default this table is not dropped.
        :param delete_pred: Boolean value to delete the prediction table.
            By default this table is dropped.

        :returns: Server response for deletion action.
        """
        # Type enforcement
        project_id = type_enforce('project_id', self.project_id, str)
        model_id = type_enforce('model_id', self.model_id, str)

        payload = {
            'project_id': project_id,
            'model_id': model_id,
            'delete_prod': delete_prod,
            'delete_pred': delete_pred,
        }

        path = ['delete_model', self.connection.org_id, project_id, model_id]
        try:
            result = self.connection.call(path, json_payload=payload)
        except Exception:
            # retry on error
            result = self.connection.call(path, json_payload=payload)

        self._delete_artifacts()

        # wait for ES to come back healthy
        for i in range(3):
            try:
                self.connection.call_executor_service(
                    ['deploy', self.connection.org_id], is_get_request=True
                )
                break
            except Exception:
                pass

        return result

    def _delete_artifacts(self):
        """Permanently delete a model artifacts.

        :param project_id: The unique identifier of the model's project on the
            Fiddler engine.
        :param model_id: The unique identifier of the model in the specified
            project on the Fiddler engine.

        :returns: Server response for deletion action.
        """
        # delete from executor service cache
        # Type enforcement
        project_id = type_enforce('project_id', self.project_id, str)
        model_id = type_enforce('model_id', self.model_id, str)

        path = ['delete_model_artifacts', self.connection.org_id, project_id, model_id]
        result = self.connection.call_executor_service(path)

        return result

    def predict(
        self,
        df: pd.DataFrame,
        log_events=False,
        casting_type=False,
    ) -> pd.DataFrame:
        """Executes a model in the Fiddler engine on a DataFrame.

        :param df: A dataframe contining model inputs as rows.
        :param log_events: Variable determining if the the predictions
            generated should be logged as production traffic
        :param casting_type: Bool indicating if fiddler should try to cast the data in the event with
        the type referenced in model info. Default to False.

        :returns: A pandas DataFrame containing the outputs of the model.
        """
        # Type enforcement
        project_id = type_enforce('project_id', self.project_id, str)
        model_id = type_enforce('model_id', self.model_id, str)

        if casting_type:
            try:
                model_info = self.get_info()
            except RuntimeError:
                raise RuntimeError(
                    f'Did not find ModelInfo for project "{project_id}" and model "{model_id}".'
                )
            df = cast_input_data(df, model_info)

        data_array = df_to_dict(df)
        payload = dict(
            project_id=project_id,
            model_id=model_id,
            data=data_array,
            logging=log_events,
        )

        payload.pop('project_id')
        payload.pop('model_id')

        path = ['execute', self.connection.org_id, project_id, model_id]
        res = self.connection.call_executor_service(path, json_payload=payload)
        return pd.DataFrame(res)

    def explanation(
        self,
        df: pd.DataFrame,
        explanations: Union[str, Iterable[str]] = 'shap',
        dataset_id: Optional[str] = None,
        n_permutation: Optional[int] = None,
        n_background: Optional[int] = None,
        casting_type: Optional[bool] = False,
        return_raw_response=False,
    ) -> Union[
        AttributionExplanation,
        MulticlassAttributionExplanation,
        List[AttributionExplanation],
        List[MulticlassAttributionExplanation],
    ]:
        """Executes a model in the Fiddler engine on a DataFrame.

        :param df: A dataframe containing model inputs as rows. Only the first
            row will be explained.
        :param explanations: A single string or list of strings specifying
            which explanation algorithms to run.
        :param dataset_id: The unique identifier of the dataset in the
            Fiddler engine. Required for most tabular explanations, but
            optional for most text explanations.
        :param n_permutation: Number of permutations used for Fiddler SHAP. Can be used for both tabular and text data.
            By default (None), we use max(500, 2 * n_features), where n_feature is the number of word tokens
            for text input data.
        :param n_background: Number of background observations used for Fiddler SHAP for tabular data.
            By default (None), we use min(dataset.shape[0], 200)
        :param casting_type: Bool indicating if fiddler should try to cast the data in the event with
        the type referenced in model info. Default to False.

        :returns: A single AttributionExplanation if `explanations` was a
            single string, or a list of AttributionExplanation objects if
            a list of explanations was requested.
        """
        # Type enforcement
        project_id = type_enforce('project_id', self.project_id, str)
        model_id = type_enforce('model_id', self.model_id, str)

        if casting_type:
            try:
                model_info = self.get_info()
            except RuntimeError:
                raise RuntimeError(
                    f'Did not find ModelInfo for project "{project_id}" and model "{model_id}".'
                )
            df = cast_input_data(df, model_info)

        # Explains a model's prediction on a single instance
        # wrap single explanation name in a list for the API
        if isinstance(explanations, str):
            explanations = (explanations,)

        data_array = df_to_dict(df)
        payload = dict(
            project_id=project_id,
            model_id=model_id,
            data=data_array[0],
            explanations=[dict(explanation=ex) for ex in explanations],
            n_permutation=n_permutation,
            n_background=n_background
        )
        if dataset_id is not None:
            payload['dataset'] = dataset_id

        payload.pop('project_id')
        payload.pop('model_id')

        path = ['explain', self.connection.org_id, project_id, model_id]
        res = self.connection.call_executor_service(path, json_payload=payload)

        explanations_list = res['explanations']

        if return_raw_response:
            return explanations_list

        # TODO: enable more robust check for multiclass explanations
        is_multiclass = ['explanation' not in x for x in explanations_list]
        deserialize_fn_list = [
            MulticlassAttributionExplanation.from_dict
            if x
            else AttributionExplanation.from_dict
            for x in is_multiclass
        ]

        ex_objs = [
            deserialize_fn(explanations_list[i])
            for i, deserialize_fn in enumerate(deserialize_fn_list)
        ]
        if len(ex_objs) == 1:
            return ex_objs[0]
        else:
            return ex_objs

    def feature_importance(
        self,
        dataset_id: str,
        dataset_splits: Optional[List[str]] = None,
        slice_query: Optional[str] = None,
        impact_not_importance: Optional[bool] = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """Get global feature importance for a model over a dataset.

        :param dataset_id: The unique identifier of the dataset in the
            Fiddler engine.
        :param dataset_splits: If specified, importance will only be computed
            over these splits. Otherwise, all splits will be used. Only a
            single split is currently supported.
        :param slice_query: A special SQL query.
        :param impact_not_importance: Boolean flag to compute either impact or importance.
        False by default (compute feature importance).
        For text models, only feature impact is implemented.
        :param kwargs: Additional parameters to be passed to the importance
            algorithm. For example, `n_inputs`, `n_iterations`, `n_references`,
            `ci_confidence_level`.
        :return: A named tuple with the explanation results.
        """
        # Type enforcement
        project_id = type_enforce('project_id', self.project_id, str)
        model_id = type_enforce('model_id', self.model_id, str)
        dataset_id = type_enforce('dataset_id', dataset_id, str)

        if (
            dataset_splits is not None
            and len(dataset_splits) > 1
            and not isinstance(dataset_splits, str)
        ):
            raise NotImplementedError(
                'Unfortunately, only a single split is '
                'currently supported for feature '
                'importances.'
            )

        source = (
            None
            if dataset_splits is None
            else dataset_splits
            if isinstance(dataset_splits, str)
            else dataset_splits[0]
        )

        payload = dict(
            subject='feature_importance',
            project_id=project_id,
            model_id=model_id,
            dataset_id=dataset_id,
            source=source,
            slice_query=slice_query,
            impact_not_importance=impact_not_importance,
        )
        payload.update(kwargs)

        payload.pop('subject')
        payload.pop('project_id')
        payload.pop('model_id')
        payload['dataset'] = payload.pop('dataset_id')

        path = ['feature_importance', self.connection.org_id, project_id, model_id]
        res = self.connection.call(path, json_payload=payload)
        # wrap results into named tuple
        res = namedtuple('FeatureImportanceResults', res)(**res)
        return res

    def fairness(
        self,
        dataset_id: str,
        protected_features: list,
        positive_outcome: Union[str, int],
        slice_query: Optional[str] = None,
        score_threshold: Optional[float] = 0.5,
    ) -> Dict[str, Any]:
        """Get fairness metrics for a model over a dataset.

        :param dataset_id: The unique identifier of the dataset in the
            Fiddler engine.
        :param protected_features: List of protected features
        :param positive_outcome: Name or value of the positive outcome
        :param slice_query: If specified, slice the data.
        :param score_threshold: positive score threshold applied to get outcomes
        :return: A dictionary with the fairness metrics, technical_metrics,
        labels distribution and model outcomes distribution
        """
        # Type enforcement
        project_id = type_enforce('project_id', self.project_id, str)
        model_id = type_enforce('model_id', self.model_id, str)
        dataset_id = type_enforce('dataset_id', dataset_id, str)

        if isinstance(protected_features, str):
            protected_features = [protected_features]

        payload = dict(
            subject='fairness',
            project_id=project_id,
            model_id=model_id,
            dataset_id=dataset_id,
            protected_features=protected_features,
            slice_query=slice_query,
            score_threshold=score_threshold,
            positive_outcome=positive_outcome,
        )

        payload.pop('subject')
        payload.pop('project_id')
        payload.pop('model_id')

        path = ['fairness', self.connection.org_id, project_id, model_id]
        res = self.connection.call(path, json_payload=payload)
        return res

    def download(self, output_dir: Path):
        """
        download the model binary, package.py and model.yaml to the given
        output dir.

        :param output_dir: output directory
        :return: model artifacts
        """
        # Type enforcement
        project_id = type_enforce('project_id', self.project_id, str)
        model_id = type_enforce('model_id', self.model_id, str)
        output_dir = type_enforce('output_dir', output_dir, Path)

        if output_dir.exists():
            raise ValueError(f'output dir already exists {output_dir}')

        headers = dict()
        headers.update(self.connection.auth_header)

        _, tfile = tempfile.mkstemp('.tar.gz')
        url = f'{self.connection.url}/get_model/{self.connection.org_id}/{project_id}/{model_id}'

        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()
            with open(tfile, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    # if chunk:
                    f.write(chunk)

        tar = tarfile.open(tfile)
        output_dir.mkdir(parents=True)
        tar.extractall(path=output_dir)
        tar.close()
        os.remove(tfile)
        return True

    def _trigger_model_predictions(self, dataset_id: str):
        """Makes the Fiddler service compute and cache model predictions on a
        dataset."""
        # Type enforcement
        project_id = type_enforce('project_id', self.project_id, str)
        model_id = type_enforce('model_id', self.model_id, str)
        dataset_id = type_enforce('dataset_id', dataset_id, str)

        return self.connection.call_executor_service(
            ['dataset_predictions', self.connection.org_id, project_id],
            dict(model=model_id, dataset=dataset_id),
        )
