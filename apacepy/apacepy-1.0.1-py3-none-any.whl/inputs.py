from deampy.parameters import _Parameter

from apacepy.transmission import get_infectivity_from_r_nut


class ModelSettings:
    """ model settings of an epidemic model """
    def __init__(self):
        self.deltaT = 1/364              # length of a simulation time step
        self.simulationDuration = 1      # simulation duration
        self.simulationOutputPeriod = 1/52  # simulation output period
        self.observationPeriod = 1/52       # observation period
        self.timeToStartDecisionMaking = 0  # time to start decision making
        self.endOfWarmUpPeriod = 0               # warmup period (for collecting cost and health outcomes)
        self.checkEradicationConditions = True  # stop the simulation if eradication conditions are met

        self.storeParameterValues = False  # set to True to store the sampled parameter values

        # Outcomes projected after the warm-up period
        # 1) cumulative incidence of sum incidence time-series (after warm-up).
        # 2) average incident ratios (after warm-up)
        self.storeProjectedOutcomes = False  # set to True to store the outcomes projected after the warm-up period

        # saving results
        self.exportTrajectories = True  # if to export simulated trajectories
        self.folderToSaveTrajs = 'outputs/trajectories'    # folder to store trajectories
        self.folderToSaveSummary = 'outputs/summary'  # folder to store summary of simulations (ids, seeds, costs, and healths)
        self.folderToSaveScenarioAnalysis = 'outputs/scenarios'  # folder to store the results of scenario analysis

        # calibration
        self.calcLikelihood = False  # set to true to calculate the likelihood weights
        self.epiTimeToStartCalibration = 0  # epidemic time to start calibrating the model
        self.exportCalibrationTrajs = True  # if to export trajectories obtained during calibration
        self.folderToSaveCalibrationResults = 'outputs/calibration/calibration_summary.csv'
        # folder to store trajectories produced during calibration
        self.folderToSaveCalibrationTrajs = 'outputs/trajectories-calibration'

        # economic evaluation
        self.collectEconEval = False   # whether to collect economic evaluation outcomes
        self.annualDiscountRate = 0.03    # annual discount rate

        # ----- these will be calculated at the initialization of the model --------------
        self.nDeltaTsInSimulation = None  # number of deltaT's in simulation duration
        self.nDeltaTsInSimOutputPeriod = None  # number of deltaT's in output periods (to aggregate observations)
        self.nDeltaTsInObsPeriod = None  # number of deltaT's in observation periods
                                         # (used for calibration and surveillance)
        self.nDeltaTsToStartDecisionMaking = None  # number of deltaT's to pass to start decision making
        self.nDeltaTsInWarmUpPeriod = 0  # number of deltaT's in the warm up period
        self.nDeltaTsToStartCalibration = 0 # number of deltaT's to start calibration

    def initialize(self):

        one_over_delta_t = 1/self.deltaT
        self.nDeltaTsInSimulation = int(self.simulationDuration * one_over_delta_t)
        self.nDeltaTsInSimOutputPeriod = int(self.simulationOutputPeriod * one_over_delta_t)
        self.nDeltaTsInObsPeriod = int(self.observationPeriod * one_over_delta_t)
        self.nDeltaTsToStartDecisionMaking = int(self.timeToStartDecisionMaking * one_over_delta_t)
        self.nDeltaTsInWarmUpPeriod = int(self.endOfWarmUpPeriod * one_over_delta_t)
        self.nDeltaTsToStartCalibration = int(self.epiTimeToStartCalibration * one_over_delta_t)

    def update_settings(self, *values):
        """
        :param values: (list) of values (float, string, etc.) that can be used to update certain settings
            This method should be overridden when using the model for scenario analysis
        """
        pass
        # raise NotImplementedError('This method is not implemented in the derived class.')


