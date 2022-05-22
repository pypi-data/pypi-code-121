from itertools import combinations
import random

import pandas
import pingouin as pg
from copy import deepcopy

import numpy as np
from graphviz import Digraph
from numba import njit
from scipy.stats.distributions import chi2
from .score import compute_weights


# random.seed(941214)


# create missing mechanism
def miss_mechanism(dag, noise='MAR', rom=0.5):
    '''

    :param dag: true DAG
    :param noise: type of missing mechanism
    :param rom: ratio of missing variables
    :return: missing mechanism
    '''
    if type(dag) is str:
        dag = from_bnlearn(dag)
    elif type(dag) is not dict:
        raise Exception('The format of input DAG is invalid.')
    varnames = list(dag.keys())
    cause_dict = {}
    if noise == 'MCAR':
        vars_miss = random.sample(varnames, round(len(varnames) * rom))
        for var in vars_miss:
            cause_dict[var] = []
    elif noise == 'MAR':
        nom = round(len(varnames) * rom)
        noc = len(varnames) - nom
        vstructs = vstructures(dag)
        vars_miss = []
        vars_comp = []
        for i in range(len(vstructs)):
            if len(vars_comp) != noc or (len(vars_comp) == noc and vstructs[i][1] in vars_comp):
                if vstructs[i][0] not in vars_miss + vars_comp:
                    cause_dict[vstructs[i][0]] = [vstructs[i][1]]
                    vars_miss.append(vstructs[i][0])
                    vars_comp = list(set(vars_comp + [vstructs[i][1]]))
                elif vstructs[i][2] not in vars_miss + vars_comp:
                    cause_dict[vstructs[i][2]] = [vstructs[i][1]]
                    vars_miss.append(vstructs[i][2])
                    vars_comp = list(set(vars_comp + [vstructs[i][1]]))
                if len(vars_miss) == nom:
                    break
        if len(vars_miss) < nom:
            vars_miss2 = random.sample([x for x in varnames if x not in vars_miss + vars_comp], nom - len(vars_miss))
            vars_comp = [x for x in varnames if x not in vars_miss + vars_miss2]
            for var in vars_miss2:
                nbr = adjacent(dag, var)
                if any(item in vars_comp for item in nbr):
                    cause_dict[var] = random.sample([x for x in nbr if x in vars_comp], 1)
                else:
                    cause_dict[var] = random.sample(vars_comp, 1)
    elif noise == 'MNAR':
        nom = round(len(varnames) * rom)
        vstructs = vstructures(dag)
        vars_miss = []
        for i in range(len(vstructs)):
            if vstructs[i][0] not in cause_dict:
                cause_dict[vstructs[i][0]] = [vstructs[i][1]]
                vars_miss = list(set(vars_miss + [vstructs[i][0], vstructs[i][1]]))
            elif vstructs[i][2] not in cause_dict:
                cause_dict[vstructs[i][2]] = [vstructs[i][1]]
                vars_miss = list(set(vars_miss + [vstructs[i][2], vstructs[i][1]]))
            if len(vars_miss) >= nom:
                break
        if len(vars_miss) < nom:
            vars_miss2 = random.sample([x for x in varnames if x not in vars_miss], nom - len(vars_miss))
            vars_comp = [x for x in varnames if x not in vars_miss + vars_miss2]
            for var in vars_miss2:
                nbr = adjacent(dag, var)
                if any(item not in vars_comp for item in nbr):
                    cause_dict[var] = random.sample([x for x in nbr if x not in vars_comp + [var]], 1)
                else:
                    cause_dict[var] = random.sample([x for x in varnames if x not in vars_comp + [var]], 1)
    else:
        raise Exception('noise ' + noise + ' is undefined.')
    return cause_dict


def vstructures(dag):
    if type(dag) is str:
        dag = from_bnlearn(dag)
    elif type(dag) is not dict:
        raise Exception('The format of input dag is invalid')

    cpdag = dag2cpdag(dag)
    vstructs = []
    for var in cpdag:
        if len(cpdag[var]['par']) > 1:
            for pair in [(a, b) for idx, a in enumerate(cpdag[var]['par']) for b in cpdag[var]['par'][idx + 1:]]:
                if pair[0] not in adjacent(cpdag, pair[1]):
                    vstructs.append([pair[0], var, pair[1]])
    return vstructs


