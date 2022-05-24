import re
from datetime import datetime
import glob
import os
import numpy as np
from itertools import chain, combinations
from scipy import special

def create_log_name(filename: str):
    _time = str(datetime.now())
    _time_obj = datetime.strptime(_time, '%Y-%m-%d %H:%M:%S.%f')
    _timestamp = _time_obj.strftime("%Y%m%d_%H%M%S")
    return filename.format(_timestamp)

def purge_old_logs(path: str):
    for file in glob.glob(path):
        if re.match(r'.*/FairDynamicRec_log.*', file):
            os.remove(file)

def get_param_config_name(parameters):
    param_name = parameters['name']['attr']['abb'] if parameters['name']['attr']['abb'] else parameters['name']['value']
    for key, value in parameters.items():
        if key != 'name':
            param_name += "-" + str(parameters[key]['attr']['abb'] if parameters[key]['attr']['abb'] else parameters[key]['value']) + str(parameters[key]['value'])
    return param_name
def get_legend_labels(rankers):
    labels = {}
    for ranker in rankers:
        param_name = get_param_config_name(ranker['config'])
        labels[param_name] = param_name
        if 'attr' in ranker['config']['name']:
            if 'viz-legend' in ranker['config']['name']['attr']:
                if ranker['config']['name']['attr']['viz-legend'].lower() == 'false':
                    labels[param_name] = ranker['config']['name']['attr']['abb']
    return labels

def get_dict_key_from_value(var_dict, value):
    return list(var_dict.keys())[list(var_dict.values()).index(value)]
def get_dict_keys_from_list(var_dict, value_list):
    result = []
    for value in value_list:
        result.append(get_dict_key_from_value(var_dict, value))
    return result

def powerset_expectation_negation_partial(rankings, gamma, K):
    ''' Expected number of clicks over all possible permutations of R by counting powersets. '''

    N = len(rankings)
    rankings_neg = (1 - np.array(rankings)).tolist()

    result = 0
    for subset in powerset(rankings_neg[:K], K):
        k = len(subset)
        prod = np.multiply.reduce(subset)
        discount = gamma ** k
        if k != N:
            discount *= (1 - gamma)
        result += prod / special.binom(K, k) * discount

    for i in range(K, N):
        discount = gamma ** (i + 1)
        if i != (N - 1):
            discount *= (1 - gamma)
        result += np.multiply.reduce(rankings_neg[:i + 1]) * discount

    return 1 - result

def powerset(iterable, maxsize):
    ''' From https://stackoverflow.com/questions/1482308/how-to-get-all-subsets-of-a-set-powerset '''
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(maxsize + 1))

def compute_user_K_prime(rankings, gamma=0.9, max_K=12, epsilon=0.02):
    ''' Compute the value of K' for a user, up to which we can shuffle with max epsilon loss in clicks '''
    E_c = np.array([powerset_expectation_negation_partial(rankings, gamma, K) for K in range(1, max_K + 1)])
    E_c /= E_c[0]
    return np.searchsorted(-E_c, -(1.0 - epsilon))