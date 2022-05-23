import numpy as np
from imblearn.over_sampling import RandomOverSampler, SMOTE
from imblearn.under_sampling import RandomUnderSampler, TomekLinks, EditedNearestNeighbours
from imblearn.combine import SMOTEENN
from imblearn.utils import check_target_type
from sklearn.utils import check_X_y
import  scipy as sp

from kdmt.ml.performance_measures import calculate_class_label_statistics


# class AutoSampler():
#     """Random samples texts to bring all class frequencies into a range.
#     """
#
#     def __init__(self, min_freq=None, max_freq=None, random_state=None):
#         self.min_freq = min_freq
#         self.max_freq = max_freq
#         self.random_state = random_state
#         self.auto_balance = False
#
#         if min_freq and max_freq:
#             self.ratio = max_freq / min_freq
#         else:
#             self.auto_balance = True
#
#     def fit(self, data, y):
#         """Find the classes statistics before to perform sampling.
#         """
#         data, y = check_X_y(data, y, accept_sparse=['csr', 'csc'], dtype=None)
#         y = check_target_type(y)
#
#         if self.auto_balance:
#             class_stats = calculate_class_label_statistics(y)
#             std = np.std(class_stats, axis=0)
#             self.min_freq = int(class_stats[-1][1] + std[1])
#             self.max_freq = int(class_stats[0][1] - std[1])
#             self.ratio = self.max_freq / self.min_freq
#
#         freq = np.unique(y, return_counts=True)
#         frequencies = dict(zip(freq[0], freq[1]))
#         labels = list(freq[0])
#
#         under_dict = {}
#         over_dict = {}
#         self.ratio_ = self.ratio
#         for lbl in labels:
#             count = frequencies[lbl]
#             if count < self.min_freq:
#                 under_dict[lbl] = count
#                 over_dict[lbl] = self.min_freq
#             elif count > self.max_freq:
#                 under_dict[lbl] = self.max_freq
#                 over_dict[lbl] = self.max_freq
#             else:
#                 under_dict[lbl] = count
#                 over_dict[lbl] = count
#         self.under_sampler = RandomUnderSampler(
#             sampling_strategy=under_dict, random_state=self.random_state)
#         self.over_sampler = RandomOverSampler(
#             sampling_strategy=over_dict, random_state=self.random_state)
#         return self
#
#     def sample(self, data, y):
#         """Resample the dataset_train.
#         """
#         new_X, new_y = self.under_sampler.fit_resample(data, y)
#         return self.over_sampler.fit_resample(new_X, new_y)
#
#     def fit_resample(self, data, y):
#         return self.fit(data, y).sample(data, y)


def fitted_function_exp(t, A, K, C):
    return A * np.exp(K * t) + C




class AutoSampler():
    """Random samples texts to bring all class frequencies into a range.
    """

    def __init__(self, random_state=None, constant_size=True, a=0.8, strategy='majority'):

        self.random_state = random_state
        self.constant_size=constant_size
        self.ratio=a
        self.strategy=strategy

    def fit(self, X, y):
        """Find the classes statistics before to perform sampling.
        """
        X, y = check_X_y(X, y, accept_sparse=['csr', 'csc'], dtype=None)
        y = check_target_type(y)


        freq = np.unique(y, return_counts=True)
        frequencies = dict(zip(freq[0], freq[1]))

        frequencies={k: v for k, v in sorted(frequencies.items(), key=lambda item: item[1])}

        labels = list(freq[0])

        A, K, C = self.fit_exp_nonlinear(np.array(range(len(labels))), np.array([f[1] for f in frequencies.items()]))
        new_freq = fitted_function_exp(range(len(labels)), A, K * self.ratio, C)
        new_freq=new_freq/sum(new_freq)

        sampling_dict={labels[i]:int(new_freq[i]*len(y)) for i in range(0,len(labels))}
        under_sampling_dict = {labels[i]: int(new_freq[i] * len(y)) for i in range(0, len(labels)) if int(new_freq[i] * len(y))<frequencies[i]}

        self.under_sampler_tomek=TomekLinks(sampling_strategy=self.strategy)
        self.under_sampler_een=EditedNearestNeighbours()
        self.over_sampler=SMOTEENN(sampling_strategy=sampling_dict)
        self.under_sampler_random=RandomUnderSampler(
            sampling_strategy=under_sampling_dict)
        return self

    def sample(self, X, y):
        """
        Resample the dataset_train.
        """
        new_X, new_y = self.under_sampler_tomek.fit_resample(X, y)
        new_X, new_y = self.under_sampler_random.fit_resample(new_X, new_y)
        new_X, new_y = self.over_sampler.fit_resample(new_X, new_y)

        return new_X, new_y

    def fit_resample(self, X, y):
        return self.fit(X, y).sample(X, y)


    def fit_exp_linear(self, classes, y, C=0):
        y = y - C
        y = np.log(y)
        K, A_log = np.polyfit(classes, y, 1)
        A = np.exp(A_log)
        return A, K

    def fit_exp_nonlinear(self, classes, y):
        opt_parms, parm_cov = sp.optimize.curve_fit(fitted_function_exp, classes, y, maxfev=1000)
        A, K, C = opt_parms
        return A, K, C