import importlib
import logging
import os
import sys
from numbers import Number
from typing import Callable, Tuple, Union

import numpy as np
import pandas as pd
import pyabc
import petab_MS.problem as problem
from ..model import MorpheusModel, MorpheusModels
from ..sumstat.base import SummaryStatistics as SumStat
logger = logging.getLogger("FitMultiCell.PEtab_MS")
try:
    import petab_MS
    import petab_MS.C as C
except ImportError:
    petab = C = None
    logger.error(
        "Install petab_MS (see https://github.com/icb-dcm/petab) "
        "to use the petab_MS functionality."
    )


# priors that are evaluated "on-scale"
SCALED_PRIORS = [
    C.PARAMETER_SCALE_UNIFORM,
    C.PARAMETER_SCALE_NORMAL,
    C.PARAMETER_SCALE_LAPLACE,
]


class PetabImporter:
    """Import a PEtab model to parameterize it using FitMultiCell pipeline.
    This class provides methods to generate prior, Morpheus, par_maps
    for a pyABC analysis.
    Parameters
    ----------
    petab_problem:
        A PEtab problem containing all information on the parameter estimation
        problem.
    """

    def __init__(self, petab_problem: petab_MS.Problem):
        self.petab_problem = petab_problem

    def create_model(self, executable=None):
        """Create a model.
        Parameters

        ----------
        executable:
            path to Morpheus executable.
        Returns
        -------
        Morpheus_model:
            A model of a class MorpheusModels
        """
        return create_model(self, executable)

    def create_prior(self) -> pyabc.Distribution:
        """Create prior.

        Note: The returned parameters are on the `objectivePriorType` scale,
        i.e. on `parameterScale` if the prior is one of `parameterScale...`,
        otherwise on linear scale.
        The model must then take care of transforming the parameters from
        prior scale to the right scale.
        Effectively, pyABC thus ignores the `parameterScale`. If this is an
        issue as sampling e.g. on lin or log scale could make a difference,
        this can be revised.

        Returns
        -------
        prior: A valid pyabc.Distribution for the parameters to estimate.
        """
        return create_prior(parameter_df=self.petab_problem.parameter_df)

    def get_objective_function(self) -> Callable:

        return get_objective_function(
            objective_function_callable=self.petab_problem.objective_callable)

    def get_par_map(self) -> dict:
        """Create parameter map to be use with the Morpheus model.
        Returns
        -------
        par_map: A dictionary with the xpath for all parameters.
        """
        return get_par_map(parameter_df=self.petab_problem.parameter_df)

    def get_nominal_parameters(
        self, target_scale: str = 'prior'
    ) -> pyabc.Parameter:
        """Get nominal parameters.
        Parameters
        ----------
        target_scale:
            Scale on which to return the parameters.
            Values: 'prior'|'scaled'|'lin'.
            If 'prior', they are on the scale the corresponding prior is on.
            If 'scaled', they are scaled, if 'lin', they are unscaled.
        Returns
        -------
        par_nominal:
            The nominal parameters if provided in the petab parameters data
            frame.
        """
        return get_nominal_parameters(
            parameter_df=self.petab_problem.parameter_df,
            target_scale=target_scale,
            prior_scales=self.prior_scales,
            scaled_scales=self.scaled_scales,
        )

    def get_bounds(
        self, target_scale: str = 'prior', use_prior: bool = True
    ) -> dict:
        """Get bounds.
        Parameters
        ----------
        target_scale:
            Scale to get the nominal parameters on.
            Can be 'lin', 'scaled', or 'prior'.
        use_prior: Whether to use prior overrides if of type uniform.
        Returns
        -------
        bounds: Dictionary with a (lower, upper) tuple per parameter.
        """
        return get_bounds(
            parameter_df=self.petab_problem.parameter_df,
            target_scale=target_scale,
            prior_scales=self.prior_scales,
            scaled_scales=self.scaled_scales,
            use_prior=use_prior,
        )

    def get_parameter_names(self, target_scale: str = 'prior'):
        """Get meaningful parameter names, corrected for target scale."""
        parameter_df = petab_MS.normalize_parameter_df(
            self.petab_problem.parameter_df
        )

        # scale
        if target_scale == C.LIN:
            target_scales = {key: C.LIN for key in self.prior_scales}
        elif target_scale == 'prior':
            target_scales = self.prior_scales
        elif target_scale == 'scaled':
            target_scales = self.scaled_scales
        else:
            raise ValueError(f"Did not recognize target scale {target_scale}")

        names = {}
        for _, row in parameter_df.reset_index().iterrows():
            if row[C.ESTIMATE] == 0:
                continue
            key = row[C.PARAMETER_ID]
            name = str(key)
            if C.PARAMETER_NAME in parameter_df:
                if not petab_MS.is_empty(row[C.PARAMETER_NAME]):
                    name = str(row[C.PARAMETER_NAME])

            target_scale = target_scales[key]
            if target_scale != C.LIN:
                # mini check whether the name might indicate the scale already
                if not name.startswith("log"):
                    name = target_scale + "(" + name + ")"
            names[key] = name
        return names

    def get_exp_cond_map(self) -> dict:
        """get a dictionary of the experimental conditions.
        Returns
        -------
        condition_dict: A dictionary of for the xpath and the value for each
        experimental conditions.
        """

        return get_exp_cond_map(condition_df=self.petab_problem.condition_df)

    def _sanity_check(self):
        """Some checks to identify potential problems."""
        if any(
            self.scaled_scales[key] != C.LIN
            and self.prior_scales[key] == C.LIN
            for key in self.prior_scales
        ):
            logger.warning(
                "Found parameters with prior scale lin, parameter scale not "
                "lin. Note that pyABC currently ignores the parameter scale "
                "in this case and just performs sampling on the prior scale."
            )


