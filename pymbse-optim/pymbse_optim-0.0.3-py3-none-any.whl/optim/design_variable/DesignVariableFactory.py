import math
from typing import List, Union

import pandas as pd

from pymbse.optim.design_variable.GeneticDesignVariable import GeneticDesignVariable, \
    GeneticLayerDesignVariable, GeneticBlockDesignVariable, GeneticMultiBlockDesignVariable

GeneticDesignVariableTypes = Union[
    GeneticDesignVariable, GeneticLayerDesignVariable, GeneticBlockDesignVariable, GeneticMultiBlockDesignVariable]


def init_genetic_design_variables_with_csv(csv_path: str) -> List[GeneticDesignVariableTypes]:
    """

    :param csv_path:
    :return:
    """
    # todo: add description of columns in the dataframe
    design_variables_df = pd.read_csv(csv_path)
    return init_genetic_design_variables_with_df(design_variables_df)


def init_genetic_design_variables_with_df(design_variables_df):
    genetic_design_variables = []
    for _, row in design_variables_df.iterrows():
        gen_dv = get_genetic_design_variable_class(row)
        genetic_design_variables.append(gen_dv)

    return genetic_design_variables


def get_genetic_design_variable_class(params: pd.DataFrame) -> GeneticDesignVariableTypes:
    """

    :param params:
    :return:
    """
    if is_param_nan(params, 'bcs') and is_param_nan(params, 'layer'):
        kwargs = params[['xl', 'xu', 'variable_type', 'variable', 'bits']].to_dict()
        design_variable = GeneticDesignVariable(**kwargs)
    elif is_param_nan(params, 'bcs') and not is_param_nan(params, 'layer'):
        kwargs = params[['xl', 'xu', 'variable_type', 'variable', 'layer', 'bits']].to_dict()
        design_variable = GeneticLayerDesignVariable(**kwargs)
    elif isinstance(params['bcs'], (int, float)) or is_str_param_numeric(params, 'bcs'):
        kwargs = params[['xl', 'xu', 'variable_type', 'variable', 'layer', 'bcs', 'bits']].to_dict()
        design_variable = GeneticBlockDesignVariable(**kwargs)
    elif '-' in params['bcs']:
        kwargs = params[['xl', 'xu', 'variable_type', 'variable', 'layer', 'bcs', 'bits']].to_dict()
        design_variable = GeneticMultiBlockDesignVariable(**kwargs)
    else:
        raise AttributeError(f'The design variable has incorrect block definition: {params.to_dict()}.')

    if '_gene' in params:
        # ToDo: add a proper setter
        design_variable._gene = (params['_gene'])

    return design_variable


def is_str_param_numeric(params: pd.DataFrame, key: str) -> bool:
    param = params[key]
    if isinstance(param, str) and '-' not in param:
        try:
            float(param)
            return True
        except ValueError:
            return False
    else:
        return False


def is_param_nan(param_to_key: pd.DataFrame, key: str) -> bool:
    """

    :param param_to_key:
    :param key:
    :return:
    """
    if key not in param_to_key:
        return True
    else:
        param = param_to_key[key]
        if isinstance(param, str) and param != '':
            return False
        else:
            return param == '' or param == 'nan' or math.isnan(param)
