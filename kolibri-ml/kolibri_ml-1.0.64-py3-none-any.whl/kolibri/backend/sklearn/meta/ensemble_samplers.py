import collections

import numpy as np

from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from scipy.sparse import issparse
from scipy.sparse import vstack
from sklearn.base import clone
from sklearn.base import is_regressor
from sklearn.ensemble import AdaBoostClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, recall_score
from sklearn.preprocessing import normalize
from sklearn.utils import check_X_y
from sklearn.utils import check_array
from sklearn.utils import check_random_state
from sklearn.utils import resample
from sklearn.metrics import average_precision_score
from kolibri.backend.sklearn.models import get_model
from kolibri.indexers.label_indexer import LabelIndexer
from kolibri.backend.base.estimator import BaseEstimator


class FinalMeta(type(AdaBoostClassifier), type(BaseEstimator)):
    pass


class SMOTEBoost(AdaBoostClassifier, BaseEstimator, metaclass=FinalMeta):
    name = 'smote_boost_classifier'

    """Implementation of SMOTEBoost.
    SMOTEBoost introduces texts sampling into the AdaBoost algorithm by
    oversampling the minority class using SMOTE on each boosting iteration.  
    """

    def __init__(self,
                 BaseEstimator_config=None,
                 new_samples=100,
                 base_estimator='linearsvm',
                 n_estimators=50,
                 learning_rate=1.,
                 algorithm='SAMME.R',
                 random_state=None,
                 sampler=SMOTE(),
                 indexer=None):

        self.new_samples = new_samples
        self.algorithm = algorithm
        self.sampler = sampler

        _estimator = get_model(base_estimator)
        if not _estimator:
            raise Exception('Could not fond "' + base_estimator + '" classification model_type')
        super(SMOTEBoost, self).__init__(
            base_estimator=_estimator,
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            random_state=random_state)
        BaseEstimator.__init__(self, BaseEstimator_config=BaseEstimator_config)
        if indexer:
            self.indexer = indexer
        else:
            self.indexer = LabelIndexer(multi_label=False)

    def predict(self, X):
        pred = super().predict(X)
        return self.indexer.inverse_transform(pred)

    def fit(self, X, y, sample_weight=None, minority_target=None):
        """Build a boosted classifier/regressor from the training set (data, y),
        performing SMOTE during each boosting step.
        """
        # Check that algorithm is supported.
        if self.algorithm not in ('SAMME', 'SAMME.R'):
            raise ValueError("algorithm %s is not supported" % self.algorithm)

        # Check parameters.
        if self.learning_rate <= 0:
            raise ValueError("learning_rate must be greater than zero")

        self.indexer.build_label_dict(y)
        y = self.indexer.numerize_label_sequences(y)

        X, y = check_X_y(X.toarray(), y, y_numeric=is_regressor(self))

        if sample_weight is None:
            # Initialize weights to 1 / n_samples.
            sample_weight = np.empty(X.shape[0], dtype=np.float64)
            sample_weight[:] = 1. / X.shape[0]
        else:
            sample_weight = check_array(sample_weight, ensure_2d=False)
            # Normalize existing weights.
            sample_weight = sample_weight / sample_weight.sum(dtype=np.float64)

            # Check that the sample weights sum is positive.
            if sample_weight.sum() <= 0:
                raise ValueError(
                    "Attempting to fit with a non-positive "
                    "weighted number of samples.")

        # Check parameters.
        self._validate_estimator()

        # Clear any previous fit results.
        self.estimators_ = []
        self.estimator_weights_ = np.zeros(self.n_estimators, dtype=np.float64)
        self.estimator_errors_ = np.ones(self.n_estimators, dtype=np.float64)

        random_state = check_random_state(self.random_state)

        for iboost in range(self.n_estimators):
            print('fitting estimator no ' + str(iboost))
            # SMOTE step.
            initial_count = len(y)
            X, y = self.sampler.fit_resample(X, y)

            added_samples = len(y) - initial_count
            sample_weight_syn = np.empty(added_samples, dtype=np.float64)
            sample_weight_syn[:] = 1. / X.shape[0]

            # Combine the weights.
            sample_weight = np.append(sample_weight, sample_weight_syn).reshape(-1, 1)
            sample_weight = np.squeeze(normalize(sample_weight, axis=0, norm='l1'))

            # Boosting step.
            sample_weight, estimator_weight, estimator_error = self._boost(
                iboost,
                X, y,
                sample_weight,
                random_state)

            # Early termination.
            if sample_weight is None:
                print('sample_weight: {}'.format(sample_weight))
                break

            self.estimator_weights_[iboost] = estimator_weight
            self.estimator_errors_[iboost] = estimator_error

            # Stop if error is zero.
            # if estimator_error == 0:
            #     print('error: {}'.format(estimator_error))
            #     break

            sample_weight_sum = np.sum(sample_weight)

            # Stop if the sum of sample weights has become non-positive.
            if sample_weight_sum <= 0:
                print('sample_weight_sum: {}'.format(sample_weight_sum))
                break

            if iboost < self.n_estimators - 1:
                # Normalize.
                sample_weight /= sample_weight_sum

        return self