def create_model(importer, executable):
    """
    Import model from petab importer.

    Parameters
    ----------
    importer:
        A petab problem importer.
    executable:
        path to Morpheus executable.

    Returns
    -------
    The imported model.
    """
    if 'par_map' not in importer.petab_problem.parameter_df:
        raise ValueError("'par_map' is missing in the parameter table")

    conditions = importer.petab_problem.condition_df
    cond_status = get_nr_exp_condition(conditions)
    par_map_imported = importer.get_par_map()
    par_scale = importer.petab_problem.get_optimization_parameter_scales()
    if 'observableFormula' in importer.petab_problem.observable_df:

        summary_statistics_callable = get_summary_statistics(
            importer.petab_problem.observable_df,
            os.path.dirname(importer.petab_problem.model_file),
        )
    # in case of no conditions are defined
    if cond_status == "no_condition":
        if executable is not None:
            model_con1 = MorpheusModel(
                importer.petab_problem.model_file,
                par_map=par_map_imported,
                par_scale=par_scale,
                sumstat=SumStat(
                    sum_stat_calculator=summary_statistics_callable),
                executable=executable,
            )
        else:
            model_con1 = MorpheusModel(
                importer.petab_problem.model_file,
                par_map=par_map_imported,
                par_scale=par_scale,
                sumstat=SumStat(
                    sum_stat_calculator=summary_statistics_callable),
            )
        return model_con1

    # in case of only one condition is defined
    elif cond_status == "one_condition":
        exp_cond_imported = importer.get_exp_cond_map()
        if executable is not None:
            model_con1 = MorpheusModel(
                importer.petab_problem.model_file,
                par_map=par_map_imported,
                exp_cond_map={'condition1': exp_cond_imported['condition1']},
                par_scale=par_scale,
                sumstat=SumStat(sum_stat_calculator=summary_statistics_callable),
                executable=executable,
            )
        else:
            model_con1 = MorpheusModel(
                importer.petab_problem.model_file,
                par_map=par_map_imported,
                exp_cond_map={'condition1': exp_cond_imported['condition1']},
                par_scale=par_scale,
                sumstat=SumStat(sum_stat_calculator=summary_statistics_callable),
            )
        return model_con1
    # in case of multiple conditions are defined
    else:
        exp_cond_imported = importer.get_exp_cond_map()
        models_list = []
        if executable is not None:
            for cond_key, cond_val in exp_cond_imported.items():
                tmp_model = MorpheusModel(
                    importer.petab_problem.model_file,
                    par_map=par_map_imported,
                    exp_cond_map={cond_key: cond_val},
                    par_scale=par_scale,
                    sumstat=SumStat(
                        sum_stat_calculator=summary_statistics_callable),
                    executable=executable,
                )
                models_list.append(tmp_model)
        else:
            for cond_key, cond_val in exp_cond_imported.items():
                tmp_model = MorpheusModel(
                    importer.petab_problem.model_file,
                    par_map=par_map_imported,
                    exp_cond_map={cond_key: cond_val},
                    par_scale=par_scale,
                    sumstat=SumStat(
                        sum_stat_calculator=summary_statistics_callable),
                )

                models_list.append(tmp_model)

        return MorpheusModels(models=models_list)