# add missing value in dataset
def add_missing(data, cause_dict):
    data_missing = deepcopy(data)
    m_min = 0.1
    m_max = 0.6
    for var in cause_dict.keys():
        if len(cause_dict[var]) == 0:
            m = np.random.uniform(m_min, m_max)
            data_missing[var][np.random.uniform(size=len(data)) < m] = None
        else:
            for cause in cause_dict[var]:
                if data[cause].dtype == 'category':
                    state_m = data[cause].mode()[0]
                    data_missing[var][(np.random.uniform(size=len(data)) < m_max) & (data[cause] == state_m)] = None
                    data_missing[var][(np.random.uniform(size=len(data)) < m_min) & (data[cause] != state_m)] = None
                elif data[cause].dtype == 'float' or data[cause].dtype == 'int':
                    thres = data[cause].quantile(0.2)
                    data_missing[var][(np.random.uniform(size=len(data)) < m_max) & (data[cause] < thres)] = None
                    data_missing[var][(np.random.uniform(size=len(data)) < m_min) & (data[cause] >= thres)] = None
                else:
                    raise Exception('data type ' + data[cause].dtype + ' is not supported.')
    return data_missing


def pairwise(data, varnames, vars, cause_list, cache_data, cache_weight, method):
    if method == 'pw':
        W = tuple(sorted([v for v in vars if v in cause_list]))
        if W not in cache_data:
            W_ids = [i for i in range(len(varnames)) if varnames[i] in W]
            if len(W):
                if 'int' in data.dtype.name:
                    cache_data[W] = data[data[:, W_ids].min(axis=1) >= 0]
                else:
                    cache_data[W] = data[~np.isnan(data[:, W_ids]).any(axis=1)]
            else:
                cache_data[W] = data
            cache_weight[W] = np.ones(len(cache_data[W]))
    elif method == 'ipw':
        W = list(vars)
        while True:
            Pa_R_vars = [cause_list[x] for x in W if x in cause_list]
            Pa_R_vars = [x for l in Pa_R_vars for x in l]
            if all(elem in W for elem in Pa_R_vars):
                break
            else:
                W = list(set(W) | set(Pa_R_vars))
        W = tuple(sorted([v for v in W if v in cause_list]))
        if W not in cache_data:
            W_ids = [i for i in range(len(varnames)) if varnames[i] in W]
            if len(W) > 0:
                if 'int' in data.dtype.name:
                    cache_data[W] = data[data[:, W_ids].min(axis=1) >= 0]
                else:
                    cache_data[W] = data[~np.isnan(data[:, W_ids]).any(axis=1)]
                cache_weight[W] = compute_weights(data, varnames, W_ids, cause_list)
            else:
                cache_data[W] = data
                cache_weight[W] = np.ones(len(data))
    elif method == 'aipw':
        Pa_R_vars = [cause_list[x] for x in vars if x in cause_list]
        Pa_R_vars = [x for l in Pa_R_vars for x in l]
        W = tuple(sorted([v for v in vars if v in cause_list.keys()]))
        pa_d = [v for v in Pa_R_vars if v not in W]
        pa_d = [v for v in pa_d if v in cause_list]
        if W not in cache_data:
            if len(W) > 0:
                W_ids = [i for i in range(len(varnames)) if varnames[i] in W]
                if 'int' in data.dtype.name:
                    cache_data[W] = data[data[:, W_ids].min(axis=1) >= 0]
                else:
                    cache_data[W] = data[~np.isnan(data[:, W_ids]).any(axis=1)]

                if pa_d:
                    cache_weight[W] = np.ones(cache_data[W].shape[0])
                else:
                    cache_weight[W] = compute_weights(data, varnames, W_ids, cause_list)
            else:
                cache_data[W] = data
                cache_weight[W] = np.ones(data.shape[0])
    else:
        raise Exception('Unknown variant of HC')
    return cache_data, cache_weight, W


