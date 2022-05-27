from abc import ABC, abstractmethod
import numpy as np
import lhcb_ftcalib.link_functions as link_functions


def p_conversion_matrix(npar):
    r""" Returns matrix :math:`C` that converts internal representation of
        parameters into the traditional form
        :math:`C\cdot (p^+_0,\cdots, p^+_n, p^-_0,\cdots,p^-_n) = (p_0,\cdots, p_n, \Delta p_0,\cdots,\Delta p_n)`

        :param npar: number of calibration parameters per flavour
        :type npar: int
        :return: parameter transformation
        :rtype: numpy.ndarray
    """
    upper = np.concatenate([0.5 * np.eye(npar), 0.5 * np.eye(npar)]).T
    lower = np.concatenate([np.eye(npar), -np.eye(npar)]).T
    return np.concatenate([upper, lower])


class CalibrationFunction(ABC):
    r"""
    Calibration function abstract base type. All calibration classes should inherit from this type.
    Calibration functions receive calibration parameters in the following order

    params :math:`= (p^+_0,\cdots, p^+_n, p^-_0,\cdots,p^-_n)`
    """

    def __init__(self, npar, link):
        self.npar = npar
        self.param_names        = [f"p{i}+" for i in range(npar)]
        self.param_names       += [f"p{i}-" for i in range(npar)]
        self.param_names_delta  = [f"p{i}"  for i in range(npar)]
        self.param_names_delta += [f"Dp{i}" for i in range(npar)]
        self.link = link
        self.basis = None  # Function specific basis representation

    def __eq__(self, other):
        equal = True
        equal &= self.npar == other.npar
        equal &= self.param_names == other.param_names
        equal &= self.param_names_delta == other.param_names_delta
        equal &= self.link == other.link
        equal &= len(self.basis) == len(other.basis)
        if equal:
            for b in range(len(self.basis)):
                equal &= np.array_equal(self.basis[b], other.basis[b])
        return equal

    @abstractmethod
    def print_basis(self):
        """ Pretty printer for the calibration basis """
        print("no basis")

    @abstractmethod
    def eval(self, params, eta, dec):
        """ Evaluate the calibration function

            :param params: Calibration function parameters
            :type params: list
            :param eta: Mistags
            :type eta: numpy.ndarray
            :param dec: Tagging decisions
            :type dec: numpy.ndarray
            :return: Calibrated mistags
            :return type: numpy.ndarray
        """
        print("no basis")

    @abstractmethod
    def init_basis(self, eta, weight=None):
        """ Initializer for the calibration function basis.
            Must be called before a calibration function is evaluated

            :param eta: Mistags
            :type eta: numpy.ndarray
            :param weight: Event weights
            :type weight: numpy.ndarray
        """
        pass

    @abstractmethod
    def eval_ignore_delta(self, params, eta):
        r""" Evaluate the calibration function and ignore differences of
            flavour specific calibrations

            :param params: Mean calibration function parameters :math:`[p_0,\cdots,p_n]`
            :type params: list
            :param eta: Mistags
            :type eta: numpy.ndarray
            :return: Calibrated mistags
            :return type: numpy.ndarray
        """
        pass

    @abstractmethod
    def eval_plotting(self, params, eta, dec):
        """ Compute the combined lineshape of the flavour specific calibration components (for plotting).

            :param params: Calibration function parameters
            :type params: list
            :param eta: Mistags
            :type eta: numpy.ndarray
            :param dec: Tagging decisions
            :type dec: numpy.ndarray
            :return: Calibrated mistags
            :return type: numpy.ndarray
        """
        pass

    @abstractmethod
    def derivative(self, partial, params, eta, dec):
        """ Evaluate the partial derivative w.r.t. one of the calibration parameters.

            :param partial: :math:`n`-th calibration parameter
            :type partial: int
            :param params: Calibration function parameters
            :type params: list
            :param eta: Mistags
            :type eta: numpy.ndarray
            :param dec: Tagging decisions
            :type dec: numpy.ndarray
            :return: Calibration function partial derivative
            :return type: numpy.ndarray
        """
        pass

    def gradient(self, params, eta, dec):
        """ Evaluate the calibration function gradient w.r.t. to the set of calibration parameters

            :param params: Calibration function parameters
            :type params: list
            :param eta: Mistags
            :type eta: numpy.ndarray
            :param dec: Tagging decisions
            :type dec: numpy.ndarray
            :return: List of all calibration function partial derivatives
            :return type: numpy.ndarray
        """
        return np.array([self.derivative(i, params, eta, dec) for i in range(self.npar * 2)])


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

    def eval_ignore_delta(self, params, eta):
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

    def gradient(self, params, eta, dec):
        return np.array([self.derivative(i, params, eta, dec) for i in range(self.npar * 2)])

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

    def eval_ignore_delta(self, params, eta):
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


