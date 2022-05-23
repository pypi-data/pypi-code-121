try:
    import matplotlib.pyplot as plt
    has_matplotlib=True
except:
    has_matplotlib=False

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, recall_score, jaccard_score, balanced_accuracy_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, LeaveOneOut
from sklearn.model_selection import learning_curve as sk_learning_curve
from kdmt.ml.metrics import classification
from kdmt.ml.metrics import plot
from kdmt.properties import requires_properties
from kdmt.objects import class_name
from sklearn import model_selection

class ClassifierEvaluator(object):
    """
    Encapsuates results from an estimator on a testing set to provide a
    simplified API from other modules. All parameters are optional, just
    fill the ones you need for your analysis.
    """
    TEMPLATE_NAME = 'classifier.md'

    def __init__(self, estimator=None, learning_curve=False):
        self._estimator = estimator
        self._y_true = None
        self._target_names = None
        self._X = None
        self.compute_learning_curve = learning_curve
        self.compute_proba = True

    @property
    def estimator_class(self):
        """Estimator class (e.g. sklearn.ensemble.RandomForestClassifier)
        """
        return class_name(self.estimator)

    @property
    def estimator(self):
        return self._estimator

    @property
    def X(self):
        return self._X

    @property
    def y_true(self):
        return self._y_true

    @property
    def y_pred(self):
        if self.compute_proba:
            return np.argmax(self._y_pred, axis=-1)
        return self._y_pred

    @property
    def predictions(self):
        if self.compute_proba:
            return np.column_stack((self.y_pred, np.max(self._y_pred, axis=-1)))
        return self._y_pred

    @property
    def y_score(self):
        return self._y_pred

    @property
    def target_names(self):
        return self._target_names

    @requires_properties(('y_true', 'y_pred'))
    def confusion_matrix_plot(self):
        """Confusion matrix plot
        """
        return plot.confusion_matrix(self.y_true, self.y_pred,
                                     self.target_names, ax=_gen_ax())
    @staticmethod
    def confusion_matrix(y_true, y_pred, target_names=None):

        if y_true is not None and y_pred is not None:
            if target_names is None:
                target_names = set(y_true)
            cm = pd.DataFrame( classification.confusion_matrix(y_true, y_pred, target_names))

        cm.columns = list(target_names)
        cm.index = list(target_names)
        return cm

    def _confusion_matrix(self, y_true=None, y_pred=None, target_names=None):

        if y_true is not None and y_pred is not None:
            if target_names is None:
                target_names = set(y_true)
            cm = pd.DataFrame(classification.confusion_matrix(y_true, y_pred, target_names))
        else:
            target_names = self.target_names
            cm = pd.DataFrame(classification.confusion_matrix(self._y_true, self.y_pred, self.target_names))

        cm.columns = list(target_names)
        cm.index = list(target_names)
        return cm
    @requires_properties(('y_true', 'y_score'))
    def roc(self):
        """ROC plot
        """
        return plot.roc(self.y_true, self.y_score, ax=_gen_ax())

    @requires_properties(('y_true', 'y_score'))
    def precision_recall(self):
        """Precision-recall plot
        """
        return plot.precision_recall(self.y_true, self.y_score, ax=_gen_ax())

    @requires_properties(('estimator',))
    def feature_importances(self):
        """Feature importances plot
        """
        return plot.feature_importances(self.estimator,
                                        feature_names=self.feature_names,
                                        ax=_gen_ax())

    @requires_properties(('estimator',))
    def feature_importances_table(self):
        """Feature importances table
        """
        from kdmt.ml.importance import feature_importances

        return feature_importances(self.estimator,
                                         feature_names=self.feature_names)

    @requires_properties(('y_true', 'y_score'))
    def precision_at_proportions(self):
        """Precision at proportions plot
        """
        return plot.precision_at_proportions(self.y_true, self.y_score,
                                             ax=_gen_ax())

    def cross_validate_predict(self, classifier, X, y, folds=4, ratio_to_use=1, n_jobs=4):

        n_jobs = min(folds, n_jobs)
        n = len(y)
        if ratio_to_use < 1:
            indices = np.random.choice(range(n), int(n * ratio_to_use))
            X = X[indices]
            y = y[indices]
        # Get cross-validation folds
        cv = LeaveOneOut() if (folds == 0) else StratifiedKFold(n_splits=folds)
        try:
            pred = model_selection.cross_val_predict(classifier, X, y, cv=cv, n_jobs=n_jobs, method='predict_proba', verbose=1)
            return pred
        except Exception as e:
            self.compute_proba = False
            return model_selection.cross_val_predict(classifier, X, y, cv=cv, n_jobs=-1, verbose=1)
    @staticmethod
    def classification_report(y_true, y_pred, target_names):
        if y_true is not None and y_pred is not None:
            return classification.classification_report(y_true, y_pred, target_names)
        return None

    def compute_performance_report(self,X=None, y=None, labels=None, folds=4, ratio_to_use=1, n_jobs=4):

        self._y_true = y
        if labels is not None:
            self._target_names = labels
        elif y is not None:
            self._target_names = set(y)
        self._X = X

        if X is not None and y is not None:
            if self.compute_learning_curve:
                train_sizes = np.linspace(.1, 1.0, 5)
                self.train_sizes, self.train_scores, self.test_scores = sk_learning_curve(self.estimator, X, y, cv=folds,
                                                                                          n_jobs=n_jobs,
                                                                                          train_sizes=train_sizes)
            self._y_pred = self.cross_validate_predict(self.estimator, X, y, folds=folds, ratio_to_use=ratio_to_use,
                                                       n_jobs=n_jobs)

            return self.get_performance_report(self.y_true, self.y_pred, self.target_names)

    @staticmethod
    def get_performance_report(y_true=None, y_pred=None, target_names=None):
        report = {}
        report['confusion_matrix'] = ClassifierEvaluator.confusion_matrix(list(y_true), list(y_pred), target_names).to_dict()
        cr = ClassifierEvaluator.classification_report(list(y_true), list(y_pred), target_names)
        report['class_report'] = cr

        report['f1_score_micro'] = f1_score(y_true, y_pred, average='micro',zero_division=0)
        report['f1_score_macro'] = f1_score(y_true, y_pred, average='macro',zero_division=0)
        report['f1_score_weighted'] = f1_score(y_true, y_pred,  average='weighted',zero_division=0)
        report['recall_score_micro'] = recall_score(y_true=y_true, y_pred=y_pred, average='micro',zero_division=0)
        report['recall_score_macro'] = recall_score(y_true=y_true, y_pred=y_pred, average='macro',zero_division=0)
        report['recall_score_weighted'] = recall_score(y_true=y_true, y_pred=y_pred,
                                                       average='weighted',zero_division=0)
        report['jaccard_score_micro'] = jaccard_score(y_true=y_true, y_pred=y_pred,
                                                      average='micro',zero_division=0)
        report['jaccard_score_macro'] = jaccard_score(y_true=y_true, y_pred=y_pred,
                                                      average='macro',zero_division=0)
        report['jaccard_score_weighted'] = jaccard_score(y_true=y_true, y_pred=y_pred,
                                                         average='weighted',zero_division=0)
        report['balanced_accuracy_score'] = balanced_accuracy_score(y_true=y_true, y_pred=y_pred)
        report['adjusted_balanced_accuracy_score'] = balanced_accuracy_score(y_true=y_true, y_pred=y_pred,
                                                                             adjusted=True)
        report['accuracy_score'] = accuracy_score(y_true=y_true, y_pred=y_pred)
#        report['roc_auc']=roc_auc_score(y_true=y_true, y_score=y_pred)

        return report


def _gen_ax():

    if not has_matplotlib:
        raise Exception('Cannot plot figures. Please install matplotlib library')
    fig = plt.figure()
    ax = fig.add_subplot(111)
    return ax