class EpiParameters:
    """ class to contain the parameters of an epidemic model """

    def __init__(self):
        self.dictOfParams = dict()   # dictionary of parameters (not varying over time)
        self.listOfTimeDependParams = []    # dictionary of time varying parameters

    def reset(self):
        pass

    def list_time_dependent_params(self):
        """ find the list of parameters that vary over time """

        for key, par in self.dictOfParams.items():
            if isinstance(par, list):
                for p in par:
                    if isinstance(p, list):
                        for q in p:
                            self._update_list_of_time_dep_params(param=q, key=key)
                    else:
                        self._update_list_of_time_dep_params(param=p, key=key)
            else:
                self._update_list_of_time_dep_params(param=par, key=key)

    def _update_list_of_time_dep_params(self, param, key):
        try:
            if param.ifTimeDep:
                self.listOfTimeDependParams.append(param)
        except AttributeError as error:
            raise AttributeError(
                "Error for parameter '{}'. Type: {}. Error message: {}.".format(key, type(param), error))

    def sample_parameters(self, rng, time):
        """ samples from all parameters """

        for key, par in self.dictOfParams.items():
            if isinstance(par, list):
                for i, p in enumerate(par):
                    if isinstance(p, list):
                        for j, p_in in enumerate(p):
                            self._sample_this_param(
                                param=p_in, rng=rng, time=time, label=key + '-' + str(i)+'-' + str(j))
                    else:
                        self._sample_this_param(param=p, rng=rng, time=time, label=key + '-' + str(i))
            else:
                self._sample_this_param(param=par, rng=rng, time=time, label=key)

    @staticmethod
    def _sample_this_param(param, rng, time, label):

        try:
            param.sample(rng=rng, time=time)
            if param.value is None:
                raise ValueError("The value of parameter '{}' is None after sampling.".format(label))

        except BaseException as e:
            raise ValueError("Error message: {}. "
                             "\nSomething to check: All parameters used to inform '{}' "
                             "should be listed before this parameters "
                             "in the dictionary of parameters.".format(str(e), label))

    def update_time_dependent_params(self, rng, time):
        """ updates only time-dependent parameters """

        # if the epidemic is not yet stated, use time=0
        if time is None:
            time = 0

        for par in self.listOfTimeDependParams:
            par.sample(rng=rng, time=time)

    def get_dic_of_parameter_samples(self):
        """
        :return: (dictionary) with parameter names as keys and the current parameter values as values
        """

        dic = dict()
        for key, par in self.dictOfParams.items():
            if isinstance(par, list):
                for i, p in enumerate(par):
                    if isinstance(p, list):
                        for j, q in enumerate(p):
                            dic[key + '-' + str(i) + '-' + str(j)] = q.value
                    else:
                        dic[key+'-'+str(i)] = p.value
            else:
                dic[key] = par.value

        return dic

    def get_list_of_parameter_samples(self):
        """
        :return: (list) of current parameter values
        """

        result = []
        for key, par in self.dictOfParams.items():
            if isinstance(par, list):
                for p in par:
                    if isinstance(p, list):
                        for q in p:
                            result.append(q.value)
                    else:
                        result.append(p.value)
            else:
                result.append(par.value)

        return result


class InfectivityFromR0(_Parameter):
    # parameter to calculate infectivity from R0

    def __init__(self, contact_matrix, par_r0,
                 list_par_susceptibilities, list_par_pop_sizes, par_inf_duration,
                 id=None, name=None):
        """
        :param contact_matrix: (list of list) contact rates
        :param par_r0: (Parameter) for R0
        :param list_par_susceptibilities: (list) of parameters for susceptibility of each group
        :param list_par_pop_sizes: (list) of parameters for size of each group
        :param par_inf_duration: (Parameter) of duration of infectiousness
        :param id: (int) id of a parameter
        :param name: (string) name of a parameter
        """

        self.parR0 = par_r0
        self.contactMatrix = contact_matrix
        self.susceptibilities = list_par_susceptibilities
        self.popSizes = list_par_pop_sizes
        self.infDur = par_inf_duration

        # if time dependent
        if_time_dep = False
        for p in self.susceptibilities:
            if p.ifTimeDep:
                if_time_dep = True
                break

        _Parameter.__init__(self, id=id, name=name, if_time_dep=if_time_dep)

    def sample(self, rng=None, time=None):

        susp_values = [p.value for p in self.susceptibilities]
        pop_size_values = [p.value for p in self.popSizes]

        self.value = get_infectivity_from_r_nut(
            r0=self.parR0.value,
            contact_matrix=self.contactMatrix,
            susceptibilities=susp_values,
            pop_sizes=pop_size_values,
            inf_dur=self.infDur.value)

        return self.value
