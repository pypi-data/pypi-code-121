"""Implements multinomial and mixed logit models"""
# pylint: disable=invalid-name

import numpy as np
from scipy.stats import t, norm
import scipy as sc
from time import time
from abc import ABC, abstractmethod
from .boxcox_functions import boxcox_transformation, boxcox_param_deriv
import warnings
from ._device import device as dev

warnings.simplefilter(action='ignore', category=FutureWarning)
"""
Notations
---------
    N : Number of choice situations
    P : Number of observations per panels
    J : Number of alternatives
    K : Number of variables (Kf: fixed + non-trans, Kr: random+non-trans,
                            Kftrans: fixed+trans, Krtrans: random+trans)
"""


class ChoiceModel(ABC):
    """Base class for estimation of discrete choice models"""

    def __init__(self):
        """Init Function

        Parameters
        ----------
        random_state: an integer used as seed to generate numpy random numbers
        """
        self.coeff_names = None
        self.coeff_ = None
        self.stderr = None
        self.zvalues = None
        self.pvalues = None
        self.loglikelihood = None
        self.numFixedCoeffs = None
        self.numTransformedCoeffs = None
        self.total_fun_eval = 0
        self.verbose = 1

    def _reset_attributes(self):
        self.coeff_names = None
        self.coeff_ = None
        self.stderr = None
        self.zvalues = None
        self.pvalues = None
        self.loglikelihood = None
        self.numFixedCoeffs = None
        self.numTransformedCoeffs = None
        self.total_fun_eval = 0
        self.verbose = 1

    @abstractmethod
    def fit(self, X, y, varnames=None, alts=None, isvars=None, transvars=None,
            transformation=None, ids=None,
            weights=None, base_alt=None, fit_intercept=False, init_coeff=None,
            maxiter=2000, random_state=None, correlation=None):
        pass

    def _as_array(self, X, y, varnames, alts, isvars, transvars, ids,
                  weights, panels, avail):
        X = np.asarray(X)
        y = np.asarray(y)
        varnames = np.asarray(varnames) if varnames is not None else None
        alts = np.asarray(alts) if alts is not None else None
        isvars = np.asarray(isvars) if isvars is not None else None
        transvars = np.asarray(transvars) if transvars is not None else []
        ids = np.asarray(ids) if ids is not None else None
        weights = np.asarray(weights) if weights is not None else None
        panels = np.asarray(panels) if panels is not None else None
        avail = np.asarray(avail) if avail is not None else None
        return X, y, varnames, alts, isvars, transvars, ids, \
            weights, panels, avail

    def _pre_fit(self, alts, varnames, isvars, transvars, base_alt,
                 fit_intercept, transformation, maxiter, panels,
                 correlation=None, randvars=None):
        self._reset_attributes()
        self._fit_start_time = time()
        self.isvars = [] if isvars is None else isvars
        self.transvars = [] if transvars is None else transvars
        self.randvars = [] if randvars is None else randvars
        with warnings.catch_warnings():
            # CURRENTLY IGNORING FUTURE WARNING
            # CURRENT PY: 3.8.3, numpy: 1.18.5
            warnings.simplefilter(action='ignore', category=FutureWarning)
            self.asvars = [v for v in varnames if ((v not in self.isvars) and
                           (v not in self.transvars) and
                           (v not in self.randvars))]

            self.asvars_construct_matrix = [v for v in varnames  # old definition of asvars used to make datasets
                                            if ((v not in self.isvars))]
        self.randtransvars = [] if transvars is None else []  # TODO?
        self.fixedtransvars = [] if transvars is None else []  # TODO?
        self.alternatives = np.unique(alts)
        self.numFixedCoeffs = ((len(self.alternatives)-1)*(len(self.isvars)) + len(self.asvars)
                               if not fit_intercept
                               else (len(self.alternatives)-1)*(len(self.isvars)+1) + len(self.asvars))
        self.numTransformedCoeffs = len(self.transvars)*2
        self.varnames = list(varnames)  # Easier to handle with lists
        self.fit_intercept = fit_intercept
        self.transformation = transformation
        self.base_alt = self.alternatives[0] if base_alt is None else base_alt
        self.correlation = False if correlation is None else correlation
        self.maxiter = maxiter
        if not hasattr(self, 'panels'):  # check panels not already set (LCM)
            self.panels = panels

    def _post_fit(self, optimization_res, coeff_names, sample_size, hess_inv=None, verbose=1):
        self.convergence = optimization_res['success']
        self.coeff_ = optimization_res['x']
        # convert hess inverse for L-BFGS-B optimisation method

        self.stderr = np.zeros_like(self.coeff_)
        std_err_estimated = False
        
        if 'stderr' in optimization_res:
            std_err_estimated = True

            self.stderr = optimization_res['stderr']

        # TODO? added is_latent_class as temp bug fix
        is_latent_class = optimization_res['is_latent_class'] if \
            'is_latent_class' in optimization_res else False
        self.is_latent_class = is_latent_class
        if is_latent_class:
            new_coeff_names = np.array([])
            # TODO! SUMMARY FOR TRANS...
            for i in range(self.num_classes):
                # X_class_idx = self._get_class_X_idx(i)
                X_class_idx = self._get_class_X_idx(i, coeff_names=coeff_names)

                # # TODO? doubling up get_class_X_idx but with Xnames..
                # tmp_coeff_names = coeff_names.copy()
                # for ii, coeff_name in enumerate(tmp_coeff_names):
                #      if coeff_name.startswith('lambda.'):
                #         tmp_coeff_names[ii] = coeff_name[7:]
                class_coeff_names = coeff_names[X_class_idx]

                class_coeff_names = np.core.defchararray.add('class-' + str(i+1) +
                                                            ': ', class_coeff_names)
                new_coeff_names = np.concatenate((new_coeff_names, class_coeff_names))
            coeff_names = new_coeff_names

        if hasattr(self, 'Hinv') and not is_latent_class:
            if dev.using_gpu:
                self.stderr = np.sqrt(np.diag(self.Hinv))
            else:
                diag_arr_tmp = np.diag(np.array(self.Hinv))
                # stop runtimewarnings from (very small) negative values
                # assume these occur from some floating point error and are 0.
                pos_vals_idx = [ii for ii, el in enumerate(diag_arr_tmp)
                                if el > 0]
                diag_arr = np.zeros(len(diag_arr_tmp))
                diag_arr[pos_vals_idx] = diag_arr_tmp[pos_vals_idx]
                # if len(neg_vals) > 0:
                #     raise Exception
                self.stderr = np.sqrt(diag_arr)
            std_err_estimated = False if np.isnan(self.stderr).any else True

        if not std_err_estimated:
            if self.method == "bfgs":
                self.stderr = np.sqrt(np.diag(optimization_res['hess_inv']))
            if self.method == "l-bfgs-b":
                hess = optimization_res['hess_inv'].todense()
                self.stderr = np.sqrt(np.diag(np.array(hess)))
        
        lambda_mask = [1 if "lambda" in x else 0 for x in coeff_names]

        if len(lambda_mask) != len(self.coeff_):
            lambda_mask = np.ones_like(self.coeff_)

        if 'is_latent_class' in optimization_res:
            lambda_mask = np.zeros_like(self.coeff_)

        self.num_params = self.Kbw + self.Kchol + self.Kf + self.Kftrans + self.Kr + self.Krtrans
        self.zvalues = np.nan_to_num((self.coeff_ - lambda_mask)/self.stderr)
        # set maximum (and minimum) limits to zvalues
        self.zvalues = [z if z < 1e+5 else 1e+5 for z in self.zvalues]
        self.zvalues = [z if z > -1e+5 else -1e+5 for z in self.zvalues]
        if sample_size < 100:  # arbitrary ... could do standard 30
            self.pvalues = 2*(1 - t.cdf(np.abs(self.zvalues), df=sample_size))
        else:
            self.pvalues = 2*(1 - norm.cdf(np.abs(self.zvalues)))
        # self.pvalues_old = 2*t.pdf(-np.abs(self.zvalues), df=sample_size)
        # self.pvalues = 2*(1 - t.cdf(np.abs(self.zvalues), df=sample_size))
        self.loglikelihood = -optimization_res['fun']
        self.coeff_names = coeff_names
        self.total_iter = optimization_res['nit']
        self.estim_time_sec = time() - self._fit_start_time
        self.sample_size = sample_size
        self.aic = 2*len(self.coeff_) - 2*self.loglikelihood
        self.bic = np.log(sample_size)*len(self.coeff_) - 2*self.loglikelihood

        # logic counting num alts
        # self.obs_num_alts = np.zeros_like(self.alternatives)
        # for ii, alt in enumerate(self.alternatives):
        #     J = len(self.alternatives)
        #     obs_num_alt = [self.y[x] for x in range(ii, len(self.y), J)]
        #     self.obs_num_alts[ii] = np.sum(obs_num_alt)
        # print("self.obs_num_alts", self.obs_num_alts)

        if 'is_latent_class' in optimization_res:
            self.is_latent_class = True
            self.class_x = optimization_res['class_x']
            self.class_x_stderr = optimization_res['class_x_stderr']
            # TODO: LATENT VERSION
            self.aic = 2*len(self.coeff_) - 2*self.loglikelihood
            self.bic = np.log(sample_size)*(len(self.coeff_) * 2 - self.num_params) - 2*self.loglikelihood
        if not self.convergence and verbose > 0:
            print("**** The optimization did not converge after {} "
                  "iterations. ****".format(self.total_iter))
            if hasattr(optimization_res, 'message'):
                print("Message: " + str(optimization_res['message']))

    def _setup_design_matrix(self, X):
        """Setups and reshapes input data after adding isvars and intercept.

        Setup the design matrix by adding the intercept when necessary and
        converting the isvars to a dummy representation that removes the base
        alternative.
        """
        if not hasattr(self, 'J'):
            J = len(self.alternatives)
        else:
            J = self.J
        N = P_N = int(len(X)/J)
        self.P = 0
        self.N = N
        self.J = J
        if self.panels is not None:
            # panels size.
            self.P_i = ((np.unique(self.panels, return_counts=True)[1])/J).astype(int)
            self.P = np.max(self.P_i)
            self.N = len(self.P_i)
        else:
            self.P = 1
            self.P_i = np.ones([N]).astype(int)
        isvars = self.isvars.copy()
        asvars = self.asvars.copy()
        asvars_construct_matrix = self.asvars_construct_matrix.copy()
        randvars = self.randvars.copy()
        randtransvars = self.randtransvars.copy()
        fixedtransvars = self.fixedtransvars.copy()
        varnames = self.varnames.copy()
        self.varnames = np.array(varnames)
        ispos = [self.varnames.tolist().index(i) for i in self.isvars]  # Position of IS vars

        # adjust index array to include isvars
        if len(self.isvars) > 0 and not hasattr(self, 'ispos'):  # check not done before...
            self.fxidx = np.insert(np.array(self.fxidx, dtype="bool_"), 0,
                                   np.repeat(True, len(self.isvars)*(J - 1)))
            self.fxtransidx = np.insert(np.array(self.fxtransidx, dtype="bool_"),
                                        0, np.repeat(False, len(self.isvars)*(J - 1)))
            if hasattr(self, 'rvidx'):
                self.rvidx = np.insert(np.array(self.rvidx, dtype="bool_"), 0,
                                       np.repeat(False, len(self.isvars)*(J - 1)))
            if hasattr(self, 'rvtransidx'):
                self.rvtransidx = np.insert(np.array(self.rvtransidx, dtype="bool_"),
                                            0, np.repeat(False, len(self.isvars)*(J - 1)))

        if self.fit_intercept:
            X = np.hstack((np.ones(J*N)[:, None], X))
            if '_inter' not in self.isvars:  # stop running in validation
                # adjust variables to allow intercept parameters
                self.isvars = np.insert(np.array(self.isvars, dtype="<U64"), 0, '_inter')
                self.varnames = np.insert(np.array(self.varnames, dtype="<U64"), 0, '_inter')
                # self.initialData = np.hstack((np.ones(J*N)[:, None], self.initialData))
                self.fxidx = np.insert(np.array(self.fxidx, dtype="bool_"), 0, np.repeat(True, J-1))
                if hasattr(self, 'rvidx'):
                    self.rvidx = np.insert(np.array(self.rvidx, dtype="bool_"), 0, np.repeat(False, J-1))
                self.fxtransidx = np.insert(np.array(self.fxtransidx, dtype="bool_"), 0, np.repeat(False, J-1))
                if hasattr(self, 'rvtransidx'):
                    self.rvtransidx = np.insert(np.array(self.rvtransidx, dtype="bool_"), 0, np.repeat(False, J-1))

        if self.transformation == "boxcox":
            self.transFunc = boxcox_transformation
            self.transform_deriv = boxcox_param_deriv

        S = np.zeros((self.N, self.P, self.J))
        for i in range(self.N):
            S[i, 0:self.P_i[i], :] = 1
        self.S = S
        ispos = [self.varnames.tolist().index(i) for i in self.isvars]  # Position of IS vars
        aspos = [self.varnames.tolist().index(i) for i in asvars_construct_matrix]  # Position of AS vars
        self.aspos = np.array(aspos) # saved for later use
        self.ispos = np.array(ispos)
        randpos = [self.varnames.tolist().index(i) for i in randvars]  # Position of AS vars
        randtranspos = [self.varnames.tolist().index(i) for i in randtransvars]  # bc transformed variables with random coeffs
        fixedtranspos = [self.varnames.tolist().index(i) for i in fixedtransvars]  # bc transformed variables with fixed coeffs
        
        # if correlation = True correlation pos is randpos, if list get correct pos
        self.correlationpos = []
        if randvars:
            self.correlationpos = [self.varnames.tolist().index(x) for x in self.varnames if x in self.randvars]  #  Position of correlated variables within randvars
        if (isinstance(self.correlation, list)):
            self.correlationpos = [self.varnames.tolist().index(x) for x in
                                   self.varnames if x in self.correlation]
            self.uncorrelatedpos = [self.varnames.tolist().index(x) for x in
                                   self.varnames if x not in self.correlation]

        self.Kf = sum(self.fxidx)  # set number of fixed coeffs from idx
        self.Kr = len(randpos)  # Number of random coefficients
        self.Kftrans = len(fixedtranspos)  # Number of fixed coefficients of bc transformed vars
        self.Krtrans = len(randtranspos)  # Number of random coefficients of bc transformed vars
        self.Kchol = 0  # Number of random beta cholesky factors
        self.correlationLength = 0
        self.Kbw = self.Kr

        # set up length of betas required to estimate correlation and/or
        # random variable standard deviations, useful for cholesky matrix
        if (self.correlation):
            if (isinstance(self.correlation, list)):
                self.correlationLength = len(self.correlation)
                self.Kbw = self.Kr - len(self.correlation)
            else:
                self.correlationLength = self.Kr
                self.Kbw = 0
        if (self.correlation):
            if (isinstance(self.correlation, list)):
                # Kchol, permutations of specified params in correlation list
                self.Kchol = int((len(self.correlation) *
                                 (len(self.correlation)+1))/2)
            else:
                # i.e. correlation = True, Kchol permutations of rand vars
                self.Kchol = int((len(self.randvars) *
                                 (len(self.randvars)+1))/2)
        # Create design matrix
        # For individual specific variables
        Xis = None
        if len(self.isvars):
            # Create a dummy individual specific variables for the alts
            dummy = np.tile(np.eye(J), reps=(P_N, 1))
            # Remove base alternative
            dummy = np.delete(dummy,
                              np.where(self.alternatives == self.base_alt)[0],
                              axis=1)
            Xis = X[:, ispos]
            # Multiply dummy representation by the individual specific data
            Xis = np.einsum('nj,nk->njk', Xis, dummy, dtype="float64")
            Xis = Xis.reshape(P_N, self.J, (self.J-1)*len(ispos))
        else:
            Xis = np.array([])
        # For alternative specific variables
        Xas = None
        if asvars_construct_matrix:
            Xas = X[:, aspos]
            Xas = Xas.reshape(N, J, -1)

        # Set design matrix based on existance of asvars and isvars
        if len(asvars_construct_matrix) and len(self.isvars):
            X = np.dstack((Xis, Xas))
        elif len(asvars_construct_matrix):
            X = Xas
        elif (len(self.isvars)):
            X = Xis
        else:
            x_varname_length = len(self.varnames) if not self.fit_intercept \
                               else (len(self.varnames) - 1)+(J-1)
            X = X.reshape(-1, len(self.alternatives), x_varname_length)

        intercept_names = ["_intercept.{}".format(j) for j in self.alternatives
                           if j != self.base_alt] if self.fit_intercept else []
        names = ["{}.{}".format(isvar, j) for isvar in isvars
                 for j in self.alternatives if j != self.base_alt]
        lambda_names_fixed = ["lambda.{}".format(transvar) for transvar in
                              fixedtransvars]
        lambda_names_rand = ["lambda.{}".format(transvar) for transvar in
                             randtransvars]
        randvars = [x for x in self.varnames if x in self.randvars]
        asvars_names = [x for x in asvars if (x not in self.randvars) and
                                             (x not in fixedtransvars) and
                                             (x not in randtransvars)]
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
        sd_rand_trans = np.char.add("sd.", self.varnames[randtranspos])
        names = np.concatenate((intercept_names, names, asvars_names, randvars,
                                chol, br_w_names, fixedtransvars,
                                lambda_names_fixed, randtransvars,
                                sd_rand_trans, lambda_names_rand))
        names = np.array(names)
        return X, names

    def _check_long_format_consistency(self, ids, alts, sorted_idx):
        alts = alts[sorted_idx]
        uq_alt = np.unique(alts)
        expect_alt = np.tile(uq_alt, int(len(ids)/len(uq_alt)))
        # TODO: BAD REMOVED CHECK !
        # if not np.array_equal(alts, expect_alt):
        #     raise ValueError('inconsistent alts values in long format')
        _, obs_by_id = np.unique(ids, return_counts=True)
        if not np.all(obs_by_id/len(uq_alt)):  # Multiple of J
            raise ValueError('inconsistent alts and ids values in long format')

    def _arrange_long_format(self, X, y, ids, alts, panels=None):
        if ids is not None:
            pnl = panels if panels is not None else np.ones(len(ids))
            alts = alts.astype(str)
            alts = alts if len(alts) == len(ids)\
                else np.tile(alts, int(len(ids)/len(alts)))
            cols = np.zeros(len(ids), dtype={'names': ['panels', 'ids', 'alts'],
                                             'formats': ['<f4', '<f4', '<U64']})
            cols['panels'], cols['ids'], cols['alts'] = pnl, ids, alts
            sorted_idx = np.argsort(cols, order=['panels', 'ids', 'alts'])
            X, y = X[sorted_idx], y[sorted_idx]
            if panels is not None:
                panels = panels[sorted_idx]
            self._check_long_format_consistency(ids, alts, sorted_idx)
        return X, y, panels

    def _validate_inputs(self, X, y, alts, varnames, isvars, ids, weights,
                         panels, base_alt, fit_intercept, max_iterations):
        if varnames is None:
            raise ValueError('The parameter varnames is required')
        if alts is None:
            raise ValueError('The parameter alternatives is required')
        if X.ndim != 2:
            raise ValueError("X must be an array of two dimensions in "
                             "long format")
        if y.ndim != 1:
            raise ValueError("y must be an array of one dimension in "
                             "long format")
        if len(varnames) != X.shape[1]:
            raise ValueError("The length of varnames must match the number "
                             "of columns in X")

    def summary(self):
        """
        Prints in console the coefficients and additional estimation outputs
        """
        if self.coeff_ is None:
            print("The current model has not been yet estimated")
            return
        if not self.convergence:
            print("-"*50)
            print("WARNING: Convergence was not reached during estimation. "
                  "The given estimates may not be reliable")
            if hasattr(self, "gtol_res"):
                print("gtol:", self.gtol)
                print("Final gradient norm:", self.gtol_res)
            print('*'*50)
        print("Estimation time= {:.1f} seconds".format(self.estim_time_sec))

        if hasattr(self, 'pred_prob'):
            print("Frequencies of alternatives: observed choice")
            print(self.obs_prob)
            print("Frequencies of alternatives: predicted choice")
            print(self.pred_prob)

        fmt = "{:19} {:13.10f} {:13.10f} {:13.10f} {:13.3g} {:3}"
        coeff_name_str_length = 19
        if self.is_latent_class:
            coeff_name_str_length = 28
            print("-"*84)
            fmt = "{:28} {:13.10f} {:13.10f} {:13.10f} {:13.3g} {:3}"
            print("{:28} {:>13} {:>13} {:>13} {:>13}"
              .format("Coefficient", "Estimate", "Std.Err.", "z-val", "P>|z|"))
            print("-"*84)
        else:
            print("-"*75)
            print("{:19} {:>13} {:>13} {:>13} {:>13}"
              .format("Coefficient", "Estimate", "Std.Err.", "z-val", "P>|z|"))
            print("-"*75)
        for i in range(len(self.coeff_)):
            signif = ""
            if self.pvalues[i] < 0.001:
                signif = "***"
            elif self.pvalues[i] < 0.01:
                signif = "**"
            elif self.pvalues[i] < 0.05:
                signif = "*"
            elif self.pvalues[i] < 0.1:
                signif = "."
            print(fmt.format(self.coeff_names[i][:coeff_name_str_length], self.coeff_[i],
                             self.stderr[i], self.zvalues[i], self.pvalues[i],
                             signif
                            ))
        if self.is_latent_class:
            zvalues = np.nan_to_num(self.class_x/self.class_x_stderr)
            # set maximum (and minimum) limits to zvalues
            zvalues = [z if z > -1e+5 else -1e+5 for z in zvalues]
            pvalues = 2*(1 - t.cdf(np.abs(zvalues), df=self.sample_size))
            self.pvalues_member = pvalues
            coeff_names_member = np.array([])
            for ii, member_class in enumerate(self.member_params_spec):
                # class_coeff_names = coeff_names[self._get_class_X_idx(i)]
                # logic for isvars
                # Remove lambda coeffs from member class param names
                # TODO! BELOW LINE IN PROGRESS
                member_class_names_idx = self._get_member_X_idx(ii) #, coeff_names=self.Xnames)
                lambda_idx = np.where(np.char.find(self.Xnames, 'lambda') != -1)[0]
                sd_idx = np.where(np.char.find(self.Xnames, 'sd') != -1)[0]
                chol_idx = np.where(np.char.find(self.Xnames, 'chol') != -1)[0]
                member_class_names_idx = [x for x in member_class_names_idx
                            if x not in sd_idx and x not in chol_idx
                            and x not in lambda_idx]
                member_class_names_idx = np.sort(member_class_names_idx)
                member_class_names = self.Xnames[member_class_names_idx]

                # member_class_names_idx = [np.where(np.char.find(self.Xnames, param) != -1)[0] for param in member_class]
                # member_class_names_idx = np.concatenate(member_class_names_idx)
                # lambda_idx = np.where(np.char.find(self.Xnames, 'lambda') != -1)[0]
                # member_class_names_idx = [x for x in member_class_names_idx
                #                           if x not in sd_idx and x not in chol_idx
                #                           and x not in lambda_idx]
                # member_class_names_idx = np.sort(member_class_names_idx)
                member_class_names = self.Xnames[member_class_names_idx]

                class_coeff_names = np.core.defchararray.add('class-' +
                                                             str(ii+2) +
                                                             ': ',
                                                             member_class_names
                                                             )
                coeff_names_member = np.concatenate((coeff_names_member, class_coeff_names))

            print("-"*84)
            print("{:30} {:>13} {:>13} {:>13} {:>13}"
                  .format("Class Member Coeff", "Estimate", "Std.Err.", "z-val", "P>|z|"))
            print("-"*84)
            for ii, coeff_name in enumerate(coeff_names_member):
                signif = ""
                if pvalues[ii] < 0.001:
                    signif = "***"
                elif pvalues[ii] < 0.01:
                    signif = "**"
                elif pvalues[ii] < 0.05:
                    signif = "*"
                elif pvalues[ii] < 0.1:
                    signif = "."
                # note below: offset coeffnames by num_params to ignore class0
                print(fmt.format(coeff_name[:30], self.class_x[ii],
                                 self.class_x_stderr[ii], zvalues[ii],
                                 pvalues[ii], signif
                                 ))

        print("-"*84) if self.is_latent_class else print("-"*75)
        print("Significance:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1")
        print("")
        print("Log-Likelihood= {:.3f}".format(self.loglikelihood))
        print("AIC= {:.3f}".format(self.aic))
        print("BIC= {:.3f}".format(self.bic))

    # def choice_pred_alts(self, verbose=True):
    #     """ Function for choice-level predicted alternatives"""
    #     fmt = "{:11}"
    #     if self.choice_pred_prob.ndim == 2:
    #         pred_alts = self.ind_pred_alts()
    #         return pred_alts
    #     N, P, _ = self.choice_pred_prob.shape
    #     pred_alts = [self.alternatives[np.argmax(choice)]
    #                  for ind in self.choice_pred_prob for choice in ind]
    #     pred_alts = np.array(pred_alts).flatten()

    #     num_alts_pred = [len(np.where(pred_alts == self.alternatives[i])[0])
    #                      for i in range(len(self.alternatives))]
        
    #     if verbose:
    #         print("Number of each altenative predicted (choice):")
    #         for alt in self.alternatives:
    #             print(fmt.format(alt), end='  ')
    #         print()
    #         for pred in num_alts_pred:
    #             print(fmt.format(pred), end='  ')
    #         print()
    #     return pred_alts.reshape((N, P))

    # def ind_pred_alts(self, verbose=True):
    #     """ Function for ind-level predicted alternatives"""
    #     fmt = "{:11}"
    #     pred_alts = [self.alternatives[np.argmax(ind_row)]
    #                  for ind_row in self.ind_pred_prob]
    #     num_alts_pred = [len(np.where(pred_alts == self.alternatives[i])[0])
    #                      for i in range(len(self.alternatives))]
    #     if verbose:
    #         print("Number of each altenative predicted (individual):")
    #         for alt in self.alternatives:
    #             print(fmt.format(alt), end='  ')
    #         print()
    #         for pred in num_alts_pred:
    #             print(fmt.format(pred), end='  ')
    #         print()

    #     return pred_alts

    def corr(self):
        corr_varnames = [self.varnames[pos] for pos in self.correlationpos]
        K = len(corr_varnames) + 1  # + 1 for coeff names row/col
        str_mat = np.array([])
        # top row of coef names
        str_mat = np.append(str_mat, np.array([''] + corr_varnames))
        self.corr_mat = np.round(self.corr_mat[0:len(corr_varnames),
                                               0:len(corr_varnames)], 8)
        fmt = "{:11}"
        print("correlation matrix")
        if dev.using_gpu:
            self.corr_mat = dev.to_cpu(self.corr_mat)
        for ii, row in enumerate(self.corr_mat):
            str_mat = np.append(str_mat, corr_varnames[ii])
            str_mat = np.append(str_mat, np.array(row))
        str_mat = str_mat.reshape((K, K))
        for row in str_mat:
            for el in row:
                print(fmt.format(el), end='  ')
            print('')

    def cov(self):
        corr_varnames = [self.varnames[pos] for pos in self.correlationpos]
        K = len(corr_varnames) + 1 # + 1 for coeff names row/col
        str_mat = np.array([])
        # top row of coef names
        str_mat = np.append(str_mat, np.array([''] + corr_varnames))
        #
        cov_mat = np.round(self.omega[0:len(corr_varnames), 0:len(corr_varnames)], 8)
        fmt = "{:11}"
        print("covariance matrix")
        if dev.using_gpu:
            cov_mat = dev.to_cpu(cov_mat)
        for ii, row in enumerate(cov_mat):
            str_mat = np.append(str_mat, corr_varnames[ii])
            str_mat = np.append(str_mat, np.array(row))
        str_mat = str_mat.reshape((K, K))
        for row in str_mat:
            for el in row:
                print(fmt.format(el), end='  ')
            print('')

    def fitted(self, type="parameters"):

        # TODO: Testing in progress
        for k in range(self.Kr):
            s_jn = np.mean(self.pch2_sd_test[:, k])
            s_jn2 = np.sum(self.pch2_sd_test[:, k])

        if type == "parameters":
            if hasattr(self, 'pch2_res'):
                return self.pch2_res
        return

    # def _get_stddev(self):
    #     coeff_names = [x for x in self.varnames if x in self.randvars]
    #     diags = np.round(np.sqrt(np.diag(self.omega)), 8)

    #     distributions = [self.randvarsdict[name] for name in coeff_names]
    #     print('Standard Deviations')
    #     stdevs = np.zeros(len(diags))

    #     means = self.betas[self.Kf:self.Kf+self.Kr]
    #     # TODO: get means

    #     for ii, val in enumerate(diags):
    #         dist = distributions[ii]
    #         if dist == 'n':
    #             stdev = val 
    #         if dist == 'ln':
    #             stdev = np.sqrt(np.exp(val ** 2) - 1) * \
    #                 np.exp(means[ii] + 0.5 * val ** 2)
    #             # stdev =  # var = exp(2m + s)[exp(s) - 1]
    #         # if dist == 'tn':
    #         #     stdev = 
    #         if dist == 'u':
    #             stdev = (val ** 2)/3
    #             # stdev =  # var
    #         if dist == 't':
    #             stdev = val
    #             # stdev = 
    #         stdevs[ii] = stdev
    #     return stdevs

    def stddev(self):
        fmt = "{:11}"

        diags = np.round(np.sqrt(np.diag(self.omega)), 8)
        corr_varnames = [self.varnames[pos] for pos in self.correlationpos]
        rv_names_noncorr = [name for name in self.varnames
                            if name in self.randvars and name not in
                            corr_varnames]
        rvtrans_names = [name for name in self.varnames
                         if name in self.randtransvars]

        distributions_corr = [self.randvarsdict[name] for name in
                              corr_varnames]
        distributions_rv = [self.randvarsdict[name] for name in rv_names_noncorr]
        distributions_rvtrans = [self.randvarsdict[name] for name in
                                 rvtrans_names]
        distributions = distributions_corr + distributions_rv + distributions_rvtrans
        print('Standard Deviations')
        stdevs = np.zeros(len(diags))

        means = self.betas[self.Kf:self.Kf+self.Kr]
        # TODO: get means
        for ii, val in enumerate(diags):
            dist = distributions[ii]
            if dist == 'n':
                stdev = val
            if dist == 'ln':
                stdev = np.sqrt(np.exp(val ** 2) - 1) * \
                    np.exp(means[ii] + 0.5 * val ** 2)
                # stdev =  # var = exp(2m + s)[exp(s) - 1]
            # if dist == 'tn':
            if dist == 'u':
                stdev = (val ** 2)/3
                # stdev =  # var
            if dist == 't':
                stdev = val
            stdevs[ii] = np.round(stdev, 8)

        rv_names_all = corr_varnames + rv_names_noncorr + rvtrans_names
        for name in rv_names_all:
            print(fmt.format(name), end='  ')
        print('')
        for std in stdevs:  # todo? diags?
            print(fmt.format(std), end='  ')
        print('')
        pass