def create_prior(parameter_df: pd.DataFrame) -> pyabc.Distribution:
    """Create prior.
    Note: The prior generates samples according to
    `OBJECTIVE_PRIOR_TYPE` and `OBJECTIVE_PRIOR_PARAMETERS`.
    These samples are only scaled if the prior type is `PARAMETER_SCALE_...`,
    otherwise unscaled. The model has to take care of converting samples
    accordingly.
    Parameters
    ----------
    parameter_df: The PEtab parameter data frame.
    Returns
    -------
    prior: A valid pyabc.Distribution for the parameters to estimate.
    """
    # add default values
    parameter_df = petab_MS.normalize_parameter_df(parameter_df)

    prior_dct = {}

    # iterate over parameters
    for _, row in parameter_df.reset_index().iterrows():
        if row[C.ESTIMATE] == 0:
            # ignore fixed parameters
            continue

        # pyabc currently only knows objective priors, no
        #  initialization priors
        prior_type = row[C.OBJECTIVE_PRIOR_TYPE]
        # pars_str = row[C.OBJECTIVE_PRIOR_PARAMETERS]
        # prior_pars = (row.lowerBound, row.upperBound)
        pars_str = row[C.OBJECTIVE_PRIOR_PARAMETERS]
        prior_pars = tuple(val for val in pars_str.split(';'))

        if prior_pars[0] == 'nan':
            prior_pars = (row.lowerBound, row.upperBound)
        if prior_type in [C.PARAMETER_SCALE_UNIFORM, C.UNIFORM]:
            lb, ub = prior_pars
            lb, ub = float(lb), float(ub)
            # scipy pars are location, width
            rv = pyabc.RV('uniform', lb, ub - lb)
        elif prior_type in [C.PARAMETER_SCALE_NORMAL, C.NORMAL]:
            mean, std = prior_pars
            mean, std = float(mean), float(std)
            # scipy pars are mean, std
            rv = pyabc.RV('norm', loc=mean, scale=std)
        elif prior_type in [C.PARAMETER_SCALE_LAPLACE, C.LAPLACE]:
            mean, b = prior_pars
            mean, b = float(mean), float(b)
            # scipy pars are loc=mean, scale=b
            rv = pyabc.RV('laplace', loc=mean, scale=b)
        elif prior_type == C.LOG_NORMAL:
            mean, std = prior_pars
            mean, std = float(mean), float(std)
            # petab pars are mean, std of the underlying normal distribution
            # scipy pars are s, loc, scale where s = std, scale = exp(mean)
            #  as a simple calculation shows
            rv = pyabc.RV('lognorm', s=std, loc=0, scale=np.exp(mean))
        elif prior_type == C.LOG_LAPLACE:
            mean, b = prior_pars
            mean, b = float(mean), float(b)
            # petab pars are mean, b of the underlying laplace distribution
            # scipy pars are c, loc, scale where c = 1 / b, scale = exp(mean)
            #  as a simple calculation shows
            rv = pyabc.RV('loglaplace', c=1 / b, scale=np.exp(mean))
        elif prior_type == C.PARAMETER_VALUE_DISCRETE:
            xk, pk = prior_pars
            rv = pyabc.RV(
                "rv_discrete", values=(eval(xk), eval(pk))  # noqa: S307
            )

        else:
            raise ValueError(f"Cannot handle prior type {prior_type}.")

        prior_dct[row[C.PARAMETER_ID]] = rv

    # create prior distribution
    prior = pyabc.Distribution(**prior_dct)

    return prior


def get_objective_function(objective_function_callable: problem) -> Callable:
    """get the objective function to be used to evaluate the discrepancy
    between the simulated and the measured data.
    Parameters
    ----------
    objective_function_callable: The PEtab objective function Callable.
    Returns
    -------
    obj_func: A Callable to the objection function.
    """
    return objective_function_callable


def get_par_map(parameter_df: pd.DataFrame) -> dict:
    """Create parameter map to be use with the Morpheus model.
    Parameters
    ----------
    parameter_df: The PEtab parameter data frame.
    Returns
    -------
    par_map: A dictionary with the xpath for all parameters.
    """
    return dict(zip(parameter_df.index, parameter_df.par_map))


def get_exp_cond_map(condition_df) -> dict:
    """get a dictionary of the experimental conditions.

    Parameters
    ----------
    condition_df: The PEtab experimental conditions data frame.
    Returns
    -------
    condition_dict: A dictionary of for the xpath and the value for each
    experimental conditions.
    """
    condition_dict = {}
    keys_values = condition_df.index.tolist()
    keys_map = condition_df.columns.tolist()[1:]
    for i, condition in enumerate(keys_values):
        tmp_dict = []
        for xpath in keys_map:
            tmp_dict.append((xpath, condition_df[xpath].tolist()[i]))
        condition_dict[condition] = dict(tmp_dict)
    return condition_dict