class RUSBoost(AdaBoostClassifier, BaseEstimator, metaclass=FinalMeta):
    name = 'rus_boost_classifier'

    """Implementation of SMOTEBoost.
    SMOTEBoost introduces texts sampling into the AdaBoost algorithm by
    oversampling the minority class using SMOTE on each boosting iteration.  
    """

    def __init__(self,
                 BaseEstimator_config=None,
                 new_samples=100,
                 base_estimator='linearsvm',
                 n_estimators=50,
                 learning_rate=1.,
                 algorithm='SAMME.R',
                 random_state=None,
                 sampler=RandomUnderSampler(),
                 indexer=None):

        self.new_samples = new_samples
        self.algorithm = algorithm
        self.sampler = sampler

        _estimator = get_model(base_estimator)
        if not _estimator:
            raise Exception('Could not fond "' + base_estimator + '" classification model_type')
        super(RUSBoost, self).__init__(
            base_estimator=_estimator,
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            random_state=random_state)
        BaseEstimator.__init__(self, BaseEstimator_config=BaseEstimator_config)
        if indexer:
            self.indexer = indexer
        else:
            self.indexer = LabelIndexer(multi_label=False)

    def predict(self, X):
        pred = super().predict(X)
        return self.indexer.reverse_numerize_label_sequences(pred)

    def fit(self, X, y, sample_weight=None, minority_target=None):
        """Build a boosted classifier/regressor from the training set (data, y),
        performing SMOTE during each boosting step.
        """
        # Check that algorithm is supported.
        if self.algorithm not in ('SAMME', 'SAMME.R'):
            raise ValueError("algorithm %s is not supported" % self.algorithm)

        # Check parameters.
        if self.learning_rate <= 0:
            raise ValueError("learning_rate must be greater than zero")

        self.indexer.build_label_dict(y)
        y = self.indexer.numerize_label_sequences(y)

        X, y = check_X_y(X.toarray(), y, y_numeric=is_regressor(self))

        if sample_weight is None:
            # Initialize weights to 1 / n_samples.
            sample_weight = np.empty(X.shape[0], dtype=np.float64)
            sample_weight[:] = 1. / X.shape[0]
        else:
            sample_weight = check_array(sample_weight, ensure_2d=False)
            # Normalize existing weights.
            sample_weight = sample_weight / sample_weight.sum(dtype=np.float64)

            # Check that the sample weights sum is positive.
            if sample_weight.sum() <= 0:
                raise ValueError(
                    "Attempting to fit with a non-positive "
                    "weighted number of samples.")

        # Check parameters.
        self._validate_estimator()

        # Clear any previous fit results.
        self.estimators_ = []
        self.estimator_weights_ = np.zeros(self.n_estimators, dtype=np.float64)
        self.estimator_errors_ = np.ones(self.n_estimators, dtype=np.float64)

        random_state = check_random_state(self.random_state)

        for iboost in range(self.n_estimators):
            print('fitting estimator no ' + str(iboost))
            # SMOTE step.

            X, y = self.sampler.fit_resample(X, y)

            indices = np.array(self.sampler.sample_indices_)

            sample_weight = sample_weight[indices]
            # Boosting step.
            sample_weight, estimator_weight, estimator_error = self._boost(
                iboost,
                X, y,
                sample_weight,
                random_state)

            # Early termination.
            if sample_weight is None:
                print('sample_weight: {}'.format(sample_weight))
                break

            self.estimator_weights_[iboost] = estimator_weight
            self.estimator_errors_[iboost] = estimator_error

            # Stop if error is zero.
            # if estimator_error == 0:
            #     print('error: {}'.format(estimator_error))
            #     break

            sample_weight_sum = np.sum(sample_weight)

            # Stop if the sum of sample weights has become non-positive.
            if sample_weight_sum <= 0:
                print('sample_weight_sum: {}'.format(sample_weight_sum))
                break

            if iboost < self.n_estimators - 1:
                # Normalize.
                sample_weight /= sample_weight_sum

        return self


