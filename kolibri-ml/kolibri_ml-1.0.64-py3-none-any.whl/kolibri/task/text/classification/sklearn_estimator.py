import copy

import joblib
from kolibri.backend.models import get_classification_model
from kolibri.backend.base.estimator import BaseEstimator
from kdmt.dict import update
from kolibri.optimizers.optuna.objective import EstimatorObjective
from kolibri.logger import get_logger
logger = get_logger(__name__)

class SklearnEstimator(BaseEstimator):

    defaults =  {"fixed": {
            "default-params": None
        },

        "tunable": {
        }
    }
    def __init__(self, hyperparameters=None, classifier=None, indexer=None):
        """Construct a new class classifier using the sklearn framework."""

        super(SklearnEstimator, self).__init__(params=hyperparameters, classifier=classifier, indexer=indexer)
        self.hyperparameters["tunable"]["model"] = get_classification_model(hyperparameters["model"])
        self.update_model_parameters()
        self.model=self.load_model_from_parameters(self.get_parameter("model"))[1]
        self.X_sampled=None
        self.y_sampled=None

        self._dask_client=None

    def update_default_hyper_parameters(self):
        self.defaults=update(self.defaults, SklearnEstimator.defaults)
        super().update_default_hyper_parameters()



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

        if self.sampler and self.X_sampled is not None and self.y_sampled is not None:
            print('sampling data. Original data size: ', len(y))
            self.X_sampled, self.y_sampled = self.sampler.fit_resample(X, y)
            print('finished sampling. Sampled data size: ', len(self.y_sampled))
        if self.X_sampled is not None and self.y_sampled is not None:
            super(SklearnEstimator, self).fit(self.X_sampled, self.y_sampled)
            self.model.fit(self.X_sampled, self.y_sampled)
        else:
            super(SklearnEstimator, self).fit(X, y)
            self.model.fit(X, y)

        if not self.get_parameter('evaluate-performance') and X_validation is not None and y_validation is not None:
            self.evaluate(X_validation, y_validation)

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
ModulesRegistry.add_module(SklearnEstimator.name, SklearnEstimator)