def get_scales(parameter_df: pd.DataFrame) -> Tuple[dict, dict]:
    """Unravel whether the priors and evaluations are on or off scale.
    Only the `parameterScale...` priors are on-scale, the other priors are on
    linear scale.
    Parameters
    ----------
    parameter_df: The PEtab parameter data frame.
    Returns
    -------
    prior_scales, scaled_scales:
        Scales for each parameter on prior and evaluation level.
    """
    # fill in objective prior columns
    parameter_df = petab_MS.normalize_parameter_df(parameter_df)
    prior_scales = {}
    scaled_scales = {}
    for _, row in parameter_df.reset_index().iterrows():
        if row[C.ESTIMATE] == 0:
            continue
        prior_scales[row[C.PARAMETER_ID]] = (
            row[C.PARAMETER_SCALE]
            if row[C.OBJECTIVE_PRIOR_TYPE] in SCALED_PRIORS
            else C.LIN
        )
        scaled_scales[row[C.PARAMETER_ID]] = row[C.PARAMETER_SCALE]
    return prior_scales, scaled_scales


def get_summary_statistics(
    observable_df: pd.DataFrame, problem_path
) -> Union[Callable, dict]:
    """Create a callable for the summary statistics function for observables.

    Parameters
    ----------
    observable_df: The PEtab observable data frame.
    problem_path: The problem path
    Returns
    -------
    summary_statistics_dict: A Callable or dictionary of callable for each
    summary statistics.
    """

    module_path = observable_df.observableFormula.to_dict()
    summary_statistics_dict = {}
    for key, path in module_path.items():
        head, tail = os.path.split(path)

        if head != '':
            raise ValueError(
                f"summary_statistics function should be within the "
                f"Petab folder. However, now it is on: {head}."
            )
        tail_info = tuple(val for val in tail.split(';'))
        filename, ext = os.path.splitext(tail_info[0])
        module_path = problem_path + '/' + tail_info[0]
        module_name = filename
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        new_module = getattr(module, tail_info[1])
        summary_statistics_dict[key] = new_module
    if summary_statistics_dict == {}:
        summary_statistics_dict = None
    return summary_statistics_dict


# def import_petab_problem(
#         petab_problem: petab_MS.Problem) -> 'MorpheusModel':
#     """
#     Import model from petab problem.
#
#     :param petab_problem:
#         A petab problem containing all relevant information on the model.
#
#     :return:
#         The imported model.
#     """
#
#     if 'par_map' not in petab_problem.parameter_df:
#         raise ValueError("'par_map' is missing in the parameter table")
#     par_map = get_par_map(petab_problem.parameter_df)
#     if 'parameterScale' not in petab_problem.parameter_df:
#         scale = 'lin'
#     else:
#         scale = petab_problem.parameter_df.parameterScale.to_dict()
#     ss_post_process_callable = None
#     if 'observableFormula' in petab_problem.observable_df:
#         ss_post_process_callable = get_ss_post_process(
#             petab_problem.observable_df)
#     exp_cond_map = get_exp_cond_map(petab_problem.condition_df)
#
#     if len(exp_cond_map) < 2:
#         model = MorpheusModel(model_file=petab_problem.model_file,
#                               par_map=par_map,
#                               par_scale=scale,
#                               exp_cond_map=exp_cond_map,
#                               ss_post_processing=ss_post_process_callable)
#         return model
#     else:
#         models_list = []
#         models = MorpheusModels(models_list=models_list)
#         for condition, val in exp_cond_map.items():
#             model = MorpheusModel(model_file=petab_problem.model_file,
#                                   par_map=par_map,
#                                   par_scale=scale,
#                                   exp_cond_map={condition: val},
#                                   ss_post_processing=ss_post_process_callable)
#             models_list.append(model)
#         return models


