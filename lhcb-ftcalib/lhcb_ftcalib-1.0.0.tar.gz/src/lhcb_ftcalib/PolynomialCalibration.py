import numpy as np
from .CalibrationFunction import CalibrationFunction
from . import link_functions


class PolynomialCalibration(CalibrationFunction):
    r""" PolynomialCalibration
        GLM for polynomial calibrations

        :math:`\displaystyle\omega(\eta)=g\left(g^{-1}(\eta) + \sum_{i=0}^mp_iP_i\right)`

        with orthogonal polynominal basis coefficient :math:`c_i=\sum_{k=0}^m B_{ik}g^{-1}(\eta)^k` with link function :math:`g`, linear parameters :math:`p_i` basis coefficients :math:`B_{ik}` and total
        number of parameters m.

        :param npar: number of calibration parameters per flavour
        :type npar: int
    """

    def __init__(self, npar, link):
        CalibrationFunction.__init__(self, npar, link)

        assert npar > 1

        # Initialize monomial basis {1, x, x^2, ...}
        self.basis = []  #: List of polynomial coefficient lists for calibration parameters
        for b in range(npar):
            self.basis.append(np.zeros(b + 1))
            self.basis[-1][0] = 1

    def set_basis(self, basis):
        r"""
        Setter for GLM basis coefficients

        The n-th provided coefficient vector will form a basis vector :math:`c_n` for parameter :math:`p_n` in the form of
        :math:`c_n=\sum_{k=0}^mB_{nk}g^{-1}(\eta)^{m - k - 1}`

        :param basis: list of polynomial basis coefficient for each linear calibration parameter.
        :type basis: list of lists
        :return: Calibrated mistags
        :return type: numpy.ndarray
        """
        self.basis = basis

    def init_basis(self, eta, weight=None):
        r"""
        Computes a mistag-density dependent basis of ortogonal polynomials (called by Tagger classes)
        :math:`\{P_n\}` for the scalar product :math:`\langle P_k,P_j
        \rangle=\sum_{n=1}^NP_k(\eta_n)P_j(\eta_n)w_n \gamma_n=\delta_{kj}`
        whereby :math:`w` is an event weight and :math:`\gamma` is an
        additional weight depending on the specified link. By default the
        monomial (not orthogonal) basis :math:`\{1, \eta, \cdots, \eta^n\}` is used.

        :param eta: Raw mistag
        :type eta: numpy.ndarray
        :param weight: Event weight
        :type weight: numpy.ndarray
        """
        moments = np.zeros((self.npar, self.npar))
        if weight is None:
            weight = np.ones(len(eta))

        if self.link != link_functions.mistag:
            denom = eta * (1 - eta) * self.link.DInvL(eta) ** 2
        else:
            denom = 1

        for i in range(self.npar):
            for j in range(self.npar):
                moments[i][j] = np.average(self.link.InvL(eta) ** (i + j) / denom, weights=weight)

        def prod(v1, v2):
            s = 0
            for i in range(self.npar):
                for j in range(self.npar):
                    s += v1[i] * v2[j] * moments[i][j]
            return s

        # Gram Schmidt
        basis = np.eye(self.npar)
        for i in range(self.npar):
            basis[i] /= np.sqrt(prod(basis[i], basis[i]))

            for j in range(i + 1, self.npar):
                basis[j] -= basis[i] * prod(basis[i], basis[j])

        for i in range(self.npar):
            basis[i] /= basis[i][i]

        basis = list(basis)
        for i in range(self.npar):
            basis[i] = basis[i][:i + 1][::-1]

        self.basis = basis

    def eval(self, params, eta, dec):
        omega = self.link.InvL(eta)
        for p in range(self.npar):
            omega[dec == +1] += params[p]             * np.polyval(self.basis[p], self.link.InvL(eta[dec == +1]))
            omega[dec == -1] += params[p + self.npar] * np.polyval(self.basis[p], self.link.InvL(eta[dec == -1]))
        return self.link.L(omega)

    def eval_averaged(self, params, eta):
        omega = self.link.InvL(eta)
        for p in range(self.npar):
            omega += params[p] * np.polyval(self.basis[p], self.link.InvL(eta))
        return self.link.L(omega)

    def eval_plotting(self, params, eta, dec):
        n_pos = np.sum(dec ==  1)
        n_neg = np.sum(dec == -1)
        f = n_pos / (n_pos + n_neg)

        omega = self.link.InvL(eta)

        for p in range(self.npar):
            omega += (f * params[p] + (1 - f) * params[p + self.npar]) * np.polyval(self.basis[p], self.link.InvL(eta))

        return self.link.L(omega)

    def derivative(self, partial, params, eta, dec):
        D = self.link.DL(self.link.InvL(self.eval(params, eta, dec)))

        if partial < self.npar:
            D[dec ==  1] *= np.polyval(self.basis[partial], self.link.InvL(eta[dec == +1]))
            D[dec == -1] = 0
        else:
            D[dec == -1] *= np.polyval(self.basis[partial - self.npar], self.link.InvL(eta[dec == -1]))
            D[dec ==  1] = 0

        return D

    def derivative_averaged(self, partial, params, eta):
        D = self.link.DL(self.link.InvL(self.eval_averaged(params, eta)))
        D *= np.polyval(self.basis[partial], self.link.InvL(eta))

        return D

    def gradient(self, params, eta, dec):
        return np.array([self.derivative(i, params, eta, dec) for i in range(self.npar * 2)])

    def gradient_averaged(self, params, eta):
        return np.array([self.derivative_averaged(i, params, eta) for i in range(self.npar)])

    def print_basis(self):
        def fmt_exp(param, ex):
            if param == 0.0:
                return ""
            elif ex == 0:
                return "1" if param == 1.0 else "{0:+.4f}".format(param)
            elif ex == 1:
                return "x" if param == 1.0 else "{0:+.4f}·x".format(param)
            else:
                num = "x" if param == 1.0 else "{0:+.4f}·x".format(param)
                return num + ''.join(['⁰¹²³⁴⁵⁶⁷⁸⁹'[int(e)] for e in str(ex)])

        for i, coeff in enumerate(self.basis):
            print(f"P_{i}(x) = {fmt_exp(coeff[0], i)} ", end="")
            for j, c in enumerate(coeff[1:]):
                print(f"{fmt_exp(c, len(coeff) - j - 2)} ", end="")
            print()