class BalancedBagging(BaseEstimator):
    name = 'balance_bagging_classifier'

    def __init__(self, BaseEstimator_config=None, n_estimators=10, base_estimator='linearsvm', sampler=SMOTE(),
                 indexer=None):
        super().__init__(BaseEstimator_config)
        self.base_estimator = base_estimator
        self.estimator = get_model(base_estimator)
        if not self.estimator:
            raise Exception('Could not find "' + base_estimator + '" classafication model_type')
        self.n_estimators = n_estimators
        self.model_list = []
        if indexer:
            self.indexer = indexer
        else:
            self.indexer = LabelIndexer(multi_label=False)
        self.sampler = sampler

        self.accuracy = "Not computed"
        self.recall = "Not computed"
        self.f1 = "Not computed"

    def fit(self, X, y, X_val=None, y_val=None):
        self.indexer.build_label_dict(y)
        y = self.indexer.numerize_label_sequences(y)

        self.model_list = []

        for ibagging in range(self.n_estimators):
            print('fitting estimateur no ' + str(ibagging))
            b = min(0.1 * ((ibagging % 10) + 1), 1)
            X_train, y_train = resample(X, y, n_samples=int(b * len(y)), stratify=y)
            X_train, y_train = self.sampler.fit_resample(X_train, y_train)
            self.estimator = get_model(self.base_estimator)
            model = self.estimator.fit(X_train, y_train)
            self.model_list.append(model)

        if X_val is not None and y_val is not None:
            pred = self.predict(X_val)

            self.accuracy = accuracy_score(y_val, pred)
            self.recall = recall_score(y_val, pred, average='micro')
            self.f1 = f1_score(y_val, pred, average='micro')

            print(classification_report(y_val, pred, target_names=list(self.indexer.idx2label.values())))
            print(confusion_matrix(y_val, pred))

        return self

    def predict_proba(self, X):
        predictions = np.array([model.predict(X) for model in self.model_list]).transpose()

        y_pred = [collections.Counter(ar).most_common()[0][0] for ar in predictions]

        return y_pred

    def predict(self, X):
        predictions = np.array([model.predict(X) for model in self.model_list]).transpose()

        y_pred = [collections.Counter(ar).most_common()[0][0] for ar in predictions]
        return self.indexer.inverse_transform(y_pred)