# find the missing mechanism of dataset with missing values
def find_causes(data, test_function='default', alpha=0.01):
    var_miss = data.columns[data.isnull().any()]
    if all(data[var].dtype.name == 'category' for var in data):
        factor = True
        data = data.apply(lambda x: x.cat.codes)
        if test_function == 'default':
            test_function = 'g_test'
    elif all(data[var].dtype.name != 'category' for var in data):
        if test_function == 'default':
            test_function = 'pearson_test'
        factor = False
    else:
        raise Exception('Mixed data is not supported.')

    causes = {}
    varnames = data.columns.tolist()
    for var in var_miss:
        causes[var] = list(varnames)
        causes[var].remove(var)
        if factor:
            data['missing'] = data[var] == -1
            data['missing'] = data['missing'].astype('int8')
        else:
            data['missing'] = data[var].isna()
        l = 0
        while len(causes[var]) > l:
            remain_causes = list(causes[var])
            for can in remain_causes:
                cond_set = list(remain_causes)
                cond_set.remove(can)
                for cond in combinations(cond_set, l):
                    if factor:
                        data_delete = data[(data[[can] + list(cond)] > -1).all(1)].to_numpy()
                    else:
                        data_delete = data.dropna(subset=[can] + list(cond))
                    cols = np.asarray(
                        [data_delete.shape[1] - 1] + [varnames.index(can)] + [varnames.index(x) for x in cond])
                    p_value = globals()[test_function](data_delete, cols)
                    if p_value > alpha:
                        causes[var].remove(can)
                        break
            l += 1
    data.pop('missing')
    return causes


# convert the dag to bnlearn format
def to_bnlearn(dag):
    output = ''
    for var in dag:
        output += '[' + var
        if dag[var]['par']:
            output += '|'
            for par in dag[var]['par']:
                output += par + ':'
            output = output[:-1]
        output += ']'
    return output


# convert bnlearn format to my format
def from_bnlearn(dag):
    dag = dag[1: len(dag) - 1]
    output = {}
    for node in dag.split(']['):
        if '|' not in node:
            output[node] = {'par': [], 'nei': []}
        else:
            output[node.split('|')[0]] = {'par': node.split('|')[1].split(':'), 'nei': []}
    return output


# random orient a CPDAG to a DAG
def random_orient(cpdag):
    undirected_edges = []
    for var in cpdag:
        for nei in cpdag[var]['nei']:
            edge = sorted([var, nei])
            if edge not in undirected_edges:
                undirected_edges.append(edge)
    random.shuffle(undirected_edges)
    orient_state = []
    orient_history = []
    dag = deepcopy(cpdag)
    index = 0
    while len(undirected_edges):
        edge = undirected_edges[index]
        sin_flag_temp, sin_direction_temp = sin_path_check(dag, edge[0], edge[1])
        v_flag_temp, v_direction_temp = v_check(dag, edge[0], edge[1])
        dag[edge[0]]['nei'].remove(edge[1])
        dag[edge[1]]['nei'].remove(edge[0])
        if (not sin_flag_temp) & (not v_flag_temp):
            orient_history.append(random.randint(0, 1))
            if orient_history[-1] == 0:
                dag[edge[0]]['par'].append(edge[1])
            else:
                dag[edge[1]]['par'].append(edge[0])
            orient_state.append(0)
            index += 1
        elif sin_flag_temp & (not v_flag_temp):
            dag[sin_direction_temp[1]]['par'].append(sin_direction_temp[0])
            if sin_direction_temp[1] == edge[0]:
                orient_history.append(0)
            else:
                orient_history.append(1)
            orient_state.append(1)
            index += 1
        elif (not sin_flag_temp) & v_flag_temp & (v_direction_temp != 'both'):
            dag[v_direction_temp[1]]['par'].append(v_direction_temp[0])
            if v_direction_temp[1] == edge[0]:
                orient_history.append(0)
            else:
                orient_history.append(1)
            orient_state.append(1)
            index += 1
        elif sin_flag_temp & v_flag_temp & (v_direction_temp == sin_direction_temp):
            dag[v_direction_temp[1]]['par'].append(v_direction_temp[0])
            if v_direction_temp[1] == edge[0]:
                orient_history.append(0)
            else:
                orient_history.append(1)
            orient_state.append(1)
            index += 1
        else:
            if 0 in orient_state[::-1]:
                last = len(orient_state) - 1 - orient_state[::-1].index(0)
                dag = deepcopy(cpdag)
                orient_history_temp = []
                for i in range(last):
                    edge = undirected_edges[i]
                    dag[edge[0]]['nei'].remove(edge[1])
                    dag[edge[1]]['nei'].remove(edge[0])
                    if orient_history[i] == 0:
                        dag[edge[0]]['par'].append(edge[1])
                    else:
                        dag[edge[1]]['par'].append(edge[0])
                    orient_history_temp.append(orient_history[i])
                edge = undirected_edges[last]
                dag[edge[0]]['nei'].remove(edge[1])
                dag[edge[1]]['nei'].remove(edge[0])
                if orient_history[last] == 0:
                    dag[edge[1]]['par'].append(edge[0])
                    orient_history_temp.append(1)
                else:
                    dag[edge[0]]['par'].append(edge[1])
                    orient_history_temp.append(0)
                index = last + 1
                orient_state = orient_state[: last + 1]
                orient_state[last] = 1
                orient_history = deepcopy(orient_history_temp)
            else:
                orient_history.append(random.randint(0, 1))
                if orient_history[-1] == 0:
                    dag[edge[0]]['par'].append(edge[1])
                else:
                    dag[edge[1]]['par'].append(edge[0])
                orient_state.append(0)
                index += 1

        if index == len(undirected_edges):
            break
    return dag


