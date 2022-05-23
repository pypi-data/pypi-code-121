import numpy as np
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split

from kolibri.task.tabular.anomaly.unsupervised_anomaly_dector import UnsupervisedAnomalyDetector
from kolibri.backend.models import get_model

ANOMALY_MODEL_FILE_NAME = "anomaly_model"


class SemiSupervisedAnomalyDetector(UnsupervisedAnomalyDetector):
    name = 'one_class_anomaly_detector'

    def __init__(self, normal_class, component_config=None, model=None, classifier='linearsvm', normalize_data=True):
        super().__init__(component_config, model, normalize_data)
        self.normal_class = normal_class
        self.classifier = get_model(classifier)

    @classmethod
    def required_packages(cls):
        return ["tensorflow"]

    def fit(self, X, y=None, X_val=None, y_val=None, test_size=None):
        if y is None:
            raise Exception('label tensor "y" cannot be null')
        X_norm = X[y == self.normal_class]
        X_anomaly = X[y != self.normal_class]

        super().fit(X_norm)
        if self.normalize_data:
            X_anomaly = self.normalizer.transform(X_anomaly)
            X_norm = self.normalizer.transform(X_norm)
        nb_normal_to_select = len(X_anomaly) * 18
        if nb_normal_to_select > len(X_norm):
            nb_normal_to_select = len(X_norm)

        X_latent_normal = self.model.encoder.predict(X_norm[:nb_normal_to_select])
        X_latent_anomaly = self.model.encoder.predict(X_anomaly)

        X_latent = np.append(X_latent_normal, X_latent_anomaly, axis=0)
        y_n = np.zeros(X_latent_normal.shape[0])
        y_f = np.ones(X_latent_anomaly.shape[0])
        y_recoded = np.append(y_n, y_f)

        self.classifier.fit(X_latent, y_recoded)

        if X_val is not None and y_val is not None:
            if self.normalize_data:
                X_val = self.normalizer.transform(X_val)
            X_val_latent_normal = self.model.encoder.predict(X_val[y_val == self.normal_class])
            X_val_latent_anomaly = self.model.encoder.predict(X_val[y_val != self.normal_class])

            X_val_latent = np.append(X_val_latent_normal, X_val_latent_anomaly, axis=0)
            y_n = np.zeros(X_val_latent_normal.shape[0])
            y_f = np.ones(X_val_latent_anomaly.shape[0])
            y_recoded = np.append(y_n, y_f)
            y_predicted = self.classifier.predict(X_val_latent)
            print(classification_report(y_recoded, y_predicted))

        elif test_size is not None:
            norm_hid_rep = self.model.encoder.predict(X_norm[:10000])
            fraud_hid_rep = self.model.encoder.predict(X_anomaly)
            rep_x = np.append(norm_hid_rep, fraud_hid_rep, axis=0)
            y_n = np.zeros(norm_hid_rep.shape[0])
            y_f = np.ones(fraud_hid_rep.shape[0])
            rep_y = np.append(y_n, y_f)
            train_x, val_x, train_y, val_y = train_test_split(rep_x, rep_y, test_size=0.25)
            self.classifier.fit(train_x, train_y)
            pred_y = self.classifier.predict(val_x)

            print("")
            print("Classification Report: ")
            print(classification_report(val_y, pred_y))

            print("")
            print("Accuracy Score: ", accuracy_score(val_y, pred_y))
