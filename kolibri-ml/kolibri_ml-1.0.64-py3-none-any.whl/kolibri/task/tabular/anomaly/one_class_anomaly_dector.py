from kolibri.task.tabular.anomaly.unsupervised_anomaly_dector import UnsupervisedAnomalyDetector

ANOMALY_MODEL_FILE_NAME = "anomaly_model"


class OneClassAnomalyDetector(UnsupervisedAnomalyDetector):
    name = 'one_class_anomaly_detector'

    def __init__(self, normal_class, component_config=None, model=None, normalize_data=True):
        super().__init__(component_config, model, normalize_data)
        self.normal_class = normal_class

    @classmethod
    def required_packages(cls):
        return ["tensorflow"]

    def fit(self, X, y=None, X_val=None, y_val=None):
        if y is None:
            raise Exception('label tensor "y" cannot be null')
        X = X[y == self.normal_class]
        super().fit(X, y, X_val, y_val)