# single direction path check
def sin_path_check(dag, var1, var2):
    sin_flag = False
    sin_direction = None
    # check single direction path var1 -> ... -> var2
    unchecked = deepcopy(dag[var2]['par'])
    checked = []
    while unchecked:
        if sin_flag:
            break
        unchecked_copy = deepcopy(unchecked)
        for dag_par in unchecked_copy:
            if var1 in dag[dag_par]['par']:
                sin_flag = True
                sin_direction = [var1, var2]
                break
            else:
                for key in dag[dag_par]['par']:
                    if key not in checked:
                        unchecked.append(key)
            unchecked.remove(dag_par)
            checked.append(dag_par)

    # check single direction path var2 -> ... -> var1
    if not sin_flag:
        unchecked = deepcopy(dag[var1]['par'])
        checked = []
        while unchecked:
            if sin_flag:
                break
            unchecked_copy = deepcopy(unchecked)
            for dag_par in unchecked_copy:
                if var2 in dag[dag_par]['par']:
                    sin_flag = True
                    sin_direction = [var2, var1]
                    break
                else:
                    for key in dag[dag_par]['par']:
                        if key not in checked:
                            unchecked.append(key)
                unchecked.remove(dag_par)
                checked.append(dag_par)
    return sin_flag, sin_direction


# v-structure check
def v_check(dag, var1, var2):
    v_flag1 = False
    v_flag2 = False
    if len(dag[var1]['par']):
        for par in dag[var1]['par']:
            if (var2 not in dag[par]['nei']) and (var2 not in dag[par]['par']) and (par not in dag[var2]['par']):
                v_flag1 = True
                break
    if len(dag[var2]['par']):
        for par in dag[var2]['par']:
            if (var1 not in dag[par]['nei']) & (var1 not in dag[par]['par']) & (par not in dag[var1]['par']):
                v_flag2 = True
                break
    if v_flag1 & (not v_flag2):
        return v_flag1, [var1, var2]
    elif (not v_flag1) & v_flag2:
        return v_flag2, [var2, var1]
    elif v_flag1 & v_flag2:
        return True, 'both'
    else:
        return False, None


# statistical G2 test
def g_test(data, cols, weights=None):
    '''
    :param data: the unique datapoints as a 2-d array, each row is a datapoint, assumed unique
    :param arities: the arities of the variables (=columns) for the contingency table order must match that of `cols`.
    :param cols: the columns (=variables) for the marginal contingency table. columns must be ordered low to high

    :returns : p value
    '''
    arities = np.amax(data, axis=0) + 1
    G, dof = g_counter(data, arities, np.array(cols), weights=weights)
    return chi2.sf(G, dof)


