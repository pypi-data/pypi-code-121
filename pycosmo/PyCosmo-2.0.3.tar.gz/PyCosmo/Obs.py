# This file is part of PyCosmo, a multipurpose cosmology calculation tool in Python.
#
# Copyright (C) 2013-2021 ETH Zurich, Institute for Particle and Astrophysics and SIS
# ID.
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.


from functools import partial

import numpy as np

from ._scipy_utils import interp1d

try:
    profile
except NameError:

    def profile(x):
        return x


class Obs(object):
    r"""
    The class is used to create an instance that is needed to calculate the observables,
    containing information about experiments and surveys. In this way the
    :class:`PyCosmo.Obs` class acts at the same level as the
    :class:`PyCosmo.Cosmo` class and is initialised using a parameter file or a set of
    parameters. As shown also in the Section *Usage* of the documentation, the following
    example illustrates how to instantiate the :class:`PyCosmo.Obs` class to compute the
    lensing power spectrum :math:`C_{\ell}^{\gamma \gamma}`:

    .. code-block:: python

            # PyCosmo instance
            cosmo = PyCosmo.Cosmo()

            # Set the fitting functions for the power spectrum
            cosmo.set(pk_type = 'EH')
            cosmo.set(pk_nonlin_type = 'rev_halofit')

            # Information about the observables
            # Note: 'perturb': 'nonlinear' can be replaced with 'linear' by the user.
            clparams = {'nz': ['smail', 'smail'],
                        'z0': 1.13,
                        'beta': 2.,
                        'alpha': 2.,
                        'probes': ['gamma', 'gamma'],
                        'perturb': 'nonlinear',
                        'normalised': False,
                        'bias': 1.,
                        'm': 0,
                        'z_grid': np.array([0.0001, 5., 1000])
                        }

            # Obs instance
            obs = PyCosmo.Obs()

            # Cls computation
            cls_haloEH = obs.cl(ells, cosmo, clparams)

    where the function :meth:`cl` is documented below.

    .. Warning ::
        Obs not supported by the Boltzmann solver yet, since it uses the Projection
        class.  Calling any function from this module while using the Boltzmann solver
        (pk_type = 'boltz') will return **ValueError: you must set pk_nonlin_type to
        access projections**
    """

    def __init__(self):
        pass

    def setup(self, obsparams):
        """
        Sets the multiplicative calibration parameters as defined in the dictionary
        *obsparams*.

        :param obsparams: dictionary containing specifications for the observables
        """

        # Ensure that the galaxy bias and the multiplicative bias are defined
        # If not, set them to 1
        if "bias" not in obsparams:
            print("WARNING: Setting bias to 1.")
            obsparams["bias"] = 1.0
        if "m" not in obsparams:
            print("WARNING: Setting m to 0.")
            obsparams["m"] = 0.0
        if "Akcmb" not in obsparams:
            print("WARNING: Setting Akcmb to 1.")
            obsparams["Akcmb"] = 1.0
        if "RSD" not in obsparams:
            obsparams["RSD"] = False
            print("WARNING: Ignoring RSD for galaxy clustering.")

        if "A_IA" not in obsparams:
            obsparams["A_IA"] = 0.0
        if "z0_IA" not in obsparams:
            obsparams["z0_IA"] = 0.0
        if "eta_IA" not in obsparams:
            obsparams["eta_IA"] = 0.0

        self._enrich_params(obsparams)
        self.windows(obsparams)

    def print_params(self):
        pass

    def _enrich_params(self, obsparams):
        """
        Set undefined parameters to default or interpreted values.

        :param obsparams: dictionary containing specifications for observable
        :return:
        """

        if "nztype" not in obsparams:
            obsparams["nztype"] = [None, None]

        if "IAmodel" not in obsparams:
            print("Setting intrinsic alignment model to NLA...")
            obsparams["IAmodel"] = "NLA"
        if "fzmodel" not in obsparams:
            print(
                "Setting F(z) model to corrected version according to"
                " Hirata & Seljak 2010."
            )
            obsparams["fzmodel"] = "corr"

        obsparams["a_grid"] = [
            1.0 / (1.0 + obsparams["z_grid"][0]),
            1.0 / (1.0 + obsparams["z_grid"][1]),
            obsparams["z_grid"][2],
        ]

    def nz(self, obsparams, nzmode=None, path2zdist=None):
        """
        Computes and normalises the redshift selection-function of a survey.

        :param obsparams: dictionary containing specifications for the observables
        :param nzmode: string tag in [``smail``, ``cfhtlens``, ``custom``]
        :param path2zdist: if :math:`n(z)` comes from a file, then this is the path to
                           the file
        :param z: redshift grid
        :return: Corresponding normalised redshift selection-function,
                 :math:`P(z)_{|norm}`.
        """

        # Todo need to think about default of a (like the Cosmo Class) or z?

        distribution_type = ["smail", "cfhtlens", "custom"]

        assert nzmode.lower() in distribution_type, (
            "The redshift distribution type in input parameters is not recognised."
            " Use one of the following: \n %s " % distribution_type
        )

        if nzmode.lower() == "smail":
            assert set(["z0", "alpha", "beta"]).issubset(obsparams), (
                "Make sure the Smail distribution parameters z0, alpha and beta"
                " are included in obsparams."
            )

            num_points = int(obsparams["z_grid"][2])
            z = np.linspace(obsparams["z_grid"][0], obsparams["z_grid"][1], num_points)
            pz = (
                np.exp(-((z / obsparams["z0"]) ** obsparams["beta"]))
                * z ** obsparams["alpha"]
            )

        elif nzmode.lower() == "cfhtlens":
            data = np.genfromtxt(path2zdist)

            z_grid = (data[:, 0][:-1] + data[:, 0][1:]) / 2.0
            z = np.append(z_grid, data[:, 0][-1])
            pz = data[:, 1]

        elif nzmode.lower() == "custom":
            datafile = np.genfromtxt(path2zdist)

            z = datafile[:, 0]
            pz = datafile[:, 1]

        else:
            z = None
            pz = None

        if z is not None:
            norm = np.trapz(pz, z)

            pz_norm = pz / norm

            # Assert that the normalisation worked
            intg = np.trapz(pz_norm, z)
            assert np.abs(intg - 1.0) <= 10 ** (
                -8
            ), "Normalisation failed to reach required accuracy."

        else:
            pz_norm = pz

        return z, pz_norm

    def bin_setup(self, obsparams):
        """
        Set up the redshift selection functions, i.e. each redshift selection function
        is either calculated from the default hard coded ones or the tabulated selection
        functions are read in and saved as attributes in self.n.

        :param obsparams: dictionary containing specifications for observable
        :return:
        """

        self.n = [0, 0]
        for i in range(len(obsparams["probes"])):
            nzmode = obsparams["nz"][i]
            if nzmode is not None:
                print(
                    "Setting up galaxy selection function for {}.".format(
                        obsparams["probes"][i]
                    )
                )
                if nzmode in ["cfhtlens", "custom"]:
                    path2zdist = obsparams["path2zdist"][i]
                    z, selec = self.nz(obsparams, nzmode, path2zdist)
                else:
                    z, selec = self.nz(obsparams, nzmode)
                self.n[i] = interp1d(z, selec, bounds_error=False, fill_value=0.0)
            else:
                self.n[i] = None

    def windows(self, obsparams):
        r"""
        Sets up the radial window functions for the surveys and the
        probes, i.e., computes the window functions appropriate
        for the galaxy overdensity, :math:`\gamma`, CMB temperature
        and CMB :math:`- \kappa` and saves them in the attribute self.window.

        :param obsparams: dictionary containing specifications for observable
        :return window: radial window function
        """

        # Read in the redshift selection functions when the class is initialised
        self.bin_setup(obsparams)

        print("Setting up redshift window function...")
        self.window = [0, 0]
        for i in range(len(obsparams["probes"])):
            probe = obsparams["probes"][i]
            if probe == "deltag":
                self.window[i] = partial(self._weight_function_clustering, n=self.n[i])
            elif probe == "gamma":
                self.window[i] = partial(self._weight_function_lensing, n=self.n[i])
            elif probe == "temp":
                self.window[i] = self._weight_function_cmbtemp
            elif probe == "cmbkappa":
                if "zrecomb" in obsparams:
                    self.zrecomb = obsparams["zrecomb"]
                else:
                    print(
                        "You have chosen to compute cls involving CMB kappa."
                        " This needs a recombination redshift."
                        " Please set it using the zrecomb keyword in params."
                    )
                self.window[i] = self._weight_function_cmblensing

    def _weight_function_cmblensing(self, a, cosmo):
        """
        Compute the radial weight function for CMB lensing as a function of scale factor
        a as

        W^kappa_CMB(a) =
               3/2 Omega_m (H0/c)^2 r(chi)(a)/a (r(chi)(a_*)-r(chi)(a))/r(chi)(a_*).

        This will be used to calculate the weak lensing angular power spectra.

        :param a_vec: scale factor [1]
        :param cosmo: instance of :class:`PyCosmo.Cosmo` (specifies cosmological model)
        :return window: radial weight function W^CMB_kappa(a) [1]
        """

        # Compute the needed distances because they are needed multiple times
        dists = cosmo.background.dist_trans_a(a=a)
        distrecomb = cosmo.background.dist_trans_a(a=1.0 / (1.0 + self.zrecomb))

        window = (
            3.0
            / 2.0
            * (cosmo.params.H0 / cosmo.params.c) ** 2
            * cosmo.params.omega_m
            * dists
            / a
            * ((distrecomb - dists) / distrecomb)
        )

        window[a < 1.0 / (1 + self.zrecomb)] = 0.0

        return window

    def _weight_function_clustering(self, a, cosmo, n):
        """
        Calculate the radial weight functions for clustering as a function of a as

        W^delta = n(a) H(a)/c.

        This will be used to calculate the clustering angular power spectra

        :param a: scale factor [1]
        :param cosmo: instance of :class:`PyCosmo.Cosmo` (specifies cosmological model)
        :param n: callable (function) redshift distribution of survey [1]
        :return window: radial weight function W^deltag(a) [1]
        """

        z = 1.0 / a - 1.0

        window = n(z) * cosmo.background.H(a) / cosmo.params.c

        return window

    def _weight_function_cmbtemp(self, a, cosmo):
        """
        Calculate the radial weight functions for CMB temperature as a function of a as
        W^CMB = 1.
        This will be used to calculate the ISW angular power spectra

        :param a: scale factor [1]
        :param cosmo: instance of :class:`PyCosmo.Cosmo` (specifies cosmological model)
        :return window: radial weight function W^CMB(a) [1]
        """

        window = np.ones(a.shape[0])

        return window

    def _weight_function_lensing(self, a_vec, cosmo, n):
        """
        Compute the radial weight function for weak lensing as a function of scale
        factor a as

        W^gamma(a) =
            3/2 Omega_m (H0/c)^2 r(chi)(a)/a
                 int_amin^amax da_s/a_s^2 n(a_s) (r(chi)(a_s)-r(chi)(a))/r(chi)(a).

        where n is the redshift distribution of the survey.

        This will be used to calculate the weak lensing angular power spectra.
        :param a_vec: scale factor [1]
        :param cosmo: instance of :class:`PyCosmo.Cosmo` (specifies cosmological model)
        :param n: callable (function) redshift distribution of survey [1]
        :return window: radial weight function W^gamma(a) [1]
        """

        # TODO For now: hard coded amin and anum
        amin = 1.0 / 15.0
        anum = 200

        # We need to test that we do not cut off the integrals too early
        assert np.abs(n(1.0 / amin - 1.0)) <= 1e-5, (
            "There is still a significant number of galaxies at the cutoff "
            "redshift. You might try a higher cutoff."
        )

        window = []

        a_temp = np.concatenate(
            (np.linspace(amin, a_vec[0], anum, endpoint=False), a_vec)
        )
        pz = n(1.0 / a_temp - 1.0) / a_temp**2
        chi = cosmo.background.dist_rad_a(a=a_temp)
        chi_a = cosmo.background.dist_rad_a(a=a_vec)
        rchi_a = cosmo.background.dist_trans_a(a=a_vec)

        for i in range(len(a_vec)):

            if cosmo.params.omega_k == 0.0:
                integrand = (
                    pz[: anum + i] * (chi[: anum + i] - chi_a[i]) / chi[: anum + i]
                )
            elif cosmo.params.omega_k < 0.0:
                integrand = (
                    pz[: anum + i]
                    * np.sin(
                        cosmo.params.sqrtk
                        * (chi[: anum + i] - chi_a[i])
                        / cosmo.params.rh
                    )
                    / np.sin(cosmo.params.sqrtk * chi[: anum + i] / cosmo.params.rh)
                )
            else:
                integrand = (
                    pz[: anum + i]
                    * np.sin(
                        cosmo.params.sqrtk
                        * (chi[: anum + i] - chi_a[i])
                        / cosmo.params.rh
                    )
                    / np.sinh(cosmo.params.sqrtk * chi[: anum + i] / cosmo.params.rh)
                )

            wind = np.trapz(integrand, a_temp[: anum + i])
            window.append(wind)
        len_wind = len(window)
        window = np.array(window).reshape(-1, len_wind)
        window *= (
            1.5
            * (cosmo.params.H0 / cosmo.params.c) ** 2
            * (cosmo.params.omega_m * rchi_a / a_vec)
        )
        window = window.reshape(len_wind)
        return window

    def _cl_lss(self, ells, cosmo, obsparams):
        """
        Calculate the cls  for LSS based on

        Cl^ij =
           int_amin^amax da
                c/(a^2 H(a)) W_i(a) W_j(a)/r(chi)(a)^2 P(k=(l+1/2)/r(chi)(a), a)

        where W is the radial weight function for clustering.

        :param ells: array of inverse angular scale [1]
        :param cosmo: instance of :class:`PyCosmo.Cosmo` (specifies cosmological model)
        :param obsparams: dictionary containing specifications for observable
        :return cls: array of spherical harmonic power spectrum coefficients Cl [1]
        """
        # Todo add dynamic setting for amin based on the weight function

        ells = np.atleast_1d(ells)

        # TODO This is for a vectorised call - need to remove at some point
        cls = cosmo.projection.cl_limber(
            ells,
            self.window[0],
            self.window[1],
            obsparams["a_grid"],
            cosmo,
            obsparams["perturb"],
        )

        if obsparams["RSD"]:
            # this sets the redshift distortion parameter used for RSD
            # denoted with beta in literature, e.g. in text after eq. (25)
            # in https://arxiv.org/pdf/astro-ph/0605302.pdf
            beta_rsd = cosmo.params.omega_m**0.6 / obsparams["bias"]

            # additional component to the window function of galaxy clustering due to
            # RSD, according to eq. (27) in https://arxiv.org/pdf/astro-ph/0605302.pdf
            rsd_corr = 1.0 + beta_rsd * (
                (2 * ells**2.0 + 2.0 * ells - 1) / ((2 * ells + 3) * (2 * ells - 1))
                - (ells * (ells - 1)) / ((2 * ells - 1) * (2 * ells + 1))
                - ((ells + 1) * (ells + 2)) / ((2 * ells + 1) * (2 * ells + 3))
            )

            if obsparams["probes"][0] == "deltag" or obsparams["probes"][1] == "deltag":
                cls *= rsd_corr

        return cls

    # TODO: These are things that potentially need to go into lin pert approx
    def growth_suba(self, cosmo, a=1.0):
        """
        Returns the growth factor divided by the scale factor a.

        :param cosmo: instance of :class:`PyCosmo.Cosmo` (specifies cosmological model)
        :param a: scale factor a
        :return: Growth factor divided by scale factor
        """

        growth_suba_temp = cosmo._lin_pert.growth_a(a=a) / a

        return growth_suba_temp

    def growth_suba_deriv(self, cosmo, a=1.0):
        """
        Returns the derivative of growth_suba by scale factor a.

        :param cosmo: instance of :class:`PyCosmo.Cosmo` (specifies cosmological model)
        :param a: scale factor a
        :return: Derivative of growth_suba w.r.t. z
        """

        delta = a * 1e-5

        growth_min2del = self.growth_suba(cosmo, a=a - 2 * delta)
        growth_min1del = self.growth_suba(cosmo, a=a - delta)
        growth_plus1del = self.growth_suba(cosmo, a=a + delta)
        growth_plus2del = self.growth_suba(cosmo, a=a + 2 * delta)

        growth_suba_deriv = (
            growth_min2del - 8 * growth_min1del + 8 * growth_plus1del - growth_plus2del
        ) / (12 * delta)

        return growth_suba_deriv

    def growth_ISW(self, a, projection, mode="num"):
        """
        Returns the generalised growth factor used in the ISW angular power spectrum
        integrand both for the analytic approximation and the numerical derivative.

        :param a: scale factor
        :param cosmo: instance of :class:`PyCosmo.Cosmo` (specifies cosmological model)
        :param mode: numerical or analytic

        :return: The value of the generalised growth factor at redshift x
        """

        if mode == "num":
            growth = projection._lin_pert.growth_a(a=a) * self.growth_suba_deriv(
                projection, a=a
            )
        elif mode == "fit":
            growth = (
                (-1.0)
                * projection._lin_pert.growth_a(a=a) ** 2
                * (projection.background._omega_m_a(a=a) ** 0.6 - 1.0)
            )

        return growth

    def _cl_ISW(self, ells, cosmo, obsparams):
        """
        Calculate the ISW cls based on

        Cl^iT = 3 Omega_m H0^2 T_CMB/c^2 1/(ell+1/2) \
                 int_1^0 da d/da [D(a)/a] D(a) W_i(a) P_lin(k=(l+1/2)/r(chi)(a), 1)

        where W_i is the radial weight function for the LSS probe.

        :param ells: array of inverse angular scale [1]
        :param cosmo: instance of :class:`PyCosmo.Cosmo` (specifies cosmological model)
        :param obsparams: dictionary containing specifications for observable
        :return: array of spherical harmonic power spectrum coefficients Cl [1]
        """
        # Todo add dynamic setting for amin based on the weight function

        ells = np.atleast_1d(ells)
        # TODO This is for a vectorised call - need to remove at some point
        cls = cosmo.projection.cl_limber_ISW(
            ells,
            self.window[0],
            self.window[1],
            self.growth_ISW,
            obsparams["a_grid"],
            obsparams["perturb"],
        )

        return cls

    def cl_multi(self, ells, cosmo, obsparams_list):
        r"""
        Calculates the C_{\ell} for the desired probes, as specified by
        the "probes" parameter in obsparams.

        :param ells: array of angular multipoles :math:`ell`
        :param cosmo: instance of :class:`PyCosmo.Cosmo` (specifies cosmological model)
        :param obsparams_list: list of dictionaries containing specifications for
                               observables
        """
        cosmo.projection._memory.clear()
        return [self._cl(ells, cosmo, obsparams) for obsparams in obsparams_list]

    def cl(self, ells, cosmo, obsparams):
        """
        Wrapper around all the other cl routines which determines from the
        obsparams dictionary for which cosmological probes the angular power
        spectrum has to be computed.

        This is especially useful when interfacing with CosmoHammer.

        :param ells: array of angular multipoles :math:`ell`
        :param cosmo: instance of :class:`PyCosmo.Cosmo` (specifies cosmological model)
        :param obsparams: dictionary containing specifications for observable
        :return: Array of values of the angular power spectrum for the desired
                     probes for ells
        """
        cosmo.projection._memory.clear()
        return self._cl(ells, cosmo, obsparams)

    def _cl(self, ells, cosmo, obsparams):

        self.setup(obsparams)

        if obsparams["probes"].count(obsparams["probes"][0]) == len(
            obsparams["probes"]
        ):
            # We want to compute an auto power spectrum
            if obsparams["probes"][0] == "deltag":
                cls = self._cl_lss(ells, cosmo, obsparams)
                # Apply a galaxy bias correction if desired
                cls *= obsparams["bias"] ** 2
            elif obsparams["probes"][0] == "gamma":
                cls = self._cl_lss(ells, cosmo, obsparams)
                if obsparams["A_IA"] != 0.0:
                    cls_IA_II = self.cl_II(ells, cosmo, obsparams)
                    cls_IA_IG = self.cl_IG(ells, cosmo, obsparams)
                    cls += cls_IA_IG + cls_IA_II

                # Apply a multiplicative bias correction of desired
                cls *= (1.0 + obsparams["m"]) ** 2
            elif obsparams["probes"][0] == "cmbkappa":
                cls = self._cl_lss(ells, cosmo, obsparams)
                # Apply a CMB lensing convergence amplitude correction if desired
                cls *= obsparams["Akcmb"] ** 2
            else:
                print(
                    "Only galaxy overdensity, cosmic shear and CMB lensing auto power"
                    " spectra supported."
                )
                return
        else:
            # We want to compute a cross power spectrum
            # First transform the list to a set; this is an unordered list which
            # can be compared to other sets without caring for the order
            probes = set(obsparams["probes"])
            if probes == set(["temp", "deltag"]):
                cls = self._cl_ISW(ells, cosmo, obsparams)
                # Apply a galaxy bias correction of desired
                cls *= obsparams["bias"]
            elif probes == set(["temp", "gamma"]):
                cls = self._cl_ISW(ells, cosmo, obsparams)
                # Apply a multiplicative bias correction of desired
                cls *= 1.0 + obsparams["m"]
            elif probes == set(["deltag", "gamma"]):
                cls = self._cl_lss(ells, cosmo, obsparams)
                # Apply a galaxy bias correction of desired
                cls *= obsparams["bias"]
                # Apply a multiplicative bias correction of desired
                cls *= 1.0 + obsparams["m"]
            elif probes == set(["temp", "cmbkappa"]):
                cls = self._cl_ISW(ells, cosmo, obsparams)
                # Apply a CMB lensing convergence amplitude correction if desired
                cls *= obsparams["Akcmb"]
            elif probes == set(["deltag", "cmbkappa"]):
                cls = self._cl_lss(ells, cosmo, obsparams)
                # Apply a galaxy bias correction of desired
                cls *= obsparams["bias"]
                # Apply a CMB lensing convergence amplitude correction if desired
                cls *= obsparams["Akcmb"]
            elif probes == set(["gamma", "cmbkappa"]):
                cls = self._cl_lss(ells, cosmo, obsparams)
                # Apply a multiplicative bias correction of desired
                cls *= 1.0 + obsparams["m"]
                # Apply a CMB lensing convergence amplitude correction if desired
                cls *= obsparams["Akcmb"]
            else:
                print(
                    "Only cross correlations between CMB temperature/CMB kappa and"
                    " galaxy density, CMB temperature/CMB kappa and cosmic shear,"
                    " galaxy density and cosmic shear and CMB temperature and CMB"
                    " kappa are currently supported."
                )
                return

        return cls

    def cl_IG(self, ells, cosmo, obsparams):
        r"""
        Calculates the angular power spectrum for GI intrinsic alignments (IAs) using
        the NLA or LA model for the multipole
        array specified by the angular multipoles :math:`\\ell`.
        The NLA implementation follows `Hildebrandt et al., 2016
        <https://arxiv.org/abs/1606.05338>`_.

        :param ells: array of angular multipoles :math:`\\ell`
        :param cosmo: instance of :class:`PyCosmo.Cosmo`
                      (it specifies the cosmological model)
        :param obsparams: dictionary containing specifications for the observables
        :return: Array of values of the angular power spectrum for GI IAs.
        """

        self.setup(obsparams)

        ells = np.atleast_1d(ells)
        F = partial(self.F, obsparams=obsparams)

        probes = set(obsparams["probes"])
        if probes == set(["gamma", "gamma"]):
            a_grid = obsparams["a_grid"]
            ia_model = obsparams["IAmodel"]
            w0, w1 = self.window
            n0, n1 = self.n
            cls1 = cosmo.projection.cl_limber_IG(ells, w0, n1, F, a_grid, ia_model)
            cls2 = cosmo.projection.cl_limber_IG(ells, w1, n0, F, a_grid, ia_model)
            cls = cls1 + cls2

            # Apply a multiplicative bias correction if desired
            cls *= (1.0 + obsparams["m"]) ** 2

        elif probes == set(["deltag", "gamma"]):
            # Cross-correlation between intrinsic alignments and galaxies causing these
            # or also tracing the DM halo
            ind1 = obsparams["probes"].index("deltag")
            ind2 = obsparams["probes"].index("gamma")
            iawindows = [0 for i in range(2)]
            iawindows[0] = self.window[ind1]
            iawindows[1] = self.n[ind2]

            cls = cosmo.projection.cl_limber_IG(
                ells,
                iawindows[0],
                iawindows[1],
                F,
                obsparams["a_grid"],
                obsparams["IAmodel"],
            )
            # Apply a galaxy bias correction of desired
            cls *= obsparams["bias"]
            # Apply a multiplicative bias correction of desired
            cls *= 1.0 + obsparams["m"]

        elif probes == set(["cmbkappa", "gamma"]):
            # Cross-correlation between intrinsic galaxy alignments and CMB convergence;
            # this is because both are produced by the same structures
            ind1 = obsparams["probes"].index("cmbkappa")
            ind2 = obsparams["probes"].index("gamma")
            iawindows = [0 for i in range(2)]
            iawindows[0] = self.window[ind1]
            iawindows[1] = self.n[ind2]

            cls = cosmo.projection.cl_limber_IG(
                ells,
                iawindows[0],
                iawindows[1],
                F,
                obsparams["a_grid"],
                obsparams["IAmodel"],
            )
            # Apply a multiplicative bias correction of desired
            cls *= 1.0 + obsparams["m"]
            # Apply a CMB lensing convergence amplitude correction if desired
            cls *= obsparams["Akcmb"]
        else:
            print(
                "Only intrinsic alignments between weak lensing/weak lensing, "
                "weak lensing/galaxy density, and weak lensing/CMB kappa are supported."
            )
            return

        return cls

    def cl_II(self, ells, cosmo, obsparams):
        r"""
        Calculates the angular power spectrum for II intrinsic alignments (IAs) using
        the NLA or LA model for the multipole array specified by :math:`\\ell`.
        The NLA implementation follows
        `Hildebrandt et al., 2016 <https://arxiv.org/abs/1606.05338>`_.

        :param ells: array of angular multipoles :math:`\\ell`
        :param cosmo: instance of :class:`PyCosmo.Cosmo` (it specifies the cosmological
                      model)
        :param obsparams: dictionary containing specifications for the observables
        :return: Array of values of the angular power spectrum for II IAs.
        """

        self.setup(obsparams)

        ells = np.atleast_1d(ells)
        F = partial(self.F, obsparams=obsparams)

        probes = set(obsparams["probes"])
        if probes == set(["gamma", "gamma"]):
            iawindows = [0 for i in range(2)]
            iawindows[0] = self.n[0]
            iawindows[1] = self.n[1]
        else:
            print("II correlation only exists for gamma x gamma.")
            return

        cls = cosmo.projection.cl_limber_II(
            ells,
            iawindows[0],
            iawindows[1],
            F,
            obsparams["a_grid"],
            obsparams["IAmodel"],
        )
        # Apply a multiplicative bias correction of desired
        cls *= (1.0 + obsparams["m"]) ** 2

        return cls

    def F(self, a, cosmo, obsparams):
        r"""
        Returns the :math:`F` function of the linear alignment model. This follows Eq.
        (8) of `Hildebrandt et al., 2016 <https://arxiv.org/abs/1606.05338>`_.
        Here we set :math:`\eta = \beta = 0`, i.e., no redshift and luminosity dependence
        is considered.

        :param a: array of scale factor values. :math:`a`
        :param cosmo: instance of :class:`PyCosmo.Cosmo` (specifies the cosmological
                      model)
        :param obsparams: dictionary containing specifications for the observables
        :return: Value of :math:`F` as a function of the scale factor :math:`a`.
        """

        C1 = self.C1(cosmo)
        rhocrit = self.rhocrit(cosmo)

        A_IA = obsparams["A_IA"]
        corrfac = A_IA if A_IA != 0 else 1.0

        if obsparams["fzmodel"] == "old":
            # Formula for f before the erratum of Hirata & Seljak, 2004 f =
            # (-1)*C1*rhocrit*cosmo.background._H2_H02_Omegam_a(a=a) /
            # (cosmo._lin_pert.growth_a(a=a)/a)
            f = (
                (-1.0)
                * corrfac
                * C1
                * rhocrit
                * cosmo.background._H2_H02_Omegam_a(a=a)
                / (cosmo._lin_pert.growth_a(a=a) / a)
            )

        elif obsparams["fzmodel"] == "corr":
            # Formula for f after correction of Hirata & Seljak, 2010
            # f = (-1)*C1*rhocrit*cosmo.params.omega_m/cosmo._lin_pert.growth_a(a=a)
            # factor = -1. * amplitude * const * rho_crit * self.Omega_m /
            # linear_growth_rate * ((1. + z) / (1. + z0))**exponent
            #
            z = (1 - a) / a
            f = (
                (-1.0)
                * corrfac
                * C1
                * rhocrit
                * cosmo.params.omega_m
                / cosmo._lin_pert.growth_a(a=a)
                * ((1.0 + z) / (1.0 + obsparams["z0_IA"])) ** obsparams["eta_IA"]
            )

        return f

    def C1(self, cosmo):
        """
        Returns th:e linear intrinsic alignment amplitude C1.

        :param cosmo: instance of PyCosmo.Cosmo (specifies cosmological model)
        :return: Linear intrinsic alignment amplitude for current value of h
        """

        c1 = 5.0 * 10**-14 * cosmo.params.h**-2 * cosmo.params.msun**-1

        return c1

    def rhocrit(self, cosmo):
        """
        Return the critical density of the Universe at a_0 = 1 (today).

        :param cosmo: instance of PyCosmo.Cosmo (specifies cosmological model)
        :return: critical density today, [rhoc] = kg/Mpc^3
        """

        rhoc = cosmo.params.rho_crit * cosmo.params.msun * cosmo.params.h**2
        return rhoc
