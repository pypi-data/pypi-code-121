import os, time
import numpy as np
import warnings
from kolibri.backend.base.estimator import BaseEstimator
from kolibri.backend.models import get_model
from kolibri.evaluators.clustering_evaluator import ClusteringEvaluator
from kolibri.logger import get_logger
import pandas as pd
from kolibri.config import TaskType
from kdmt.dict import update


logger = get_logger(__name__)
warnings.filterwarnings("ignore")
MODEL_FILE_NAME="clustering_model.pkl"

class ClusteringEstimator(BaseEstimator):

    defaults={
        "fixed":{
            "log_plot": False,
            "n_clusters": 4,
            "round": 4,
            "verbose": False,
            "ground-truth":None,
            "model": None,
            "seed": 42,
            'task-type': TaskType.CLUSTERING
        },
        "model": {

            }
    }
    def __init__(self, configs={}):
        super().__init__(configs)
        self.hyperparameters["tunable"]["model"]=get_model(self.get_parameter("model"), task_type=self.get_parameter("task-type"))
        self.update_model_parameters()
        self.model=self.load_model_from_parameters(self.get_parameter("model"))[1]

        self.evaluator=ClusteringEvaluator()
    def reload_model(self, new_config=None):
        if new_config is not None:
            for c in new_config:
                if c in self.hyperparameters["tunable"]["model"]["parameters"]:
                    self.hyperparameters["tunable"]["model"]["parameters"][c]["value"]= new_config[c]

        self.model=self.load_model_from_parameters(get_model(self.get_parameter("model"), task_type=self.get_parameter("task-type")))[1]

    def fit( self, X: None, y=None, **kwargs):


            logger.info("Start model estimation")

            # general dependencies
            seed=self.get_parameter("random_state")
            np.random.seed(seed)

            logger.info("Fitting Model")
            model_fit_start = time.time()
            self.model.fit(X)
            model_fit_end = time.time()

            model_fit_time = np.array(model_fit_end - model_fit_start).round(2)

            print("fit time: ", model_fit_time)

            if y is not None:
                gt = y
            else:
                gt = None


            metrics = self.evaluator.calculate_unsupervised_metrics(X, self.model.labels_, ground_truth=gt)


            logger.info(str(self.model))
            logger.info(
                "create_models() succesfully completed......................................"
            )

            logger.info("Uploading results into container")

            self.model_results = pd.DataFrame(metrics, index=[0])
            self.model_results =self.model_results.round(self.get_parameter("round"))

            return self.model

    def predict(self, X=None):

        logger.info("Initializing predict()")

            # calculation labels and attaching to dataframe

        outputs=[]
        if self.get_parameter("task-type") == TaskType.CLUSTERING:
            labels = [f"Cluster {i}" for i in self.model.labels_]
            outputs= labels
        elif self.get_parameter("task-type") == TaskType.ANOMALY_DETECTION:
            anomalies = self.model.predict(X)
            scores = self.model.decision_scores_
            outputs=[{anomalies[i]:scores[i]} for i in range(len(anomalies))]

        logger.info(
            "assign_model() succesfully completed......................................"
        )

        return outputs

    def persist(self, model_dir):
        """Persist this model_type into the passed directory."""

        classifier_file = os.path.join(model_dir, MODEL_FILE_NAME)
        import joblib

        joblib.dump(self, classifier_file)

        return {"model_file": MODEL_FILE_NAME}

    @classmethod
    def load(cls,
             model_dir=None,
             model_metadata=None,
             cached_component=None,
             **kwargs
             ):

        file_name = model_metadata.get("model_file", MODEL_FILE_NAME)
        classifier_file = os.path.join(model_dir, file_name)
        import joblib
        if os.path.exists(classifier_file):
            model = joblib.load(classifier_file)

            return model
        else:
            return cls(model_metadata)

from kolibri.registry import ModulesRegistry
ModulesRegistry.add_module(ClusteringEstimator.name, ClusteringEstimator)