class BalanceCascade(BaseEstimator):
    """
    The implementation of BalanceCascade.
    Hyper-parameters:
        base_estimator : scikit-learn classifier object
            optional (default=DecisionTreeClassifier)
            The base estimator from which the ensemble is built.
        n_estimators:       Number of iterations / estimators
        k_bins:             Number of hardness bins
    """
    name = 'balance_cascade_classifier'

    def __init__(self, BaseEstimator_config=None, base_estimator='logreg', n_estimators=10, sampler=RandomUnderSampler(),
                 random_seed=None,
                 indexer=None):
        super().__init__(BaseEstimator_config)
        self.base_estimator = base_estimator
        self.n_estimators = n_estimators
        self.random_seed = random_seed
        self.model_list = []
        self.sampler = sampler
        # Will be set in the fit function
        self.feature_cols = None
        self.base_estimator = get_model(base_estimator)
        if not self.base_estimator:
            raise Exception('Could not find "' + base_estimator + '" classafication model_type')

        if indexer:
            self.indexer = indexer
        else:
            self.indexer = LabelIndexer(multi_label=False)

    def _fit_baselearner(self, X, y):
        model = clone(self.base_estimator)
        return model.fit(X, y)

    def class_label_statistics(self, y):

        unique, counts = np.unique(y, return_counts=True)
        class_stats = dict(zip(unique, counts))

        return sorted(class_stats.items(), key=lambda x: -x[1])

    def fit(self, X, y, print_log=False, visualize=False):
        self.indexer.build_label_dict(y)
        y = np.array(self.indexer.numerize_label_sequences(y))

        class_counts = self.class_label_statistics(y)
        n_min = self.class_label_statistics(y)[-1][1]
        n_maj = self.class_label_statistics(y)[0][1]
        ir = n_min / n_maj
        keep_fp_rate = np.power(ir, 1 / (self.n_estimators - 1))

        # Algorithm start
        for ibagging in range(1, self.n_estimators):
            X_train, y_train = self.sampler.fit_resample(X, y)

            # print ('Cascade Iter: {} X_maj: {} X_rus: {} X_min: {}'.format(
            #     ibagging, len(df_maj), len(df_min), len(df_min)))
            self.model_list.append(self._fit_baselearner(X_train, y_train))
            # drop "easy" majority samples
            y_pred = self.predict_proba(X)
            indices_to_remove = []
            for cls in class_counts:
                cls_indices = np.where(y == cls[0])[0]
                ratio_to_remove = len(cls_indices) - int(keep_fp_rate * (len(cls_indices) - n_min))
                sorted_pred_class_indices = y_pred[:, 0].argsort()
                indices_to_remove.extend([i for i in sorted_pred_class_indices[:ratio_to_remove] if i in cls_indices])

            indices_to_keep = list(range(0, len(y)))
            indices_to_keep = [i for i in indices_to_keep if i not in indices_to_remove]
            X = X[indices_to_keep]
            y = y[indices_to_keep]

        return self

    def predict_proba(self, X):
        prediction = [model.predict_proba(X) for model in self.model_list]
        y_pred = np.array(prediction).mean(axis=0)
        if y_pred.ndim == 1:
            y_pred = y_pred[:, np.newaxis]
        if y_pred.shape[1] == 1:
            y_pred = np.append(1 - y_pred, y_pred, axis=1)
        return y_pred

    def predict(self, X):
        y_pred = self.predict_proba(X)
        y_pred = np.argmax(y_pred, axis=1)
        return self.indexer.reverse_numerize_label_sequences(y_pred)