def get_bounds(
    parameter_df: pd.DataFrame,
    target_scale: str,
    prior_scales: dict,
    scaled_scales: dict,
    use_prior: bool,
) -> dict:
    """Get bounds.
    Parameters
    ----------
    parameter_df: The PEtab parameter data frame.
    target_scale:
        Scale to get the nominal parameters on.
        Can be 'lin', 'scaled', or 'prior'.
    prior_scales: Prior scales.
    scaled_scales: On-scale scales.
    use_prior: Whether to use prior overrides if of type uniform.
    Returns
    -------
    bounds: Dictionary with a (lower, upper) tuple per parameter.
    """
    parameter_df = petab_MS.normalize_parameter_df(parameter_df)

    # scale
    if target_scale == C.LIN:
        target_scales = {key: C.LIN for key in prior_scales}
    elif target_scale == 'prior':
        target_scales = prior_scales
    elif target_scale == 'scaled':
        target_scales = scaled_scales
    else:
        raise ValueError(f"Did not recognize target scale {target_scale}")

    # extract bounds
    bounds = {}
    for _, row in parameter_df.reset_index().iterrows():
        if row[C.ESTIMATE] == 0:
            # ignore fixed parameters
            continue

        key = row[C.PARAMETER_ID]

        # from lower and upper bound
        lower, upper = row[C.LOWER_BOUND], row[C.UPPER_BOUND]
        origin_scale = C.LIN

        # from prior
        prior_type = row[C.OBJECTIVE_PRIOR_TYPE]
        if use_prior and prior_type in [C.UNIFORM, C.PARAMETER_SCALE_UNIFORM]:
            pars_str = row[C.OBJECTIVE_PRIOR_PARAMETERS]
            lower, upper = tuple(float(val) for val in pars_str.split(';'))
            if prior_type == C.PARAMETER_SCALE_UNIFORM:
                origin_scale = row[C.PARAMETER_SCALE]

        # convert to target scale
        lower = rescale(
            lower, origin_scale=origin_scale, target_scale=target_scales[key]
        )
        upper = rescale(
            upper, origin_scale=origin_scale, target_scale=target_scales[key]
        )
        bounds[key] = (lower, upper)
    return bounds


def get_nominal_parameters(
    parameter_df: pd.DataFrame,
    target_scale: str,
    prior_scales: dict,
    scaled_scales: dict,
) -> pyabc.Parameter:
    """Get nominal parameters.
    Parameters
    ----------
    parameter_df: The PEtab parameter data frame.
    target_scale:
        Scale to get the nominal parameters on.
        Can be 'lin', 'scaled', or 'prior'.
    prior_scales: Prior scales.
    scaled_scales: On-scale scales.
    Returns
    -------
    par_nominal: The nominal parameters if provided in the data frame.
    """
    # unscaled parameters
    par = pyabc.Parameter(
        {
            key: parameter_df.loc[key, C.NOMINAL_VALUE]
            for key in prior_scales.keys()
        }
    )

    # scale
    if target_scale == C.LIN:
        # nothing to be done
        return par
    elif target_scale == 'prior':
        target_scales = prior_scales
    elif target_scale == 'scaled':
        target_scales = scaled_scales
    else:
        raise ValueError(f"Did not recognize target scale {target_scale}")
    # map linear to target scales component-wise
    return map_rescale(par, origin_scales=C.LIN, target_scales=target_scales)


def rescale(val: Number, origin_scale: str, target_scale: str) -> Number:
    """Convert parameter value from origin scale to target scale.
    Parameters
    ----------
    val: Parameter value to rescale.
    origin_scale: Origin scale.
    target_scale: Target scale.
    Returns
    -------
    val: The rescaled parameter value.
    """
    if origin_scale == target_scale:
        # nothing to be done
        return val
    # origin to linear to target
    return petab_MS.scale(petab.unscale(val, origin_scale), target_scale)


def map_rescale(
    par: pyabc.Parameter,
    origin_scales: Union[dict, str],
    target_scales: Union[dict, str],
) -> pyabc.Parameter:
    """Rescale parameter dictionary.
    Parameters
    ----------
    par: The parameter to rescale.
    origin_scales: The origin scales.
    target_scales: The target scales.
    Returns
    -------
    par: The rescaled parameter.
    """
    # handle convenience input
    if isinstance(origin_scales, str):
        origin_scales = {key: origin_scales for key in par.keys()}
    if isinstance(target_scales, str):
        target_scales = {key: target_scales for key in par.keys()}

    # rescale each component
    for key, val in par.items():
        par[key] = rescale(
            val=val,
            origin_scale=origin_scales[key],
            target_scale=target_scales[key],
        )

    return par


def get_nr_exp_condition(condition_df):
    if condition_df.shape[0] <= 1:
        if condition_df.shape[1] <= 1:
            return "no_condition"
        else:
            return "one_condition"
    else:
        return "multiple_conditions"


# =======
#    if 'observableFormula' not in petab_problem.observable_df:
#        ss_post_process = None
#    else:
#        ss_post_process = petab_problem.observable_df.
#        observableFormula.to_dict()
#        ss_post_process_callable = get_ss_post_process(
#        petab_problem.observable_df)
#    model = MorpheusModel(model_file=model_dir,
#                          par_map=par_map,
#                          par_scale=scale,
#                          ss_post_processing=ss_post_process_callable)
#    return model
# >>>>>>> 0637f8e (allow for post_processing on simulation result comming
# from Morpheus)