@njit(fastmath=True)
def g_counter(data, arities, cols, weights=None):
    if weights is None:
        weights = np.ones(len(data))
    strides = np.empty(len(cols), dtype=np.uint32)
    idx = len(cols) - 1
    stride = 1
    while idx > -1:
        strides[idx] = stride
        stride *= arities[cols[idx]]
        idx -= 1
    N_ijk = np.zeros(stride)
    N_ik = np.zeros(stride)
    N_jk = np.zeros(stride)
    N_k = np.zeros(stride)
    for rowidx in range(data.shape[0]):
        idx_ijk = 0
        idx_ik = 0
        idx_jk = 0
        idx_k = 0
        for i in range(len(cols)):
            idx_ijk += data[rowidx, cols[i]] * strides[i]
            if i != 0:
                idx_jk += data[rowidx, cols[i]] * strides[i]
            if i != 1:
                idx_ik += data[rowidx, cols[i]] * strides[i]
            if (i != 0) & (i != 1):
                idx_k += data[rowidx, cols[i]] * strides[i]
        N_ijk[idx_ijk] += weights[rowidx]
        for j in range(arities[cols[1]]):
            N_ik[idx_ik + j * strides[1]] += weights[rowidx]
        for i in range(arities[cols[0]]):
            N_jk[idx_jk + i * strides[0]] += weights[rowidx]
        for i in range(arities[cols[0]]):
            for j in range(arities[cols[1]]):
                N_k[idx_k + i * strides[0] + j * strides[1]] += weights[rowidx]
    G = 0
    for i in range(stride):
        if N_ijk[i] != 0:
            G += 2 * N_ijk[i] * np.log(N_ijk[i] * N_k[i] / N_ik[i] / N_jk[i])
    dof = (arities[cols[0]] - 1) * (arities[cols[1]] - 1) * strides[1]
    return G, dof


# statistical fisher's z test
def z_test(data, varnames, cols):
    data = pandas.DataFrame(data, columns=varnames)
    if len(cols) == 2:
        return pg.partial_corr(data, varnames[cols[0]], varnames[cols[1]])['p-val'][0]
    elif len(cols) > 2:
        return pg.partial_corr(data, varnames[cols[0]], varnames[cols[1]], [varnames[i] for i in cols[2:]])['p-val'][0]
    else:
        raise Exception('Length of input cols is less than 2')


# plot the bnlearn DAG
def plot(dag, filename):
    if type(dag) is not dict:
        dag = from_bnlearn(dag)
    dot = Digraph()
    for node in dag:
        dot.node(node)
        for parent in dag[node]['par']:
            if parent not in dot.body:
                dot.node(parent)
            dot.edge(parent, node)
    dot.render(filename, view=True)


# random orient a PDAG to a DAG
def pdag2dag(pdag):
    pdag_dc = deepcopy(pdag)
    dag = {var: {'par': [] + pdag[var]['par'], 'nei': []} for var in pdag}

    while pdag_dc:
        pdag_length = len(pdag_dc)
        for var in list(pdag_dc.keys()):
            if all(var not in pdag_dc[x]['par'] for x in pdag_dc):
                if pdag_dc[var]['nei']:
                    if pdag_check(pdag_dc, var):
                        for nei in pdag_dc[var]['nei']:
                            dag[var]['par'].append(nei)
                            pdag_dc[nei]['nei'].remove(var)
                        pdag_dc.pop(var)
                else:
                    pdag_dc.pop(var)
        if len(pdag_dc) == pdag_length:
            return None
    return dag


# check function used for pdag2dag
def pdag_check(pdag, x):
    for y in pdag[x]['nei']:
        x_adj = [v for v in pdag if v in set().union(*pdag[x].values()) or x in pdag[v]['par']]
        x_adj.remove(y)
        for x_a in x_adj:
            if y not in set().union(*pdag[x_a].values()) and x_a not in pdag[y]['par']:
                return False
    return True


