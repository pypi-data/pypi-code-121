import numpy as np
from .CalibrationFunction import CalibrationFunction


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

    def eval_averaged(self, params, eta):
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

    def derivative_averaged(self, partial, params, eta):
        basis_splines = self._basis_splines(eta)

        D = self.link.DL(self.link.InvL(self.eval_averaged(params, eta)))
        D *= basis_splines[partial]

        return D

    def print_basis(self):
        print("BSpline node positions:", ", ".join([str(n) for n in self.nodes]))
