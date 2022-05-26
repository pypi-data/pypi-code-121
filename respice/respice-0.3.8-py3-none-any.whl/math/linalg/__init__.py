import numpy as np
from scipy.optimize import check_grad

from .TaylorPolynomial import TaylorPolynomial


def linsys_jac(x, A, dA, db):
    r"""
    Computes the Jacobian matrix of a linear system whose :math:`A` and :math:`b` parts are functions.

    Consider a linear system with a random (vector) parameter :math:`y`:

    .. math::

        A(y) x = b(y)

    When the solution :math:`x` is known, the Jacobian :math:`J_x(y)` is then:

    .. math::

        J_x(y) = A^{-1} \left( \frac{\partial b}{\partial y} - \frac{\partial A}{\partial y} x \right)

    :param x:
        The solution of :math:`A(y) x = b(y)`.
    :param A:
        Linear system matrix :math:`A(y)`.
    :param dA:
        A 3rd-order tensor containing the element-wise derivatives of each matrix entry in :math:`A(y)`
        over each :math:`y`.
    :param db:
        The derivative matrix of :math:`b(y)`.
    :return:
    """
    return np.linalg.inv(A) @ (db - (dA @ x).transpose())


def check_jacobian(func, jac, x, *args, **kwargs):
    # Obtain dimension.
    fx = func(x, *args, **kwargs)

    def func_item(x, i, *args, **kwargs):
        return func(x, *args, **kwargs)[i]

    def jac_item(x, i, *args, **kwargs):
        return jac(x, *args, **kwargs)[i]

    return np.array([check_grad(func_item, jac_item, x, i, *args, **kwargs)
                     for i in range(len(fx))])
