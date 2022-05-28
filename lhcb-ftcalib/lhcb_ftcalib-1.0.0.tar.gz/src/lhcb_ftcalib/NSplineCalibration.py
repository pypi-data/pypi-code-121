import numpy as np
from .CalibrationFunction import CalibrationFunction
from . import link_functions


class NSplineCalibration(CalibrationFunction):
    r""" NSplineCalibration
        Cubic spline GLM

        :math:`\displaystyle\omega(\eta)=g\left(g^{-1}(\eta) + \sum_{i=0}^mp_ic_ib_i\right)`

        with calibration parameters :math:`p_i`, orthogonal spline basis coefficients :math:`c_i` and spline basis vectors :math:`b_i`.
        By default, the nodes are positioned at the :math:`q\in[1/n, 2/n, \cdots, (n+1)/n]` quantiles of the mistag distribution
        for :math:`n+2` given nodes.

        :param npar: number of calibration parameters per flavour
        :type npar: int
    """

    def __init__(self, npar, link):
        CalibrationFunction.__init__(self, npar + 2, link)

        assert npar >= 0

        # Initialize non-orthogonal basis
        self.basis = np.eye(self.npar)
        self.nodes = np.sort(link.InvL(np.linspace(0, 0.5, self.npar)))

    def init_basis(self, eta, weight=None):
        r"""
        Computes a mistag-density dependent basis of ortogonal cubic splines (called by Tagger classes)
        :math:`\{S_n\}` for the scalar product :math:`\langle S_k,S_j
        \rangle=\sum_{n=1}^NS_k(\eta_n)S_j(\eta_n)w_n \gamma_n=\delta_{kj}`
        whereby :math:`w` is an event weight and :math:`\gamma` is an
        additional weight depending on the specified link. By default no basis
        is initialized and calibration function is not callable.

        :param eta: Raw mistag
        :type eta: list
        :param weight: Event weight
        :type weight: list
        """
        self.nodes = np.sort(self.link.InvL(np.quantile(eta, np.linspace(0, 1, self.npar))))

        deg = self.npar
        moments = np.zeros((deg, deg))
        if weight is None:
            weight = np.ones(len(eta))

        if self.link != link_functions.mistag:
            denom = eta * (1 - eta) * self.link.DInvL(eta) ** 2
        else:
            denom = 1

        basis_values = self.__get_basis_values_for_identity(self.link.InvL(eta))

        for i in range(deg):
            for j in range(deg):
                moments[i][j] = np.sum(basis_values[i] * basis_values[j] * weight / denom)
        moments /= np.sum(weight)

        def prod(v1, v2):
            s = 0
            for i in range(deg):
                for j in range(deg):
                    s += v1[i] * v2[j] * moments[i][j]
            return s

        # Gram Schmidt
        basis = np.eye(deg)
        for i in range(deg):
            basis[i] /= np.sqrt(prod(basis[i], basis[i]))

            for j in range(i + 1, deg):
                basis[j] -= basis[i] * prod(basis[i], basis[j])

        for i in range(deg):
            basis[i] /= basis[i][i]

        basis = list(basis)
        for i in range(deg):
            basis[i] = basis[i][:i + 1][::-1]

        self.basis = basis

    def set_basis(self, basis, nodes):
        self.basis = basis
        self.nodes = np.sort(nodes)

    def __get_basis_values_for_identity(self, eta):
        # Computes spline basis coefficients {1, x, n2(x), n3(x), ...} for identity basis
        cub = (self.npar) * [None]
        # Basic cubic spline
        for s in range(self.npar):
            cub[s] = (eta - self.nodes[s]) ** 3
            cub[s][eta < self.nodes[s]] = 0.0

        # Boundary conditions
        last = self.npar - 1
        for s in range(self.npar - 1):
            cub[s] = cub[s] - cub[last]
            cub[s] /= self.nodes[last] - self.nodes[s]

        # Basis coefficients
        basis_values = np.zeros((self.npar, len(eta)))
        basis_values[0] = np.ones(len(eta))
        basis_values[1] = eta
        for s in range(self.npar - 2):
            basis_values[s + 2] = cub[s] - cub[last - 1]

        return basis_values

    def eval(self, params, eta, dec):
        basis_values = self.__get_basis_values_for_identity(self.link.InvL(eta))
        omega = self.link.InvL(eta)

        for p, bvec in enumerate(self.basis):
            for k, basis_coeff in enumerate(reversed(bvec)):
                omega[dec == +1] += params[p]             * basis_coeff * basis_values[k][dec == +1]
                omega[dec == -1] += params[p + self.npar] * basis_coeff * basis_values[k][dec == -1]

        return self.link.L(omega)

    def eval_averaged(self, params, eta):
        basis_values = self.__get_basis_values_for_identity(self.link.InvL(eta))
        omega = self.link.InvL(eta)

        for p, bvec in enumerate(self.basis):
            for k, basis_coeff in enumerate(reversed(bvec)):
                omega += params[p] * basis_coeff * basis_values[k]

        return self.link.L(omega)

    def eval_plotting(self, params, eta, dec):
        n_pos = np.sum(dec ==  1)
        n_neg = np.sum(dec == -1)
        f = n_pos / (n_pos + n_neg)

        omega = self.link.InvL(eta)

        basis_values = self.__get_basis_values_for_identity(self.link.InvL(eta))
        for p, bvec in enumerate(self.basis):
            for k, basis_coeff in enumerate(reversed(bvec)):
                omega += (f * params[p] + (1 - f) * params[p + self.npar]) * basis_coeff * basis_values[k]

        return self.link.L(omega)

    def derivative(self, partial, params, eta, dec):
        D_outer = self.link.DL(self.link.InvL(self.eval(params, eta, dec)))
        basis_values = self.__get_basis_values_for_identity(self.link.InvL(eta))

        D_inner = np.zeros(len(eta))
        if partial < self.npar:
            for k, basis_coeff in enumerate(reversed(self.basis[partial])):
                D_inner[dec == +1] += basis_coeff * basis_values[k][dec == +1]
        else:
            for k, basis_coeff in enumerate(reversed(self.basis[partial - self.npar])):
                D_inner[dec == -1] += basis_coeff * basis_values[k][dec == -1]

        return D_outer * D_inner

    def derivative_averaged(self, partial, params, eta):
        D_outer = self.link.DL(self.link.InvL(self.eval_averaged(params, eta)))
        basis_values = self.__get_basis_values_for_identity(self.link.InvL(eta))

        D_inner = np.zeros(len(eta))
        for k, basis_coeff in enumerate(reversed(self.basis[partial])):
            D_inner += basis_coeff * basis_values[k]

        return D_outer * D_inner

    def print_basis(self):
        print("Spline node positions (mistag quantiles)")
        print(", ".join([str(np.round(n, 4)) for n in self.nodes]))

        def fmt_exp(coeff, i, N):
            ex = ""
            if N - i - 1 == 0:
                ex = "1" if coeff == 1.0 else "{0:+.4f}".format(coeff)
            elif N - i - 1 == 1:
                ex = "x" if coeff == 1.0 else "{0:+.4f}·x".format(coeff)
            elif N - i - 1 > 1:
                ex = f"n{N - i - 1}(x)"
                if i > 0:
                    ex = "{0:+.4f}·".format(coeff) + ex
            return ex

        print("Spline basis")
        for i, bvec in enumerate(self.basis):
            print(f"S_{i}(x) = {fmt_exp(bvec[0], 0, len(bvec))}", end=" ")
            for c, coeff in enumerate(bvec[1:]):
                print(fmt_exp(coeff, c + 1, len(bvec)), end=" ")
            print()
