"""
AugmentedLagrangeFunction class
"""
import numpy as np

from science_optimization.function import BaseFunction, LinearFunction, FunctionsComposite


class AugmentedLagrangeFunction(BaseFunction):
    """
    Class that deals with the function used in the Augmented Lagrangian method
    """
    eq_aux_func = None
    ineq_aux_func = None
    aux_rho = None

    _flag_num_g = False     # this function uses analytical gradient

    def input_check(self, x):
        """Check input dimension.

        Args:
            x: (numpy array) point to be evaluated.
        """

        # check if input is numpy
        self.numpy_check(x)

        if not x.shape[0] == self.dimension():
            raise Warning("Point x must have {} dimensions.".format(self.parameters['n']))

    def eval(self, x):
        """

        Args:
            x:

        Returns:

        """
        if self.ineq_aux_func is not None:
            aux_max = self.ineq_aux_func.eval(x=x)
            aux_max[aux_max < 0] = 0

            ineq_part = 0.5 * self.rho * sum(aux_max ** 2)

        else:
            ineq_part = 0

        if self.eq_aux_func is not None:
            eq_part = 0.5 * sum((self.aux_rho * (self.eq_aux_func * self.eq_aux_func)).eval(x=x))

        else:
            eq_part = 0

        return self.f_obj.eval(x) + eq_part + ineq_part

    def gradient(self, x):

        if self.ineq_aux_func is not None:
            aux_max = self.ineq_aux_func.eval(x=x)
            aux_max[aux_max < 0] = 0

            ineq_part = self.rho * np.dot(self.g.gradient(x), aux_max)

        else:
            ineq_part = 0

        if self.eq_aux_func is not None:
            eq_part = self.rho * np.dot(self.h.gradient(x), self.eq_aux_func.eval(x))

        else:
            eq_part = 0

        return self.f_obj.gradient(x) + eq_part + ineq_part

    def hessian(self, x):

        if self.ineq_aux_func is not None:
            aux_grad = self.g.gradient(x)
            aux_hess = self.g.hessian(x)

            aux_max = self.ineq_aux_func.eval(x=x)
            aux_max[aux_max < 0] = 0

            ineq_part = np.zeros((self.dimension(), self.dimension()))

            for i in range(self.g.n_functions):

                if aux_max[i] > 0:
                    ineq_part += (
                        (aux_hess[i] * aux_max[i]) +
                        np.dot(aux_grad[0], aux_grad[0].transpose())
                    )

            ineq_part = self.rho * ineq_part

        else:
            ineq_part = 0

        if self.eq_aux_func is not None:
            aux_grad = self.h.gradient(x)
            aux_hess = self.h.hessian(x)

            eq_part = np.zeros((self.dimension(), self.dimension()))

            # TODO (Feres) tirar o for
            for i in range(self.h.n_functions):
                eq_part += (
                    (aux_hess[i] * self.eq_aux_func.eval(x)[i]) +
                    np.dot(aux_grad[0], aux_grad[0].transpose())
                )

            eq_part = self.rho * eq_part

        else:
            eq_part = 0

        return self.f_obj.hessian(x) + eq_part + ineq_part

    def dimension(self):
        return self.f_obj.dimension()

    def __init__(self, f_obj, g, h, rho, c):
        """
        Initialize functions and multipliers properly
        Args:
            f_obj: (FunctionsComposite) objective function
            g: (FunctionsComposite) inequality constraints
            h: (FunctionsComposite) inequality constraints
            rho: (float) initial rho value (penalty parameter)
            c: (float) constant used to update rho value
        """
        self.f_obj = f_obj
        self.g = g
        self.h = h

        self.lag_eq = np.zeros((h.n_functions, 1))  # lagrangian multipliers (equality constraints)
        self.lag_ineq = np.zeros((g.n_functions, 1))  # lagrangian multipliers (equality constraints)

        self.rho = rho
        self.c = c

        self.update_aux_functions()

    def update_aux_functions(self):
        """
        Uses current multipliers and rho value to update auxiliary functions use to evaluate function

        Returns:

        """
        self.aux_rho = LinearFunction(c=np.zeros((self.dimension(), 1)), d=self.rho)

        aux_lag_eq = FunctionsComposite()
        for aux in self.lag_eq:
            aux_lag_eq.add(LinearFunction(
                c=np.zeros((self.dimension(), 1)), d=aux
            ))

        aux_lag_ineq = FunctionsComposite()
        for aux in self.lag_ineq:
            aux_lag_ineq.add(LinearFunction(
                c=np.zeros((self.dimension(), 1)), d=aux
            ))

        if self.h.n_functions > 0:
            self.eq_aux_func = (self.h + aux_lag_eq / self.aux_rho)

        if self.g.n_functions > 0:
            self.ineq_aux_func = (self.g + aux_lag_ineq / self.aux_rho)

    def update_multipliers(self, x_new):
        """
        Uses current point to update lagrange multipliers properly
        Args:
            x_new: (np array) new point found by the unconstrained optimization

        Returns:

        """
        h_val = self.h.eval(x_new)
        self.lag_eq = self.lag_eq + self.rho * h_val

        g_val = self.g.eval(x_new)
        self.lag_ineq = self.lag_ineq + self.rho * g_val
        self.lag_ineq[self.lag_ineq < 0] = 0

        # TODO (Feres) adicionar condicional aqui
        self.rho = self.c * self.rho

        self.update_aux_functions()