class SelfPacedEnsemble(BaseEstimator):
    """ Self-paced Ensemble (SPE)

    Parameters
    ----------

    base_estimator : object, optional (default=sklearn.Tree.DecisionTreeClassifier())
        The base estimator to fit on self-paced under-sampled subsets of the dataset_train.
        NO need to support sample weighting.
        Built-in `fit()`, `predict()`, `predict_proba()` methods are required.

    hardness_func :  function, optional
        (default=`lambda y_true, y_pred: np.absolute(y_true-y_pred)`)
        User-specified classification hardness function
            Parameters:
                y_true: 1-d array-like, shape = [n_samples]
                y_pred: 1-d array-like, shape = [n_samples]
            Returns:
                hardness: 1-d array-like, shape = [n_samples]

    n_estimators :  integer, optional (default=10)
        The number of base estimators in the ensemble.

    k_bins :        integer, optional (default=10)
        The number of hardness bins that were used to approximate hardness distribution.

    random_state :  integer / RandomState instance / None, optional (default=None)
        If integer, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used by
        `numpy.random`.


    Attributes
    ----------

    base_estimator_ : estimator
        The base estimator from which the ensemble is grown.

    estimators_ : list of estimator
        The collection of fitted base estimators.

    Example:
    ```
    import numpy as np
    from sklearn import datasets
    from sklearn.tree import DecisionTreeClassifier
    from self_paced_ensemble import SelfPacedEnsemble
    from utils import make_binary_classification_target, imbalance_train_test_split

    data, y = datasets.fetch_covtype(return_X_y=True)
    y = make_binary_classification_target(y, 7, True)
    X_train, X_test, y_train, y_test = imbalance_train_test_split(
            data, y, test_size=0.2, random_state=42)

    def absolute_error(y_true, y_pred):
        # Self-defined classification hardness function
        return np.absolute(y_true - y_pred)

    spe = SelfPacedEnsemble(
        base_estimator=DecisionTreeClassifier(),
        hardness_func=absolute_error,
        n_estimators=10,
        k_bins=10,
        random_state=42,
    ).fit(
        data=X_train,
        y=y_train,
    )
    print('auc_prc_score: {}'.format(spe.score(X_test, y_test)))
    ```

    """

    name = 'paced_classifier'

    def __init__(self, BaseEstimator_config=None, base_estimator='logreg',
                 hardness_func=lambda y_true, y_pred: np.absolute(0.5 - y_pred), n_estimators=10, k_bins=10,
                 random_state=None, indexer=None):

        super().__init__(BaseEstimator_config=BaseEstimator_config)
        self.base_estimator_ = get_model(base_estimator)
        self.estimators_ = []
        self._hardness_func = hardness_func
        self._n_estimators = n_estimators
        self._k_bins = k_bins
        self._random_state = random_state
        if indexer:
            self.indexer = indexer
        else:
            self.indexer = LabelIndexer(multi_label=False)
        self.sampler = RandomUnderSampler()

    def _fit_base_estimator(self, X, y):
        """Private function used to train a single base estimator."""
        return clone(self.base_estimator_).fit(X, y)

    def _random_under_sampling(self, X, y):
        """Private function used to perform random under-sampling."""

        return self.sampler.fit_resample(X, y)

    def class_label_statistics(self, y):

        unique, counts = np.unique(y, return_counts=True)
        class_stats = dict(zip(unique, counts))

        return sorted(class_stats.items(), key=lambda x: -x[1])

    def _self_paced_under_sampling(self, X, y, maj_samples_indexes, maj_class_index, X_min, y_min, i_estimator):
        """Private function used to perform self-paced under-sampling."""

        X_maj = X[maj_samples_indexes]
        y_maj = y[maj_samples_indexes]
        # Update hardness value estimation
        y_pred_maj = self._y_pred_maj[maj_samples_indexes][:, maj_class_index]
        hardness = self._hardness_func(y_maj, y_pred_maj)

        # If hardness values are not distinguishable, perform random smapling
        if hardness.max() == hardness.min():
            X_train, y_train = self._random_under_sampling(X_maj, y_maj, X_min, y_min)
        # Else allocate majority samples into k hardness bins
        else:
            step = (hardness.max() - hardness.min()) / self._k_bins
            bins = [];
            ave_contributions = []
            for i_bins in range(self._k_bins):
                idx = (
                        (hardness >= i_bins * step + hardness.min()) &
                        (hardness < (i_bins + 1) * step + hardness.min())
                )
                # Marginal samples with highest hardness value -> kth bin
                if i_bins == (self._k_bins - 1):
                    idx = idx | (hardness == hardness.max())
                bins.append(X_maj[idx])
                ave_contributions.append(hardness[idx].mean())

            # Update self-paced factor alpha
            alpha = np.tan(np.pi * 0.5 * (i_estimator / (self._n_estimators - 1)))
            # Caculate sampling weight
            weights = 1 / (ave_contributions + alpha)
            weights[np.isnan(weights)] = 0
            # Caculate sample number from each bin
            n_sample_bins = X_min.shape[0] * weights / weights.sum()
            n_sample_bins = n_sample_bins.astype(int) + 1

            # Perform self-paced under-sampling
            sampled_bins = []
            for i_bins in range(self._k_bins):
                if min(bins[i_bins].shape[0], n_sample_bins[i_bins]) > 0:
                    np.random.seed(self._random_state)
                    idx = np.random.choice(
                        bins[i_bins].shape[0],
                        min(bins[i_bins].shape[0], n_sample_bins[i_bins]),
                        replace=False)
                    sampled_bins.append(bins[i_bins][idx])
            if issparse(sampled_bins[0]):
                X_train = vstack(sampled_bins)
            #                X_train = vstack([X_train_maj, X_min])
            else:
                X_train_maj = np.concatenate(sampled_bins, axis=0)
            #                X_train = np.concatenate([X_train_maj, X_min])

            y_train = np.full(X_train.shape[0], y_maj[0])
        #            y_train = np.concatenate([y_train_maj, y_min])

        return X_train, y_train

    def _self_paced_under_sampling_multi(self, X, y, i_estimator):
        """Private function used to perform self-paced under-sampling."""
        class_statistics = self.class_label_statistics(y)
        label_min = class_statistics[-1][0]
        label_maj = class_statistics[0][0]

        X_min = X[y == label_min]
        y_min = y[y == label_min]

        maj_indexes = np.where(y == label_maj)
        X_train, y_train = self._self_paced_under_sampling(X, y, maj_indexes, 0, X_min, y_min, i_estimator)

        for c in class_statistics[1:-1]:
            label_maj = c[0]
            maj_indexes = np.where(y == label_maj)

            X_train_, y_train_ = self._self_paced_under_sampling(X, y, maj_indexes, label_maj, X_min, y_min,
                                                                 i_estimator)
            X_train = vstack([X_train, X_train_])
            y_train = np.concatenate([y_train, y_train_])

        return vstack([X_train, X_min]), np.concatenate([y_train, y_min])

    def fit(self, X, y, label_maj=0, label_min=1):
        """Build a self-paced ensemble of estimators from the training set (data, y).

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape = [n_samples, n_features]
            The training input samples. Sparse matrices are accepted only if
            they are supported by the base estimator.

        y : array-like, shape = [n_samples]
            The label values (class y_values).

        label_maj : int, bool or float, optional (default=0)
            The majority class label, default to be negative class.

        label_min : int, bool or float, optional (default=1)
            The minority class label, default to be positive class.

        Returns
        ------
        self : object
        """

        self.indexer.build_label_dict(y)
        y = np.array(self.indexer.numerize_label_sequences(y))
        self.estimators_ = []

        # Random under-sampling in the 1st round (cold start)
        X_train, y_train = self._random_under_sampling(X, y)
        self.estimators_.append(
            self._fit_base_estimator(
                X_train, y_train))
        self._y_pred_maj = self.predict_proba(X)

        # Loop start
        for i_estimator in range(1, self._n_estimators):
            X_train, y_train = self._self_paced_under_sampling_multi(X, y, i_estimator)
            self.estimators_.append(
                self._fit_base_estimator(
                    X_train, y_train))
            # update predicted probability
            n_clf = len(self.estimators_)
            y_pred_maj_last_clf = self.estimators_[-1].predict_proba(X)
            self._y_pred_maj = (self._y_pred_maj * (n_clf - 1) + y_pred_maj_last_clf) / n_clf

        return self

    def predict_proba(self, X):
        """Predict class probabilities for data.

        The predicted class probabilities of an input sample is computed as
        the mean predicted class probabilities of the base estimators in the
        ensemble. If base estimators do not implement a ``predict_proba``
        method, then it resorts to voting and the predicted class probabilities
        of an input sample represents the proportion of estimators predicting
        each class.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape = [n_samples, n_features]
            The training input samples. Sparse matrices are accepted only if
            they are supported by the base estimator.

        Returns
        -------
        p : array of shape = [n_samples, n_classes]
            The class probabilities of the input samples.
        """
        y_pred = np.array(
            [model.predict_proba(X) for model in self.estimators_]
        ).mean(axis=0)

        return y_pred

    def predict(self, X):
        """Predict class for data.

        The predicted class of an input sample is computed as the class with
        the highest mean predicted probability. If base estimators do not
        implement a ``predict_proba`` method, then it resorts to voting.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape = [n_samples, n_features]
            The training input samples. Sparse matrices are accepted only if
            they are supported by the base estimator.

        Returns
        -------
        y : array of shape = [n_samples]
            The predicted classes.
        """

        y_pred = self.predict_proba(X)
        y_pred = np.argmax(y_pred, axis=1)
        return self.indexer.inverse_transform(y_pred)

    def score(self, X, y):
        """Returns the average precision score (equivalent to the area under
        the precision-recall curve) on the given test texts and y_values.

        Parameters
        ----------
        X : array-like, shape = (n_samples, n_features)
            Test samples.

        y : array-like, shape = (n_samples) or (n_samples, n_outputs)
            True y_values for data.

        Returns
        -------
        score : float
            Average precision of self.predict_proba(data)[:, 1] wrt. y.
        """
        return average_precision_score(
            y, self.predict_proba(X)[:, 1])
