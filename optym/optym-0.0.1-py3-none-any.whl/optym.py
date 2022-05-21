import pandas as pd
import numpy as np


class GradientDescent:
    """
    Simple implementation of Gradient-Descent algorithm.
    Example
    -------
    import numpy as np
    from optym import GradientDescent
    def cost(parameters):
        target_parameters = np.array([1,1])
        return np.sum(np.square(target_parameters-parameters))
    gd = GradientDescent(learning_rate = 0.05, iterations = 100, delta_x=0.001)
    start_parameters = np.random.random(2)
    par_hist, cost_hist = gd(cost, start_parameters)
    print(gd.param_in_min)
    """

    def __init__(self, delta_x=0.001, **kwargs):

        self.learning_rate = None

        self.iterations = None

        self.delta_x = delta_x

        self.min = None

        self.param_in_min = None

        kwargs.update(dict(delta_x=self.delta_x))

        self.set_params(**kwargs)

    def __repr__(self):
        return f"GradientDescent(learning_date={self.learning_rate}, iterations={self.iterations})"

    def __call__(self, cost, start_parameters, **kwargs):

        self.set_params(**kwargs)

        parameters_hist = [start_parameters]

        cost_hist = []

        for it in range(self.iterations):

            old_cost, grad = self.__eval_gradient(cost, parameters_hist[-1])

            new_parameters = parameters_hist[-1] - self.learning_rate * grad

            parameters_hist.append(new_parameters)

            cost_hist.append(old_cost)

        cost_hist.append(cost(parameters_hist[-1]))

        self.__update_minimum(parameters_hist, cost_hist)

        return np.array(parameters_hist), np.array(cost_hist)

    def set_params(self, **kwargs):
        for par in kwargs:
            if par in dir(self):
                self.__setattr__(par, kwargs[par])
            else:
                raise KeyError(f"Attribute {par} not found.")

    def __update_minimum(self, parameters_hist, cost_hist):

        argmin_cost_hist = np.argmin(cost_hist)

        min_cost_hist = cost_hist[argmin_cost_hist]

        min_par_hist = parameters_hist[argmin_cost_hist]

        if self.min is None:
            self.min = min_cost_hist
            self.param_in_min = min_par_hist
        else:
            if min_cost_hist < self.min:
                self.min = min_cost_hist
                self.param_in_min = min_par_hist

    def __kronecker_delta(self, i, j):
        return int(i == j)

    def __eval_gradient(self, cost, parameters):

        grad = []

        old_cost = cost(parameters)

        for current_par_index in range(len(parameters)):
            current_par = [
                parameters[i]
                + self.__kronecker_delta(i, current_par_index) * self.delta_x
                for i in range(len(parameters))
            ]

            dL = (cost(current_par) - old_cost) / self.delta_x

            grad.append(dL)

        return old_cost, np.array(grad)


class MCMC:
    def __init__(
        self,
        min_parameters,
        max_parameters,
        method="metropolis_hastings",
        clip_limits=False,
    ):

        self.learning_rate = None

        self.iterations = None

        self.min_parameters = min_parameters

        self.max_parameters = max_parameters

        self.method = method

        self.clip_limits = clip_limits

        self.amp_parameters = None

        self.stp_parameters = None

        self.max = None

        self.param_in_max = None

    def __repr__(self):
        return f"""MCMC(method = {self.method})"""

    def __call__(self, cost, start_parameters, learning_rate=0.01, iterations=100):

        self.learning_rate = learning_rate

        self.iterations = iterations

        self.amp_parameters = np.array(self.max_parameters) - np.array(
            self.min_parameters
        )

        self.stp_parameters = self.amp_parameters * self.learning_rate

        X0 = start_parameters

        y0 = cost(X0)

        parameters_hist = [X0]

        cost_hist = [y0]

        for it in range(self.iterations):

            X_new = self.__propose_parameter(X0, self.stp_parameters)

            y_new = cost(X_new)

            if self.method == "metropolis_hastings":

                A = min(1, y_new / y0)

                u = np.random.random()

                if u <= A:
                    X0 = X_new
                    y0 = y_new

            elif self.method == "maximize":
                if y_new > y0:
                    X0 = X_new
                    y0 = y_new

            elif self.method == "minimize":
                if y_new < y0:
                    X0 = X_new
                    y0 = y_new

            parameters_hist.append(X0)

            cost_hist.append(y0)

        self.__update_maximum(parameters_hist, cost_hist)

        return np.array(parameters_hist), np.array(cost_hist)

    def __propose_parameter(self, X, stp_X):

        X = np.array(X)

        delta = stp_X * np.random.randn(*X.shape)

        if self.clip_limits:
            pos_par = X + delta
            neg_par = X - delta

            new_par = np.where(
                (pos_par >= self.min_parameters) & (pos_par <= self.max_parameters),
                pos_par,
                neg_par,
            )

        else:
            new_par = X + delta

        return new_par

    def set_params(self, **kwargs):
        for par in kwargs:
            if par in dir(self):
                self.__setattr__(par, kwargs[par])
            else:
                raise KeyError(f"Attribute {par} not found.")

    def __update_maximum(self, parameters_hist, cost_hist):

        argmax_cost_hist = np.argmax(cost_hist)

        max_cost_hist = cost_hist[argmax_cost_hist]

        max_par_hist = parameters_hist[argmax_cost_hist]

        if self.max is None:
            self.max = max_cost_hist
            self.param_in_max = max_par_hist
        else:
            if self.min_cost_hist > self.max:
                self.max = max_cost_hist
                self.param_in_max = max_par_hist