# convert DAG into CPDAG
def dag2cpdag(dag):
    # initialise CPDAG
    cpdag = {var: {'par': [], 'nei': [v for v in dag[var]['nei']]} for var in dag}
    # remain all unshielded colliders
    for var in dag:
        if len(dag[var]['par']) > 1:
            par_adj = {par: [par] + dag[par]['par'] + dag[par]['nei'] + [v for v in dag if par in dag[v]['par']] for par
                       in dag[var]['par']}
            check_list = [val for lst in par_adj.values() for val in lst]
            for par in dag[var]['par']:
                if check_list.count(par) < len(dag[var]['par']):
                    cpdag[var]['par'].append(par)
                else:
                    if par not in cpdag[var]['nei']:
                        cpdag[var]['nei'].append(par)
                    if var not in cpdag[par]['nei']:
                        cpdag[par]['nei'].append(var)
        elif len(dag[var]['par']) == 1:
            par = dag[var]['par'][0]
            if par not in cpdag[var]['nei']:
                cpdag[var]['nei'].append(par)
            if var not in cpdag[par]['nei']:
                cpdag[par]['nei'].append(var)
    while True:
        stop_flag = True
        for var in dag:
            for nei in cpdag[var]['nei']:
                # Meek's Rule 1
                if len(cpdag[var]['par']) > 0:
                    par_adj = {par: dag[par]['par'] + dag[par]['nei'] + [v for v in dag if par in dag[v]['par']]
                               for par in cpdag[var]['par']}
                    check_list = [val for lst in par_adj.values() for val in lst]
                    if check_list.count(nei) < len(cpdag[var]['par']):
                        cpdag[nei]['par'].append(var)
                        cpdag[var]['nei'].remove(nei)
                        cpdag[nei]['nei'].remove(var)
                        stop_flag = False
                        break
                # Meek's Rule 2
                if len(cpdag[nei]['par']) > 0:
                    # check directed path var -> ... -> nei
                    dir_flag = False
                    unchecked = deepcopy(cpdag[nei]['par'])
                    checked = []
                    while unchecked:
                        if dir_flag:
                            break
                        unchecked_copy = deepcopy(unchecked)
                        for dag_par in unchecked_copy:
                            if var in cpdag[dag_par]['par']:
                                dir_flag = True
                                break
                            else:
                                for key in cpdag[dag_par]['par']:
                                    if key not in checked:
                                        unchecked.append(key)
                            unchecked.remove(dag_par)
                            checked.append(dag_par)
                    if dir_flag:
                        cpdag[var]['nei'].remove(nei)
                        cpdag[nei]['nei'].remove(var)
                        cpdag[nei]['par'].append(var)
                        stop_flag = False
                        break
                # Meek's Rule 3
                if len(cpdag[nei]['par']) > 1:
                    for par_pair in combinations(cpdag[nei]['par'], 2):
                        p1 = par_pair[0]
                        p2 = par_pair[1]
                        if p1 not in cpdag[p2]['par'] + cpdag[p2]['nei'] and p2 not in cpdag[p1]['par']:
                            if var in cpdag[p1]['nei'] and var in cpdag[p2]['nei']:
                                cpdag[var]['nei'].remove(nei)
                                cpdag[nei]['nei'].remove(var)
                                cpdag[nei]['par'].append(var)
                                stop_flag = False
                                break
                # Meek's Rule 4
                if len(cpdag[nei]['par']) > 0 and len(cpdag[var]['nei']) > 2:
                    for par_nei in cpdag[nei]['par']:
                        if par_nei in cpdag[var]['nei'] and len(cpdag[par_nei]['par']) > 0:
                            for par_par_nei in cpdag[par_nei]['par']:
                                if par_par_nei in cpdag[var]['nei']:
                                    cpdag[var]['nei'].remove(nei)
                                    cpdag[nei]['nei'].remove(var)
                                    cpdag[nei]['par'].append(var)
                                    stop_flag = False
                                    break
                        if not stop_flag:
                            break
            if not stop_flag:
                break
        if stop_flag:
            return cpdag


# statistical test
def independence_test(data, cols, varnames=None, weights=None, test='g-test', threshold=0.05):
    '''
    :param data: the unique datapoints as a 2-d array, each row is a datapoint, assumed unique
    :param cols: the columns (=variables) for the marginal contingency table. columns must be ordered low to high
    :param test: the name of test
    :param threshold: the threshold for G-test

    :returns 1st element: test result
    :returns 2nd element: test score
    '''
    if test == 'g-test':
        p = g_test(data, cols, weights)
    elif test == 'z-test':
        p = z_test(data, varnames, cols)
    else:
        raise Exception('Undefined test function.')
    return p > threshold, p


