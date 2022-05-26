from .multinomial_logit import MultinomialLogit
from .mixed_logit import MixedLogit
from .latent_class_model import LatentClassModel
from .latent_class_mixed_model import LatentClassMixedModel
import numpy as np
# import pandas as pd
import time
import datetime
import matplotlib.pyplot as plt
import sys
import math
import copy
import logging
from ._device import device as dev
# from matplotlib.backends.backend_pdf import PdfPages

logger = logging.getLogger(__name__)

# TODO: global vars up here
# boxc_l is the list of suffixes used to denote manually transformed variables
boxc_l = ['L1', 'L2']  # ['L1','L2','L3']
l1 = np.log
l2 = 0.5


class Search():
    def __init__(self, dist=None, code_name="abc", avail=None, weights=None,
                 varnames=None, df=None, df_test=None, choice_set=None,
                 choice_var=None, test_choice=None,
                 alt_var=None, choice_id=None, ind_id=None, isvarnames=None,
                 asvarnames=None, trans_asvars=None, ftol=1e-5, gtol=1e-5,
                 latent_class=False, num_classes=2, maxiter=200, verbose=0,
                 multi_objective=False, p_val=0.05, Chosen_alts_test=None,
                 test_chid=None, test_ind_id=None,
                 test_alt_var=None, test_av=None, test_weight_var=None,
                 allow_random=True, allow_bcvars=True, base_alt=None, logger_level = None):
        # TODO? GOOD ARANGING AND DESCRIPTION OF INIT PARAMS
        # TODO! LOGGING ONLY IF NOT SET ALREADY
        self.dist = dist  # List of random distributions to select from
        self.code_name = code_name
        self.current_date = datetime.datetime.now().strftime("%d%m%Y-%H%M%S")

        logger_name = code_name + "_" + self.current_date + ".log"
        if logger_level is None:
            logger_level = logging.INFO
        logging.basicConfig(filename=logger_name, level=logger_level)
        self.logger_name = logger_name

        self.avail = avail
        self.weights = weights
        self.varnames = varnames
        self.df = df
        self.df_test = df_test
        self.choice_set = choice_set
        self.choice_var = choice_var
        self.test_choice = test_choice
        self.alt_var = alt_var
        self.choice_id = choice_id
        self.ind_id = ind_id

        if isvarnames is None:
            isvarnames = []
        self.isvarnames = isvarnames

        if asvarnames is None:
            asvarnames = []
        self.asvarnames = asvarnames

        self.trans_asvars = trans_asvars
        self.ftol = ftol
        self.gtol = gtol
        self.latent_class = latent_class
        self.num_classes = num_classes
        self.maxiter = maxiter
        self.verbose = verbose
        self.test_av = test_av
        self.test_weight_var = test_weight_var
        self.multi_objective = multi_objective
        self.p_val = p_val
        self.test_chid = test_chid  # TODO? Handle automatically?
        self.test_ind_id = test_ind_id
        self.test_alt_var = test_alt_var
        self.allow_random = allow_random
        self.allow_bcvars = allow_bcvars  # TODO! NOT WORKING EVERYWHERE...
        self.base_alt = base_alt

        self.val_share = 0.25  # Proportion of sample held out for validation
        if Chosen_alts_test is None:
            try:
                Chosen_alts_test = df_test.query('choice == True')['alt']
            except Exception:
                Chosen_alts_test = df_test.query('CHOICE == True')['alt']

        self.obs_freq = (np.array(Chosen_alts_test.value_counts().
                         values.tolist()))/(df_test.shape[0]/len(choice_set))

    def prespec_features(self, ind_psasvar, ind_psisvar, ind_pspecdist,
                         ind_psbcvar, ind_pscorvar, isvarnames, asvarnames):
        """
        Generates lists of features that are predetermined by the modeller for
        the model development
        Inputs:
        (1) ind_psasvar - indicator list for prespecified asvars
        (2) ind_psisvar - indicator list for prespecified isvars
        (3) ind_pspecdist - indicator list for vars with prespecified coefficient distribution
        (4) ind_psbcvar - indicator list for vars with prespecified transformation
        (5) ind_pscorvar - indicator list for vars with prespecified correlation
        """
        # prespecified alternative-specific variables
        ps_asvar_pos = [i for i, x in enumerate(ind_psasvar) if x == 1]
        ps_asvars = [var for var in asvarnames if asvarnames.index(var) in ps_asvar_pos]

        # prespecified individual-specific variables
        ps_isvar_pos = [i for i, x in enumerate(ind_psisvar) if x == 1]
        ps_isvars = [var for var in isvarnames if isvarnames.index(var) in ps_isvar_pos]

        # prespecified coeff distributions for variables
        ps_rvar_ind = dict(zip(asvarnames, ind_pspecdist))
        ps_rvars = {k: v for k, v in ps_rvar_ind.items() if v != "any"}

        # prespecified non-linear transformed variables
        ps_bcvar_pos = [i for i, x in enumerate(ind_psbcvar) if x == 1]
        ps_bcvars = [var for var in asvarnames if asvarnames.index(var) in ps_bcvar_pos]

        # prespecified correlated variables
        ps_corvar_pos = [i for i, x in enumerate(ind_pscorvar) if x == 1]
        ps_corvars = [var for var in asvarnames if asvarnames.index(var) in ps_corvar_pos]

        return(ps_asvars, ps_isvars, ps_rvars, ps_bcvars, ps_corvars)

    def avail_features(self, asvars_ps, isvars_ps, rvars_ps, bcvars_ps,
                       corvars_ps, isvarnames, asvarnames):
        """
        Generates lists of features that are availbale to select from for model development
        Inputs:
        (1) asvars_ps - list of prespecified asvars
        (2) isvars_ps - list of prespecified isvars
        (3) rvars_ps - list of vars and their prespecified coefficient distribution
        (4) bcvars_ps - list of vars that include prespecified transformation
        (5) corvars_ps - list of vars with prespecified correlation
        """
        # available alternative-specific variables for selection
        avail_asvars = [var for var in asvarnames if var not in asvars_ps]

        # available individual-specific variables for selection
        avail_isvars = [var for var in isvarnames if var not in isvars_ps]

        # available variables for coeff distribution selection
        avail_rvars = [var for var in asvarnames if var not in rvars_ps.keys()]

        # available alternative-specific variables for transformation
        avail_bcvars = [var for var in asvarnames if var not in bcvars_ps]

        # available alternative-specific variables for correlation
        avail_corvars = [var for var in asvarnames if var not in corvars_ps]

        return (avail_asvars, avail_isvars, avail_rvars, avail_bcvars, avail_corvars)

    def df_coeff_col(self, seed, dataframe, test_df, names_asvars,
                     choiceset, var_alt):
        """
        This function creates dummy dataframe columns for variables,
        which are randomly selected to be estimated with
        alternative-specific coefficients.
        Inputs: random seed - int
                dataframe - pd.dataframe
                asvars - list of variable names to be considered
                choise_set - list of available alternatives
                var_alt - dataframe column consisting of alternative variable
        Output: List of as variables considered for model development
        """
        np.random.seed(seed)
        random_matrix = np.random.randint(0, 2, len(names_asvars))
        asvars_new = []
        alt_spec_pos_str = [str(var) for var in names_asvars if
                            random_matrix[names_asvars.index(var)] == 1]
        for i in alt_spec_pos_str:
            for j in choiceset:
                # TODO?: SAVE THIS PROPERLY?
                dataframe[i + '_' + j] = dataframe[i]*(var_alt == j)
                test_df[i + '_' + j] = test_df[i]*(var_alt == j)
                asvars_new.append(i + '_' + j)
    
        asvars_new.extend([str(integer) for integer in names_asvars
                           if random_matrix[names_asvars.index(integer)] == 0])
        return(asvars_new)

    # Removing redundancy if the same variable is included in the model with and without transformation
    # or with a combination of alt-spec and generic coefficients
    def remove_redundant_asvars(self, asvar_list, transasvars, seed, asvarnames):
        redundant_asvars = [s for s in asvar_list if any(xs in s for xs in transasvars)]
        unique_vars = [var for var in asvar_list if var not in redundant_asvars]
        np.random.seed(seed)
        # When transformations are not applied, the redundancy is created if a variable has both generic & alt-spec co-effs
        if len(transasvars) == 0:
            gen_var_select = [var for var in asvar_list if var in asvarnames]
            alspec_final = [var for var in asvar_list if var not in gen_var_select]
        else:
            gen_var_select = []
            alspec_final = []
            for var in transasvars:
                redun_vars = [item for item in asvar_list if var in item]
                gen_var = [var for var in redun_vars if var in asvarnames]
                if gen_var:
                    gen_var_select.append(np.random.choice(gen_var))
                alspec_redun_vars = [item for item in asvar_list
                                     if var in item and item not in asvarnames]
                trans_alspec = [i for i in alspec_redun_vars
                                if any(l for l in boxc_l if l in i)]
                lin_alspec = [var for var in alspec_redun_vars
                              if var not in trans_alspec]
                if np.random.randint(2):
                    alspec_final.extend(lin_alspec)
                else:
                    alspec_final.extend(trans_alspec)
        np.random.seed(seed)
        if len(gen_var_select) and len(alspec_final) != 0:
            if np.random.randint(2):
                final_asvars = gen_var_select
                final_asvars.extend(unique_vars)
            else:
                final_asvars = alspec_final
                final_asvars.extend(unique_vars)

        elif len(gen_var_select) != 0:
            final_asvars = gen_var_select
            final_asvars.extend(unique_vars)
        else:
            final_asvars = alspec_final
            final_asvars.extend(unique_vars)

        return(list(dict.fromkeys(final_asvars)))

    def generate_sol(self, data, test_df, seed, asvars_avail, isvars_avail, rvars_avail,
                     transasvars, bcvars_avail, corvars_avail, asvars_ps,  # TODO? ADD CLASS, MEMBER PS?
                     isvars_ps, rvars_ps, bcvars_ps, corvars_ps, bctrans_ps,
                     cor_ps, intercept_ps, asvarnames, choice_set, alt_var):
        """
        Generates list of random model features and then includes modeller prespecifications
        Inputs:
        (1) seed - seed for random generators
        (2) asvars_avail - list of available asvars for random selection
        (3) isvars_avail - list of available isvars for random selection
        (4) rvars_avail - list of available vars for randomly selected coefficient distribution
        (5) bcvars_avail - list of available vars for random selection of transformation
        (6) corvars_avail - list of available vars for random selection of correlation
        ## Prespecification information
        (1) asvars_ps - list of prespecified asvars
        (2) isvars_ps - list of prespecified isvars
        (3) rvars_ps - list of vars and their prespecified coefficient distribution
        (4) bcvars_ps - list of vars that include prespecified transformation
        (5) corvars_ps - list of vars with prespecified correlation
        (6) bctrans_ps - prespecified transformation boolean
        (7) cor_ps - prespecified correlation boolean
        (8) intercept_ps - prespecified intercept boolean

        """

        np.random.seed(seed)
        ind_availasvar = []
        for i in range(len(asvars_avail)):
            ind_availasvar.append(np.random.randint(2))
        asvar_select_pos = [i for i, x in enumerate(ind_availasvar) if x == 1]
        asvars_1 = [var for var in asvars_avail if asvars_avail.index(var)
                    in asvar_select_pos]
        asvars_1.extend(asvars_ps)

        asvars_new = self.remove_redundant_asvars(asvars_1, transasvars, seed,
                                                  asvarnames)
        # TODO! TESTING REMOVAL
        # asvars = self.df_coeff_col(seed, data, test_df, asvars_new,
        #                            choice_set, alt_var)
        asvars = asvars_new

        ind_availisvar = []
        for i in range(len(isvars_avail)):
            ind_availisvar.append(np.random.randint(2))
        isvar_select_pos = [i for i, x in enumerate(ind_availisvar) if x == 1]
        isvars = [var for var in isvars_avail if isvars_avail.index(var) in isvar_select_pos]
        isvars.extend(isvars_ps)

        if intercept_ps is None:
            asc_ind = bool(np.random.randint(2, size=1))
        else:
            asc_ind = intercept_ps


        # TODO! MORE IN TESTING CODE ...
        asc_var = ['_inter'] if asc_ind else []  # Add intercept to class param
        all_vars = asvars + isvars + asc_var
        class_vars = asvars + asc_var
        member_vars = isvars # TODO! REMOVED ASC_VAR? + asc_var
        class_params_spec = None
        member_params_spec = None
        if self.latent_class:
            class_params_spec = np.array(np.repeat('tmp', self.num_classes),
                                        dtype='object')

            member_params_spec = np.array(np.repeat('tmp', self.num_classes-1),
                                        dtype='object')

            for i in range(self.num_classes):
                tmp_class_spec = np.array([])
                for var in class_vars:
                    # TODO! ARBITRARY PROB HERE OF ACCEPTANCE... kept high...
                    if np.random.uniform() < 0.8:  # 0.5 prob of accepting asvar  TODO?
                        tmp_class_spec = np.append(tmp_class_spec, var)
                class_params_spec[i] = tmp_class_spec

            for i in range(self.num_classes-1):
                tmp_member_spec = np.array([])
                for var in member_vars:
                    if np.random.uniform() < 0.8:  # 0.5 prob of accepting asvar  TODO?
                        tmp_member_spec = np.append(tmp_member_spec, var)
                member_params_spec[i] = tmp_member_spec

        r_dist = []
        avail_rvar = [var for var in asvars if var in rvars_avail]

        for i in range(len(avail_rvar)):
            r_dist.append(np.random.choice(self.dist))

        rvars = dict(zip(avail_rvar, r_dist))
        rvars.update(rvars_ps)

        rand_vars = {k: v for k, v in rvars.items() if v != "f" and k in asvars}
        r_dis = [dis for dis in self.dist if dis != "f"]
        for var in corvars_ps:
            if var in asvars and var not in rand_vars.keys():
                rand_vars.update({var: np.random.choice(r_dis)})

        if bctrans_ps is None:
            bctrans = bool(np.random.randint(2, size=1))
        else:
            bctrans = bctrans_ps

        if bctrans:
            ind_availbcvar = []
            for i in range(len(bcvars_avail)):
                ind_availbcvar.append(np.random.randint(2))
            bcvar_select_pos = [i for i, x in enumerate(ind_availbcvar) if x == 1]
            bcvars = [var for var in bcvars_avail if bcvars_avail.index(var) in bcvar_select_pos]
            bcvars.extend(bcvars_ps)
            bc_vars = [var for var in bcvars if var in asvars and var not in corvars_ps]
            # variables with random parameters cannot be estimated with lambda
            # TODO?? IS THIS RIGHT
            bc_vars = [var for var in bc_vars if var not in rand_vars.keys()]
        else:
            bc_vars = []

        if cor_ps is None:
            cor = bool(np.random.randint(2, size=1))
        else:
            cor = cor_ps

        if cor:
            ind_availcorvar = []
            for i in range(len(corvars_avail)):
                ind_availcorvar.append(np.random.randint(2))
            corvar_select_pos = [i for i, x in enumerate(ind_availcorvar)
                                 if x == 1]
            corvars = [var for var in corvars_avail if corvars_avail.index(var)
                       in corvar_select_pos]
            corvars.extend(corvars_ps)
            cor_vars = [var for var in corvars if var in rand_vars.keys()
                        and var not in bc_vars]
            if len(cor_vars) < 2:
                cor = False
                cor_vars = []
        else:
            cor_vars = []

        return(asvars, isvars, rand_vars, bc_vars, cor_vars, bctrans, cor,
               class_params_spec, member_params_spec,
               asc_ind)

    def fit_mnl(self, dat, test_df, as_vars, is_vars, bcvars, choice, alt,
                id_choice,
                test_choice, asc_ind, alt_var, avail=None, weights=None,
                iterations=200,
                ftol=1e-4, gtol=1e-4):
        """
        Estimates multinomial model for the generated solution
        Inputs:
        (1) dat in csv
        (2) as_vars: list of alternative-specific variables
        (3) is_vars: list of individual-specific variables
        (4) bcvars: list of box-cox variables
        (5) choice: df column with choice variable
        (6) alt: df column with alternative variables
        (7) id_choice: df column with choice situation id
        (8) asc_ind: boolean for fit_intercept
        """
        # data = dat.copy()
        try:
            all_vars = as_vars + is_vars
            avail = avail or self.avail
            weights = weights or self.weights

            X = dat[all_vars].values
            y = choice
            model = MultinomialLogit()
            model.fit(X, y, varnames=all_vars, isvars=is_vars, alts=alt_var,
                    ids=id_choice, fit_intercept=asc_ind,
                    transformation="boxcox", transvars=bcvars,
                    maxiter=self.maxiter, ftol=ftol, gtol=self.gtol, avail=avail,
                    weights=weights, base_alt=self.base_alt)
    
            bic = round(model.bic)
            ll = round(model.loglikelihood)
            def_vals = model.coeff_

            rand_vars = {}
            cor_vars = []
            bc_vars = [var for var in bcvars if var not in self.isvarnames]

            old_stdout = sys.stdout
            log_file = open(self.logger_name, "a")
            sys.stdout = log_file
            model.summary()
            sys.stdout = old_stdout
            log_file.close()

            conv = model.convergence
            pvals = model.pvalues
            coef_names = model.coeff_names

            # TODO? MOOF specific?
            # Validation
            X_test = test_df[all_vars].values
            y_test = test_choice
            # TODO? val not used?
            val = round(model.validation_loglik(X_test, y_test.values))

            # Choice frequecy obtained from estimated model applied on testing sample
            # predicted_probabilities_val = model.pred_prob

            ## Calculating MAE
            model = MultinomialLogit()
            model.fit(X_test, y_test, varnames=all_vars, isvars=is_vars, alts=alt_var, ids=self.test_chid, fit_intercept=asc_ind,
                    transformation="boxcox",transvars = bcvars,maxiter=0, init_coeff=def_vals, gtol = self.gtol,
                    avail = self.test_av,weights=self.test_weight_var, base_alt = self.base_alt)

            ### Choice frequecy obtained from estimated model applied on testing sample
            predicted_probabilities_val = model.pred_prob * 100
            obs_freq = model.obs_prob * 100

            MAE = round((1/len(self.choice_set))  * (np.sum(np.abs(predicted_probabilities_val - obs_freq))), 2)
            #  TODO? Below not used here
            MAPE = round((100/len(self.choice_set))*(np.sum(abs((predicted_probabilities_val - obs_freq)/obs_freq))))
        except Exception as e:
            logger.error("Error: ", e)
            bic = 1000000
            MAE= 100.00
            MAPE = 100.00
            ll = 1000000
            val = 1000000
            as_vars = []
            is_vars = []
            rand_vars = {}
            bc_vars = []
            cor_vars = []
            conv = False
            pvals = []
            coef_names = []

        logger.info("model BIC: {}".format(bic))
        logger.info("model LL: {}".format(ll))
        logger.info("model val: {}".format(val))
        logger.info("MAE: {}".format(MAE))
        logger.info("MAPE: {}".format(MAPE))
        logger.info("model convergence: {}".format(conv))
        logger.info("dof: {}".format(len(coef_names)))


        if any(l for l in coef_names if l.startswith("lambda.")):
            logger.info("model type is nonlinear MNL")
        else:
            logger.info("model type is MNL")

        # TODO: RYAN ADD - VAL MAE FOR MOOF AND LL FOR SOOF
        val = ll
        if self.multi_objective:
            val = MAE

        return(bic, val, as_vars, is_vars, rand_vars, bc_vars, cor_vars,
               conv, pvals, coef_names)

    def fit_mxl(self, dat, test_df, as_vars, is_vars, rand_vars, bcvars, corvars,
                choice, alt, id_choice, id_val, test_choice,
                asc_ind, avail=None,
                weights=None, iterations=200, tol=1e-2, R=200):
        """
        Estimates the model for the generated solution
        Inputs:
        (1) dat: dataframe in csv
        (2) as_vars: list of alternative-specific variables
        (3) is_vars: list of individual-specific variables
        (4) bcvars: list of box-cox variables
        (5) choice: df column with choice variable
        (6) corvars: list of variables allowed to correlate
        (7) alt: df column with alternative variables
        (8) id_choice: df column with choice situation id
        (9) id_val: df column with individual id
        (10) asc_ind: boolean for fit_intercept
        """
        # data = dat.copy()  # TODO?
        all_vars = as_vars + is_vars
        X = dat[all_vars]
        y = choice
        if corvars == []:
            corvars = False

        bcvars = [var for var in bcvars if var not in self.isvarnames]
        try:
            model = MixedLogit()
            model.fit(X, y, varnames=all_vars, alts=alt, isvars=is_vars,
                    ids=id_choice, panels=id_val, randvars=rand_vars,
                    n_draws=R, fit_intercept=asc_ind, correlation=corvars,
                    transformation="boxcox", transvars=bcvars,
                    maxiter=self.maxiter, avail=avail, ftol=tol, gtol=tol,
                    weights=weights, base_alt=self.base_alt)

            bic = round(model.bic)
            ll = round(model.loglikelihood)
            def_vals = model.coeff_
            old_stdout = sys.stdout
            log_file = open(self.logger_name, "a")
            sys.stdout = log_file
            model.summary()
            conv = model.convergence
            pvals = model.pvalues
            coef_names = model.coeff_names

            logel.debug("model convergence", model.convergence)

            # Validation
            X_test = test_df[all_vars].values
            y_test = test_choice
            val = model.loglikelihood - round(model.validation_loglik(X_test,
                                                                y_test.values,
                                                                panels=self.test_ind_id)
                                        / self.val_share)

            sys.stdout = old_stdout
            log_file.close()

            logger.info("val: {}".format(val))

            # MAE
            model = MixedLogit()
            model.fit(X_test, y_test, varnames=all_vars, alts=self.test_alt_var,
                    isvars=is_vars,
                    ids=self.test_chid, panels=self.test_ind_id,
                    randvars=rand_vars, n_draws=R,
                    fit_intercept=asc_ind, correlation=corvars,
                    transformation="boxcox",
                    transvars=bcvars, avail=self.test_av, maxiter=0,
                    init_coeff=def_vals, gtol=self.gtol,
                    weights=self.test_weight_var,
                    base_alt=self.base_alt)

            # Calculating MAE

            # Choice frequecy obtained from estimated model applied on testing sample
            predicted_probabilities_val = model.pred_prob * 100
            obs_freq = model.obs_prob * 100

            # TODO! GPU issues
            MAE = round((1/len(self.choice_set))*(np.sum(abs(predicted_probabilities_val -
                                                    obs_freq))), 2)
            MAPE = round((100/len(self.choice_set))*(np.sum(abs((predicted_probabilities_val - obs_freq)/obs_freq))))
        except:
            bic = 1000000
            MAE = 100.00
            MAPE = 100.00
            ll = 1000000
            val = 1000000
            as_vars = []
            is_vars = []
            rand_vars = {}
            bcvars = []
            corvars = []
            conv = False
            pvals = []
            coef_names = []

        if any(l for l in coef_names if l.startswith("chol.")):
            if any(l for l in coef_names if l.startswith("lambda.")):
                logger.info("model type is nonlinear correlated MXL")
            else:
                logger.info("model type is linear correlated MXL")
        elif any(l for l in coef_names if l.startswith("lambda.")):
            logger.info("model type is nonlinear MXL")
        else:
            logger.info("model type is MXL")

        logger.info("model BIC: {}".format(bic))
        logger.info("model LL: {}".format(ll))
        logger.info("model val: {}".format(val))
        logger.info("MAE: {}".format(MAE))
        logger.info("MAPE: {}".format(MAPE))
        logger.info("model convergence: {}".format(conv))
        logger.info("dof: {}".format(len(coef_names)))

        return(bic, MAE, as_vars, is_vars, rand_vars, bcvars, corvars, conv, pvals, coef_names)

    def fit_lccm(self, dat, test_df, as_vars, is_vars, class_params_spec,
                 member_params_spec,
                 num_classes,
                 bcvars, choice, alt, id_choice, test_choice, asc_ind):
        """Estimates multinomial model for the generated solution.
        Inputs:
        (1) dat in csv
        (2) as_vars: list of alternative-specific variables
        (3) is_vars: list of individual-specific variables
        (4) num_classes: number of latent classes
        (5) bcvars: list of box-cox variables
        (6) choice: df column with choice variable
        (7) alt: df column with alternative variables
        (8) id_choice: df column with choice situation id
        (9) asc_ind: boolean for fit_intercept
        """
        logger.debug('as_vars: {}'.format(as_vars))
        logger.debug('is_vars: {}'.format(is_vars))
        logger.debug('bcvars: {}'.format(bcvars))
        logger.debug('class_params_spec: {}'.format(class_params_spec))
        logger.debug('member_params_spec: {}'.format(member_params_spec))
        logger.debug('asc_ind: {}'.format(asc_ind))

        class_vars = list(np.concatenate(class_params_spec))
        member_vars = list(np.concatenate(member_params_spec))
        all_vars = class_vars + member_vars
        #  remove intecept name
        all_vars = [var_name for var_name in all_vars if var_name != '_inter']
        all_vars = np.unique(all_vars)

        X = dat[all_vars]
        y = choice
        model = LatentClassModel()
        if self.num_classes is None:
            optimal_num, model = \
                model.optimal_class_fit(X, y, varnames=all_vars,
                                        isvars=is_vars,
                                        alts=self.alt_var, ids=id_choice,
                                        fit_intercept=asc_ind,
                                        transformation="boxcox",
                                        transvars=bcvars,
                                        maxiter=self.maxiter,
                                        gtol=self.gtol,
                                        avail=self.avail,
                                        weights=self.weights,
                                        num_classes=self.num_classes)
        else:
            logger.debug('num_classes: {}'.format(self.num_classes))
            model.fit(X, y, varnames=all_vars,
                    #   isvars=is_vars,  # TODO: confirm removal of param
                      class_params_spec=class_params_spec,  # TODO!
                      member_params_spec=member_params_spec, # TODO!
                      num_classes=self.num_classes, alts=self.alt_var,
                      ids=id_choice, fit_intercept=asc_ind,
                      transformation="boxcox", transvars=bcvars,
                      maxiter=self.maxiter, gtol=self.gtol, avail=self.avail,
                      weights=self.weights)
        bic = model.bic
        # def_vals = model.coeff_
        rand_vars = {}
        cor_vars = []
        bc_vars = [var for var in bcvars if var not in self.isvarnames]
        old_stdout = sys.stdout
        log_file = open(self.logger_name, "a")
        sys.stdout = log_file
        model.summary()
        conv = model.convergence
        pvals = model.pvalues
        pvals_member = model.pvalues_member
        coef_names = model.coeff_names
        logger.info("model convergence: {}".format(conv))

        # Validation
        X_test = self.df_test[all_vars].values
        y_test = self.df_test['choice']
        val = model.loglikelihood - (model.validation_loglik(X_test,
                                                             y_test.values)
                                     / self.val_share)

        sys.stdout = old_stdout
        log_file.close()


        logger.info("val: {}".format(val))

        # Choice frequecy obtained from estimated model applied on testing sample
        predicted_probabilities_val = model.pred_prob

        # TODO? GPU issues
        # MAE = 1.0  # Safe default option for SOOF
        val = model.loglikelihood
        if self.multi_objective:
            MAE = (1/len(self.choice_set))*(np.sum(abs(predicted_probabilities_val
                                                    - self.obs_freq)))
            val = MAE
            logger.info("MAE: {}".format(val))
        else:
            logger.info("Log-likelihood: {}".format(val))



        return(bic, val, as_vars, is_vars, rand_vars, bc_vars, cor_vars,
               conv, pvals, pvals_member, coef_names)

    def fit_lccmm(self, dat, test_df, as_vars, is_vars, class_params_spec,
                  member_params_spec, num_classes, rand_vars,
                  bcvars, corvars, choice, alt, id_choice, id_val, test_choice,
                  asc_ind):
        logger.debug("estimating lccmm")
        logger.debug('as_vars: {}'.format(as_vars))
        logger.debug('is_vars: {}'.format(is_vars))
        logger.debug('rand_vars: {}'.format(rand_vars))
        logger.debug('bcvars: {}'.format(bcvars))
        logger.debug('corvars: {}'.format(corvars))
        logger.debug('asc_ind: {}'.format(asc_ind))
        R = 200  # TODO CHECK - set to Reduce computation
        # is_vars = []  # TODO! TEMP FIX AS ISVARS BROKEN WITH LCCM
        all_vars = as_vars + is_vars
        X = dat[all_vars]
        y = choice
        if corvars == []:
            corvars = False
        bcvars = [var for var in bcvars if var not in self.isvarnames]
        model = LatentClassMixedModel()
        if self.num_classes is None:
            optimal_num, model = model.fit(X, y, varnames=all_vars,
                                           alts=self.alt_var, isvars=is_vars,
                                           ids=id_choice, panels=id_val,
                                           randvars=rand_vars, n_draws=R,
                                           fit_intercept=asc_ind,
                                           correlation=corvars,
                                           transformation="boxcox",
                                           transvars=bcvars,
                                           maxiter=self.maxiter,
                                           avail=self.avail,
                                           gtol=self.gtol,
                                           weights=self.weights,
                                           grad=True,
                                           num_classes=self.num_classes)
        else:
            model.fit(X, y, varnames=all_vars, alts=self.alt_var,
                      isvars=is_vars, num_classes=self.num_classes,
                      ids=id_choice, panels=id_val,
                      randvars=rand_vars, n_draws=R,
                      fit_intercept=asc_ind, correlation=corvars,
                      transformation="boxcox", transvars=bcvars,
                      maxiter=self.maxiter, avail=self.avail,
                      gtol=self.gtol, weights=self.weights,
                      grad=True)
        bic = model.bic
        def_vals = model.coeff_
        old_stdout = sys.stdout
        log_file = open(self.logger_name, "a")
        sys.stdout = log_file
        model.summary()
        conv = model.convergence
        pvals = model.pvalues
        pvals_member = model.pvalues_member
        coef_names = model.coeff_names

        logger.info("model convergence: {}".format(model.convergence))

        # Validation
        X_test = test_df[all_vars].values
        y_test = test_choice
        # val = abs(model.loglikelihood- (model.validation_loglik(X_test,
        # y_test,panels=test_ind_id)/val_share))
        val = model.loglikelihood - \
            (model.validation_loglik(X_test,
                                     y_test.values,
                                     panels=self.df_test['id'].values)
             / self.val_share)

        sys.stdout = old_stdout
        log_file.close()


        logger.info("val: {}".format(val))
        # MAE

        # TODO: What's going on here?
        model = LatentClassMixedModel()

        model.fit(X_test, y_test, varnames=all_vars, alts=self.df_test['alt'],
                  isvars=is_vars, num_classes=self.num_classes,
                  ids=self.df_test['id'], panels=self.df_test['id'],
                  randvars=rand_vars, n_draws=R,
                  fit_intercept=asc_ind, correlation=corvars,
                  transformation="boxcox",
                  transvars=bcvars, avail=self.test_av, maxiter=0,
                  init_coeff=def_vals,  # TODO? weird saving?
                  gtol=self.gtol, weights=self.test_weight_var,
                  grad=True)

        # Calculating MAE

        # Choice frequecy obtained from estimated model applied on testing sample
        predicted_probabilities_val = model.pred_prob

        # TODO! GPU issues
        MAE = (1/len(self.choice_set))*(np.sum(abs(predicted_probabilities_val
                                                   - self.obs_freq)))
        logger.info("MAE: {}".format(MAE))

        return(bic, MAE, as_vars, is_vars, rand_vars, bcvars, corvars, conv,
               pvals, pvals_member, coef_names)

    def check_latent_validity(self, class_params_spec, member_params_spec):
        check_latent = True
        if self.latent_class:
            for class_params in class_params_spec:
                if len(class_params) == 0:
                    check_latent = False
            for member_params in member_params_spec:
                if len(member_params) == 0:
                    check_latent = False
            if class_params_spec == []:
                check_latent = False
            if member_params_spec == []:
                check_latent = False
        return check_latent

    def evaluate_objective_function(self, new_df, test_df, seed, as_vars,
                                    is_vars, rand_vars, bc_vars, cor_vars,
                                    class_params_spec, member_params_spec,
                                    choice, test_choice, alts, id_choice,
                                    id_val, asc_ind,
                                    ps_asvars, asvarnames, isvarnames,
                                    ps_isvars, ps_intercept, choice_set,
                                    ps_rvars, ps_corvars):
        """
        (1) Evaluates the objective function (estimates the model and BIC) for
        a given list of variables (estimates the model coefficeints, LL and BIC)
        (2) If the solution generated in (1) contains statistically insignificant variables,
        a new model is generated by removing such variables and the model is re-estimated
        (3) the functions returns estimated solution only if it converges
        Inputs: lists of variable names, individual specific variables,
        variables with random coefficients,
        name of the choice variable in df, list of alternatives, choice_id,
        individual_id(for panel data) and fit intercept bool
        """
        all_vars = as_vars + is_vars

        default_sol = [-10000000.0, 1.0, [], [], {}, [], [], False, [], []]
        sol = default_sol
        convergence = False

        if not cor_vars:  # TODO! RYAN CHANGE CHECK
            cor_vars = []

        check_latent = self.check_latent_validity(class_params_spec, member_params_spec)
        # TODO: DEBUG
        logger.debug('check_latent: {}'.format(check_latent))
        logger.debug('class_params_spec: {}'.format(class_params_spec))
        logger.debug('member_params_spec: {}'.format(member_params_spec))
        # Estimate model if input variables are present in specification

        # TODO! Remove remaining intercept from class params
        if not asc_ind and self.latent_class and check_latent:
            for ii, class_params in enumerate(class_params_spec):
                for jj, var in enumerate(class_params):
                    if '_inter' in var:
                        if len(class_params) > 1:
                            class_params_spec[ii] = np.delete(class_params, jj)
                        else:
                            class_params_spec[ii] = np.array([])
            for ii, member_params in enumerate(member_params_spec):
                for jj, var in enumerate(member_params):
                    if '_inter' in var:
                        if len(member_params) > 1:
                            member_params_spec[ii] = np.delete(member_params, jj)
                        else:
                            member_params_spec[ii] = np.array([])

        check_latent = self.check_latent_validity(class_params_spec, member_params_spec)

        # TODO! handle class_params / intercept here ?

        if all_vars:
            iterations = 200  # iterations for MNL fit...
            features_str =  ' '.join(as_vars) + ' '.join(is_vars)
            logger.info(("features for round 1: asvars: {}, isvars: {}, "
                         "rand_vars: {}, bc_vars: {}, cor_vars: {}, "
                         "asc_ind: {}").format(as_vars, is_vars, rand_vars,
                                               bc_vars, cor_vars, asc_ind))

            # TODO! INCLUDE DF TEST IN ALL MODELS
            if bool(rand_vars):
                if self.latent_class and check_latent:
                    # TODO: better way of including num_classes
                    bic, val, asvars, isvars, randvars, bcvars, corvars, \
                        conv, sig, sig_member, coefs = self.fit_lccmm(new_df,
                                                          self.df_test,
                                                          as_vars, is_vars,
                                                          class_params_spec,
                                                          member_params_spec,
                                                          2,
                                                          rand_vars, bc_vars,
                                                          cor_vars, choice,
                                                          alts, id_choice,
                                                          id_val,
                                                          self.test_choice,
                                                          asc_ind)
                else:
                    logger.info("estimating an MXL model")
                    bic, val, asvars, isvars, randvars, bcvars, corvars, \
                        conv, sig, coefs = self.fit_mxl(new_df, self.df_test,
                                                        as_vars, is_vars,
                                                        rand_vars, bc_vars,
                                                        cor_vars,
                                                        choice, alts,
                                                        id_choice,
                                                        id_val,
                                                        self.test_choice,
                                                        asc_ind,
                                                        avail=self.avail)
            else:
                if self.latent_class:
                    if check_latent:
                        bic, val, asvars, isvars, randvars, bcvars, corvars, \
                            conv, sig, sig_member, coefs = self.fit_lccm(new_df, self.df_test,
                                                            as_vars, is_vars,
                                                            class_params_spec,
                                                            member_params_spec,
                                                            2,
                                                            bc_vars, choice, alts,
                                                            id_choice,
                                                            self.test_choice,
                                                            asc_ind)
                    else:
                        # NOTE: using empty class and member params as sig
                        # and sigmember

                        logger.warning("Latent class generated not valid. Using default sol.")
                        default_opts = default_sol.copy()
                        default_opts.append([])
                        bic, val, asvars, isvars, randvars, bcvars, corvars, \
                            conv, sig, sig_member, coefs = [opt for opt in default_opts]
                else:
                    logger.info("estimating an MNL model")
                    bic, val, asvars, isvars, randvars, bcvars, corvars, \
                        conv, sig, coefs = self.fit_mnl(new_df, self.df_test,
                                                        as_vars, is_vars,
                                                        bc_vars, choice, alts,
                                                        id_choice,
                                                        self.test_choice,
                                                        asc_ind, alts,
                                                        self.avail,
                                                        self.weights,
                                                        iterations,
                                                        self.ftol,
                                                        self.gtol)  # TODO? ugly
            if conv:
                if not corvars:
                    corvars = []
                logger.info("solution converged in first round")
                sol = [bic, val, asvars, isvars, randvars, bcvars, corvars,
                       asc_ind, class_params_spec, member_params_spec]
                convergence = conv
                if all(v for v in sig <= self.p_val):
                    logger.info("solution has all sig-values in first  round")
                    return (sol, convergence)
                else:
                    while any([v for v in sig if self.p_val]):
                        logger.info("solution consists insignificant coeffs")
                        # create dictionary of {coefficient_names: p_values}
                        p_vals = dict(zip(coefs, sig))

                        r_dist = [dis for dis in self.dist if dis != 'f']  # list of random distributions
                        # create list of variables with insignificant coefficients
                        non_sig = [k for k, v in p_vals.items()
                                   if v > self.p_val]  # list of non-significant coefficient names
                        logger.info("non-sig coeffs are: {}".format(non_sig))
                        # keep only significant as-variables
                        asvars_round2 = [var for var in asvars if var not in non_sig]  # as-variables with significant p-vals
                        asvars_round2.extend(ps_asvars)
                        logger.info("asvars_round2 for round 2: {}".format(asvars_round2))
                        # replace non-sig alt-spec coefficient with generic coefficient
                        nsig_altspec = []
                        for var in asvarnames:
                            ns_alspec = [x for x in non_sig if x.startswith(var)]
                            nsig_altspec.extend(ns_alspec)
                            nsig_altspec_vars = [var for var in nsig_altspec
                                                 if var not in asvarnames]
                        logger.info("nsig_altspec_vars: {}".format(nsig_altspec_vars))

                        rem_asvars = []
                        # Replacing non-significant alternative-specific coeffs with generic coeffs estimation
                        if not self.latent_class or not check_latent:
                            if nsig_altspec_vars:
                                gen_var = []
                                for i in range(len(nsig_altspec_vars)):
                                    gen_var.extend(nsig_altspec_vars[i].split("_"))
                                gen_coeff = [var for var in asvarnames if var
                                            in gen_var]
                                if asvars_round2:
                                    redund_vars = [s for s in gen_coeff if any(s
                                                in xs for xs in asvars_round2)]
                                    logger.info("redund_vars for round 2: {}".format(redund_vars))
                                    asvars_round2.extend([var for var in gen_coeff
                                                        if var not in redund_vars])
                                    # rem_asvars = remove_redundant_asvars(asvars_round2,trans_asvars,seed)
                                    logger.info("asvars_round2 before removing redundancy: {}".format(asvars_round2))
                                    # rem_asvars = remove_redundant_asvars(asvars_round2,trans_asvars,seed)
                                    # checking if remove_redundant_asvars is needed or not
                                    rem_asvars = sorted(list(set(asvars_round2)))
                                else:
                                    rem_asvars = gen_coeff
                            else:
                                rem_asvars = sorted(list(set(asvars_round2)))
                            logger.info("rem_asvars = {}".format(rem_asvars))

                        rem_class_params_spec = copy.deepcopy(class_params_spec)
                        rem_member_params_spec = copy.deepcopy(member_params_spec)

                        if self.latent_class and check_latent:
                            i = 0
                            for ii, class_params in enumerate(class_params_spec):
                                tmp_class_params = class_params.copy()
                                delete_idx = []
                                for jj, _ in enumerate(class_params):
                                    if sig[i] > 0.05:
                                        delete_idx.append(jj)
                                    i += 1
                                tmp_class_params = np.delete(tmp_class_params, delete_idx)
                                rem_class_params_spec[ii] = tmp_class_params

                        if self.latent_class and check_latent:
                            i = 0
                            # rem_member_params_spec = member_params_spec.copy()
                            for ii, member_params in enumerate(member_params_spec):
                                tmp_member_params = member_params.copy()
                                delete_idx = []
                                for jj, _ in enumerate(member_params):
                                    if sig_member[i] > 0.05:
                                        delete_idx.append(jj)
                                    i += 1
                                tmp_member_params = np.delete(tmp_member_params, delete_idx)
                                rem_member_params_spec[ii] = tmp_member_params


                        # # TODO: BUG FIX Remove remaining intercept from class params
                        # if not asc_ind and self.latent_class and check_latent:
                        #     for ii, class_params in enumerate(rem_class_params_spec):
                        #         for jj, var in enumerate(class_params):
                        #             if '_inter' in var:
                        #                 if len(class_params) > 1:
                        #                     rem_class_params_spec[ii] = np.delete(class_params, jj)
                        #                 else:
                        #                     rem_class_params_spec[ii] = np.array([])
                        #     for ii, member_params in enumerate(rem_member_params_spec):
                        #         for jj, var in enumerate(member_params):
                        #             if '_inter' in var:
                        #                 if len(member_params) > 1:
                        #                     rem_member_params_spec[ii] = np.delete(member_params, jj)
                        #                 else:
                        #                     rem_member_params_spec[ii] = np.array([])


                            # 

                        # remove insignificant is-variables
                        ns_isvars = []
                        for isvar in isvarnames:
                            ns_isvar = [x for x in non_sig if
                                        x.startswith(isvar)]
                            ns_isvars.extend(ns_isvar)
                        remove_isvars = []
                        for i in range(len(ns_isvars)):
                            remove_isvars.extend(ns_isvars[i].split("."))

                        remove_isvar = [var for var in remove_isvars if var
                                        in isvars]
                        most_nsisvar = {x: remove_isvar.count(x) for x
                                        in remove_isvar}
                        rem_isvar = [k for k, v in most_nsisvar.items()
                                     if v == (len(choice_set)-1)]
                        isvars_round2 = [var for var in is_vars if var
                                         not in rem_isvar]  # individual specific variables with significant p-vals
                        isvars_round2.extend(ps_isvars)

                        rem_isvars = sorted(list(set(isvars_round2)))

                        # remove intercept if not significant and not prespecified
                        ns_intercept = [x for x in non_sig if
                                        '_intercept.' in x]  # non-significant intercepts

                        new_asc_ind = asc_ind

                        if ps_intercept is None:
                            if len(ns_intercept) == len(choice_set)-1:
                                new_asc_ind = False
                        else:
                            new_asc_ind = ps_intercept

                        # TODO! Remove remaining intercept from class params
                        if not new_asc_ind and self.latent_class and check_latent:
                            for ii, class_params in enumerate(rem_class_params_spec):
                                for jj, var in enumerate(class_params):
                                    if '_inter' in var:
                                        if len(class_params) > 1:
                                            rem_class_params_spec[ii] = np.delete(class_params, jj)
                                        else:
                                            rem_class_params_spec[ii] = np.array([])
                            for ii, member_params in enumerate(rem_member_params_spec):
                                for jj, var in enumerate(member_params):
                                    if '_inter' in var:
                                        if len(member_params) > 1:
                                            rem_member_params_spec[ii] = np.delete(member_params, jj)
                                        else:
                                            rem_member_params_spec[ii] = np.array([])
                        
                        # bug fix when old class params in while loop
                        class_params_spec = copy.deepcopy(rem_class_params_spec)
                        member_params_spec = copy.deepcopy(rem_member_params_spec)

                        # remove insignificant random coefficients

                        ns_sd = [x for x in non_sig if x.startswith('sd.')]  # non-significant standard deviations
                        ns_sdval = [str(i).replace('sd.', '') for i in ns_sd]  # non-significant random variables

                        # non-significant random variables that are not pre-included
                        remove_rdist = [x for x in ns_sdval if x not in
                                        ps_rvars.keys() or x not in rem_asvars]
                        # random coefficients for significant variables
                        rem_rand_vars = {k: v for k, v in randvars.items()
                                         if k in rem_asvars and k not in
                                         remove_rdist}
                        rem_rand_vars.update({k: v for k, v in ps_rvars.items()
                                              if k in rem_asvars and v != 'f'})
                        logger.info("rem_rand_vars = {}".format(rem_rand_vars))
                        # including ps_corvars in the model if they are included in rem_asvars
                        for var in ps_corvars:
                            if var in rem_asvars and var not in rem_rand_vars.keys():
                                rem_rand_vars.update({var: np.random.choice(r_dist)})

                        # remove transformation if not significant and non prespecified
                        ns_lambda = [x for x in non_sig if x.startswith('lambda.')]  # insignificant transformation coefficient
                        ns_bctransvar = [str(i).replace('lambda.', '')
                                         for i in ns_lambda]  # non-significant transformed var
                        rem_bcvars = [var for var in bcvars if var in
                                      rem_asvars and var not in ns_bctransvar
                                      and var not in ps_corvars]

                        # remove insignificant correlation
                        ns_chol = [x for x in non_sig if x.startswith('chol.')]  # insignificant cholesky factor
                        ns_cors = [str(i).replace('chol.', '') for i in ns_chol]  # insignicant correlated variables
                        # create a list of variables whose correlation coefficient is insignificant
                        if ns_cors:
                            ns_corvar = []
                            for i in range(len(ns_cors)):
                                ns_corvar.extend(ns_cors[i].split("."))
                            most_nscorvars = {x: ns_corvar.count(x)
                                              for x in ns_corvar}
                            logger.info('most_nscorvars: {}'.format(most_nscorvars))
                            # check frequnecy of variable names in non-significant coefficients
                            nscorvars = [k for k, v in most_nscorvars.items()
                                         if v >= int(len(corvars)*0.75)]
                            logger.info('nscorvars: {}'.format(nscorvars))
                            nonps_nscorvars = [var for var in nscorvars
                                               if var not in ps_corvars]
                            # if any variable has insignificant correlation
                            # with all other variables, their correlation is
                            # removed from the solution
                            if nonps_nscorvars:
                                # list of variables allowed to correlate
                                rem_corvars = [var for var in
                                               rem_rand_vars.keys() if var
                                               not in nonps_nscorvars and
                                               var not in rem_bcvars]
                            else:
                                rem_corvars = [var for var in
                                               rem_rand_vars.keys() if var
                                               not in rem_bcvars]

                            # need atleast two variables in the list to
                            # estimate correlation coefficients
                            if len(rem_corvars) < 2:
                                rem_corvars = []
                        else:
                            rem_corvars = [var for var in corvars if var in
                                           rem_rand_vars.keys() and var not in
                                           rem_bcvars]
                            if len(rem_corvars) < 2:
                                rem_corvars = []

                        # Evaluate objective function with significant feautures from round 1

                        rem_alvars = rem_asvars + rem_isvars
                        if rem_alvars:
                            if (set(rem_alvars) != set(all_vars) or
                                set(rem_rand_vars) != set(rand_vars) or
                                set(rem_bcvars) != set(bcvars) or
                                set(rem_corvars) != set(corvars) or
                                    new_asc_ind != asc_ind):
                                logger.info("not same as round 1 model")
                            else:
                                logger.info("model 2 same as round 1 model")
                                return(sol, convergence)

                            check_latent = self.check_latent_validity(rem_class_params_spec, rem_member_params_spec)

                            if bool(rem_rand_vars):
                                if self.latent_class and check_latent:
                                    bic, val, asvars, isvars, randvars, \
                                        bcvars, corvars, conv, sig, sig_member, coefs = \
                                            self.fit_lccmm(new_df,
                                                           self.df_test,
                                                           as_vars,
                                                           is_vars,
                                                           class_params_spec,  # todo... all params check really
                                                           member_params_spec,
                                                           2,
                                                           rand_vars,
                                                           bc_vars,
                                                           cor_vars,
                                                           choice,
                                                           alts,
                                                           id_choice,
                                                           id_val,
                                                           self.test_choice,
                                                           asc_ind)
                                else:
                                    logger.info("MXL model round 2")
                                    bic, val, asvars, isvars, randvars, bcvars, \
                                        corvars, conv, sig, coefs = \
                                            self.fit_mxl(new_df,
                                                         self.df_test,
                                                         rem_asvars,
                                                         rem_isvars,
                                                         rem_rand_vars,
                                                         rem_bcvars,
                                                         rem_corvars,
                                                         choice,
                                                         alts,
                                                         id_choice,
                                                         id_val,
                                                         self.test_choice,
                                                         new_asc_ind,
                                                         avail=self.avail)
                            else:
                                if self.latent_class and check_latent:
                                    bic, val, asvars, isvars, randvars, \
                                        bcvars, corvars, conv, sig, sig_member, coefs = \
                                            self.fit_lccm(new_df, self.df_test,
                                                          rem_asvars,
                                                          rem_isvars,
                                                          rem_class_params_spec,
                                                          rem_member_params_spec,
                                                          2,
                                                          rem_bcvars,
                                                          choice,
                                                          alts,
                                                          id_choice,
                                                          self.test_choice,
                                                          new_asc_ind)
                                else:
                                    logger.info("MNL model round 2")
                                    bic, val, asvars, isvars, randvars, bcvars, \
                                        corvars, conv, sig, coefs = \
                                            self.fit_mnl(new_df,
                                                         self.df_test,
                                                         rem_asvars,
                                                         rem_isvars,
                                                         rem_bcvars,
                                                         choice, alts,
                                                         id_choice,
                                                         self.test_choice,
                                                         new_asc_ind,
                                                         alts)

                            if conv:
                                sol = [bic, val, asvars, isvars, randvars,
                                       bcvars, corvars, new_asc_ind,
                                       class_params_spec, member_params_spec]
                                convergence = conv
                                if all([v for v in sig if v <= self.p_val]):
                                    break
                                    # return(sol,convergence)
                                # if only some correlation coefficients or
                                # intercept values are insignificant, we accept
                                # the solution
                                p_vals = dict(zip(coefs, sig))
                                non_sig = [k for k, v in p_vals.items()
                                           if v > self.p_val]
                                logger.info("non_sig in round 2: {}".format(non_sig))

                                sol[2] = [var for var in sol[2] if var not in
                                          non_sig or var in ps_asvars]  # keep only significant vars

                                # Update other features of solution based on sol[1]
                                sol[4] = {k: v for k, v in sol[4].items() if k in sol[2]}
                                sol[5] = [var for var in sol[5] if var in sol[2] and var not in ps_corvars]
                                if sol[6]:
                                    sol[6] = [var for var in sol[6] if var in sol[4].keys and var not in sol[5]]

                                # fit_intercept = False if all intercepts are insignificant
                                if len([var for var in non_sig if var in
                                       ['_intercept.' + var for var
                                        in choice_set]]) == len(non_sig):
                                    if len(non_sig) == len(choice_set)-1:
                                        sol[-1] = False
                                        return(sol, convergence)

                                all_ns_int = [x for x in non_sig if x.startswith('_intercept.')]
                                all_ns_cors = [x for x in non_sig if x.startswith('chol.')]

                                all_ns_isvars = []
                                for isvar in isvarnames:
                                    ns_isvar = [x for x in non_sig if x.startswith(isvar)]
                                    all_ns_isvars.extend(ns_isvar)

                                irrem_nsvars = all_ns_isvars + all_ns_int + all_ns_cors
                                if all(nsv in irrem_nsvars for nsv in non_sig):
                                    logger.info("non-significant terms cannot be further eliminated")
                                    return(sol, convergence)

                                if (non_sig == all_ns_cors or
                                    non_sig == all_ns_int or
                                    non_sig == list(set().union(all_ns_cors,
                                                                all_ns_int))):
                                    logger.info("only correlation coefficients or intercepts are insignificant")
                                    return(sol, convergence)

                                if all([var in ps_asvars or var in ps_isvars or
                                        var in ps_rvars.keys() for var in non_sig]):
                                    logger.info("non-significant terms are pre-specified")
                                    return(sol, convergence)

                                if (len([var for var in non_sig if var in
                                        ['sd.' + var for var
                                         in ps_rvars.keys()]]) == len(non_sig)):
                                    logger.info("non-significant terms are pre-specified random coefficients")
                                    return(sol, convergence)

                            else:
                                # convergence = False
                                logger.info("convergence not reached in round 2 so final sol is from round 1")
                                return(sol, convergence)
                        else:
                            logger.info("no vars for round 2")
                            return(sol, convergence)
            else:
                convergence = False
                logger.info("convergence not reached in round 1")
                return(sol, convergence)
        else:
            logger.info("no vars when function called first time")
        return(sol, convergence)

    # Initialize harmony memory and opposite harmony memory of size HMS with random slutions
    def initialize_memory(self, choice_data, HMS, asvars_avail, isvars_avail,
                          rvars_avail, bcvars_avail, corvars_avail, asvars_ps,
                          isvars_ps, rvars_ps, bcvars_ps, corvars_ps,
                          bctrans_ps, cor_ps, intercept_ps, trans_asvars,
                          asvarnames, choice_set, alt_var, choice_var,
                          choice_id, ind_id, ps_asvars, isvarnames, ps_isvars,
                          ps_intercept, ps_rvars, ps_corvars):
        """
        Creates two lists (called the harmony memory and opposite harmony memory)
        harmony memory - containing the initial randomly generated solutions
        opposite harmony memory - containing random solutions that include variables not included in harmony memory
        Inputs: harmony memory size (int), all variable names, individual-specific variable, prespecifications provided by user
        """
        init_HM = self.code_name + 'initialize_memory_' + \
                  self.current_date + '.txt'
        # if self.verbose < 2:
        #     sys.stdout = open(init_HM, 'wt')  # TODO: TURN OFF?

        # Set Random Seed  # TODO: INVESTIGATE
        global_seed = 1609
        np.random.seed(global_seed)
        seeds = np.random.choice(50000, 23000, replace=False)

        # set random seeds

        HM = []
        opp_HM = []
        base_model = [1000000, 1.0, [], [], {}, [], [], False, [], []]  # TODO

        HM.append(base_model)
        # logger.info("HM with base model is", HM)

        # Add an MXL with full covriance structure

        # Create initial harmony memory
        unique_HM = []
        for i in range(len(seeds)):
            seed = seeds[i]
            asvars, isvars, randvars, bcvars, corvars, bctrans, cor, class_params_spec, member_params_spec, \
            asconstant = \
                self.generate_sol(choice_data, self.df_test, seed, asvars_avail,
                                  isvars_avail, rvars_avail, trans_asvars,
                                  bcvars_avail, corvars_avail, asvars_ps,
                                  isvars_ps, rvars_ps, bcvars_ps,
                                  corvars_ps, bctrans_ps, cor_ps, intercept_ps,
                                  asvarnames, choice_set, alt_var)
            sol, conv = \
                self.evaluate_objective_function(choice_data, self.df_test, seed, asvars,
                                                 isvars, randvars, bcvars,
                                                 corvars,
                                                 class_params_spec, member_params_spec,
                                                 choice_var,
                                                 self.test_choice, alt_var,
                                                 choice_id, ind_id, asconstant,
                                                 ps_asvars, asvarnames,
                                                 isvarnames, ps_isvars,
                                                 ps_intercept, choice_set,
                                                 ps_rvars, ps_corvars)
            # if conv:
            #     # add to memory
            #     # Similarity check to keep only unique solutions in harmony memory
            #     # TODO? CHECK STILL WANTED
            #     if len(HM) > 0:  # only do check if there are already solutions
            #         bic_list = [hm_sol[0] for hm_sol in HM]
            #         discrepancy = 0.1 * min(bic_list)  # TODO!: arbitrary!

            #         unique_HM_discrepancy = []
            #         for sol_hm in HM:
            #             # TODO: below line makes no sense
            #             if np.abs(sol_hm[0] - sol_hm[0]) <= discrepancy:
            #                 unique_HM_discrepancy.append(sol_hm)

                    # if len(unique_HM_discrepancy) > 0:
                    #     # check if varnames, randvars, bcvars, corrvars and
                    #     # fit are the same as similar BIC solns
                    #     # if 2 or more are same then do not accept solution
                    #     # TODO! CHECK / IMPROVE INDICES...
                    #     hm_varnames = [sol_hm[2] for sol_hm in unique_HM_discrepancy]
                    #     hm_randnames = [sol_hm[4] for sol_hm in unique_HM_discrepancy]
                    #     hm_trans = [sol_hm[5] for sol_hm in unique_HM_discrepancy]
                    #     hm_correlation = [sol_hm[6] for sol_hm in unique_HM_discrepancy]
                    #     hm_intercept = [sol_hm[7] for sol_hm in unique_HM_discrepancy]

                    #     similarities = 0
                    #     if sol[2] in hm_varnames:
                    #         similarities += 1

                    #     if len(sol[4]) > 0 and sol[4] in hm_randnames:
                    #         similarities += 1

                    #     if len(sol[5]) > 0 and sol[5] in hm_trans:
                    #         similarities += 1

                    #     # if len(sol[6]) > 0 and sol[6] in hm_correlation:
                    #         # similarities += 1

                    #     if sol[7] in hm_intercept:
                    #         similarities += 1

                    #     if similarities > 3:  # accepts solution if 2 or more aspects of solution are different
                    #         conv = False  # make false so solution isn't added
            if conv:
                HM.append(sol)
                # keep only unique solutions in memory
                used = set()
                unique_HM = [used.add(tuple(x[:1])) or x for x in HM
                             if tuple(x[:1]) not in used]
                unique_HM = sorted(unique_HM, key=lambda x: x[0])
                logger.debug("harmony memory for iteration: {}, is: {}".format(i, str(unique_HM)))

            logger.debug("estimating opposite harmony memory")

            # create opposite harmony memory with variables that were not included in the harmony memory's solution

            # list of variables that were not present in previously generated solution for HM
            ad_var = [x for x in self.varnames if x not in sol[2]]
            seed = seeds[i+HMS]
            op_asvars, op_isvars, op_rvars, op_bcvars, op_corvars, \
                op_bctrans, op_cor, op_class_params_spec, op_member_params_spec, op_asconstant = \
                    self.generate_sol(choice_data, self.df_test, seed,
                                      asvars_avail, isvars_avail,
                                      rvars_avail, trans_asvars, bcvars_avail,
                                      corvars_avail, asvars_ps, isvars_ps,
                                      rvars_ps,
                                      bcvars_ps, corvars_ps, bctrans_ps,
                                      cor_ps,
                                      intercept_ps, asvarnames, choice_set,
                                      alt_var)

            # evaluate objective function of opposite solution
            logger.info(("opp sol features - as_vars: {}, is_vars: {}, "
                         "rand_vars: {}, bc_vars: {}, cor_vars: {}, "
                         "class_params_spec: {}, member_params_spec: {}, "
                         "asc_ind: {}").format(op_asvars, op_isvars, op_rvars,
                                               op_bcvars, op_corvars,
                                               op_bctrans, op_cor,
                                               op_class_params_spec,
                                               op_member_params_spec,
                                               op_asconstant))

            # TODO: temporary fixes for class_params
            # Remove intercept from classes if asc is false
            # if not op_asconstant:
                # for ii, class_i in enumerate(op_class_params_spec):
                    # for lass_var in class_i:
                        # REMOVE INTERCEPT FROM CLASS
            # same for member params...
            opp_sol, opp_conv = \
                self.evaluate_objective_function(choice_data, self.df_test,
                                                 seed, op_asvars,
                                                 op_isvars, op_rvars,
                                                 op_bcvars, op_corvars,
                                                 op_class_params_spec, op_member_params_spec,  # TODO! just re=using here
                                                 choice_var,
                                                 self.test_choice,
                                                 alt_var,
                                                 choice_id, ind_id,
                                                 op_asconstant, ps_asvars,
                                                 asvarnames, isvarnames,
                                                 ps_isvars, ps_intercept,
                                                 choice_set, ps_rvars,
                                                 ps_corvars)
            # if opp_conv:
                # Similarity check to keep only unique solutions in opposite harmony memory
                # if len(opp_HM) > 0:  # only do check if there are already solutions
                #     bic_list = [sol[0] for sol in self.unique_opp_HM]
                #     discrepancy = 0.1 * min(bic_list)    # TODO: arbitrary choice ... improve?

                #     unique_opp_HM_discrepancy = []
                #     for opp in opp_HM:
                #         if np.abs(opp[0] - opp_sol[0]) <= discrepancy:
                #             unique_opp_HM_discrepancy.append(opp)

                #     if len(unique_opp_HM_discrepancy) > 0:
                #         # check if varnames, randvars, bcvars, corrvars and fit
                #         # are the same as similar BIC solns
                #         # if 2 or more are same then do not accept solution
                #         opp_HM_varnames = [sol[2] for sol in unique_opp_HM_discrepancy]
                #         opp_HM_randnames = [sol[4] for sol in unique_opp_HM_discrepancy]
                #         opp_HM_trans = [sol[5] for sol in unique_opp_HM_discrepancy]
                #         opp_HM_correlation = [sol[6] for sol in unique_opp_HM_discrepancy]
                #         opp_HM_intercept = [sol[7] for sol in unique_opp_HM_discrepancy]
                #         opp_class_params = [sol[8] for sol in unique_opp_HM_discrepancy]
                #         opp_member_params = [sol[9] for sol in unique_opp_HM_discrepancy]
                #         # TODO? include class+member params

                #         similarities = 0
                #         if opp_sol[2] in opp_HM_varnames:
                #             similarities += 1

                #         if opp_sol[4] in opp_HM_randnames:
                #             similarities += 1

                #         if opp_sol[5] in opp_HM_trans:
                #             similarities += 1

                #         if opp_sol[6] in opp_HM_correlation:
                #             similarities += 1

                #         if opp_sol[7] in opp_HM_intercept:
                #             similarities += 1

                #         # if opp_sol[8] in opp_class_params:
                #             # similarities += 1

                #         # if opp_sol[9] in opp_member_params:
                #             # similarities += 1

                #         # accepts solution if --- or more aspects of solution are different
                #         if similarities > 4:  # TODO! CHANGED abitrary
                #             opp_conv = False  # make false so solution isn't added

            unique_opp_HM = []
            if opp_conv:
                opp_HM.append(opp_sol)
                opp_used = set()
                unique_opp_HM = [opp_used.add(tuple(x[:1])) or x for x in opp_HM
                                 if tuple(x[:1]) not in opp_used]
                unique_opp_HM = sorted(unique_opp_HM, key=lambda x: x[0])
                logger.debug("unique_opp_HM is for iteration: {} is: {}".format(i, str(unique_opp_HM)))
                self.unique_opp_HM = unique_opp_HM  # TODO? POOR
                if len(unique_opp_HM) == HMS:
                        break

            # Final Initial Harmony
            Init_HM = unique_HM + unique_opp_HM

            unique = set()
            unique_Init_HM = [unique.add(tuple(x[:1])) or x for x in Init_HM
                              if tuple(x[:1]) not in unique]
            if len(unique_Init_HM) >= HMS:
                unique_Init_HM = unique_Init_HM[:HMS]
                return(unique_Init_HM)
                # break
        return(unique_Init_HM)
        # sys.stdout.flush()

        # return(unique_HM,unique_opp_HM)
    # We need to make sure that the BICs of solutions in harmony memory are different from each other by atleast the throshold value

    def harmony_consideration(self, har_mem, HMCR_itr, seeds, itr, HMS, df,
                              avail_asvars, avail_isvars, avail_rvars,
                              trans_asvars, avail_bcvars, avail_corvars,
                            #   class_params_spec, member_params_spec,
                              ps_asvars, ps_isvars, ps_rvars, ps_bcvars,
                              ps_corvars, ps_bctrans, ps_cor, ps_intercept,
                              asvarnames, choice_set, alt_var, HM):
        """
        If a generated random number is less than or equal to the harmony memory consideration rate (HMCR)
        then 90% of a solution already in memory will be randomly selected to build the new solution.
        Else a completely new random solution is generated
        Inputs: harmony memory, HMCR for the current interation, random seeds, iteration number
        """
        seed = seeds[HMS*2+itr]
        new_sol = []
        # TODO? confirm fronts, pareto legit
        Fronts = None
        Pareto = None
        if self.multi_objective:
            har_mem = self.non_dominant_sorting(har_mem)
            Fronts = self.get_fronts(har_mem)
            Pareto = self.pareto(Fronts, har_mem)

        if np.random.choice([0, 1], p=[1-HMCR_itr, HMCR_itr]) <= HMCR_itr:
            logger.info("harmony consideration")
            m_pos = np.random.choice(len(har_mem)) #randomly choose the position of any one solution in harmony memory
            select_new_asvars_index = np.random.choice([0, 1],
                                                       size=len(har_mem[m_pos][2]),
                                                       p=[1-HMCR_itr, HMCR_itr])
            select_new_asvars = [i for (i, v) in zip(har_mem[m_pos][2],
                                                     select_new_asvars_index)
                                                     if v]
            select_new_asvars = list(np.random.choice(har_mem[m_pos][2],
                                                      int((len(har_mem[m_pos][2]))*HMCR_itr),
                                                      replace=False))  # randomly select 90% of the variables from solution at position m_pos in harmony memory
            n_asvars = sorted(list(set().union(select_new_asvars, ps_asvars)))
            new_asvars = self.remove_redundant_asvars(n_asvars, trans_asvars,
                                                      seed, asvarnames)
            new_sol.append(new_asvars)
            logger.info("new_asvars: {}".format(new_asvars))

            select_new_isvars_index = np.random.choice([0, 1],
                                                       size=len(har_mem[m_pos][3]),
                                                       p=[1-HMCR_itr, HMCR_itr])
            select_new_isvars = [i for (i, v) in zip(har_mem[m_pos][3], select_new_isvars_index) if v]
            # select_new_isvars = list(np.random.choice(har_mem[m_pos][2],int((len(har_mem[m_pos][2]))*HMCR_itr),replace = False, p=[1-HMCR_itr, HMCR_itr]))
            new_isvars = sorted(list(set().union(select_new_isvars, ps_isvars)))
            logger.info("new_isvars: {}".format(new_isvars))
            new_sol.append(new_isvars)

            # include distributions for the variables in new solution based on the solution at m_pos in memory
            # TODO: RYAN ADD - SAFEGUARD
            if self.multi_objective:  # TODO! CHECK BEHAVIOUR FOR SOOF
                if m_pos < len(Pareto):
                    r_pos = {k: v for k, v in har_mem[m_pos][4].items() if k
                            in new_asvars}
                    logger.info("r_pos: {}".format(r_pos))
                    new_sol.append(r_pos)
                else:
                    new_sol.append(dict())
            else:
                new_sol.append(dict())

            new_bcvars = [var for var in har_mem[m_pos][5] if var in new_asvars
                          and var not in ps_corvars]
            new_sol.append(new_bcvars)

            new_corvars = har_mem[m_pos][6]
            if new_corvars:
                new_corvars = [var for var in har_mem[m_pos][6] if var
                            in r_pos.keys() and var not in new_bcvars]
            new_sol.append(new_corvars)

            # Take fit_intercept from m_pos solution in memory
            intercept = har_mem[m_pos][7]
            new_sol.append(intercept)

            class_params_spec = har_mem[m_pos][8]
            new_sol.append(class_params_spec)
            member_params_spec = har_mem[m_pos][9]
            new_sol.append(member_params_spec)

            logger.info("new sol after HMC-1: {}".format(str(new_sol)))
        else:
            logger.info("harmony not considered")
            # if harmony memory consideration is not conducted, then a new solution is generated

            asvars, isvars, randvars, bcvars, corvars, bctrans, cor, class_params_spec, member_params_spec, asconstant = \
                self.generate_sol(df, self.df_test, seed, avail_asvars,
                                  avail_isvars, avail_rvars, trans_asvars,
                                  avail_bcvars, avail_corvars, ps_asvars,
                                  ps_isvars, ps_rvars, ps_bcvars,
                                  ps_corvars, ps_bctrans, ps_cor,
                                  ps_intercept, asvarnames, choice_set,
                                  alt_var)
            new_sol = [asvars, isvars, randvars, bcvars, corvars, asconstant,
                       class_params_spec, member_params_spec]  # TODO? RYAN ADD IN BIC, VAL ??
            logger.info("new sol after HMC-2: {}".format(new_sol))
        return(new_sol)

    def add_new_asfeature(self, solution, seed):
        """
        Randomly selects an as variable, which is not already in solution
        Inputs: solution list contianing all features generated from harmony consideration
        # TODO: Include alternative-specific coefficients
        """
        new_asvar = [var for var in self.asvarnames if var not in solution[0]]
        logger.info('new_asvar: {}'.format(new_asvar))
        if new_asvar:
            n_asvar = list(np.random.choice(new_asvar, 1))
            solution[0].extend(n_asvar)
            solution[0] = self.remove_redundant_asvars(solution[0],
                                                       self.trans_asvars,
                                                       seed,
                                                       self.asvarnames)
            solution[0] = sorted(list(set(solution[0])))
            logger.info("new sol: {}".format(str(solution[0])))

            dis = []
            r_vars = {}
            if self.allow_random:
                for i in solution[0]:
                    if i in solution[2].keys():
                        r_vars.update({k: v for k, v in solution[2].items()
                                    if k == i})
                        logger.debug("r_vars: {}".format(r_vars))
                    else:
                        if i in self.ps_rvars.keys():
                            r_vars.update({i: self.ps_rvars[i]})
                            logger.debug("r_vars: {}".format(r_vars))
                        else:
                            # TODO! RYAN - REMOVED
                            if len(self.dist) > 0:  # TODO: RYAN ADD
                                r_vars.update({i: np.random.choice(self.dist)})
                            logger.debug("r_vars: {}".format(r_vars))
                solution[2] = {k: v for k, v in r_vars.items() if k
                            in solution[0] and v != 'f'}

        if solution[4]:
            solution[4] = [var for var in solution[4] if var in solution[2].keys()
                        and var not in solution[3]]
            # TODO: is this the right solution indices? does it switch up throughout?
        if self.ps_intercept is None:
            solution[5] = bool(np.random.randint(2))
        logger.info('solution: {}'.format(solution))

        return(solution)

    def add_new_isfeature(self, solution):
        """
        Randomly selects an is variable, which is not already in solution
        Inputs: solution list contianing all features generated from harmony consideration
        """
        if solution[1]:
            new_isvar = [var for var in self.isvarnames if var
                         not in solution[1]]
            if new_isvar:
                n_isvar = list(np.random.choice(new_isvar, 1))
                solution[1] = sorted(list(set(solution[1]).union(n_isvar)))
        return(solution)

    def add_new_bcfeature(self, solution, PAR_itr):
        """
        Randomly selects a variable to be transformed, which is not already in solution
        Inputs: solution list contianing all features generated from harmony consideration
        """
        if self.ps_bctrans is None:
            bctrans = bool(np.random.randint(2, size=1))
        else:
            bctrans = self.ps_bctrans
        if bctrans:
            select_new_bcvars_index = np.random.choice([0, 1],
                                                       size=len(solution[0]),
                                                       p=[1-PAR_itr, PAR_itr])
            new_bcvar = [i for (i, v) in zip(solution[0],
                                             select_new_bcvars_index) if v]
            solution[3] = sorted(list(set(solution[3]).union(new_bcvar)))
            solution[3] = [var for var in solution[3] if var
                           not in self.ps_corvars]
        else:
            solution[3] = []
        solution[4] = [var for var in solution[4] if var not in solution[3]]
        return(solution)

    def add_new_corfeature(self, solution):
        """
        Randomly selects variables to be correlated, which is not already in solution
        Inputs: solution list contianing all features generated from harmony consideration
        """
        if self.ps_cor is None:
            cor = bool(np.random.randint(2, size=1))
        else:
            cor = self.ps_cor
        if cor:
            new_corvar = [var for var in solution[2].keys() if var
                          not in solution[3]]
            solution[4] = sorted(list(set(solution[4]).union(new_corvar)))
        else:
            solution[4] = []
        if len(solution[4]) < 2:
            solution[4] = []
        solution[3] = [var for var in solution[3] if var not in solution[4]]
        return(solution)

    def add_new_class_paramfeature(self, solution):
        """ # TODO
        """
        class_params_spec = solution[6]
        class_params_spec_new = copy.deepcopy(class_params_spec)
        all_vars = self.asvarnames #+ self.isvarnames # TODO? check up on -> inc. intercept?
        for ii, class_i in enumerate(class_params_spec):
            new_params = [var for var in all_vars if var not in class_i]
            if len(new_params) > 0:
                new_params = np.random.choice(new_params, 1)
                new_param = np.array([])
                new_class_spec = class_i
                # TODO? remove redundant asvars ?
                if len(new_params) > 0:
                    new_param = np.random.choice(new_params, 1)

                    new_class_spec = np.sort(np.union1d(class_i, new_param))
                # TODO! Consider randvars
                class_params_spec_new[ii] = new_class_spec
            else:
                class_params_spec_new[ii] = class_i

        solution[6] = class_params_spec_new
        return solution

    def add_new_member_paramfeature(self, solution):
        """  # TODO
        """
        member_params_spec = solution[7]
        member_params_spec_new = copy.deepcopy(member_params_spec)
        all_vars = self.isvarnames # + self.asvarnames  # TODO? check up on -> inc. intercept?
        for ii, class_i in enumerate(member_params_spec):
            if len(class_i) > 0:
                new_params = np.array([var for var in all_vars if var not in class_i])
                new_param = np.array([])
                new_member_spec = class_i
                # TODO? remove redundant asvars ?
                if len(new_params) > 0:
                    new_param = np.random.choice(new_params, 1)
                    # TODO? remove redundant asvars ?
                    new_member_spec = np.sort(np.union1d(class_i, new_param))
                # TODO! consider randvars
                member_params_spec_new[ii] = new_member_spec
            else:
                member_params_spec_new[ii] = class_i

        solution[7] = member_params_spec_new

        return solution

    def remove_asfeature(self, solution):
        """
        Randomly excludes an as variable from solution generated from harmony consideration
        Inputs: solution list contianing all features
        """
        if solution[0]:
            rem_asvar = list(np.random.choice(solution[0], 1))
            solution[0] = [var for var in solution[0] if var not in rem_asvar]
            solution[0] = sorted(list(set(solution[0]).union(self.ps_asvars)))
            solution[2] = {k: v for k, v in solution[2].items() if k
                           in solution[0]}
            solution[3] = [var for var in solution[3] if var in solution[0]
                           and var not in self.ps_corvars]
            solution[4] = [var for var in solution[4] if var in solution[0]
                           and var not in self.ps_bcvars]
        return(solution)

    def remove_isfeature(self, solution):
        """
        Randomly excludes an is variable from solution generated from harmony consideration
        Inputs: solution list contianing all features
        """
        if solution[1]:
            rem_isvar = list(np.random.choice(solution[1], 1))
            solution[1] = [var for var in solution[1] if var not in rem_isvar]
            solution[1] = sorted(list(set(solution[1]).union(self.ps_isvars)))
        return(solution)

    def remove_bcfeature(self, solution):
        """
        Randomly excludes a variable transformation from solution generated from harmony consideration
        Inputs: solution list contianing all features
        """
        if solution[3]:
            rem_bcvar = list(np.random.choice(solution[3], 1))
            rem_nps_bcvar = [var for var in rem_bcvar if var
                             not in self.ps_bcvars]
            solution[3] = [var for var in solution[3] if var in solution[0]
                           and var not in rem_nps_bcvar]
            solution[4] = [var for var in solution[4] if var not in solution[3]]
            solution[3] = [var for var in solution[3] if var not in solution[4]]
        return(solution)

    def remove_corfeature(self, solution):
        """
        Randomly excludes correlaion feature from solution generated from harmony consideration
        Inputs: solution list contianing all features
        """
        if solution[4]:
            rem_corvar = list(np.random.choice(solution[4], 1))
            rem_nps_corvar = [var for var in rem_corvar if var
                              not in self.ps_corvars]
            solution[4] = [var for var in solution[4] if var
                           in solution[2].keys() and var not in rem_nps_corvar]
            if len(solution[4]) < 2:
                solution[4] = []
        return(solution)

    def remove_class_paramfeature(self, solution):
        """ # TODO
        """
        class_params_spec = copy.deepcopy(solution[6])
        if solution[6] is not None:
            for ii, class_i in enumerate(class_params_spec):
                if len(class_i) > 0:
                    rem_asvar = list(np.random.choice(class_i, 1))
                    tmp_class_i = [var for var in class_i if not rem_asvar]
                    class_params_spec[ii] = np.array(tmp_class_i)
                else:
                    class_params_spec[ii] = class_i
        solution[6] = class_params_spec
        return solution

    def remove_member_paramfeature(self, solution):
        """ # TODO
        """ 
        member_params_spec = copy.deepcopy(solution[7])
        if solution[7] is not None:
            for ii, class_i in enumerate(member_params_spec):
                if len(class_i) > 0:
                    rem_asvar = list(np.random.choice(class_i, 1))
                    tmp_class_i = [var for var in class_i if not rem_asvar]
                    member_params_spec[ii] = np.array(tmp_class_i)
                else:
                    member_params_spec[ii] = class_i
        solution[7] = member_params_spec
        return solution

    def assess_sol(self, solution, har_mem, seed):
        """
        (1) Evaluates the objective function of a given solution
        (2) Evaluates if the solution provides an improvement in BIC by atleast a threshold value compared to any other solution in memory
        (3) Checks if the solution is unique to other solutions in memory
        (4) Replaces the worst solution in memory, if (2) and (3) are true
        Inputs: solution list contianing all features, harmony memory
        """
        data = self.df.copy()

        # Stop bug where _inter in class params but intercept is false
        check_latent = self.check_latent_validity(solution[6], solution[7])
        asc_ind = solution[5]
        # TODO! Check ... removing _inter from class params if no intercept
        if not asc_ind and self.latent_class and check_latent:
            rem_class_params_spec = solution[6]
            rem_member_params_spec = solution[7]
            for ii, class_params in enumerate(rem_class_params_spec):
                for jj, var in enumerate(class_params):
                    if '_inter' in var:
                        if len(class_params) > 1:
                            rem_class_params_spec[ii] = np.delete(class_params, jj)
                        else:
                            rem_class_params_spec[ii] = np.array([])
            for ii, member_params in enumerate(rem_member_params_spec):
                for jj, var in enumerate(member_params):
                    if '_inter' in var:
                        if len(member_params) > 1:
                            rem_member_params_spec[ii] = np.delete(member_params, jj)
                        else:
                            rem_member_params_spec[ii] = np.array([])

            solution[6] = rem_class_params_spec
            solution[7] = rem_member_params_spec

        improved_sol, conv = \
            self.evaluate_objective_function(data, self.df_test, seed,
                                             solution[0], solution[1],
                                             solution[2], solution[3],
                                             solution[4],
                                             solution[6], solution[7],
                                             self.choice_var,
                                             self.test_choice, self.alt_var,
                                             self.choice_id, self.ind_id,
                                             solution[5], self.ps_asvars,
                                             self.asvarnames, self.isvarnames,
                                             self.ps_isvars, self.ps_intercept,
                                             self.choice_set, self.ps_rvars,
                                             self.ps_corvars)
        if conv:
            har_mem.append(improved_sol)
            # TODO? what happened to below
            # if all(har_mem[sol][0] != improved_sol[0] for sol in range(len(har_mem))):
            #     if all(har_mem[sol][0] - improved_sol[0] >= threshold for sol in range(1,len(har_mem))):
            #         if all(abs(har_mem[sol][0]-improved_sol[0]) >= threshold for sol in range(len(har_mem))):
            #             har_mem[-1] = improved_sol
        seen = set()
        seen_add = seen.add
        new_hm = [x for x in har_mem if tuple(x[:2]) not in seen and
                  not seen_add(tuple(x[:2]))]

        new_har_mem = new_hm
        if self.multi_objective:
            fronts = self.get_fronts(new_hm)
            Pareto = self.pareto(fronts, new_hm)
            new_har_mem = self.non_dominant_sorting(new_hm)
        
        logger.info("new_har_mem: {}".format(str(new_har_mem)))
        return(new_har_mem, improved_sol)

    def pitch_adjustment(self, sol, har_mem, PAR_itr, seeds, itr, HMS):
        seed = seeds[HMS*3+itr]
        """
        (1) A random binary indicator is generated. If the number is 1,
            then a new feature is added to the solution
            generated in the Harmony Memory consideration step.
            Else a feature is randomly excluded from the solution
        (2) The objective function of a given solution is evaluated.
        (3) The worst solution in harmony memory is repalced with the solution,
            if it is unique and provides an improved BIC

        Inputs:
        solution list generated from harmony consideration step
        harmony memory
        Pitch adjustment rate for the given iteration
        """
        improved_harmony = har_mem
        if np.random.choice([0, 1], p=[1-PAR_itr, PAR_itr]) <= PAR_itr:
            if np.random.randint(2):
                logger.info("pitch adjustment adding as variables")
                pa_sol = self.add_new_asfeature(sol, seed)
                improved_harmony, current_sol = self.assess_sol(pa_sol,
                                                                har_mem,
                                                                seed)

                if self.isvarnames:
                    logger.info("pitch adjustment adding is variables")
                    pa_sol = self.add_new_isfeature(pa_sol)
                    improved_harmony, current_sol = self.assess_sol(pa_sol,
                                                                    har_mem,
                                                                    seed)

                if self.ps_bctrans is None or self.ps_bctrans:
                    logger.info("pitch adjustment adding bc variables")
                    pa_sol = self.add_new_bcfeature(pa_sol, PAR_itr)
                    improved_harmony, current_sol = self.assess_sol(pa_sol,
                                                                    har_mem,
                                                                    seed)

                if self.ps_cor is None or self.ps_cor:
                    logger.info("pitch adjustment adding cor variables")
                    pa_sol = self.add_new_corfeature(pa_sol)
                    improved_harmony, current_sol = self.assess_sol(pa_sol,
                                                                    har_mem,
                                                                    seed)

                if pa_sol[6] is not None:  # todo? confirm
                    logger.info("pitch adjustment adding class param variables")
                    pa_sol = self.add_new_class_paramfeature(pa_sol)
                    improved_harmony, current_sol = self.assess_sol(pa_sol,
                                                                    har_mem,
                                                                    seed)

                if pa_sol[7] is not None:  # todo? confirm
                    logger.info("pitch adjustment adding member param variables")
                    pa_sol = self.add_new_member_paramfeature(pa_sol)
                    improved_harmony, current_sol = self.assess_sol(pa_sol,
                                                                    har_mem,
                                                                    seed)

            elif len(sol[0]) > 1:
                logger.info("pitch adjustment by removing as variables")
                pa_sol = self.remove_asfeature(sol)
                improved_harmony, current_sol = self.assess_sol(pa_sol,
                                                                har_mem,
                                                                seed)

                if self.isvarnames or sol[1]:
                    logger.info("pitch adjustment by removing is variables")
                    pa_sol = self.remove_isfeature(pa_sol)
                    improved_harmony, current_sol = self.assess_sol(pa_sol,
                                                                    har_mem,
                                                                    seed)

                if self.ps_bctrans is None or self.ps_bctrans:
                    logger.info("pitch adjustment by removing bc variables")
                    pa_sol = self.remove_bcfeature(pa_sol)
                    improved_harmony, current_sol = self.assess_sol(pa_sol,
                                                                    har_mem,
                                                                    seed)

                if self.ps_cor is None or self.ps_cor:
                    logger.info("pitch adjustment by removing cor variables")
                    pa_sol = self.remove_corfeature(pa_sol)
                    improved_harmony, current_sol = self.assess_sol(pa_sol,
                                                                    har_mem,
                                                                    seed)

                if pa_sol[6] is not None:  # check if has class_params_spec
                    logger.info("pitch adjustment by removing class param variables")
                    pa_sol = self.remove_class_paramfeature(pa_sol)
                    improved_harmony, current_sol = self.assess_sol(pa_sol,
                                                                    har_mem,
                                                                    seed)

                if pa_sol[7] is not None:  # check if has member_params_spec
                    logger.info("pitch adjustment by removing member param variables")
                    pa_sol = self.remove_member_paramfeature(pa_sol)
                    improved_harmony, current_sol = self.assess_sol(pa_sol,
                                                                    har_mem,
                                                                    seed)

            else:
                logger.info("pitch adjustment by adding asfeature")
                pa_sol = self.add_new_asfeature(sol, seed)
                improved_harmony, current_sol = self.assess_sol(pa_sol,
                                                                har_mem,
                                                                seed)
        else:
            logger.info("no pitch adjustment")
            improved_harmony, current_sol = self.assess_sol(sol, har_mem, seed)
        return(improved_harmony, current_sol)

    def best_features(self, har_mem):
        """
        Generates lists of best features in harmony memory
        Inputs:
        Harmony memory
        """
        HM = self.find_bestsol(har_mem)
        best_asvars = HM[2].copy()
        best_isvars = HM[3].copy()
        best_randvars = HM[4].copy()
        best_bcvars = HM[5].copy()
        best_corvars = HM[6].copy()
        asc_ind = HM[7]
        best_class_params_spec = None
        best_member_params_spec = None
        if HM[8] is not None:
            best_class_params_spec = HM[8].copy()
        if HM[9] is not None:
            best_member_params_spec = HM[9].copy()

        return(best_asvars, best_isvars, best_randvars, best_bcvars,
               best_corvars, asc_ind, best_class_params_spec, best_member_params_spec)

    def local_search(self, improved_harmony, seeds, itr, PAR_itr):
        """
        Initiate Artificial Bee-colony optimization
        Check if finetuning the best solution in harmony improves solution's BIC
        Inputs: improved memory after harmony consideration and pitch adjustment
        """
        seed = seeds[self.HMS*4+itr]
        # For plots (BIC vs. iterations)
        best_bic_points = []
        current_bic_points = []
        x = []
        # pp = PdfPages('BIC_plots_localsearch.pdf')

        # Select best solution features
        best_asvars, best_isvars, best_randvars, best_bcvars, best_corvars, \
            asc_ind, best_class_params_spec, best_member_params_spec \
                = self.best_features(improved_harmony)

        logger.info(("first set of best features input for local search - "
                     "as_vars: {}, is_vars: {}, rand_vars: {}, bc_vars: {}, "
                     "cor_vars: {}, best_class_params_spec: {}, "
                     "best_member_params_spec: {}").format(best_asvars,
                                                          best_isvars,
                                                          best_randvars,
                                                          best_bcvars,
                                                          best_corvars,
                                                          best_class_params_spec,
                                                          best_member_params_spec))
        # for each additional feature to the best solution, the objective function is tested

        # Check if changing coefficient distributions of best solution improves the solution BIC
        for var in best_randvars.keys():
            if var not in self.ps_rvars:
                rm_dist = [dis for dis in self.dist if dis != best_randvars[var]]
                best_randvars[var] = np.random.choice(rm_dist)
        best_randvars = {key: val for key, val in best_randvars.items()
                         if key in best_asvars and val != 'f'}
        best_bcvars = [var for var in best_bcvars if var in best_asvars
                       and var not in self.ps_corvars]
        best_corvars = [var for var in best_randvars.keys() if var
                        not in best_bcvars]
        solution_1 = [best_asvars, best_isvars, best_randvars, best_bcvars,
                      best_corvars, asc_ind, best_class_params_spec, best_member_params_spec]
        logger.info('solution_1: {}'.format(solution_1))
        improved_harmony, current_sol = self.assess_sol(solution_1,
                                                        improved_harmony,
                                                        seed)
        logger.info('sol after local search step 1: {}'.format(str(improved_harmony[0])))

        # check if having a full covariance matrix has an improvement in BIC
        best_asvars, best_isvars, best_randvars, best_bcvars, best_corvars, \
            asc_ind, best_class_params_spec, best_member_params_spec = self.best_features(improved_harmony)
        best_bcvars = [var for var in best_asvars if var in self.ps_bcvars]
        if self.ps_cor is None or self.ps_cor:
            best_corvars = [var for var in best_randvars.keys() if var
                            not in best_bcvars]
        elif len(best_corvars) < 2:
            best_corvars = []
        else:
            best_corvars = []
        solution_2 = [best_asvars, best_isvars, best_randvars, best_bcvars,
                      best_corvars, asc_ind, best_class_params_spec, best_member_params_spec]
        improved_harmony, current_sol = self.assess_sol(solution_2,
                                                        improved_harmony,
                                                        seed)
        logger.info("sol after local search step 2: {}".format(str(improved_harmony[0])))

        # check if having a all the variables transformed has an improvement in BIC
        best_asvars, best_isvars, best_randvars, best_bcvars, best_corvars, \
            asc_ind, best_class_params_spec, best_member_params_spec = self.best_features(improved_harmony)
        if self.ps_bctrans is None or self.ps_bctrans:
            best_bcvars = [var for var in best_asvars if var
                           not in self.ps_corvars]
        else:
            best_bcvars = []
        best_corvars = [var for var in best_randvars.keys() if var
                        not in best_bcvars]
        solution_3 = [best_asvars, best_isvars, best_randvars, best_bcvars,
                      best_corvars, asc_ind, best_class_params_spec, best_member_params_spec]
        improved_harmony, current_sol = self.assess_sol(solution_3,
                                                        improved_harmony,
                                                        seed)
        logger.info("sol after local search step 3: {}".format(str(improved_harmony[0])))

        if len(best_asvars) < len(self.asvarnames):
            logger.info("local search by adding variables")
            solution = [best_asvars, best_isvars, best_randvars, best_bcvars,
                        best_corvars, asc_ind, best_class_params_spec, best_member_params_spec]
            solution_4 = self.add_new_asfeature(solution, seed)
            improved_harmony, current_sol = self.assess_sol(solution_4,
                                                            improved_harmony,
                                                            seed)
            logger.info("sol after local search step 4: {}".format(str(improved_harmony[0])))

        best_asvars, best_isvars, best_randvars, best_bcvars, best_corvars, \
            asc_ind, best_class_params_spec, best_member_params_spec = self.best_features(improved_harmony)
        solution = [best_asvars, best_isvars, best_randvars, best_bcvars,
                    best_corvars, asc_ind, best_class_params_spec, best_member_params_spec]
        solution_5 = self.add_new_isfeature(solution)
        improved_harmony, current_sol = self.assess_sol(solution_5,
                                                        improved_harmony,
                                                        seed)
        logger.info("sol after local search step 5: {}".format(str(improved_harmony[0])))

        best_asvars, best_isvars, best_randvars, best_bcvars, best_corvars, \
             asc_ind, best_class_params_spec, best_member_params_spec = self.best_features(improved_harmony)
        solution = [best_asvars, best_isvars, best_randvars, best_bcvars,
                    best_corvars, asc_ind, best_class_params_spec, best_member_params_spec]
        solution_6 = self.add_new_bcfeature(solution, PAR_itr)
        improved_harmony, current_sol = self.assess_sol(solution_6,
                                                        improved_harmony,
                                                        seed)
        logger.info("sol after local search step 6: {}".format(str(improved_harmony[0])))

        best_asvars, best_isvars, best_randvars, best_bcvars, best_corvars, \
            asc_ind, best_class_params_spec, best_member_params_spec = self.best_features(improved_harmony)
        solution = [best_asvars, best_isvars, best_randvars, best_bcvars,
                    best_corvars, asc_ind, best_class_params_spec, best_member_params_spec]
        solution_7 = self.add_new_corfeature(solution)
        improved_harmony, current_sol = self.assess_sol(solution_7,
                                                        improved_harmony,
                                                        seed)
        logger.info("sol after local search step 7: {}".format(str(improved_harmony[0])))

        # Sort unique harmony memory from min.BIC to max. BIC
        # improved_harmony = sorted(improved_harmony, key = lambda x: x[0])

        # Check if changing coefficient distributions of best solution improves the solution BIC
        best_asvars, best_isvars, best_randvars, best_bcvars, best_corvars, \
            asc_ind, best_class_params_spec, best_member_params_spec = self.best_features(improved_harmony)

        for var in best_randvars.keys():
            if var not in self.ps_rvars:
                rm_dist = [dis for dis in self.dist if dis != best_randvars[var]]
                best_randvars[var] = np.random.choice(rm_dist)
        best_randvars = {key: val for key, val in best_randvars.items()
                         if key in best_asvars and val != 'f'}
        best_bcvars = [var for var in best_bcvars if var in best_asvars and
                       var not in self.ps_corvars]
        if self.ps_cor is None or self.ps_cor:
            best_corvars = [var for var in best_randvars.keys() if var
                            not in best_bcvars]
        if self.ps_cor is False:
            best_corvars = []
        if len(best_corvars) < 2:
            best_corvars = []
        solution = [best_asvars, best_isvars, best_randvars, best_bcvars,
                    best_corvars, asc_ind, best_class_params_spec, best_member_params_spec]
        improved_harmony, current_sol = self.assess_sol(solution,
                                                        improved_harmony,
                                                        seed)
        logger.info("sol after local search step 8: {}".format(str(improved_harmony[0])))

        # check if having a full covariance matrix has an improvement in BIC
        best_asvars, best_isvars, best_randvars, best_bcvars, best_corvars, \
            asc_ind, best_class_params_spec, best_member_params_spec = self.best_features(improved_harmony)
        best_bcvars = [var for var in best_asvars if var in self.ps_bcvars]
        if self.ps_cor is None or self.ps_cor:
            best_corvars = [var for var in best_randvars.keys() if var not in best_bcvars]
        else:
            best_corvars = []
        if len(best_corvars) < 2:
            best_corvars = []
        solution = [best_asvars, best_isvars, best_randvars, best_bcvars,
                    best_corvars, asc_ind, best_class_params_spec, best_member_params_spec]
        improved_harmony, current_sol = self.assess_sol(solution, improved_harmony,
                                                        seed)
        logger.info("sol after local search step 9: {}".format(str(improved_harmony[0])))

        # check if having all the variables transformed has an improvement in BIC
        best_asvars, best_isvars, best_randvars, best_bcvars, best_corvars, \
            asc_ind, best_class_params_spec, best_member_params_spec = self.best_features(improved_harmony)
        if self.ps_bctrans is None or self.ps_bctrans:
            best_bcvars = [var for var in best_asvars if var not in self.ps_corvars]
        else:
            best_bcvars = []
        if self.ps_cor is None or self.ps_cor:
            best_corvars = [var for var in best_randvars.keys()
                            if var not in best_bcvars]
        else:
            best_corvars = []

        if len(best_corvars) < 2:
            best_corvars = []
        solution = [best_asvars, best_isvars, best_randvars, best_bcvars,
                    best_corvars, asc_ind, best_class_params_spec, best_member_params_spec]
        improved_harmony, current_sol = self.assess_sol(solution,
                                                        improved_harmony,
                                                        seed)
        logger.info("sol after local search step 10: {}".format(str(improved_harmony[0])))

        # Sort unique harmony memory from min.BIC to max. BIC
        # final_harmony_sorted = sorted(improved_harmony, key = lambda x: x[0])
        final_harmony_sorted = improved_harmony
        return(final_harmony_sorted, current_sol)

    # Function to conduct harmony memory consideraion, pitch adjustment and local search
    def improvise_harmony(self, HCR_max, HCR_min, PR_max, PR_min, har_mem,
                          max_itr, threshold, itr_prop,
                          ps_corvars, ps_bctrans, ps_cor, ps_intercept,
                          asvarnames, choice_set, alt_var, HM):
        # Set Random Seed  # TODO: INVESTIGATE
        global_seed = 1609  # TODO? yuck
        np.random.seed(global_seed)
        seeds = np.random.choice(50000, 23000, replace=False)

        # improve_harmony = self.code_name + 'improvise_harmony_' + self.current_date + '.txt'
        # sys.stdout = open(improve_harmony, 'wt')
        itr = 0

        # for BIC vs. iteration plots
        best_bic_points = []
        current_bic_points = []
        best_val_points = []
        # pdf_name = 'BIC_plots_final_' + self.code_name + self.current_date + '.pdf'
        # pp = PdfPages(pdf_name)
        # np.random.seed(500)
        np.random.seed(seeds[itr])
        while itr < max_itr:
            itr += 1
            # Estimate dynamic HMCR and PCR values for each iteration
            HMCR_itr = (HCR_min + ((HCR_max-HCR_min)/max_itr)*itr) * max(0, math.sin(itr))
            PAR_itr = (PR_min + ((PR_max-PR_min)/max_itr)*itr) * max(0, math.sin(itr))
            # seed = seeds[itr]
            # Conduct Harmony Memory Consideration
            hmc_sol = \
                self.harmony_consideration(har_mem, HMCR_itr, seeds, itr, self.HMS,
                                           self.df, self.avail_asvars, self.avail_isvars,
                                           self.avail_rvars, self.trans_asvars,
                                           self.avail_bcvars, self.avail_corvars,
                                           self.ps_asvars, self.ps_isvars, self.ps_rvars,
                                           self.ps_bcvars,
                                           ps_corvars, ps_bctrans, ps_cor,
                                           ps_intercept, asvarnames,
                                           choice_set, alt_var, HM)
            logger.info("solution after HMC at iteration {}, is: {}".format(itr, str(hmc_sol)))
            # Conduct Pitch Adjustment
            pa_hm, current_sol = self.pitch_adjustment(hmc_sol, har_mem,
                                                       PAR_itr, seeds, itr,
                                                       self.HMS)
            logger.info("best solution after HMC & PA at iteration: {}, is - {}" .format(itr, str(pa_hm[0])))
            current_bic_points.append(current_sol[0])
            # Sort unique harmony memory from min.BIC to max. BIC
            # har_mem_sorted = sorted(pa_hm, key = lambda x: x[0])
            har_mem = pa_hm
            # Trim the Harmony memory's size as per the harmony memory size
            # har_mem = har_mem_sorted[:HMS]
            # Append y-axis points for the plots
            # best_bic_points = []
            # for ii, _ in enumerate(har_mem):
            #     bic_points = [har_mem_jj[0] for jj, har_mem_jj in enumerate(har_mem[0:ii])]
            #     best_bic_points.append(min(bic_points))
            # plt.scatter(best_val_points, best_bic_points)
            # plt.xlabel('Validation measure')
            # plt.ylabel('BIC')
            # plt.plot(best_val_points, best_bic_points, label="Pareto solutions")
            # plt.show()
            # sys.stdout.flush()

            # check iteration to initiate local search
            if itr > int(itr_prop * max_itr):
                logger.info("HM before starting local search: {}".format(str(har_mem)))
                logger.info("local search initiated at iteration: {}".format(itr))
                # seed = seeds[itr]
                har_mem, current_sol = self.local_search(har_mem, seeds, itr,
                                                         PAR_itr)
                # Sort unique harmony memory from min.BIC to max. BIC
                # har_mem = sorted(har_mem, key = lambda x: x[0])
                # Trim the Harmony memory's size as per the harmony memory size
                # har_mem = har_mem[:HMS]

                logger.info("final harmony in current iteration {}, is - {} ".format(itr, str(har_mem)))

                best_bic_points.append(har_mem[0][0])
                current_bic_points.append(current_sol[0])
                logger.debug(har_mem[0][0])

                # best_bic_points = [har_mem[x][0] for x in range(len(har_mem))]  # TODO? all not best?
                # best_val_points = [har_mem[x][1] for x in range(len(har_mem))]  # TODO? all not best?
                logger.debug(har_mem[0][0])

                # plt.scatter(best_val_points, best_bic_points)
                # plt.xlabel('Validation measure')
                # plt.ylabel('BIC')
                # pp.savefig(plt.gcf())
                # plt.show()
            #     sys.stdout.flush()
            # sys.stdout.flush()

            if itr == max_itr:  # Plot on final iteration
                valid_idx = [ii for ii, har_mem_ii in enumerate(har_mem) if np.abs(har_mem_ii[0]) != 1000000]
                all_bic_points = [har_mem[x][0] for x in range(len(har_mem))]
                all_val_points = [har_mem[x][1] for x in range(len(har_mem))]

                best_bic_points = []
                best_val_points = []
                min_bic = 1e+30
                max_val = -1e+30
                # min_bic = har_mem[0][0]
                # best_bic_points.append(min_bic)
                for ii, bic in enumerate(list(np.array(all_bic_points)[valid_idx])):
                    if bic < min_bic:
                        min_bic = bic
                    best_bic_points.append(min_bic)

                for ii, val in enumerate(list(np.array(all_val_points)[valid_idx])):
                    if val == 1:  # Some values default to 1 for MAE causing issues
                        val = -1e+30
                    if val > max_val:
                        max_val = val
                    best_val_points.append(max_val)
                
                all_bic = list(np.array(all_bic_points)[valid_idx])
                all_val = list(np.array(all_val_points)[valid_idx])

                logger.debug('best_bic_points: {}'.format(best_bic_points))
                logger.debug('best_val_points: {}'.format(best_val_points))

                if self.multi_objective:  # Plot for MOOF
                    Fronts = self.get_fronts(har_mem)
                    Pareto = self.pareto(Fronts, har_mem)
                    
                    # har_mem = [har_mem_ii for ii, har_mem_ii in enumerate(har_mem) if har_mem_ii[0] != 1000000]

                    fig, ax = plt.subplots()
                    # all_bic = [har_mem[i][0] for i in range(len(har_mem))]
                    # all_val = [har_mem[i][1] for i in range(len(har_mem))]
                    lns1 = ax.scatter(all_bic, np.log(all_val), label="All solutions", marker='o')
                    init_sols = [init_sol for _, init_sol in enumerate(HM) if init_sol[0] != 1000000]
                    init_bic = [init_sol[0] for _, init_sol in enumerate(init_sols)]
                    init_val = [init_sol[1] for _, init_sol in enumerate(init_sols)]
                    lns2 = ax.scatter(init_bic, np.log(init_val), label="Initial solutions",  marker='x')
                    # if hasattr(self, 'benchmark_bic'):
                    #     lns2_5 = ax.scatter(self.benchmark_bic, self.benchmark_val)
                    Pareto = [pareto for _, pareto in enumerate(Pareto) if pareto[0] != 1000000]
                    pareto_bic = [pareto[0] for _, pareto in enumerate(Pareto)]
                    pareto_val = np.log([pareto[1] for _, pareto in enumerate(Pareto)])
                    # lns3 = ax.scatter(pareto_bic, pareto_val, label="Pareto Front", marker='o')
                    lns4 = ax.plot(pareto_bic, pareto_val, color="r", label="Pareto Front")
                    lns = (lns1, lns2, lns4[0])
                    labs = [l_pot.get_label() for l_pot in lns]
                    ax.set_xlabel("BIC - training dataset")
                    ax.set_ylabel("Log MAE - testing dataset")
                    lgd = ax.legend(lns, labs, loc='upper center', bbox_to_anchor=(0.5, -0.1))  # TODO! FIX
                    current_time = datetime.datetime.now().strftime("%d%m%Y-%H%M%S")
                    plt.savefig(self.code_name + current_time +"_MOOF.png", bbox_extra_artists=(lgd,), bbox_inches='tight')

                else:  # Plot for SOOF
                    fig, ax1 = plt.subplots()
                    ax2 = ax1.twinx()

                    # TODO: REMOVE 100000?
                    current_bic_points = [har_mem_ii[0] for ii, har_mem_ii in enumerate(har_mem) if np.abs(har_mem_ii[0]) != -1000000.0]

                    lns1 = ax1.plot(np.arange(len(all_bic)), all_bic, label="BIC of solution estimated at current iteration")
                    lns2 = ax1.plot(np.arange(len(best_bic_points)), best_bic_points, label="BIC of best solution in memory at current iteration", linestyle="dotted")
                    lns3 = ax2.plot(np.arange(len(best_val_points)), best_val_points, label="In-sample LL of best solution in memory at current iteration", linestyle="dashed")
                    lns = lns1 + lns2 + lns3
                    labs = [l_pot.get_label() for l_pot in lns]
                    handles, _ = ax1.get_legend_handles_labels()
                    lgd = ax1.legend(lns, labs, loc='upper center', bbox_to_anchor=(0.5, -0.1))
                    ax1.set_xlabel("Iterations")
                    ax1.set_ylabel("BIC")
                    ax2.set_ylabel("LL")
                    current_time = datetime.datetime.now().strftime("%d%m%Y-%H%M%S")

                    plt.savefig(self.code_name + current_time + "_SOOF.png", bbox_extra_artists=(lgd,), bbox_inches='tight')

                pass

            if itr == max_itr+1:
                break
                """
                #plt.figure()
                #plt.xlabel('Iterations')
                #plt.ylabel('BIC')
                #plt.plot(x, current_bic_points, label = "BIC from current iteration")
                plt.plot(x, best_bic_points, label = "BIC of best solution in memory")
                #pp.savefig(plt.gcf()) 
                plt.show()
                """

        # pp.close()  # TODO: IF OPENED?
        # plt.plot(x, best_bic_points, label = "BIC of best solution in memory")
        # plt.savefig("best_bic_points.png")

        return(har_mem, best_bic_points, current_bic_points)

    def _prep_inputs(self, asvarnames=[], isvarnames=[]):
        """Include modellers' model prerequisites if any."""
        # pre-included alternative-sepcific variables
        # binary indicators representing alternative-specific variables
        # that are prespecified by the user
        psasvar_ind = [0] * len(asvarnames)

        # binary indicators representing individual-specific variables prespecified by the user
        psisvar_ind = [0] * len(isvarnames)

        # pre-included distributions
        # pspecdist_ind = ["f"]* 9 + ["any"] * (len(asvarnames)-9)
        # variables whose coefficient distribution have been prespecified by the modeller
        pspecdist_ind = ["any"] * len(asvarnames)

        # prespecification on estimation of intercept
        ps_intercept = None  # (True or False or None)

        # prespecification on transformations
        ps_bctrans = False  # (True or False or None)
        # indicators representing variables with prespecified transformation by the modeller
        ps_bcvar_ind = [0] * len(asvarnames)

        # prespecification on estimation of correlation
        ps_cor = False  # (True or False or None)
        # [1,1,1,1,1] indicators representing variables with prespecified correlation by the modeller
        ps_corvar_ind = [0] * len(asvarnames)

        # prespecified interactions
        ps_interaction = None  # (True or False or None)  # TODO? REMOVE?
        return (psasvar_ind, psisvar_ind, pspecdist_ind, ps_bcvar_ind,
                ps_corvar_ind)

    def run_search(self, HMS=10, HMCR_min=0.6, HMCR_max=0.9, PAR_max=0.85,
                   PAR_min=0.3, itr_max=30, v=0.8, threshold=15, val_share=0.25):
        n_gpus = dev.get_device_count()
        logger.info("{} GPU device(s) available. searchlogit will use GPU processing".format(n_gpus))

        psasvar_ind, psisvar_ind, pspecdist_ind, ps_bcvar_ind, ps_corvar_ind = \
            self._prep_inputs(asvarnames=self.asvarnames, isvarnames=self.isvarnames)
        ps_bctrans = None  # (True or False or None)  # TODO
        ps_cor = False  # (True or False or None) # TODO
        ps_interaction = None  # (True or False or None) # TODO
        ps_intercept = None  # (True or False or None)

        ps_asvars, ps_isvars, ps_rvars, ps_bcvars, ps_corvars = \
            self.prespec_features(psasvar_ind, psisvar_ind, pspecdist_ind,
                                  ps_bcvar_ind, ps_corvar_ind, self.isvarnames,
                                  self.asvarnames)
        self.ps_asvars = ps_asvars
        self.ps_isvars = ps_isvars
        self.ps_intercept = ps_intercept
        self.ps_rvars = ps_rvars
        self.ps_corvars = ps_corvars
        self.ps_bctrans = ps_bctrans
        self.ps_cor = ps_cor
        self.ps_bcvars = ps_bcvars
        self.ps_interaction = ps_interaction
        avail_asvars, avail_isvars, avail_rvars, avail_bcvars, avail_corvars = \
            self.avail_features(ps_asvars, ps_isvars, ps_rvars, ps_bcvars,
                                ps_corvars, self.isvarnames, self.asvarnames)
        # TODO: SAVING AVAILS HERE TO STOP BUG
        self.avail_asvars = avail_asvars
        self.avail_isvars = avail_isvars

        # TODO!
        if not self.allow_random:
            avail_rvars = []
        self.avail_rvars = avail_rvars
        if not self.allow_bcvars:
            avail_bcvars = []
        self.avail_bcvars = avail_bcvars  # TODO? testing...
        self.avail_corvars = avail_corvars
        # TODO? 5 is a random seed?
        asvars_new = self.df_coeff_col(5,
                                       self.df,
                                       self.df_test,
                                       avail_asvars,
                                       self.choice_set,
                                       self.alt_var)
        self.remove_redundant_asvars(asvars_new, self.trans_asvars, 3,
                                     self.asvarnames)
        self.generate_sol(self.df, self.df_test, 2, avail_asvars, avail_isvars,
                          avail_rvars, self.trans_asvars, avail_bcvars,
                          avail_corvars, ps_asvars, ps_isvars, ps_rvars,
                          ps_bcvars, ps_corvars, ps_bctrans, ps_cor,
                          ps_intercept, self.asvarnames, self.choice_set,
                          self.alt_var)
        Init_HM = self.initialize_memory(self.df, HMS, avail_asvars,
                                         avail_isvars, avail_rvars,
                                         avail_bcvars, avail_corvars,
                                         ps_asvars, ps_isvars, ps_rvars,
                                         ps_bcvars, ps_corvars, ps_bctrans,
                                         ps_cor, ps_intercept,
                                         self.trans_asvars, self.asvarnames,
                                         self.choice_set, self.alt_var,
                                         self.choice_var, self.choice_id,
                                         self.ind_id, ps_asvars,
                                         self.isvarnames, ps_isvars,
                                         ps_intercept, ps_rvars, ps_corvars)
        # Combine both harmonies
        # Init_HM = HM + O_HM

        # Remove duplicate solutions if present
        unique = set()
        unique_HM = [unique.add(tuple(x[:1])) or x for x in Init_HM if tuple(x[:1]) not in unique]

        # Sort unique harmony memory from min.BIC to max. BIC
        HM_sorted = sorted(unique_HM, key=lambda x: x[0])

        # Trim the Harmony memory's size as per the harmony memory size
        HM = HM_sorted[:HMS]
        hm = HM.copy()

        # TODO! IMPORTANT TUNING PARAMS HERE - ABLE TO SET
        self.HMS = HMS
        # HMCR_min = 0.6  # 0.9 #minimum harmony memory consideration rate
        # HMCR_max = 0.9  # 0.99 #maximum harmony memory consideration rate
        # PAR_max = 0.85
        # PAR_min = 0.3  # 0.8 #min pitch adjustment
        # itr_max = 30  # TODO?
        # # proportion of iterations to improvise harmony. The rest will be for local search
        # v = 0.80
        # threshold = 15  # threshold to compare new solution with worst solution in memory
        self.val_share = val_share  # TODO? MAKE ALL TUNING PARAMS SELF ATTRIBUTES?

        Initial_harmony = hm.copy()
        new_HM, best_BICs, current_BICs = \
            self.improvise_harmony(HMCR_max, HMCR_min, PAR_max, PAR_min,
            Initial_harmony, itr_max,
            threshold, v,
            # HMS, self.df, avail_asvars,
            # avail_isvars, avail_rvars, self.trans_asvars, avail_bcvars,
            # avail_corvars, ps_asvars, ps_isvars, ps_rvars, ps_bcvars,
            ps_corvars, ps_bctrans, ps_cor, ps_intercept, self.asvarnames,
            self.choice_set, self.alt_var, HM)
        improved_harmony = new_HM.copy()

        # benchmark_bic = improved_harmony[0][0]  # TODO? not used
        # best_asvarnames = improved_harmony[0][1]
        # best_isvarnames = improved_harmony[0][2]
        # best_randvars = improved_harmony[0][3]
        # best_bcvars = improved_harmony[0][4]
        # best_corvars = improved_harmony[0][5]
        # best_Intercept = improved_harmony[0][6]
        # benchmark_bic,best_asvarnames,best_isvarnames,best_randvars,best_bcvars,best_corvars,best_Intercept
        # TODO! SOOF VS MOOF ??

        if self.multi_objective:
            # TODO!
            hm = self.non_dominant_sorting(improved_harmony)
            best_sol = hm[0]
        else:  # single objective - bic, the 0-th index
            # TODO? Check some strange results
            improved_harmony.sort(key=lambda x: x[0])
            best_sol = improved_harmony[0]
        logger.info("Search ended at: {}".format(str(time.ctime())))
        # benchmark_bic = best_sol[0]  # TODO? not used
        # benchmark_val = best_sol[1]
        best_asvarnames = best_sol[2]
        best_isvarnames = best_sol[3]
        best_randvars = best_sol[4]
        best_bcvars = best_sol[5]
        best_corvars = best_sol[6]
        best_Intercept = best_sol[7]
        best_class_params_spec = best_sol[8]
        best_member_params_spec = best_sol[9]
        # self.benchmark_bic = benchmark_bic
        # self.benchmark_val = benchmark_val
        check_latent = self.check_latent_validity(best_class_params_spec, best_member_params_spec)
        if self.latent_class and check_latent:
            class_vars = list(np.concatenate(best_class_params_spec))
            member_vars = list(np.concatenate(best_member_params_spec))
            all_vars = class_vars + member_vars + best_isvarnames
            best_varnames = np.unique(all_vars)
        else:
            best_varnames = best_asvarnames + best_isvarnames

        # delete '_inter' bug fix
        if '_inter' in best_varnames:
            best_varnames = np.delete(best_varnames, np.argwhere(best_varnames == '_inter'))

        df = self.df
        X = df[best_varnames]
        if bool(best_randvars):
            if self.latent_class and check_latent:
                model = LatentClassMixedModel()
                model.fit(X, self.choice_var, varnames=best_varnames, isvars=best_isvarnames,
                          class_params_spec=best_class_params_spec,
                          member_params_spec=best_member_params_spec,
                          num_classes=self.num_classes, alts=self.alt_var,
                          ids=id_choice, panels=self.ind_id,
                          fit_intercept=best_Intercept,
                          transformation="boxcox", transvars=best_bcvars,
                          randvars=best_randvars,
                          correlation=best_corvars,
                          maxiter=self.maxiter, gtol=self.gtol,
                          avail=self.avail,
                          weights=self.weights)
            else:
                model = MixedLogit()
                model.fit(X=df[best_varnames], y=self.choice_var, varnames=best_varnames,
                        isvars=best_isvarnames, alts=self.alt_var, ids=self.choice_id,
                        panels=self.ind_id, randvars=best_randvars,
                        transformation="boxcox", transvars=best_bcvars,
                        correlation=best_corvars, fit_intercept=best_Intercept,
                        n_draws=200)
        else:
            if self.latent_class and check_latent:
                model = LatentClassModel()
                # TODO! FIX THIS UP WHEN INCORPORATE CLASS PARAMS
                model.fit(X, self.choice_var, varnames=best_varnames,
                          # isvars=best_isvarnames,
                          class_params_spec=best_class_params_spec,  # TODO!
                          member_params_spec=best_member_params_spec, # TODO!
                          num_classes=self.num_classes, alts=self.alt_var,
                          ids=self.choice_id, fit_intercept=best_Intercept,
                          transformation="boxcox", transvars=best_bcvars,
                        #   randvars=best_randvars,
                        #   correlation=best_corvars,
                          maxiter=self.maxiter, gtol=self.gtol, avail=self.avail,
                          weights=self.weights)
            else:
                model = MultinomialLogit()
                model.fit(X=df[best_varnames], y=self.choice_var,
                        varnames=best_varnames, isvars=best_isvarnames,
                        alts=self.alt_var, ids=self.choice_id,
                        transformation="boxcox", transvars=best_bcvars,
                        fit_intercept=best_Intercept)

        old_stdout = sys.stdout
        log_file = open(self.logger_name, "a")
        sys.stdout = log_file
        model.summary()
        sys.stdout = old_stdout
        log_file.close()
        logger.info(best_BICs)
        logger.info(current_BICs)

        return model

    def run_search_latent(self, HMS=10, min_classes=2, max_classes=5,
                          HMCR_min=0.6, HMCR_max=0.9, PAR_max=0.85,
                          PAR_min=0.3, itr_max=30, v=0.8, threshold=15,
                          val_share=0.25):
        models = []
        prev_bic = 1e+30
        for q in range(max_classes, min_classes-1, -1):
            self.num_classes = q
            model = self.run_search(HMS=HMS, HMCR_min=HMCR_min,
                                    HMCR_max=HMCR_max, PAR_max=PAR_max,
                                    PAR_min=PAR_min, itr_max=itr_max,v=v,
                                    threshold=threshold, val_share=val_share)
            models.append(model)
            if model.bic < prev_bic:
                prev_bic = model.bic
            else:
                break

        return models

    def check_dominance(self, obj1, obj2):
        """
        Function checks dominance between solutions for two objective functions
        Inputs: obj1 - List containing values of the two objective functions for solution 1
                obj2 - List containing values of the two objective functions for solution 2
        Output: Returns True if solution 1 dominates 2, False otherwise
        """
        indicator = False
        for a, b in zip(obj1, obj2):
            if a < b:
                indicator = True
            # if one of the objectives is dominated, then return False
            elif a > b:
                return False
        return indicator

    # Final Pareto-front identifier
    def get_fronts(self, HM):
        """
        Funtion for non-dominant sorting of the given set of solutions
        ni - the number of solutions which dominate the solution i
        si - a set of solutions which the solution i dominates

        Inputs: List containing set of solutions

        Output: Dict with keys indicating the Pareto rank and values containing indices of solutions in Input
        """
        si = {}
        ni = {}
        for i in range(len(HM)):
            sp_i = []
            np_i = 0
            for j in range(len(HM)):
                if i != j:
                    dominance = self.check_dominance(HM[i][:2], HM[j][:2])
                    if dominance:
                        sp_i.append(j)
                    else:
                        dominance = self.check_dominance(HM[j][:2], HM[i][:2])
                        if dominance:
                            np_i += 1
            si.update({i: sp_i})
            ni.update({i: np_i})
        # Identify solutions in each front
        Fronts = {}
        itr = 0
        for k in range(max(ni.keys())):
            Fi_idx = [key for key, val in ni.items() if val == k]
            if len(Fi_idx) > 0:
                Fronts.update({'F_{}'.format(itr): Fi_idx})
                itr += 1
        logger.info("Fronts: {}".format(str(Fronts)))
        return(Fronts)

    def crowding_dist(self, Fronts, HM):
        """
        Function to estimate crowding distance between 2 solutions
        Inputs:
        Fronts-Dict with keys indicating Pareto rank and values indicating indices of solutions belonging to the rank
        HM - List of solutions
        """
        v_dis = {}
        for v in Fronts.values():
            v.sort(key=lambda x: HM[x][0])
            for i in v:
                v_dis.update({i: 0})
        # Calculate crowding distance based on first objective
        for v in Fronts.values():
            for j in v:
                if v[0] == j or v[-1] == j:
                    v_dis.update({j: 1000000})
                else:
                    dis = abs(v_dis.get(j) +
                              ((HM[v[v.index(j) + 1]][0] -
                                HM[j][0]) / (max(HM[x][0] for x in
                                                 range(len(HM))) -
                                             min(HM[x][0] for x in
                                                 range(len(HM))))))
                    v_dis.update({j: dis})

        # Calculate crowding distance based on second objective
        q_dis = {}
        for v in Fronts.values():
            v.sort(key=lambda x: HM[x][1])
            for k in v:
                q_dis.update({k: 0})
        for v in Fronts.values():
            for l in v:
                if v[0] == l or v[-1] == l:
                    q_dis.update({l: 1000000})
                else:
                    dis = abs(q_dis.get(l) + ((HM[v[v.index(l)+1]][1] -
                                               HM[l][1])
                                               / (max(HM[x][1] for x
                                                     in range(len(HM))) -
                                                 min(HM[x][1] for x in
                                                     range(len(HM))))))
                    q_dis.update({l: dis})
        # Adding crowding distance from both objectives
        crowd = {k: q_dis[k] + v_dis[k] for k in v_dis.keys()}
        return(crowd)

    def pareto(self, Fronts, HM):
        Pareto_front_id = []
        for k, v in Fronts.items():
            if len(v) > 0:
                Pareto_front_id = Fronts.get(k)
                break
        Pareto_front = [HM[x] for x in Pareto_front_id]
        return(Pareto_front)
    # Fronts = get_fronts(unique_HM)
    # pareto_front = pareto(Fronts,unique_HM)
    # pareto_front

    def sort_InitHM(self, Fronts, v_dis, HM):
        """
        Function to sort memory from best solution to worst solution
        Inputs:
        Fronts-Dict with keys indicating Pareto rank and values indicating indices of solutions belonging to the rank
        v_dis - Dict with keys indicating index of solution in memory and value indicating crowding distance
        Output:
        Sorted_HM - Sorted list of solutions
        """
        Sorted_HM_id = []
        for k, v in Fronts.items():
            pareto_sols = {key: val for key, val in v_dis.items() if key
                            in Fronts.get(k)}
            Sorted_HM_id.extend([ke for ke, va in
                                sorted(pareto_sols.items(),
                                       key=lambda item: item[1],
                                       reverse=True)])

            # Sorted_HM_id.extend([ke for ke, va in sorted(pareto_sols.items(), key=lambda item: item[1])])
            if len(Sorted_HM_id) >= self.HMS:
                break
        Sorted_HM = [HM[x] for x in Sorted_HM_id]
        return(Sorted_HM)

    def non_dominant_sorting_initHM(self, HM):
        Front = self.get_fronts(HM)
        crowd = self.crowding_dist(Front, HM)
        Final_HM = self.sort_InitHM(Front, crowd, HM)
        return(Final_HM)

    # hm = non_dominant_sorting_initHM(unique_HM)
    # fronts = get_fronts(hm)
    # pf = pareto(fronts,hm)

    def sort_HM(self, Fronts, v_dis, HM):
        """
        Function to sort memory from best solution to worst solution
        Inputs:
        Fronts-Dict with keys indicating Pareto rank and values indicating indices of solutions belonging to the rank
        v_dis - Dict with keys indicating index of solution in memory and value indicating crowding distance
        Output:
        Sorted_HM - Sorted list of solutions
        """
        Sorted_HM_id = []
        for k, v in Fronts.items():
            pareto_sols = {key: val for key, val in v_dis.items()
                           if key in Fronts.get(k)}
            # Sorted_HM_id.extend([ke for ke, va in sorted(pareto_sols.items(), key=lambda item: item[1], reverse = True)])
            Sorted_HM_id.extend([ke for ke, va in
                                 sorted(pareto_sols.items(),
                                        key=lambda item: item[1])])
            # if len(Sorted_HM_id) >= HMS:
            # break
        Sorted_HM = [HM[x] for x in Sorted_HM_id]
        return(Sorted_HM)

    def non_dominant_sorting(self, HM):
        Front = self.get_fronts(HM)
        crowd = self.crowding_dist(Front, HM)
        Final_HM = self.sort_HM(Front, crowd, HM)
        return(Final_HM)

    def find_bestsol(self, HM):
        max_obj1 = max(HM[x][0] for x in range(len(HM)))
        max_obj2 = max(HM[x][1] for x in range(len(HM)))
        min_obj1 = min(HM[x][0] for x in range(len(HM)))
        min_obj2 = min(HM[x][1] for x in range(len(HM)))
        weights_obj1 = [(HM[x][0])-min_obj1/(max_obj1-min_obj1) for x in range(len(HM))]
        weights_obj2 = [(HM[x][1])-min_obj2/(max_obj2-min_obj2) for x in range(len(HM))]
        weights = [weights_obj1[x] + weights_obj2[x] for x in range(len(HM))]
        best_solid = weights.index(min(weights))
        logger.info("best sol for local search: {}".format(HM[best_solid]))
        return(HM[best_solid])
