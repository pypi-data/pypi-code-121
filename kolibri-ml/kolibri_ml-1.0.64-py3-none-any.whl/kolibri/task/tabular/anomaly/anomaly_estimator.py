

from kolibri.logger import get_logger
import time
import numpy as np
from kolibri.config import TaskType
from kolibri.task.tabular.clustering.clustering import ClusteringEstimator
from kolibri.backend.models import get_model
_DEFAULT_N_ANOMALYS = 4

logger=get_logger(__name__)
MODEL_FILE_NAME="anomaly_model.pkl"
class UnsupervisedAnomalyEstimator(ClusteringEstimator):
    """
    Base anomaly model estimator class. Ensures consistent format across the various algorithms.
    """
    defaults = {
        "fixed":{
            "task-type":TaskType.ANOMALY_DETECTION
        },
        "tunable":{
            "outliers_ratio":{"value":0.05}
        }
    }
    def __init__(self, params):
        super().__init__(params)
        self.update_model_parameters()


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

            logger.info(str(self.model))
            logger.info(
                "create_models() succesfully completed......................................"
            )


            return self.model