class BSplineCalibration(CalibrationFunction):
    r""" BSplineCalibration
        Cubic spline calibration function. Cubic splines are uniquely determined
        by a set of :math:`\mathrm{npar} - 2` node positions. By default, the nodes are positioned
        at the :math:`q\in[1/n, 2/n, \cdots, (n-1)/n]` quantiles of the mistag distribution
        for :math:`n-2` given nodes.

        :math:`\displaystyle\omega(\eta)=g\left(g^{-1}(\eta) + \sum_{j=1}^mp_j s_j(\eta)\right)`

        whereby :math:`s_j(\eta)` is the :math:`j`-th cubic basis spline.

        :param npar: Number of parameters per predicted flavour. Must be >= 4.
        :type npar: int
        :param link: Link function
        :type link: ft.link_functions.link_function
    """

    def __init__(self, npar, link):
        CalibrationFunction.__init__(self, npar, link)
        # From: T.Hastie, R. Tibshirani, J. Friedman "The Elements of Statistical Learning"
        # Springer Learning Series. Chapter: "Appendix: Computations for Splines"
        assert npar >= 4
        self.nnodes = npar - 2

        # Initialize non-orthogonal basis
        self.basis = np.eye(self.nnodes)
        self.nodes = np.linspace(0, 0.5, self.nnodes)

        self._tau = np.zeros(self.nnodes + 6)

    def init_basis(self, eta, weight=None):
        """
        Initializer for cubic spline node positions.

        :param eta: Mistags
        :type eta: numpy.ndarray
        :param weight: Unused
        :type weight: None
        """
        self.nodes = np.quantile(eta, np.linspace(0, 1, self.nnodes))

        self._tau[:3] = self.nodes[0]
        self._tau[3:self.nnodes + 3] = self.nodes
        self._tau[self.nnodes + 3: self.nnodes + 6] = self.nodes[-1]

    def set_basis(self, nodes):
        r"""
        Setter for cubic spline node positions

        :param nodes: list of node positions for the cubic spline model.
        :type nodes: list of lists
        """
        assert len(nodes) == self.npar - 2, "#nodes = #parameters - 2"
        self.nodes = np.sort(np.array(nodes))

        self._tau[:3] = self.nodes[0]
        self._tau[3:self.nnodes + 3] = self.nodes
        self._tau[self.nnodes + 3: self.nnodes + 6] = self.nodes[-1]

    def _basis_splines(self, eta, weight=None):
        clamp_eta = np.clip(eta, self.nodes[0], self.nodes[-1])

        b1 = np.zeros((self.nnodes + 5, len(eta)))
        b2 = np.zeros((self.nnodes + 4, len(eta)))
        b3 = np.zeros((self.nnodes + 3, len(eta)))
        b4 = np.zeros((self.nnodes + 2, len(eta)))

        tau = self._tau

        for i in range(self.nnodes + 5):
            b1[i][(clamp_eta >= tau[i]) & (clamp_eta < tau[i + 1])] = 1

        for i in range(self.nnodes + 4):
            bset = b1[i] > 0
            bnextset = b1[i + 1] > 0
            b2[i][bset] += (clamp_eta[bset] - tau[i]) / (tau[i + 1] - tau[i]) * b1[i][bset]
            b2[i][bnextset] += (tau[i + 2] - clamp_eta[bnextset]) / (tau[i + 2] - tau[i + 1]) * b1[i + 1][bnextset]

        for i in range(self.nnodes + 3):
            bset = b2[i] > 0
            bnextset = b2[i + 1] > 0
            b3[i][bset] += (clamp_eta[bset] - tau[i]) / (tau[i + 2] - tau[i]) * b2[i][bset]
            b3[i][bnextset] += (tau[i + 3] - clamp_eta[bnextset]) / (tau[i + 3] - tau[i + 1]) * b2[i + 1][bnextset]

        for i in range(self.nnodes + 2):
            bset = b3[i] > 0
            bnextset = b3[i + 1] > 0
            b4[i][bset] += (clamp_eta[bset] - tau[i]) / (tau[i + 3] - tau[i]) * b3[i][bset]
            b4[i][bnextset] += (tau[i + 4] - clamp_eta[bnextset]) / (tau[i + 4] - tau[i + 1]) * b3[i + 1][bnextset]

        return b4

    def eval(self, params, eta, dec):
        basis_splines = self._basis_splines(eta)
        omega = self.link.InvL(eta)

        for i in range(self.npar):
            omega[dec == +1] += params[i]             * basis_splines[i][dec == +1]
            omega[dec == -1] += params[i + self.npar] * basis_splines[i][dec == -1]

        return self.link.L(omega)

    def eval_ignore_delta(self, params, eta):
        basis_splines = self._basis_splines(eta)
        omega = self.link.InvL(eta)

        for i in range(self.npar):
            omega += params[i] * basis_splines[i]

        return self.link.L(omega)

    def eval_plotting(self, params, eta, dec):
        basis_splines = self._basis_splines(eta)

        n_pos = np.sum(dec ==  1)
        n_neg = np.sum(dec == -1)
        f = n_pos / (n_pos + n_neg)

        omega = self.link.InvL(eta)

        for i in range(self.npar):
            omega += (f * params[i] + (1 - f) * params[i + self.npar]) * basis_splines[i]

        return self.link.L(omega)

    def derivative(self, partial, params, eta, dec):
        basis_splines = self._basis_splines(eta)

        D = self.link.DL(self.link.InvL(self.eval(params, eta, dec)))

        if partial < self.npar:
            D[dec ==  1] *= basis_splines[partial][dec == +1]
            D[dec == -1] = 0
        else:
            D[dec == -1] *= basis_splines[partial - self.npar][dec == -1]
            D[dec ==  1] = 0

        return D

    def print_basis(self):
        print("BSpline node positions:", ", ".join([str(n) for n in self.nodes]))
