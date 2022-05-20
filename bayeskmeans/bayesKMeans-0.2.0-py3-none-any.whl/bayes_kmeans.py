import numpy as np
from sklearn.cluster import KMeans
from skopt import gp_minimize
import warnings
from bayeskmeans.bayes_parameters import BayesKMeansParameters
from bayeskmeans.bayes_methods import BayesKMeansMethods

warnings.filterwarnings('ignore')

__version__ = 'dev'


def test():
    print(1)


class BayesKMeans(object):
    def __init__(self, data):
        self.data = data

        # Определение переменных на будущее
        self.x_iters = None
        self.func_vals = None
        self.found_k = None
        self.border = None
        self.params = None

        # Определение метода
        self.method = BayesKMeansMethods(data=self.data)
        if len(data) <= 4000:
            self.method_name = 'silhouette'
            self.method.set_score_function(self.method.silhouette)
        else:
            self.method_name = 'davies_bouldin'
            self.method.set_score_function(self.method.davies_bouldin)

    def find_k(self):
        self.__bayesian_optimization()

    def get_k(self):
        return self.found_k

    def set_bayes_parameters(self, parameters):
        self.params = parameters

    def choose_optimization_method(self, optimized_method):
        if optimized_method == 'silhouette':
            self.method.set_score_function(self.method.silhouette)
        elif optimized_method == 'daviesBouldin':
            self.method.set_score_function(self.method.davies_bouldin)

    def __get_elbow(self, n_clusters):
        if n_clusters not in self.params.x_0:
            model = KMeans(n_clusters=n_clusters)
            predicts = model.fit_predict(self.data)
            self.params.x_0.append(n_clusters)
            self.params.y_0.append(self.method.score_function([n_clusters], predicts))
            self.params.elbow.append(model.inertia_)
            return model.inertia_
        else:
            i = 0
            while self.params.x_0[i] != n_clusters:
                i += 1
            return self.params.elbow[i]

    def determine_right_border(self):
        step = 50
        diff = 20
        level = 0.75
        border = step
        k_0 = self.__get_elbow(border)
        k_1 = self.__get_elbow(border + diff)
        while k_1 / k_0 < level:
            border += step
            k_0 = self.__get_elbow(border)
            k_1 = self.__get_elbow(border + diff)
        self.params.bounds = [[2, border]]
        x0 = self.params.x_0[:-1]
        for i in range(len(x0)):
            x0[i] = [x0[i]]
        self.params.x_0 = x0
        self.params.y_0 = self.params.y_0[:-1]
        print('Right border is {0}'.format(border))

    def set_optimization_method(self, method):
        self.method = method

    def __bayesian_optimization(self):
        if self.params is None:
            self.params = BayesKMeansParameters()
            self.params.method = self.method
            self.determine_right_border()
            self.params.auto_set_params()

        result = gp_minimize(
            self.method.score_function,
            self.params.bounds,
            acq_func=self.params.acq_func,
            n_calls=self.params.n_calls,
            n_initial_points=self.params.n_init_points,
            initial_point_generator=self.params.initial_point_generator,
            acq_optimizer=self.params.acq_optimizer,
            n_restarts_optimizer=self.params.n_restarts_optimizer,
            kappa=self.params.kappa,
            xi=self.params.xi,
            noise=self.params.noise,
            x0=self.params.x_0,
            y0=self.params.y_0
        )
        x_it = []
        for x in result.x_iters:
            x_it.append(x[0])
        self.x_iters = x_it
        self.func_vals = result.func_vals
        self.found_k = result.x[0]
        self.min_function_value = result.fun

        for d in range(max([self.found_k - self.params.dispersion, 2]), self.found_k + self.params.dispersion + 1):
            if d not in self.x_iters:
                self.x_iters.append(d)
                self.func_vals = np.append(self.func_vals, self.method.score_function([d]))
                if self.func_vals[-1] < self.min_function_value:
                    self.min_function_value = self.func_vals[-1]
                    self.found_k = d
