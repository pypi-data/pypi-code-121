import copy
import joblib
from tqdm import tqdm
import kolibri.backend.models
from kolibri.config import ModelConfig
from kolibri.backend.base.estimator import BaseEstimator
from kolibri.backend.models import get_classification_model
from kdmt.dict import update
from kolibri.optimizers.optuna.objective import EstimatorObjective
from copy import deepcopy
from kolibri.logger import get_logger
from kdmt.objects import class_from_module_path
from kolibri.evaluators.classifier_evaluator import ClassifierEvaluator
import pandas as pd
from tabulate import tabulate

logger = get_logger(__name__)

class ZooEstimator(BaseEstimator):

    defaults =  {"fixed": {
            "default-params": None,
            "classifiers": "all",
            "fast-models-only": False
        },

        "tunable": {
        }
    }
    def __init__(self, hyperparameters=None, classifier=None, indexer=None):
        """Construct a new class classifier using the sklearn framework."""

        super(ZooEstimator, self).__init__(params=hyperparameters, classifier=classifier, indexer=indexer)
        all_classifiers = kolibri.backend.models.sklearn_classification_models_names

        selected_models=all_classifiers
        if isinstance(self.get_parameter("classifiers", []), list):
            selected_models=self.get_parameter("classifiers", [])

        self.models=[]
        for model_name in selected_models:
            model=self.load_model_from_parameters(get_classification_model(model_name))
            print(model_name)
            if model is not None:
                if self.get_parameter("fast-models-only") and model[0]["performance"] !="fast":
                    continue
                print("adding: ", model_name)
                self.models.append((model[0],model[1]))

        self.X_sampled=None
        self.y_sampled=None

        self._dask_client=None

    def update_default_hyper_parameters(self):
        self.defaults=update(self.defaults, ZooEstimator.defaults)
        super().update_default_hyper_parameters()

    def load_model_from_parameters(self, model_params):
        model_params=deepcopy(model_params)
        model=class_from_module_path(model_params["class"])
        if model is None:
            return None
        default_params={p:model_params["parameters"][p]["value"] for p in model_params["parameters"]}
        for param, param_val in default_params.items():
            if isinstance(param_val, list):
                for i, p in enumerate(param_val):
                    if isinstance(p, dict):
                        default_params[param][i]=self.load_model_from_parameters(p)
            elif isinstance(param, dict):
                default_params[param] = self.load_model_from_parameters(param_val)

        return (model_params, model(**default_params))

    def fit(
        self,
        X,
        y,
        sample_weight=None,
        X_validation=None,
        y_validation=None,
        sample_weight_validation=None,
        log_to_file=None,
        max_time=None,
    ):

        self.indexer.build_vocab(None, y)
        y = self.indexer.transform(y)


        if self.get_parameter('priors-thresolding'):
            self.compute_priors(y)

        X_sampled=X
        y_sampled=y
        if self.sampler and self.X_sampled is not None and self.y_sampled is not None:
            print('sampling data. Original data size: ', len(y))
            X_sampled, y_sampled = self.sampler.fit_resample(X, y)
            print('finished sampling. Sampled data size: ', len(y_sampled))
        names=[]
        self.performace_scores=[]
        pd_report_scores=[]
        for params, model in tqdm(self.models):
            print('fitting: '+params["name"])
            if self.get_parameter('optimize-estimator'):
                self.optimize(X_sampled, y_sampled)
#            elif self.get_parameter('evaluate-performance'):
            evaluator = ClassifierEvaluator(estimator=model)
            if params["matrix"]=="sparse":
                 performace_score=evaluator.compute_performance_report(X=X, y=y, labels=list(
                        self.indexer.token2idx.keys()))
            else:
                performace_score=evaluator.compute_performance_report(X=X.toarray(), y=y, labels=list(
                        self.indexer.token2idx.keys()))
            performace_score["classif_name"]=params["name"]
            names.append(params["name"])
            self.performace_scores.append(performace_score)
            performace_score_pd=deepcopy(performace_score)
            del performace_score_pd["confusion_matrix"]
            del performace_score_pd["class_report"]
            pd_report_scores.append(performace_score_pd)
        scores = pd.DataFrame(pd_report_scores)
        scores = scores.sort_values(by="accuracy_score", ascending=False).set_index(
            "classif_name"
        )
        print(tabulate(scores, headers='keys', tablefmt='psql'))

    def copy(self):
        return copy.deepcopy(self)

    def save(self, model_file_path):
        logger.debug("SklearnAlgorithm save to {0}".format(model_file_path))
        joblib.dump(self.model, model_file_path, compress=True)
        self.model_file_path = model_file_path

    def load_model(self, model_file_path):
        logger.debug("SklearnAlgorithm loading model from {0}".format(model_file_path))
        self.model = joblib.load(model_file_path)
        self.model_file_path = model_file_path

    def is_fitted(self):
        return (
            hasattr(self.model, "n_features_")
            and self.model.n_features_ is not None
            and self.model.n_features_ > 0
        )

    def objective(self, X, y):
        objective=EstimatorObjective(X, y, self, None, eval_metric=self.get_parameter('opt-metric-name'),n_jobs=-1, random_state=42)
        return objective



from kolibri.registry import ModulesRegistry
ModulesRegistry.add_module(ZooEstimator.name, ZooEstimator)
