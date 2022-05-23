import uuid, os
import numpy as np
from kolibri.core.component import Component
from kolibri.indexers.label_indexer import LabelIndexer
from kdmt.ml.common import sklearn_numpy_warning_fix
from kolibri.evaluators.classifier_evaluator import ClassifierEvaluator
from kolibri.explainers.shap_explainer import PlotSHAP
from kolibri.utils.common import construct_learner_name
from kolibri.config import TaskType
from kolibri.utils.common import get_cv_splitter, get_groups
from kolibri.config import ParamType
from kdmt.dict import update
from sklearn.utils.multiclass import type_of_target
from copy import deepcopy
from kdmt.objects import class_from_module_path
from kolibri.logger import get_logger
from kolibri import settings
import gc
import time

logger = get_logger(__name__)

import joblib

KOLIBRI_MODEL_FILE_NAME = "classifier_kolibri.pkl"

class BaseEstimator(Component):
    """
    This is an abstract class.
    All estimators inherit from BaseEstimator.
    The notion of Estimator represents any mathematical model_type that estimate a response function. In machine learning it can represent either
    a supervised or unsupervised classification algorithm.

    Estimators have the following paramters that can be modified using the configuration object.

    Fixed Hyperparameters
    ---------------------
    base-estimator: a defined kolibri or sklearn.BaseEstimator (default=LogisticRegression)
        This is used by kolibri.bakend.meta estimators as a base estimator for each member of the ensemble is an instance of the base estimator

    explain : boolean (default=False)
        used to output an explanation file in the output folder.

    sampler: str (default=None), A sampler such as SMOTE can be used to balance the data in case the dataset is heavily unbalanced.
    see kolibri.samplers for various options that can be used.

    "priors-thresolding":boolean (default=False), a strategy to handle unbalanced dataset, by class prior probability.

    evaluate-performance: boolean (default=False), use this config to generate performance data before training the model_type.

    optimize-estimator: boolean (default=False), use this config to optimise the parameters of the estimtors. the optimisation stategy optimised the tunable parameters.

    Tunable Hyperparameters
    ---------------------

    These hyper parameters are used in optimization strategies to optimize the performances.
    one obvious parameter to optimise is the base model_type used to train the data.

    """

    short_name = "Unknown"

    provides = ["classification", "target_ranking"]

    requires = ["text_features"]

    defaults = {
            "fixed": {
                "target": None,
                "transform-target-method": None,
                "auto-ml": False,
                "base-estimator": None,
                "explain": False,
                "sampler": None,
                "priors-thresolding": False,
                'evaluate-performance': False,
                'task-type': TaskType.CLASSIFICATION,
                'optimize-estimator': False,
                'max-nb-models': 5,
                'resampling-strategy': 'holdout', #'cv'
                'data-split-shuffle': True,
                "data-split-stratify": False,
                'imputer': 'none',
                'fold-shuffle': True,
                "fold": 5,
            },

            "tunable": {
                "model": {
                    "description": "This is just an example of a tuneable variable",
                    "value": "logreg",
                    "type": ParamType.CATEGORICAL,
                }

            }
        }

    def __init__(self, params, classifier=None, indexer=None):
        super().__init__(parameters=params)
        self.params = params
        self.stop_training = False
        self.library_version = None
        self.model = classifier
        self.uid = params.get("uid", str(uuid.uuid4()))
        self.ml_task = None
        self.model_file_path = None
        self.component_type = 'estimator'
        if indexer is not None:
            self.indexer = indexer
        else:
            self.indexer = LabelIndexer(multi_label=False)

        self.validatation_data=None

        sklearn_numpy_warning_fix()
        self.sampler=None
        if self.get_parameter('sampler'):
            from kolibri.samplers import get_sampler
            self.sampler = get_sampler(self.get_parameter('sampler'))

        self.class_priors = None
        self.performace_scores = "Not computed"

        # CV params
        fold_param = self.get_parameter("fold")


        fold_shuffle_param = self.get_parameter("fold-shuffle")

        from sklearn.model_selection import (
            StratifiedKFold,
            KFold,
            GroupKFold,
            TimeSeriesSplit,
        )

        fold_seed = self.get_parameter("random-state") if fold_shuffle_param else None
        if self.get_parameter("fold_strategy") == "kfold":
            self.fold_generator = KFold(
                fold_param, random_state=fold_seed, shuffle=fold_shuffle_param
            )
        elif self.get_parameter("fold_strategy") == "stratifiedkfold":
            self.fold_generator = StratifiedKFold(
                fold_param, random_state=fold_seed, shuffle=fold_shuffle_param
            )
        elif self.get_parameter("fold_strategy") == "groupkfold":
            self.fold_generator = GroupKFold(fold_param)
        elif self.get_parameter("fold_strategy") == "timeseries":
            self.fold_generator = TimeSeriesSplit(fold_param)
        else:
            self.fold_generator = self.get_parameter("fold_strategy")

    def task_type(self):
        return self.get_parameter("task-type")

    def update_default_hyper_parameters(self):
        self.defaults=update( BaseEstimator.defaults, self.defaults,)
        super().update_default_hyper_parameters()

    def load_model_from_parameters(self, model_params):
        model_params=deepcopy(model_params)
        model=class_from_module_path(model_params["class"])
        if model is None:
            raise ValueError('Could not fint '+model_params["class"]+". Please make the name is correct and/or install any missing libraries")

        default_params={p:model_params["parameters"][p]["value"] for p in model_params["parameters"]}
        for param, param_val in default_params.items():
            if isinstance(param_val, list):
                for i, p in enumerate(param_val):
                    if isinstance(p, dict):
                        default_params[param][i]=self.load_model_from_parameters(p)
            elif isinstance(param, dict):
                default_params[param] = self.load_model_from_parameters(param_val)

        return (model_params["name"], model(**default_params))

    def update_model_parameters(self):
        if "fixed" in self.hyperparameters:
            for c in self.hyperparameters["fixed"]:

                if c in self.hyperparameters["tunable"]["model"]["parameters"]:
                    self.hyperparameters["tunable"]["model"]["parameters"][c]["value"]=self.hyperparameters["fixed"][c]

    def set_learner_name(self, fold, repeat, repeats):
        self.lerner_name = construct_learner_name(fold, repeat, repeats)

    def is_fitted(self):
        # base class method
        return False

    def reload(self):
        if not self.is_fitted() and self.model_file_path is not None:
            self.load_model(self.model_file_path)

    def fit(self, X, y, sample_weight=None,
        X_validation=None,
        y_validation=None,
        sample_weight_validation=None,
        log_to_file=None,
        max_time=None,
    ):
        target_type = type_of_target(y)
        supported_types = ['binary', 'multiclass', 'multilabel-indicator']
        if target_type not in supported_types:
            raise ValueError("Classification with data of type {} is "
                             "not supported. Supported types are {}. "
                             "".format(
                                    target_type,
                                    supported_types
                                )
                             )

        if self.get_parameter('optimize-estimator'):
            self.optimize(X, y)
        elif self.get_parameter('evaluate-performance'):
            evaluator=ClassifierEvaluator(estimator=self.model)
            self.performace_scores = evaluator.compute_performance_report(X=X, y=y, labels=list(
                self.indexer.token2idx.keys()))
            self.validatation_data=np.column_stack((self.indexer.inverse_transform(evaluator.predictions[:,0]), evaluator.predictions[:,1]))


    def update(self, update_params):
        pass

    def copy(self):
        pass

    def save(self, model_file_path):
        pass

    def load_model(self, model_file_path):
        pass

    def get_fname(self):
        return f"{self.name}.{self.file_extension()}"

    def explain(
        self,
        X_train,
        y_train,
        X_validation,
        y_validation,
        model_file_path,
        learner_name,
        target_name=None,
        class_names=None,
        ml_task=None,
    ):
        # do not produce feature importance for Baseline
        if self.algorithm_short_name == "Baseline":
            return
        PlotSHAP.compute(
                self,
                X_train,
                y_train,
                X_validation,
                y_validation,
                model_file_path,
                learner_name,
                class_names,
                ml_task,
            )

    def get_metric_name(self):
        return None

    def get_params(self):
        params = {
            "library_version": self.library_version,
            "algorithm_name": self.algorithm_name,
            "algorithm_short_name": self.algorithm_short_name,
            "uid": self.uid,
            "params": self.params,
            "name": self.name,
        }
        if hasattr(self, "best_ntree_limit") and self.best_ntree_limit is not None:
            params["best_ntree_limit"] = self.best_ntree_limit
        return params

    def set_params(self, json_desc, learner_path):
        self.library_version = json_desc.get("library_version", self.library_version)
        self.algorithm_name = json_desc.get("algorithm_name", self.algorithm_name)
        self.algorithm_short_name = json_desc.get(
            "algorithm_short_name", self.algorithm_short_name
        )
        self.uid = json_desc.get("uid", self.uid)
        self.params = json_desc.get("params", self.params)
        self.name = json_desc.get("name", self.name)
        self.model_file_path = learner_path

        if hasattr(self, "best_ntree_limit"):
            self.best_ntree_limit = json_desc.get(
                "best_ntree_limit", self.best_ntree_limit
            )


    @classmethod
    def required_packages(cls):
        return ["sklearn"]

    def evaluate(self, X_val=None, y_val=None):

        if X_val is not None and y_val is not None:
            pred = self.predict(X_val)

            self.performace_scores = ClassifierEvaluator().get_performance_report(y_true=y_val, y_pred=pred)

    def compute_priors(self, y):
        unique, counts = np.unique(y, return_counts=True)
        self.class_priors = dict(zip(unique, counts))

        total = sum(self.class_priors.values(), 0.0)
        self.class_priors = {k: v / total for k, v in self.class_priors.items()}

    def transform(self, document):

        return self.clf.transform(document, )

    def predict_proba(self, X):
        """Given a bow vector of an input text, predict the class label.

        Return probabilities for all y_values.

        :param X: bow of input text
        :return: vector of probabilities containing one entry for each label"""
        raw_predictions=None
        try:
            if self.get_parameter('task-type') == TaskType.BINARY_CLASSIFICATION:
                raw_predictions=self.model.predict_proba(X)[:, 1]
            elif self.get_parameter('task-type') == TaskType.CLASSIFICATION:
                raw_predictions=self.model.predict_proba(X)
        except:
            raise Exception('Predict_proba raised an error in Estimator')


        if self.get_parameter("priors-thresolding"):
            if not raw_predictions is None:
                try:
                    priors = np.array([v for v in self.class_priors.values()])
                    raw_predictions = (raw_predictions.T - priors[:, None]) / priors[:, None]
                    raw_predictions = np.argmax(raw_predictions.T, axis=1)
                except Exception as e:
                    print(e)

        # sort the probabilities retrieving the indices of
        # the elements in sorted order
        sorted_indices = np.fliplr(np.argsort(raw_predictions, axis=1))

        return raw_predictions, sorted_indices, [p[sorted_indices[i]] for i, p in enumerate(raw_predictions)]

    def predict(self, X):
        """Given a bow vector of an input text, predict most probable label.

        Return only the most likely label.

        :param X: bow of input text
        :return: tuple of first, the most probable label and second,
                 its probability."""
        probabilities=[]
        try:
            raw_predictions, class_ids, probabilities=self.predict_proba(X)
        except:
            class_ids=self.model.predict(X)

        classes = [self.indexer.inverse_transform(np.ravel(class_id)) for class_id in class_ids]

        return self.process([list(zip(classe, probability)) for classe, probability in zip(classes, probabilities)])


    def process(self, results):

        if results is not None:
            ranking= [result[:settings.TARGET_RANKING_LENGTH] for result in results]

            target = [{"name": result[0][0], "confidence": result[0][1]} for result in results]

            target_ranking = [[{"name":r[0], "confidence":r[1]} for r in rank] for rank in ranking]
        else:
            target = {"name": None, "confidence": 0.0}
            target_ranking = []


        response={
            "label": target,
            "ranking": target_ranking
        }
        return response

    @classmethod
    def load(cls, model_dir=None, model_metadata=None, cached_component=None, **kwargs):

        file_name = model_metadata.get("classifier_file", KOLIBRI_MODEL_FILE_NAME)
        classifier_file = os.path.join(model_dir, file_name)

        if os.path.exists(classifier_file):
            model = joblib.load(classifier_file)
            return model
        else:
            return cls(model_metadata)

    def persist(self, model_dir):
        """Persist this model_type into the passed directory."""

        classifier_file = os.path.join(model_dir, KOLIBRI_MODEL_FILE_NAME)
        joblib.dump(self, classifier_file)

        return {
            "classifier_file": KOLIBRI_MODEL_FILE_NAME,
            "performace_scores": self.performace_scores,
        }