# orient v-structrues
def orient_v_structure(data, varnames, pc, sepset, test, threshold=0.05):
    dag = {}
    v_candidate = {}
    for var in pc:
        dag[var] = {}
        dag[var]['par'] = []
        dag[var]['nei'] = [v for v in pc[var]]
        if len(pc[var]) > 1:
            pc_copy = [v for v in pc[var]]
            for var1 in pc_copy:
                for var2 in pc_copy[pc_copy.index(var1) + 1:]:
                    if var2 in sepset[var1]:
                        if var not in sepset[var1][var2]:
                            cols = np.array([varnames.index(v) for v in [var1, var2] + list(sepset[var1][var2])])
                            v_candidate[tuple([var, var1, var2])] = \
                                independence_test(data, cols, varnames=varnames, test=test, threshold=threshold)[1]
    while len(v_candidate):
        pair = min(v_candidate, key=v_candidate.get)
        if (pair[0] not in dag[pair[1]]['par']) & (pair[0] not in dag[pair[2]]['par']):
            if (sin_path_check(dag, pair[0], pair[1])[1] != [pair[0], pair[1]]) & \
                    (sin_path_check(dag, pair[0], pair[2])[1] != [pair[0], pair[2]]):
                if pair[1] in dag[pair[0]]['nei']:
                    dag[pair[0]]['par'].append(pair[1])
                    dag[pair[0]]['nei'].remove(pair[1])
                    dag[pair[1]]['nei'].remove(pair[0])
                if pair[2] in dag[pair[0]]['nei']:
                    dag[pair[0]]['par'].append(pair[2])
                    dag[pair[0]]['nei'].remove(pair[2])
                    dag[pair[2]]['nei'].remove(pair[0])
        del v_candidate[pair]
    return dag


# orientation propagation
def orient_propagation(dag):
    while True:
        dag_check = {var: {'par': [v for v in dag[var]['par']], 'nei': [v for v in dag[var]['nei']]} for var in dag}
        # check cycles
        for var in dag:
            if len(dag_check[var]['nei']):
                nei_set = [v for v in dag_check[var]['nei']]
                for nei in nei_set:
                    sin_flag, sin_direction = sin_path_check(dag, var, nei)
                    v_flag, v_direction = v_check(dag_check, var, nei)
                    if sin_flag:
                        if (not v_flag) | (sin_direction == v_direction):
                            if sin_direction[0] not in dag[sin_direction[1]]['par']:
                                dag[sin_direction[1]]['par'].append(sin_direction[0])
                            if sin_direction[0] in dag[sin_direction[1]]['nei']:
                                dag[sin_direction[1]]['nei'].remove(sin_direction[0])
                                dag[sin_direction[0]]['nei'].remove(sin_direction[1])
        # check v-structures
        for var in dag:
            if len(dag_check[var]['nei']):
                nei_set = [v for v in dag_check[var]['nei']]
                for nei in nei_set:
                    sin_flag, sin_direction = sin_path_check(dag, var, nei)
                    v_flag, v_direction = v_check(dag_check, var, nei)
                    if v_flag & (v_direction != 'both'):
                        if (not sin_flag) | (sin_direction == v_direction):
                            if v_direction[0] not in dag[v_direction[1]]['par']:
                                dag[v_direction[1]]['par'].append(v_direction[0])
                            if v_direction[0] in dag[v_direction[1]]['nei']:
                                dag[v_direction[1]]['nei'].remove(v_direction[0])
                                dag[v_direction[0]]['nei'].remove(v_direction[1])

        # check Meek's rule 3
        for var in dag:
            if len(dag_check[var]['nei']):
                nei_set = [v for v in dag_check[var]['nei']]
                for nei in nei_set:
                    if (not sin_path_check(dag_check, var, nei)[0]) & (not v_check(dag_check, var, nei)[0]):
                        common_var = list(set(dag[nei]['par']).intersection(dag[var]['nei']))
                        if len(common_var) > 1:
                            flag = False
                            for var1 in common_var:
                                common_var_remain = deepcopy(common_var)
                                common_var_remain.remove(var1)
                                for var2 in common_var_remain:
                                    if (var1 not in (dag[var2]['par'] + dag[var2]['nei'])) & (
                                            var2 not in dag[var1]['par']):
                                        flag = True
                                        dag[var]['nei'].remove(nei)
                                        dag[nei]['nei'].remove(var)
                                        dag[nei]['par'].append(var)
                                        break
                                if flag:
                                    break
        if dag_check == dag:
            break
    return dag


# get the adjacent variables of a certain node in a graph
def adjacent(graph, var):
    return graph[var]['par'] + graph[var]['nei'] + [v for v in graph if var in graph[v]['par']]
