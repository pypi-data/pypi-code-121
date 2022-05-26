"""Implements Latent Class Mixed Model."""

from .mixed_logit import MixedLogit
import numpy as np
from scipy.optimize import minimize
import copy
import logging
# from ._device import device as dev

# define the computation boundary values not to be exceeded
min_exp_val = -700
max_exp_val = 700

max_comp_val = 1e+300
min_comp_val = 1e-300

logger = logging.getLogger(__name__)


class LatentClassMixedModel(MixedLogit):
    """Class for estimation of Latent Class Models.

    The design of this class is partly based on the LCCM package,
    https://github.com/ferasz/LCCM (El Zarwi, 2017).

    References
    ----------
    El Zarwi, F. (2017). lccm, a Python package for estimating latent
    class choice models using the Expectation Maximization (EM)
    algorithm to maximize the likelihood function.
    """
    def __init__(self):
        super(LatentClassMixedModel, self).__init__()

    def fit(self, X, y, varnames=None, alts=None, isvars=None, num_classes=2,
            class_params_spec=None, member_params_spec=None,
            transvars=None,
            transformation=None, ids=None, weights=None, avail=None,
            randvars=None, panels=None, base_alt=None, fit_intercept=False,
            init_coeff=None, maxiter=2000, random_state=None, correlation=None,
            n_draws=1000, halton=True, verbose=1, batch_size=None,
            halton_opts=None, ftol=1e-8, gtol=1e-5, gtol_membership_func=1e-5, hess=True,
            grad=True, method="bfgs"):
        """Fit multinomial and/or conditional logit models.

        Parameters
        ----------
        X : array-like, shape (n_samples, n_variables)
            Input data for explanatory variables in long format

        y : array-like, shape (n_samples,)
            Choices in long format

        varnames : list, shape (n_variables,)
            Names of explanatory variables that must match the number and
            order of columns in ``X``

        alts : array-like, shape (n_samples,)
            Alternative indexes in long format or list of alternative names

        isvars : list
            Names of individual-specific variables in ``varnames``

        num_classes: int
            Number of latent classes

        class_params_spec: array-like, shape (n_samples,)
            Array of lists containing names of variables for latent class

        member_params_spec: array-like, shape (n_samples,)
            Array of lists containing names of variables for class membership

        transvars: list, default=None
            Names of variables to apply transformation on

        ids : array-like, shape (n_samples,)
            Identifiers for choice situations in long format.

        transformation: string, default=None
            Name of transformation to apply on transvars

        randvars : dict
            Names (keys) and mixing distributions (values) of variables that
            have random parameters as coefficients. Possible mixing
            distributions are: ``'n'``: normal, ``'ln'``: lognormal,
            ``'u'``: uniform, ``'t'``: triangular, ``'tn'``: truncated normal

        weights : array-like, shape (n_variables,), default=None
            Weights for the choice situations in long format.

        avail: array-like, shape (n_samples,)
            Availability of alternatives for the choice situations. One when
            available or zero otherwise.

        base_alt : int, float or str, default=None
            Base alternative

        fit_intercept : bool, default=False
            Whether to include an intercept in the model.

        init_coeff : numpy array, shape (n_variables,), default=None
            Initial coefficients for estimation.

        maxiter : int, default=200
            Maximum number of iterations

        random_state : int, default=None
            Random seed for numpy random generator

        verbose : int, default=1
            Verbosity of messages to show during estimation. 0: No messages,
            1: Some messages, 2: All messages

        method: string, default="bfgs"
            specify optimisation method passed into scipy.optimize.minimize

        batch_size : int, default=None
            Size of batches of random draws used to avoid overflowing memory during computations.

        halton_opts : dict, default=None
            Options for generation of halton draws. The dictionary accepts the following options (keys):

                shuffle : bool, default=False
                    Whether the Halton draws should be shuffled

                drop : int, default=100
                    Number of initial Halton draws to discard to minimize correlations between Halton sequences

                primes : list
                    List of primes to be used as base for generation of Halton sequences.

        ftol : int, float, default=1e-5
            Sets the tol parameter in scipy.optimize.minimize - Tolerance for
            termination.

        gtol: int, float, default=1e-5
            Sets the gtol parameter in scipy.optimize.minimize(method="bfgs) -
            Gradient norm must be less than gtol before successful termination.

        grad : bool, default=True
            Calculate and return the gradient in _loglik_and_gradient

        hess : bool, default=True
            Calculate and return the gradient in _loglik_and_gradient

        scipy_optimisation : bool, default=False
            Use scipy_optimisation for minimisation. When false uses own
            bfgs method.

        Returns
        -------
        None.
        """
        self.ftol = ftol
        self.gtol = gtol
        self.gtol_membership_func = gtol_membership_func
        self.num_classes = num_classes

        # default to using all varnames in each latent class if not specified
        if class_params_spec is None:
            class_params_spec = np.array([])
            class_params_spec = np.vstack([varnames for i in range(num_classes)])
        self.class_params_spec = class_params_spec
        # self.class_params_spec = np.atleast_2d(class_params_spec)

        if member_params_spec is None:
            member_params_spec = np.vstack([varnames for i in range(num_classes-1)])
        self.member_params_spec = np.atleast_2d(member_params_spec)

        self.panels = panels
        self.init_df = X
        self.init_y = y
        self.ids = ids

        # TODO: MORE LOGIC
        batch_size = n_draws if batch_size is None else min(n_draws, batch_size)

        super(LatentClassMixedModel, self).fit(X, y, varnames, alts, isvars,
                                               transvars, transformation, ids,
                                               weights, avail, randvars,
                                               panels, base_alt,
                                               fit_intercept, init_coeff,
                                               maxiter, random_state,
                                               correlation, n_draws, halton,
                                               self._expectation_maximisation_algorithm,
                                               verbose, batch_size,
                                               halton_opts, ftol, gtol,
                                               hess, grad, method)

    def optimal_class_fit(self, X, y, varnames=None, alts=None, isvars=None,
                          num_classes=2, class_params_spec=None,
                          member_params_spec=None, transvars=None,
                          transformation=None, ids=None, weights=None,
                          avail=None, randvars=None, panels=None,
                          base_alt=None, fit_intercept=False, init_coeff=None,
                          maxiter=2000, random_state=None, correlation=None,
                          n_draws=1000, halton=True, verbose=1,
                          batch_size=None, halton_opts=None, ftol=1e-8,
                          gtol=1e-5, gtol_membership_func=1e-5, hess=True,
                          grad=True, method="bfgs"):
        """Find optimal number of latent classes.

        Determines optimal number of latent classes based on BIC.
        Note current implementation only considers latent classes with
        the same variables.
        """
        self.num_classes = num_classes
        self.panels = panels
        self.init_df = X
        self.init_y = y
        self.ids = ids

        curr_bic = -1
        prev_bic = 0
        model = copy.copy(self)
        num_classes = self.num_classes
        prev_model = None
        curr_model = None

        while curr_bic < prev_bic and num_classes > 1:  # lowest BIC
            class_params_spec = np.vstack([varnames for i in range(num_classes)])
            model.class_params_spec = class_params_spec

            member_params_spec = np.vstack([varnames for i in range(num_classes-1)])
            model.member_params_spec = member_params_spec

            model.fit(X, y, varnames, alts, isvars, num_classes,
                      class_params_spec, member_params_spec, transvars,
                      transformation, ids, weights, avail, randvars, panels,
                      base_alt, fit_intercept, init_coeff, maxiter,
                      random_state, correlation, n_draws, halton, verbose,
                      batch_size, halton_opts, ftol, gtol,
                      gtol_membership_func, hess, grad,
                      model._expectation_maximisation_algorithm  # method
                      #   verbose,  # TODO?
                      #   method,
                      #   scipy_optimisation
                      )
            prev_bic = curr_bic
            prev_model = curr_model
            curr_model = model
            curr_bic = model.bic
            num_classes -= 1

        if num_classes == 1:
            # TODO? could compare with standard (1 class) mixedlogit here
            pass

        # check cause of termination
        optimal_num = -1
        if curr_bic > prev_bic:
            optimal_num = num_classes+2
            model = prev_model
        else:
            optimal_num = num_classes+1
            model = curr_model

        print('Optimal number of classes', optimal_num)
        return (optimal_num, model)

    def _post_fit(self, optimization_res, coeff_names, sample_size,
                  hess_inv=None, verbose=1):
        # new_coeff_names = np.array([])
        randvars = self.randvars.copy()
        for i in range(self.num_classes):
            class_coeff_names = coeff_names[self._get_class_X_idx(i)]
            chol = ["chol." + self.varnames[self.correlationpos[i]] + "." +
                    self.varnames[self.correlationpos[j]] for i
                    in range(self.correlationLength) for j in range(i+1)]
            br_w_names = []
            # three cases for corr. varnames: no corr, corr list, corr Bool (All)
            if (self.correlation is not True and not isinstance(self.correlation, list)):
                if(hasattr(self, "rvidx")):  # avoid errors with multinomial logit
                    br_w_names = np.char.add("sd.", randvars)
            if (isinstance(self.correlation, list)):  # if not all r.v.s correlated
                sd_uncorrelated_pos = [self.varnames.tolist().index(x)
                                       for x in self.varnames
                                       if x not in self.correlation and
                                       x in randvars]
                br_w_names = np.char.add("sd.", self.varnames[sd_uncorrelated_pos])
            class_coeff_names = np.concatenate((class_coeff_names, chol,
                                                br_w_names))
            # class_coeff_names = np.core.defchararray.add('class-' + str(i+1) +
            #                                              ': ', class_coeff_names)
            # new_coeff_names = np.concatenate((new_coeff_names, class_coeff_names))

        super(LatentClassMixedModel, self)._post_fit(optimization_res,
                                                     class_coeff_names,
                                                     sample_size)

    def _compute_probabilities_latent(self, betas, X, y, panel_info, draws,
                                      drawstrans, avail, idx):
        """Compute the standard logit-based probabilities.

        Random and fixed coefficients are handled separately.
        """
        beta_segment_names = ["Bf", "Br_b", "chol", "Br_w", "Bftrans",
                              "flmbda", "Brtrans_b", "Brtrans_w", "rlmda"]
        var_list = dict()
        # number of parameters for each corresponding segment
        iterations = [self.Kf, self.Kr, self.Kchol, self.Kbw, self.Kftrans,
                      self.Kftrans, self.Krtrans, self.Krtrans, self.Krtrans]

        i = 0
        for count, iteration in enumerate(iterations):
            prev_index = i
            i = int(i + iteration)
            var_list[beta_segment_names[count]] = betas[prev_index:i]

        Bf, Br_b, chol, Br_w, Bftrans, flmbda, Brtrans_b, Brtrans_w, rlmda = \
            var_list.values()

        chol_mat = np.zeros((self.correlationLength, self.correlationLength))
        chol_mat_temp = np.zeros((self.Kr, self.Kr))
        indices = np.tril_indices(self.correlationLength)
        chol_mat[indices] = chol

        chol_mat_temp[:self.correlationLength, :self.correlationLength] = \
            chol_mat
        for i in range(self.Kr - self.correlationLength):
            chol_mat_temp[i+self.correlationLength,
                          i+self.correlationLength] = \
                Br_w[i]
        chol_mat = chol_mat_temp

        V = np.zeros((self.N, self.P, self.J, self.n_draws))
        # class_fx_idx = [ii for ii, x in enumerate(self.fxidx) if x and ii in idx]
        Xf = X[:, :, :, self.fxidx]
        Xf = Xf.astype('float')
        Xftrans = X[:, :, :, self.fxtransidx]
        Xftrans = Xftrans.astype('float')
        Xr = X[:, :, :, self.rvidx]
        Xr = Xr.astype('float')
        Xrtrans = X[:, :, :, self.rvtransidx]
        Xrtrans = Xrtrans.astype('float')

        if self.Kf != 0:
            XBf = np.einsum('npjk,k -> npj', Xf, Bf, dtype=np.float64)
            V += XBf[:, :, :, None]*self.S[:, :, :, None]
        if self.Kr != 0:
            Br = Br_b[None, :, None] + np.matmul(chol_mat, draws)
            Br = self._apply_distribution(Br, self.rvdist)
            self.Br = Br  # save Br to use later
            XBr = np.einsum('npjk, nkr -> npjr', Xr, Br, dtype=np.float64)  # (N, P, J, R)
            V += XBr*self.S[:, :, :, None]
        #  transformation
        #  transformations for variables with fixed coeffs
        if self.Kftrans != 0:
            Xftrans_lmda = self.transFunc(Xftrans, flmbda)
            Xftrans_lmda[np.isneginf(Xftrans_lmda)] = -max_comp_val
            Xftrans_lmda[np.isposinf(Xftrans_lmda)] = max_comp_val
            # Estimating the linear utility specificiation (U = sum XB)
            Xbf_trans = np.einsum('npjk,k -> npj', Xftrans_lmda, Bftrans, dtype=np.float64)
            # combining utilities
            V += Xbf_trans[:, :, :, None]

        # transformations for variables with random coeffs
        if self.Krtrans != 0:
            # creating the random coeffs
            Brtrans = Brtrans_b[None, :, None] + \
                    drawstrans[:, 0:self.Krtrans, :] * Brtrans_w[None, :, None]
            Brtrans = self._apply_distribution(Brtrans, self.rvtransdist)
            # applying transformation
            Xrtrans_lmda = self.transFunc(Xrtrans, rlmda)
            Xrtrans_lmda[np.isposinf(Xrtrans_lmda)] = 1e+30
            Xrtrans_lmda[np.isneginf(Xrtrans_lmda)] = -1e+30

            Xbr_trans = np.einsum('npjk, nkr -> npjr', Xrtrans_lmda, Brtrans, dtype=np.float64)  # (N, P, J, R)
            # combining utilities
            V += Xbr_trans  # (N, P, J, R)

        #  Combine utilities of fixed and random variables
        # V[V > max_exp_val] = max_exp_val
        # Exponent of the utility function for the logit formula
        eV = np.exp(V)
        if avail is not None:
            if self.panels is not None:
                eV = eV*avail[:, :, :, None]  # Acommodate availablity of alts with panels
            else:
                eV = eV*avail[:, None, :, None]  # Acommodate availablity of alts.

        # Thresholds to avoid overflow warnings
        eV[np.isposinf(eV)] = max_comp_val
        eV[np.isneginf(eV)] = -max_comp_val  # TODO? Check max vals
        sum_eV = np.sum(eV, axis=2, keepdims=True, dtype=np.float64)
        p = np.divide(eV, sum_eV, out=np.zeros_like(eV), where=(sum_eV != 0),
                      dtype=np.float64)

        if panel_info is not None:
            p = p*panel_info[:, :, None, None]
        p = y*p

        # collapse on alts
        pch = np.sum(p, axis=2)  # (N, P, R)

        if hasattr(self, 'panel_info'):
            pch = self._prob_product_across_panels(pch, self.panel_info)
        else:
            pch = np.mean(pch, axis=1)  # (N, R)
        pch = np.mean(pch, axis=1)  # (N)
        return pch.flatten()

    def _prob_product_across_panels(self, pch, panel_info):
        if not np.all(panel_info):  # If panels unbalanced. Not all ones
            idx = panel_info == .0
            for i in range(pch.shape[2]):
                pch[:, :][idx] = 1  # Multiply by one when unbalanced
        pch[pch < 1e-30] = 1e-30
        pch = pch.prod(axis=1, dtype=np.float64)  # (N,R)
        pch[pch < 1e-30] = 1e-30
        return pch  # (N,R)

    def _balance_panels(self, X, y, panels):
        """Balance panels if necessary and produce a new version of X and y.

        If panels are already balanced, the same X and y are returned. This
        also returns panel_info, which keeps track of the panels that needed
        balancing.
        """
        _, J, K = X.shape
        _, p_obs = np.unique(panels, return_counts=True)
        p_obs = (p_obs/J).astype(int)
        N = len(p_obs)  # This is the new N after accounting for panels
        P = np.max(p_obs)  # panels length for all records
        if not np.all(p_obs[0] == p_obs):  # Balancing needed
            y = y.reshape(X.shape[0], J, 1)
            Xbal, ybal = np.zeros((N*P, J, K)), np.zeros((N*P, J, 1))
            panel_info = np.zeros((N, P))
            cum_p = 0  # Cumulative sum of n_obs at every iteration
            for n, p in enumerate(p_obs):
                # Copy data from original to balanced version
                Xbal[n*P:n*P + p, :, :] = X[cum_p:cum_p + p, :, :]
                ybal[n*P:n*P + p, :, :] = y[cum_p:cum_p + p, :, :]
                panel_info[n, :p] = np.ones(p)
                cum_p += p
        else:  # No balancing needed
            Xbal, ybal = X, y
            panel_info = np.ones((N, P))
        self.panel_info = panel_info  # TODO: bad code
        return Xbal, ybal, panel_info

    def _posterior_est_latent_class_probability(self, class_thetas, X):
        """Get the prior estimates of the latent class probabilities

        Args:
            class_thetas (array-like): (number of latent classes) - 1 array of
                                       latent class vectors
            X (array-like): Input data for explanatory variables in wide format

        Returns:
            H [array-like]: Prior estimates of the class probabilities
        """
        if class_thetas.ndim == 1:
            class_thetas = class_thetas.reshape(self.num_classes - 1, -1)

        class_thetas_base = np.zeros(len(class_thetas[0]))

        eZB = np.zeros((self.num_classes, self.N))

        base_X_idx = self._get_member_X_idx(0)
        zB_q = np.dot(class_thetas_base[None, :],
                      np.transpose(self.short_df[:, base_X_idx]))

        eZB[0, :] = np.exp(zB_q)

        for i in range(1, self.num_classes):
            class_X_idx = self._get_member_X_idx(i)
            zB_q = np.dot(class_thetas[i-1, :],
                          np.transpose(self.short_df[:, class_X_idx]))
            # zB_q[np.where(max_exp_val < zB_q)] = max_exp_val
            eZB[i, :] = np.exp(zB_q)

        H = eZB/np.sum(eZB, axis=0, keepdims=True)

        return H

    def _class_member_func(self, class_thetas, weights, X):
        """Used in Maximisaion step. Used to find latent class vectors that
           minimise the negative loglik where there is no observed dependent
           variable (H replaces y).

        Args:
            class_thetas (array-like): (number of latent classes) - 1 array of
                                       latent class vectors
            weights (array-like): weights is prior probability of class by the
                                  probability of y given the class.
            X (array-like): Input data for explanatory variables in wide format
        Returns:
            ll [np.float64]: Loglik
        """
        H = self._posterior_est_latent_class_probability(class_thetas, X)

        H[np.where(H < 1e-30)] = 1e-30
        weight_post = np.multiply(np.log(H), weights)
        ll = -np.sum(weight_post)
        return ll

    def _get_class_X_idx(self, class_num, coeff_names=None):
        """Get indices for X dataset based on which parameters have been
            specified for the latent class

        Args:
            class_num (int): latent class number

        Returns:
            X_class_idx [np.ndarray]: indices to retrieve relevant
                                        explantory params of specified
                                        latent class
        """
        #  below line: return indices of that class params in Xnames
        #  pattern matching for isvars
        # X_class_idx = np.array([], dtype='int')
        # for param in self.class_params_spec[class_num]:
        #     param_idx = np.where(np.char.find(self.Xnames, param) != -1)[0]
        #     X_class_idx = np.concatenate((X_class_idx, param_idx))
        # X_class_idx = X_class_idx.flatten()
        # sd_idx = np.where(np.char.find(self.Xnames, 'sd') != -1)[0]
        # chol_idx = np.where(np.char.find(self.Xnames, 'chol') != -1)[0]
        # X_class_idx = np.array(X_class_idx).flatten()
        # if not include_sd:
        #     X_class_idx = np.array([x for x in X_class_idx if x not in sd_idx and x not in chol_idx])

        if coeff_names is None:
            coeff_names = self.varnames.copy()

        tmp_varnames = coeff_names.copy()
        for ii, varname in enumerate(tmp_varnames):
            # remove lambda so can get indices correctly
            if varname.startswith('lambda.'):
                tmp_varnames[ii] = varname[7:]
            if varname.startswith('sd.'):
                tmp_varnames[ii] = varname[3:]

        X_class_idx = np.array([], dtype="int")
        for var in self.class_params_spec[class_num]:
            for ii, var2 in enumerate(tmp_varnames):
                if var == var2:
                    X_class_idx = np.append(X_class_idx, ii)

        X_class_idx = np.sort(X_class_idx)
        # X_class_idx_tmp = np.array([], dtype='int')
        # counter = 0
        # for idx_pos in X_class_idx:
        #     if idx_pos in self.ispos:
        #         for i in range(self.J - 1):
        #             X_class_idx_tmp = np.append(X_class_idx_tmp, int(counter))
        #             counter += 1
        #     else:
        #         X_class_idx_tmp = np.append(X_class_idx_tmp, int(counter))
        #         counter += 1

        # X_class_idx = X_class_idx_tmp

        return X_class_idx

    def _get_member_X_idx(self, class_num, coeff_names=None):
        """Get indices for X dataset based on which parameters have been
            specified for the latent class membership

        Args:
            class_num (int): latent class number

        Returns:
            X_class_idx [np.ndarray]: indices to retrieve relevant
                                        explantory params of specified
                                        latent class
        """
        # X_class_idx = np.array([], dtype='int')
        # for param in self.member_params_spec[class_num-1]:
        #     param_idx = np.where(np.char.find(self.Xnames, param) != -1)[0]
        #     X_class_idx = np.concatenate((X_class_idx, param_idx))
        # sd_idx = np.where(np.char.find(self.Xnames, 'sd') != -1)[0]
        # chol_idx = np.where(np.char.find(self.Xnames, 'chol') != -1)[0]
        # X_class_idx = np.array(X_class_idx).flatten()
        # X_class_idx = np.array([x for x in X_class_idx if x not in sd_idx and x not in chol_idx])

        if coeff_names is None:
            coeff_names = self.varnames.copy()

        # X_class_idx = np.concatenate([np.where(np.char.find(self.varnames, param) != -1)[0]
        #                for param in self.member_params_spec[class_num]])
        # if self.fit_intercept and 'intercept' in self.member_params_spec[class_num]:  # code smell
        #     X_class_idx = X_class_idx - np.repeat(self.J-1, len(X_class_idx))
        # X_class_idx = np.concatenate([x for x in X_class_idx])
            # factor in isvars

        tmp_varnames = coeff_names.copy()
        for ii, varname in enumerate(tmp_varnames):
            # remove lambda so can get indices correctly
            if varname.startswith('lambda.'):
                tmp_varnames[ii] = varname[7:]

        X_class_idx = np.array([], dtype="int")
        for var in self.member_params_spec[class_num-1]:
            for ii, var2 in enumerate(tmp_varnames):
                if var == var2:
                    X_class_idx = np.append(X_class_idx, ii)

        # factor in isvars
        X_class_idx = np.sort(X_class_idx)
        # X_class_idx_tmp = np.array([], dtype='int')
        # counter = 0
        # for idx_pos in X_class_idx:
        #     if idx_pos in self.ispos:
        #         for i in range(self.J - 1):
        #             X_class_idx_tmp = np.append(X_class_idx_tmp, int(counter))
        #             counter += 1
        #     else:
        #         X_class_idx_tmp = np.append(X_class_idx_tmp, int(counter))
        #         counter += 1

        # X_class_idx = X_class_idx_tmp

        return X_class_idx

    def _get_kchol(self, specs):
        randvars_specs = [param for param in specs if param in self.randvars]
        Kchol = 0
        if (self.correlation):
            if (isinstance(self.correlation, list)):
                # Kchol, permutations of specified params in correlation list
                Kchol = int((len(self.correlation) *
                            (len(self.correlation)+1))/2)
            else:
                # i.e. correlation = True, Kchol permutations of rand vars
                Kchol = int((len(randvars_specs) *
                            (len(randvars_specs)+1))/2)
        return Kchol

    def _get_betas_length(self, class_num):
        """Get betas length (parameter vectors) for the specified latent class

        Args:
            class_num (int): latent class number

        Returns:
            betas_length (int): number of betas for latent class
        """
        class_idx = self._get_class_X_idx(class_num)
        self._set_bw(class_idx)
        class_params_spec = self.class_params_spec[class_num]
        class_isvars = [x for x in class_params_spec if x in self.isvars]
        class_asvars = [x for x in class_params_spec if x in self.asvars]
        class_randvars = [x for x in class_params_spec if x in self.randvars]
        # class_corrvars = []
        has_intercept = True if 'intercept' in class_params_spec else False
        betas_length = ((len(self.alternatives)-1)*(len(class_isvars)) +
                        len(class_asvars) + len(class_randvars)
                        if not has_intercept
                        else (len(self.alternatives)-1)*(len(class_isvars)+1) +
                        len(class_asvars) + len(class_randvars))
        # copied from choice model logic for Kchol
        Kchol = self._get_kchol(class_params_spec)
        betas_length += Kchol
        betas_length += self.Kbw  # TODO: CHECK LOGIC
        # self._ge
        return betas_length

    def _make_short_df(self, X):
        """Make an shortened dataframe average over alts, used in latent
        class estimation.
        """
        short_df = np.sum(np.mean(X, axis=2), axis=1)
        short_df = np.array([short_df[i, :]/np.sum(self.panel_info[i, :])
                             for i in range(self.N)])
        self.short_df = short_df  # store for use..average df over indiv.

    def _set_bw(self, specs):
        """Logic copied from _choice_model class"""
        specs = self.Xnames[specs]
        randvars_specs = [param for param in specs if param in self.randvars]
        Kr = len(randvars_specs)
        self.Kbw = Kr
        # set up length of betas required to estimate correlation and/or
        # random variable standard deviations, useful for cholesky matrix
        if (self.correlation):
            if (isinstance(self.correlation, list)):
                self.correlationLength = len(self.correlation)
                self.Kbw = Kr - len(self.correlation)
            else:
                self.correlationLength = Kr
                self.Kbw = 0

    def _expectation_maximisation_algorithm(self, tmp_fn, tmp_betas, args,
                                            class_betas=None,
                                            class_thetas=None,
                                            validation=False,
                                            **kwargs):
        """Run the EM algorithm by iterating between computing the
           posterior class probabilities and re-estimating the model parameters
           in each class by using a probability weighted loglik function

        Args:
            X (array-like): Input data for explanatory variables in wide format
            y (array-like):  Choices (outcome) in wide format
            weights (array-like): weights is prior probability of class by the
                                  probability of y given the class.
            avail (array-like): Availability of alternatives for the
                                choice situations. One when available or
                                zero otherwise.

        Returns:
            optimisation_result (dict): Dictionary mimicking the optimisation
                                        result in scipy.optimize.minimize
        """
        X, y, panel_info, draws, drawstrans, weights, avail, batch_size = args
        if X.ndim != 4:
            X = X.reshape(self.N, self.P, self.J, -1)
            y = y.reshape(self.N, self.P, self.J, -1)

        converged = False

        if class_betas is None:
            class_betas = [np.random.uniform(0, 1, self._get_betas_length(i))
                           for i in range(self.num_classes)]
        # else:
        #     # TODO? any checks here
        #     class_betas = [tmp_betas[i] for i in range(self.num_classes)]

        if class_thetas is None:
            # class member ship probability
            class_thetas = np.stack([
                            np.repeat(.1, len(self._get_member_X_idx(i)))
                            for i in range(1, self.num_classes)], axis=0)

        log_lik_old = 0

        self._make_short_df(X)
        max_iter = 2000
        iter_num = 0
        class_betas_sd = [np.ones(len(betas))
                          for betas in class_betas]
        class_thetas_sd = np.repeat(.1, class_thetas.size)

        class_idxs = []
        # TODO: work for any varnames order...
        class_fxidxs = []
        class_fxtransidxs = []
        class_rvidxs = []
        class_rvtransidxs = []
        global_fxidx = self.fxidx
        global_fxtransidx = self.fxtransidx
        global_rvidx = self.rvidx
        global_rvtransidx = self.rvtransidx
        for class_num in range(self.num_classes):
            X_class_idx = self._get_class_X_idx(class_num)
            class_idxs.append(X_class_idx)
            # deal w/ fix indices
            class_fx_idx = [fxidx for ii, fxidx in enumerate(global_fxidx)
                            if ii in X_class_idx]
            class_fxtransidx = np.repeat(False, len(X_class_idx))
            class_fxidxs.append(class_fx_idx)
            class_fxtransidxs.append(class_fxtransidx)
            # deal w/ random indices
            class_rv_idx = [rvidx for ii, rvidx in enumerate(global_rvidx)
                            if ii in X_class_idx]
            class_rvtransidx = np.repeat(False, len(X_class_idx))
            class_rvidxs.append(class_rv_idx)
            class_rvtransidxs.append(class_rvtransidx)

        # TODO? Pylogit for design matrices?

        while not converged and iter_num < max_iter:
            # Expectation step
            # reset Kf, Kr in case weird isvars/intercept issues
            print('iter_num', iter_num)
            self.Kf = sum(class_fxidxs[0])
            self.Kr = sum(class_rvidxs[0])
            self.fxidx = class_fxidxs[0]
            self.fxtransidx = class_fxtransidxs[0]
            self.rvidx = class_rvidxs[0]
            self.rvtransidx = class_rvtransidxs[0]
            self._set_bw(class_idxs[0])  # sets sd. and corr length params
            self.Kchol = self._get_kchol(self.Xnames[class_idxs[0]])
            rand_idx = [ii for ii, param in enumerate(self.randvars)
                        if param in self.Xnames[class_idxs[0]]]
            p = self._compute_probabilities_latent(class_betas[0],
                                                   X[:, :, :, class_idxs[0]],
                                                   y,
                                                   panel_info,
                                                   draws[:, rand_idx, :],
                                                   drawstrans,
                                                   avail,
                                                   class_idxs[0])

            k = len(class_betas[0])

            # k = np.atleast_2d(self.member_params_spec)[0].size
            H = self._posterior_est_latent_class_probability(class_thetas,
                                                             X)
            for class_i in range(1, self.num_classes):
                self.Kf = sum(class_fxidxs[class_i])
                self.Kr = sum(class_rvidxs[class_i])
                self.fxidx = class_fxidxs[class_i]
                self.fxtransidx = class_fxtransidxs[class_i]
                self.rvidx = class_rvidxs[class_i]
                self.rvtransidx = class_rvtransidxs[class_i]
                self._set_bw(class_idxs[class_i])  # sets sd. and corr length
                self.Kchol = self._get_kchol(self.Xnames[class_idxs[class_i]])
                rand_idx = [ii for ii, param in enumerate(self.randvars)
                            if param in self.Xnames[class_idxs[class_i]]]

                new_p = self._compute_probabilities_latent(class_betas[class_i],
                                                    X[:, :, :, class_idxs[class_i]],
                                                    y,
                                                    panel_info,
                                                    draws[:, rand_idx, :],
                                                    drawstrans,
                                                    avail,
                                                    X_class_idx)
                p = np.vstack((p, new_p))

            weights = np.multiply(p, H)
            weights[weights == 0] = min_comp_val

            lik = np.sum(weights, axis=0)
            lik[np.where(lik < min_comp_val)] = min_comp_val
            log_lik = np.log(np.sum(weights, axis=0))  # sum over classes

            log_lik_new = np.sum(log_lik)
            # print('log_lik_new', log_lik_new)
            if validation:
                return log_lik_new
            # print('log_lik_new', log_lik_new)
            weights = np.divide(weights, np.tile(np.sum(weights, axis=0),
                                                 (self.num_classes, 1)))

            # Maximisation step
            opt_res = minimize(self._class_member_func,
                               class_thetas,
                               args=(weights, X),
                               method='BFGS',
                               tol=self.ftol,
                               options={'gtol': self.gtol_membership_func}
                               )
            if opt_res['success']:
                class_thetas = opt_res['x']
                # print('class_thetas', class_thetas)
                tmp_thetas_sd = np.sqrt(np.diag(opt_res['hess_inv']))
                # in scipy.optimse if "initial guess" is close to optimal
                # solution it will not build up a guess at the Hessian inverse
                # this if statement prevents this case
                if not np.allclose(tmp_thetas_sd,
                                   np.ones(len(tmp_thetas_sd))):
                    # TODO? potentially do element by element check
                    class_thetas_sd = tmp_thetas_sd
            if not hasattr(self, 'panel_info'):
                self.panel_info = None
            for s in range(0, self.num_classes):
                class_X_idx = self._get_class_X_idx(s)
                self.Kf = sum(class_fxidxs[s])
                self.Kr = sum(class_rvidxs[s])
                self._set_bw(class_X_idx)  # sets sd. and corr length params
                self.fxidx = class_fxidxs[s]
                self.fxtransidx = class_fxtransidxs[s]
                self.rvidx = class_rvidxs[s]
                self.rvtransidx = class_rvtransidxs[s]

                self.Kchol = self._get_kchol(self.Xnames[class_idxs[s]])
                rand_idx = [ii for ii, param in enumerate(self.randvars) if param in self.Xnames[class_idxs[s]]]

                jac = True if self.grad else False

                opt_res = minimize(self._loglik_gradient,
                                   class_betas[s],
                                   args=(X[:, :, :, class_X_idx],
                                         y,
                                         self.panel_info,
                                         draws[:, rand_idx, :],
                                         drawstrans,
                                         weights[s, :],
                                         avail,
                                         batch_size),
                                   method="BFGS",
                                   jac=jac,
                                   tol=self.ftol,
                                   options={'gtol': self.gtol}
                                   )

                if opt_res['success']:
                    class_betas[s] = opt_res['x']
                    tmp_calc = np.sqrt(np.diag(opt_res['hess_inv']))
                    # in scipy.optimse if "initial guess" is close to optimal
                    # solution it will not build up a guess at the Hessian inverse
                    # this if statement prevents this case
                    if not np.allclose(tmp_calc,
                                       np.ones(len(tmp_calc))):
                        class_betas_sd[s] = tmp_calc

            converged = np.abs(log_lik_new - log_lik_old) < self.ftol

            log_lik_old = log_lik_new
            iter_num += 1
            class_thetas = class_thetas.reshape((self.num_classes-1, -1))

        x = np.array([])
        for betas in class_betas:
            betas = np.array(betas)
            x = np.concatenate((x, betas))

        stderr = np.concatenate(class_betas_sd)

        optimisation_result = {'x': x,
                               'success': opt_res['success'],  # TODO? correct?
                               'fun': log_lik_new, 'nit': iter_num,
                               'stderr': stderr, 'is_latent_class': True,
                               'class_x': class_thetas.flatten(),
                               'class_x_stderr': class_thetas_sd,
                               'hess_inv': opt_res['hess_inv']
                               }

        self.fxidx = global_fxidx
        self.fxtransidx = global_fxtransidx
        self.rvidx = global_rvidx
        self.rvtransidx = global_rvtransidx

        return optimisation_result

    def validation_loglik(self, validation_X, validation_Y, ids=None,
                          panel_info=None, avail=None, weights=None, betas=None,
                          batch_size=None, alts=None, panels=None):
        """Computes the log-likelihood on the validation set using
        the betas fitted using the training set.
        """
        if panels is not None:
            N = len(np.unique(panels))
        else:
            N = self.N
        validation_X, Xnames = self._setup_design_matrix(validation_X)
        self.N = N

        # X, y, panels = self._arrange_long_format(validation_X, validation_Y,
        #   ids, alts, panel_info)
        # N, K = validation_X.shape
        # # N = int(N/self.J)
        # self.init_df = validation_X
        # # validation_X = validation_X.reshape((-1, self.J, K))
        # validation_X, _ = self._setup_design_matrix(validation_X)
        if len(np.unique(panels)) != (N/self.J):
            # N = len(np.unique(ids))
            X, y, panel_info = self._balance_panels(validation_X, validation_Y, panels)
            validation_X = X.reshape((N, self.P, self.J, -1))
            validation_Y = y.reshape((N, self.P, self.J, -1))
        else:
            validation_X = validation_X.reshape(N, self.P, self.J, -1)
            validation_Y = validation_Y.reshape(N, self.P, -1)

        batch_size = self.n_draws  # TODO! Logic for batch_size

        self.N = N  # store for use in EM alg
        # self.ids = ids

        draws, drawstrans = self._generate_draws(N, self.n_draws)  # (N,Kr,R)

        # stop errors relating to S
        S = np.zeros((N, self.P, self.J))
        for i in range(N):
            S[i, 0:self.P_i[i], :] = 1
        self.S = S

        class_betas = []
        counter = 0
        for ii, param_spec in enumerate(self.class_params_spec):
            # count + add coeff_
            idx = counter + self._get_betas_length(0)
            class_betas.append(self.coeff_[counter:idx])
            counter = idx

        class_thetas = np.array([])
        counter = 0
        # TODO...
        for ii, param_spec in enumerate(self.member_params_spec):
            # count + add coeff_
            idx = counter + len(param_spec)
            class_betas.append(self.coeff_[counter:idx])
            counter = idx

        tmp_fn = None
        tmp_betas = class_betas  # TODO? CHECK HANDLED?
        args = (validation_X, validation_Y, panel_info, draws, drawstrans,
                weights, avail, batch_size)
        res = self._expectation_maximisation_algorithm(tmp_fn, tmp_betas, args,
                                                       validation=True)

        loglik = -res
        print('Validation loglik: ', loglik)
        return loglik

    def _bfgs_optimization(self, betas, X, y, weights, avail, maxiter):
        """Override bfgs function in multinomial logit to use EM."""
        opt_res = self._expectation_maximisation_algorithm(X, y, avail)
        return opt_res
