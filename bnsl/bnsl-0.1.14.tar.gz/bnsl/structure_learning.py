import itertools
import time
from itertools import chain, combinations

import numpy as np
import pandas

pandas.options.mode.chained_assignment = None
from .accessory import g_test, z_test, find_causes, pairwise, dag2cpdag, independence_test, orient_v_structure, \
    orient_propagation, to_bnlearn
from .score import local_score


def pre_process(data):
    '''
    preprocess the original input data to remove unused states and single state columns
    :param data: input data in pandas dataframe format
    :return: prunned data and list of single value columns
    '''
    # remove unused states
    if all(data[var].dtype.name == 'category' for var in data):
        for var in list(data):
            data.loc[:, var] = data[var].cat.remove_unused_categories()
        # data = pandas.DataFrame(data.to_numpy(), columns=list(data.columns), dtype='category')
    # remove single value columns
    dc = data.nunique() == 1
    dc = dc[dc].index.values
    data = data.drop(dc, axis=1)
    return data, dc


def post_process(graph, dc):
    '''
    postprocess the learned graph to add those single value variables
    :param graph: learned graph
    :param dc: list of single value columns
    :return: expanded graph
    '''
    for node in dc:
        graph[node] = {'par': [], 'nei': []}
    return graph


def check_cycle(vi, vj, dag):
    # whether adding or orientating edge vi->vj would cause cycle. In other words, this function check whether there is a direct path from vj to vi except the possible edge vi<-vj
    underchecked = [x for x in dag[vi]['par'] if x != vj]
    checked = []
    cyc_flag = False
    while underchecked:
        if cyc_flag:
            break
        underchecked_copy = list(underchecked)
        for vk in underchecked_copy:
            if dag[vk]['par']:
                if vj in dag[vk]['par']:
                    cyc_flag = True
                    break
                else:
                    for key in dag[vk]['par']:
                        if key not in checked + underchecked:
                            underchecked.append(key)
            underchecked.remove(vk)
            checked.append(vk)
    return cyc_flag


def hc(data, method='standard', score_function='default', alpha=0.3, debug=False):
    '''
        :param data: the training data used for learn BN
        :param method: the method for dealing with missing values, including:
                       lw (listwise deletion)
                       pw (pairwise deletion)
                       ipw (inverse probability weighting)
                       aipw (adaptive ipw)
                       standard (standard HC)
        :param score_function: score function, including:
                       bic (Bayesian Information Criterion for discrete variable)
                       nal (Node Average Likelihood for discrete variable)
        :return: the learned BN
    '''
    if score_function == 'default':
        if all(data[var].dtype.name == 'category' for var in data):
            score_function = 'bic'
        elif all(data[var].dtype.name != 'category' for var in data):
            score_function = 'bic_g'
        else:
            raise Exception('Mixed type of data is not supported yet.')
    data, dc = pre_process(data)
    if method == 'lw':
        data_listwise = data.dropna()
        dag = hc(data_listwise, score_function=score_function, debug=debug)
    elif method == 'pw' or method == 'ipw' or method == 'aipw':
        # calculate the run time
        time_total = time.time()
        time_checkcycle = 0
        time_score = 0
        time_delete = 0
        # initialize the candidate set for each variable
        candidate = {}
        dag = {}
        # store the computed scores
        cache_score = {}
        cache_data = {}
        cache_weight = {}
        start_time = time.time()
        varnames = data.columns.tolist()
        if method == 'pw':
            cause_list = data.columns[data.isnull().any()].tolist()
        else:
            cause_list = find_causes(data)
        if all(data[var].dtype.name == 'category' for var in data):
            data = data.apply(lambda x: x.cat.codes).to_numpy()
        elif all(data[var].dtype.name != 'category' for var in data):
            data = data.to_numpy()
        else:
            raise Exception('Mixed data is not supported.')
        for var in varnames:
            candidate[var] = list(varnames)
            candidate[var].remove(var)
            dag[var] = {}
            dag[var]['par'] = []
            dag[var]['nei'] = []
            cache_score[var] = {}
        time_preprocess = time.time() - start_time

        diff = 1
        cache_dag = [{var: {'par': [v for v in dag[var]['par']], 'nei': [v for v in dag[var]['nei']]} for var in dag}]
        while diff > 0:
            diff = 0
            edge_candidate = []
            for vi in varnames:
                # attempt to add edges vi->vj
                for vj in candidate[vi]:
                    # calculate the time for checking cycles
                    start_time = time.time()
                    cyc_flag = check_cycle(vi, vj, dag)
                    time_checkcycle += time.time() - start_time
                    dag[vj]['par'] = sorted(dag[vj]['par'] + [vi])
                    if not cyc_flag and dag not in cache_dag:
                        dag[vj]['par'].remove(vi)
                        # perform pairwise deletion based on variables with different parents
                        start_time = time.time()
                        vars = [vi] + dag[vj]['par'] + [vj]
                        cache_data, cache_weight, W = pairwise(data, varnames, vars, cause_list, cache_data,
                                                               cache_weight, method)
                        time_delete += time.time() - start_time
                        # calculate the time for computing the score
                        start_time = time.time()
                        # compute the local score for the current graph
                        par_cur = tuple(dag[vj]['par'])
                        if par_cur not in cache_score[vj]:
                            cache_score[vj][par_cur] = {}
                        if W not in cache_score[vj][par_cur]:
                            cols = [varnames.index(vj)] + [varnames.index(x) for x in varnames if x in par_cur]
                            cache_score[vj][par_cur][W] = local_score(cache_data[W], cols, score_function,
                                                                      cache_weight[W], alpha=alpha)
                        # compute the local score for the searching graph
                        par_sea = tuple(sorted(dag[vj]['par'] + [vi]))
                        if par_sea not in cache_score[vj]:
                            cache_score[vj][par_sea] = {}
                        if W not in cache_score[vj][par_sea]:
                            cols = [varnames.index(vj)] + [varnames.index(x) for x in varnames if x in par_sea]
                            cache_score[vj][par_sea][W] = local_score(cache_data[W], cols, score_function,
                                                                      cache_weight[W], alpha=alpha)
                        if cache_score[vj][par_sea][W] != np.nan:
                            diff_temp = cache_score[vj][par_sea][W] - cache_score[vj][par_cur][W]
                            if debug:
                                print(vi, vj, diff_temp, 'a')
                            if diff_temp - diff > 1e-10:
                                diff = diff_temp
                                edge_candidate = [vi, vj, 'a']
                        time_score += time.time() - start_time
                    else:
                        dag[vj]['par'].remove(vi)
                parents = list(dag[vi]['par'])
                for par_vi in parents:
                    # attempt to reverse edges from vi<-par_vi to vi->par_vi
                    # calculate the time for checking cycles
                    start_time = time.time()
                    cyc_flag = check_cycle(vi, par_vi, dag)
                    time_checkcycle += time.time() - start_time
                    dag[vi]['par'].remove(par_vi)
                    dag[par_vi]['par'] = sorted(dag[par_vi]['par'] + [vi])
                    if not cyc_flag and dag not in cache_dag:
                        dag[vi]['par'] = sorted(dag[vi]['par'] + [par_vi])
                        dag[par_vi]['par'].remove(vi)
                        # do pairwise deletion on dataset based on variables with different parents
                        start_time = time.time()
                        vars = list(set([vi] + dag[vi]['par'] + [par_vi] + dag[par_vi]['par']))
                        cache_data, cache_weight, W = pairwise(data, varnames, vars, cause_list, cache_data,
                                                               cache_weight, method)
                        time_delete += time.time() - start_time
                        # calculate the time for computing the score
                        start_time = time.time()
                        # compute the local score for the current graph
                        par_cur_par_vi = tuple(dag[par_vi]['par'])
                        if par_cur_par_vi not in cache_score[par_vi]:
                            cache_score[par_vi][par_cur_par_vi] = {}
                        if W not in cache_score[par_vi][par_cur_par_vi]:
                            cols = [varnames.index(par_vi)] + [varnames.index(x) for x in varnames if
                                                               x in par_cur_par_vi]
                            cache_score[par_vi][par_cur_par_vi][W] = local_score(cache_data[W], cols, score_function,
                                                                                 cache_weight[W], alpha=alpha)
                        par_cur_vi = tuple(dag[vi]['par'])
                        if par_cur_vi not in cache_score[vi]:
                            cache_score[vi][par_cur_vi] = {}
                        if W not in cache_score[vi][par_cur_vi]:
                            cols = [varnames.index(vi)] + [varnames.index(x) for x in varnames if x in par_cur_vi]
                            cache_score[vi][par_cur_vi][W] = local_score(cache_data[W], cols, score_function,
                                                                         cache_weight[W], alpha=alpha)
                        # compute the local score for the searching graph
                        par_sea_par_vi = tuple(sorted(dag[par_vi]['par'] + [vi]))
                        if par_sea_par_vi not in cache_score[par_vi]:
                            cache_score[par_vi][par_sea_par_vi] = {}
                        if W not in cache_score[par_vi][par_sea_par_vi]:
                            cols = [varnames.index(par_vi)] + [varnames.index(x) for x in varnames if
                                                               x in par_sea_par_vi]
                            cache_score[par_vi][par_sea_par_vi][W] = local_score(cache_data[W], cols,
                                                                                 score_function, cache_weight[W],
                                                                                 alpha=alpha)
                        par_sea_vi = tuple([x for x in dag[vi]['par'] if x != par_vi])
                        if par_sea_vi not in cache_score[vi]:
                            cache_score[vi][par_sea_vi] = {}
                        if W not in cache_score[vi][par_sea_vi]:
                            cols = [varnames.index(vi)] + [varnames.index(x) for x in varnames if x in par_sea_vi]
                            cache_score[vi][par_sea_vi][W] = local_score(cache_data[W], cols, score_function,
                                                                         cache_weight[W], alpha=alpha)
                        if cache_score[vi][par_cur_vi][W] != np.nan and cache_score[par_vi][par_sea_par_vi][
                            W] != np.nan:
                            diff_temp = cache_score[vi][par_sea_vi][W] + cache_score[par_vi][par_sea_par_vi][W] - \
                                        cache_score[vi][par_cur_vi][W] - cache_score[par_vi][par_cur_par_vi][W]
                            if diff_temp - diff > 1e-10:
                                diff = diff_temp
                                edge_candidate = [vi, par_vi, 'r']
                            if debug:
                                print(vi, par_vi, diff_temp, 'r')
                        time_score += time.time() - start_time
                    else:
                        dag[vi]['par'] = sorted(dag[vi]['par'] + [par_vi])
                        dag[par_vi]['par'].remove(vi)
                    # attempt to delete edges vi<-par_vi
                    dag[vi]['par'].remove(par_vi)
                    if dag not in cache_dag:
                        dag[vi]['par'] = sorted(dag[vi]['par'] + [par_vi])
                        # do pairwise deletion on dataset based on variables with different parents
                        start_time = time.time()
                        vars = [vi] + dag[vi]['par']
                        cache_data, cache_weight, W = pairwise(data, varnames, vars, cause_list, cache_data,
                                                               cache_weight, method)
                        time_delete += time.time() - start_time
                        # calculate the time for computing the score
                        start_time = time.time()
                        # compute the local score for the current graph
                        par_cur = tuple(dag[vi]['par'])
                        if par_cur not in cache_score[vi]:
                            cache_score[vi][par_cur] = {}
                        if W not in cache_score[vi][par_cur]:
                            cols = [varnames.index(vi)] + [varnames.index(x) for x in varnames if x in par_cur]
                            cache_score[vi][par_cur][W] = local_score(cache_data[W], cols, score_function,
                                                                      cache_weight[W], alpha=alpha)
                        # compute the local score for the searching graph
                        par_sea = tuple([x for x in dag[vi]['par'] if x != par_vi])
                        if par_sea not in cache_score[vi]:
                            cache_score[vi][par_sea] = {}
                        if W not in cache_score[vi][par_sea]:
                            cols = [varnames.index(vi)] + [varnames.index(x) for x in varnames if x in par_sea]
                            cache_score[vi][par_sea][W] = local_score(cache_data[W], cols, score_function,
                                                                      cache_weight[W], alpha=alpha)
                        if cache_score[vi][par_cur][W] != np.nan:
                            diff_temp = cache_score[vi][par_sea][W] - cache_score[vi][par_cur][W]
                            if diff_temp - diff > 1e-10:
                                diff = diff_temp
                                edge_candidate = [par_vi, vi, 'd']
                            if debug:
                                print(par_vi, vi, diff_temp, 'd')
                        time_score += time.time() - start_time
                    else:
                        dag[vi]['par'] = sorted(dag[vi]['par'] + [par_vi])
            dag, candidate = dag_update(dag, edge_candidate, candidate, diff, debug)
            cache_dag.append(
                {var: {'par': [v for v in dag[var]['par']], 'nei': [v for v in dag[var]['nei']]} for var in dag})
        time_total = time.time() - time_total
        if debug:
            print('total cost: %.2f seconds' % time_total)
            print('preprocess cost: %.2f%%' % (time_preprocess / time_total * 100))
            print('check cycle cost: %.2f%%' % (time_checkcycle / time_total * 100))
            print('compute score cost: %.2f%%' % (time_score / time_total * 100))
            print('pairwise deletion cost: %.2f%%' % (time_delete / time_total * 100))
            print('others cost: %.2f%%' % (
                    (time_total - time_preprocess - time_checkcycle - time_score - time_delete) / time_total * 100))
    elif method == 'standard':
        # calculate the run time
        time_total = time.time()
        time_checkcycle = 0
        time_score = 0
        start_time = time.time()
        varnames = data.columns.tolist()
        if all(data[var].dtype.name == 'category' for var in data):
            data = data.apply(lambda x: x.cat.codes).to_numpy()
        elif all(data[var].dtype.name != 'category' for var in data):
            data = data.to_numpy()
        else:
            raise Exception('Mixed data is not supported.')
        # initialise dag, cached scores and candidate parents for each variable
        dag = {var: {'par': [], 'nei': []} for var in varnames}
        cache = {var: {tuple([]): local_score(data, [varnames.index(var)], score_function, alpha=alpha)} for var in
                 varnames}
        candidate = {var: [v for v in varnames if v is not var] for var in varnames}
        time_preprocess = time.time() - start_time
        diff = 1
        while diff > 0:
            diff = 0
            edge_candidate = []
            for vi in varnames:
                # attempt to add edges vi->vj
                for vj in candidate[vi]:
                    # calculate the time for checking cycles
                    start_time = time.time()
                    cyc_flag = check_cycle(vi, vj, dag)
                    time_checkcycle += time.time() - start_time
                    if not cyc_flag:
                        # calculate the time for computing the score
                        start_time = time.time()
                        par_sea = tuple(sorted(dag[vj]['par'] + [vi]))
                        if par_sea not in cache[vj]:
                            cols = [varnames.index(x) for x in (vj,) + par_sea]
                            cache[vj][par_sea] = local_score(data, cols, score_function, alpha=alpha)
                        time_score += time.time() - start_time
                        diff_temp = cache[vj][par_sea] - cache[vj][tuple(dag[vj]['par'])]
                        if debug:
                            print(vi, vj, diff_temp, 'a')
                        if diff_temp - diff > 1e-10:
                            diff = diff_temp
                            edge_candidate = [vi, vj, 'a']
                for par_vi in dag[vi]['par']:
                    # attempt to reverse edges from vi<-par_vi to vi->par_vi
                    # calculate the time for checking cycles
                    start_time = time.time()
                    cyc_flag = check_cycle(vi, par_vi, dag)
                    time_checkcycle += time.time() - start_time
                    if not cyc_flag:
                        # calculate the time for computing the score
                        start_time = time.time()
                        par_sea_par_vi = tuple(sorted(dag[par_vi]['par'] + [vi]))
                        if par_sea_par_vi not in cache[par_vi]:
                            cols = [varnames.index(x) for x in (par_vi,) + par_sea_par_vi]
                            cache[par_vi][par_sea_par_vi] = local_score(data, cols, score_function, alpha=alpha)
                        par_sea_vi = tuple([x for x in dag[vi]['par'] if x != par_vi])
                        if par_sea_vi not in cache[vi]:
                            cols = [varnames.index(x) for x in (vi,) + par_sea_vi]
                            cache[vi][par_sea_vi] = local_score(data, cols, score_function, alpha=alpha)
                        time_score += time.time() - start_time
                        diff_temp = cache[par_vi][par_sea_par_vi] + cache[vi][par_sea_vi] - cache[par_vi][
                            tuple(dag[par_vi]['par'])] - cache[vi][tuple(dag[vi]['par'])]
                        if diff_temp - diff > 1e-10:
                            diff = diff_temp
                            edge_candidate = [vi, par_vi, 'r']
                        if debug:
                            print(vi, par_vi, diff_temp, 'r')

                    # attempt to delete edges vi<-par_vi
                    # calculate the time for computing the score
                    start_time = time.time()
                    par_sea = tuple([x for x in dag[vi]['par'] if x != par_vi])
                    if par_sea not in cache[vi]:
                        cols = [varnames.index(x) for x in (vi,) + par_sea]
                        cache[vi][par_sea] = local_score(data, cols, score_function, alpha=alpha)
                    time_score += time.time() - start_time
                    diff_temp = cache[vi][par_sea] - cache[vi][tuple(dag[vi]['par'])]
                    if diff_temp - diff > 1e-10:
                        diff = diff_temp
                        edge_candidate = [par_vi, vi, 'd']
                    if debug:
                        print(par_vi, vi, diff_temp, 'd')
            dag, candidate = dag_update(dag, edge_candidate, candidate, diff, debug)
        time_total = time.time() - time_total
        if debug:
            print('total cost:', time_total, 'seconds')
            print('preprocess cost: %.2f%%' % (time_preprocess / time_total * 100))
            print('check cycle cost: %.2f%%' % (time_checkcycle / time_total * 100))
            print('compute score cost: %.2f%%' % (time_score / time_total * 100))
            print('others cost: %.2f%%' % (
                    (time_total - time_preprocess - time_checkcycle - time_score) / time_total * 100))
    else:
        raise Exception('The input method:' + method + 'is invalid.')
    return  post_process(dag, dc)


def pc_stable(data, test='default', threshold=0.05, debug=False):
    '''

    Args:
        data: original input data (in pandas dataframe format)
        test: statistical CI test (mutual information for categorical data and fisher's z test for continuous data)
        threshold: threshold for p-value
        debug: whether or not to output debug information

    Returns:

    '''
    if test == 'default':
        if all(data[var].dtype.name == 'category' for var in data):
            test = 'g-test'
        elif all(data[var].dtype.name != 'category' for var in data):
            test = 'z-test'
        else:
            raise Exception('Mixed type of data is not supported yet.')
    data, dc = pre_process(data)
    varnames = data.columns.tolist()
    if all(data[var].dtype.name == 'category' for var in data):
        data = data.apply(lambda x: x.cat.codes).to_numpy()
    elif all(data[var].dtype.name != 'category' for var in data):
        data = data.to_numpy()
    else:
        raise Exception('Mixed data is not supported.')
    # initialise pc set as full for all variables
    pc = {var: [v for v in varnames if v != var] for var in varnames}
    sepset = {var: {} for var in varnames}
    l = 0
    # find PC set for each variable
    while max({key: len(value) for key, value in pc.items()}.values()) > l:
        pc_copy = {var: [v for v in pc[var]] for var in pc}
        for var in varnames:
            for adj in pc_copy[var]:
                if adj not in sepset[var]:
                    pc_var = [v for v in pc_copy[var]]
                    pc_var.remove(adj)
                    for con in itertools.combinations(pc_var, l):
                        cols = np.array([varnames.index(v) for v in [var, adj] + list(con)])
                        test_result, p = independence_test(data, cols, test=test, varnames=varnames,
                                                           threshold=threshold)
                        if test_result:
                            if debug:
                                print(var + ' and ' + adj + ' are independent given ' + con + ', p value=' + p)
                            pc[var].remove(adj)
                            pc[adj].remove(var)
                            sepset[var][adj] = con
                            sepset[adj][var] = con
                            break
        l += 1
    # orient v-structrues
    cpdag = orient_v_structure(data, varnames, pc, sepset, test, threshold=threshold)
    # orientation propagation
    cpdag = orient_propagation(cpdag)
    # force undirected edges to be directed if its orientation causes either cycles or new v-structures (force them to form v-structures)
    cpdag = dag2cpdag(cpdag)
    return post_process(cpdag, dc)


# def h2pc(data, debug=False):
#     data, dc = pre_process(data)
#     dag = bnlearn.h2pc(data, debug=debug)
#     return post_process(dag, dc)


def ges(data, method='complete', score_function='default', prune=True, thres=0.1, alpha=0.3, debug=False):
    '''
    greedy equivalence search algorithm
    :param data: the training data used for learn BN
    :param method: the method for dealing with missing values, including:
                   lw (listwise deletion)
                   pw (pairwise deletion)
                   ipw (inverse probability weighting)
                   aipw (adaptive ipw)
                   complete (regular)
    :param score_function: score function, including:
                   bic (Bayesian Information Criterion for discrete variable)
                   bic_g (Bayesian Information Criterion for continuous variable)
                   nal (Node Average Likelihood for discrete variable)
    :param prune: when using pruning method, only edges between dependent variables will be considered
    :param thres: threshold for CI test used in pruning process
    :return: the learned CPDAG
    '''
    data, dc = pre_process(data)

    # calculate the run time
    time_total = time.time()
    varnames = data.columns.tolist()
    # initialize the cpdag, candidate parents and score function
    cpdag = {var: {'par': [], 'nei': []} for var in varnames}
    candidate = {var: [x for x in varnames if x != var] for var in varnames}
    if method == 'complete':
        if all(data[var].dtype.name == 'category' for var in data):
            datatype = 'category'
            data = data.apply(lambda x: x.cat.codes).to_numpy()
            if score_function == 'default':
                score_function = 'bic'
        elif all(data[var].dtype.name != 'category' for var in data):
            datatype = 'continuous'
            data = data.to_numpy()
            if score_function == 'default' or score_function == 'bic':
                score_function = 'bic_g'
            elif score_function == 'nal':
                score_function = 'nal_g'
        else:
            raise Exception('Mixed data is not supported.')
        cache = {var: {} for var in varnames}
        # initialize the candidate nodes for each variable to be connected with
        if prune:
            for i in range(len(varnames) - 1):
                for j in range(i + 1, len(varnames)):
                    cols = [i, j]
                    p = g_test(data, cols) if datatype == 'category' else z_test(data, varnames, cols)
                    if p > thres:
                        candidate[varnames[i]].remove(varnames[j])
                        candidate[varnames[j]].remove(varnames[i])
        # forward phase
        while True:
            diff = 0
            operator_candidate = []
            for x in varnames:
                for y in candidate[x]:
                    # do insert (var, can, T)
                    # ncnav means neighbour of can but not adjacent of var
                    ncnav = [v for v in cpdag[y]['nei'] if
                             v not in set().union(*cpdag[x].values()) and x not in cpdag[v]['par']]
                    for T in all_subsets(ncnav):
                        T = list(T)
                        if validity_test(cpdag, x, y, T, 'insert'):
                            # compute change in score
                            NA = [v for v in cpdag[y]['nei'] if
                                  v in set().union(*cpdag[x].values()) or x in cpdag[v]['par']]
                            parents_new = tuple(sorted(NA + T + cpdag[y]['par'] + [x]))
                            parents_cur = tuple(sorted(NA + T + cpdag[y]['par']))

                            if parents_new not in cache[y]:
                                cols = [varnames.index(v) for v in (y,) + parents_new]
                                cache[y][parents_new] = local_score(data, cols, score_function)
                            score_new = cache[y][parents_new]
                            if parents_cur not in cache[y]:
                                cols = [varnames.index(v) for v in (y,) + parents_cur]
                                cache[y][parents_cur] = local_score(data, cols, score_function)
                            score_cur = cache[y][parents_cur]
                            diff_temp = score_new - score_cur
                            if diff_temp > diff:
                                diff = diff_temp
                                operator_candidate = [x, y, T]
            if diff:
                # print(operator_candidate)
                cpdag[operator_candidate[1]]['par'].append(operator_candidate[0])
                candidate[operator_candidate[1]].remove(operator_candidate[0])
                candidate[operator_candidate[0]].remove(operator_candidate[1])
                for t in operator_candidate[2]:
                    cpdag[operator_candidate[1]]['par'].append(t)
                    cpdag[operator_candidate[1]]['nei'].remove(t)
                    cpdag[t]['nei'].remove(operator_candidate[1])
                cpdag = dag2cpdag(cpdag)
            else:
                break
        # backward phase
        while True:
            diff = 0
            operator_candidate = []
            for y in varnames:
                for x in set().union(*cpdag[y].values()):
                    # nvac means neighbours of var that are adjacent to can
                    nvac = [v for v in cpdag[y]['nei'] if v in set().union(*cpdag[x].values()) or x in cpdag[v]['par']]
                    for H in all_subsets(nvac):
                        H = list(H)
                        if validity_test(cpdag, x, y, H, 'delete'):
                            NA = [v for v in cpdag[y]['nei'] if
                                  v in set().union(*cpdag[x].values()) or x in cpdag[v]['par']]
                            NAwH = [v for v in NA if v not in H]
                            parents_new = NAwH + cpdag[y]['par']
                            if x in parents_new:
                                parents_new.remove(x)
                            parents_new = tuple(sorted(parents_new))
                            parents_cur = NAwH + cpdag[y]['par']
                            if x not in parents_cur:
                                parents_cur.append(x)
                            parents_cur = tuple(sorted(parents_cur))

                            if parents_new not in cache[y]:
                                cols = [varnames.index(v) for v in (y,) + parents_new]
                                cache[y][parents_new] = local_score(data, cols, score_function)
                            score_new = cache[y][parents_new]
                            if parents_cur not in cache[y]:
                                cols = [varnames.index(v) for v in (y,) + parents_cur]
                                cache[y][parents_cur] = local_score(data, cols, score_function)
                            score_cur = cache[y][parents_cur]
                            diff_temp = score_new - score_cur
                            if diff_temp > diff:
                                diff = diff_temp
                                operator_candidate = [x, y, H]
            if diff:
                if operator_candidate[0] in cpdag[operator_candidate[1]]['par']:
                    cpdag[operator_candidate[1]]['par'].remove(operator_candidate[0])
                else:
                    cpdag[operator_candidate[1]]['nei'].remove(operator_candidate[0])
                    cpdag[operator_candidate[0]]['nei'].remove(operator_candidate[1])
                for h in operator_candidate[2]:
                    cpdag[h]['nei'].remove(operator_candidate[1])
                    cpdag[operator_candidate[1]]['nei'].remove(h)
                    cpdag[h]['par'].append(operator_candidate[1])
                    if h in cpdag[operator_candidate[0]]['nei']:
                        cpdag[h]['nei'].remove(operator_candidate[0])
                        cpdag[operator_candidate[0]]['nei'].remove(h)
                        cpdag[h]['par'].append(operator_candidate[0])
                cpdag = dag2cpdag(cpdag)
            else:
                break
    elif method in ['pw', 'ipw', 'aipw']:
        cache_data = {}
        cache_weights = {}
        cache_score = {var: {} for var in varnames}
        cause_list = data.columns[data.isnull().any()].tolist() if method == 'pw' else find_causes(data)
        if all(data[var].dtype.name == 'category' for var in data):
            datatype = 'category'
            data = data.apply(lambda x: x.cat.codes).to_numpy()
            if score_function == 'default':
                score_function = 'bic'
        elif all(data[var].dtype.name != 'category' for var in data):
            datatype = 'continuous'
            data = data.to_numpy()
            if score_function == 'default' or score_function == 'bic':
                score_function = 'bic_g'
            elif score_function == 'nal':
                score_function = 'nal_g'
        else:
            raise Exception('Mixed data is not supported.')
        # initialize the candidate nodes for each variable to be connected with
        if prune:
            for i in range(len(varnames) - 1):
                for j in range(i + 1, len(varnames)):
                    cache_data, cache_weights, W = pairwise(data, varnames, [varnames[i], varnames[j]], cause_list,
                                                            cache_data, cache_weights, method)
                    if len(cache_data[W]) != 0:
                        cols = [i, j]
                        p = g_test(cache_data[W], cols, cache_weights[W]) if datatype == 'category' else z_test(
                            cache_data[W], varnames, cols)
                        if p > thres:
                            candidate[varnames[i]].remove(varnames[j])
                            candidate[varnames[j]].remove(varnames[i])
        # forward phase
        while True:
            diff = 0
            operator_candidate = []
            for x in varnames:
                for y in candidate[x]:
                    # do insert (var, can, T)
                    # ncnav means neighbour of can but not adjacent of var
                    ncnav = [v for v in cpdag[y]['nei'] if
                             v not in set().union(*cpdag[x].values()) and x not in cpdag[v]['par']]
                    for T in all_subsets(ncnav):
                        T = list(T)
                        if validity_test(cpdag, x, y, T, 'insert'):
                            # compute change in score
                            NA = [v for v in cpdag[y]['nei'] if
                                  v in set().union(*cpdag[x].values()) or x in cpdag[v]['par']]
                            parents_new = tuple(sorted(NA + T + cpdag[y]['par'] + [x]))
                            parents_cur = tuple(sorted(NA + T + cpdag[y]['par']))

                            cache_data, cache_weights, W = pairwise(data, varnames, (y,) + parents_new, cause_list,
                                                                    cache_data, cache_weights, method)
                            if W not in cache_score[y]:
                                cache_score[y][W] = {}
                            if parents_new not in cache_score[y][W]:
                                cols = [varnames.index(v) for v in (y,) + parents_new]
                                cache_score[y][W][parents_new] = local_score(cache_data[W], cols, score_function,
                                                                             weights=cache_weights[W], alpha=alpha)
                            score_new = cache_score[y][W][parents_new]

                            if parents_cur not in cache_score[y][W]:
                                cols = [varnames.index(v) for v in (y,) + parents_cur]
                                cache_score[y][W][parents_cur] = local_score(cache_data[W], cols, score_function,
                                                                             weights=cache_weights[W], alpha=alpha)
                            score_cur = cache_score[y][W][parents_cur]
                            diff_temp = score_new - score_cur
                            if diff_temp > diff:
                                diff = diff_temp
                                operator_candidate = [x, y, T]
            if diff:
                cpdag[operator_candidate[1]]['par'].append(operator_candidate[0])
                candidate[operator_candidate[1]].remove(operator_candidate[0])
                candidate[operator_candidate[0]].remove(operator_candidate[1])
                for t in operator_candidate[2]:
                    cpdag[operator_candidate[1]]['par'].append(t)
                    cpdag[operator_candidate[1]]['nei'].remove(t)
                    cpdag[t]['nei'].remove(operator_candidate[1])
                cpdag = dag2cpdag(cpdag)
            else:
                break
        # backward phase
        while True:
            diff = 0
            operator_candidate = []
            for y in varnames:
                for x in set().union(*cpdag[y].values()):
                    # nvac means neighbours of var that are adjacent to can
                    nvac = [v for v in cpdag[y]['nei'] if
                            v in set().union(*cpdag[x].values()) or x in cpdag[v]['par']]
                    for H in all_subsets(nvac):
                        H = list(H)
                        if validity_test(cpdag, x, y, H, 'delete'):
                            NA = [v for v in cpdag[y]['nei'] if
                                  v in set().union(*cpdag[x].values()) or x in cpdag[v]['par']]
                            NAwH = [v for v in NA if v not in H]
                            parents_new = NAwH + cpdag[y]['par']
                            if x in parents_new:
                                parents_new.remove(x)
                            parents_new = tuple(sorted(parents_new))
                            parents_cur = NAwH + cpdag[y]['par']
                            if x not in parents_cur:
                                parents_cur.append(x)
                            parents_cur = tuple(sorted(parents_cur))

                            cache_data, cache_weights, W = pairwise(data, varnames, (y,) + parents_cur, cause_list,
                                                                    cache_data, cache_weights, method)
                            if W not in cache_score[y]:
                                cache_score[y][W] = {}
                            if parents_new not in cache_score[y][W]:
                                cols = [varnames.index(v) for v in (y,) + parents_new]
                                cache_score[y][W][parents_new] = local_score(cache_data[W], cols, score_function,
                                                                             weights=cache_weights[W], alpha=alpha)
                            score_new = cache_score[y][W][parents_new]
                            if parents_cur not in cache_score[y][W]:
                                cols = [varnames.index(v) for v in (y,) + parents_cur]
                                cache_score[y][W][parents_cur] = local_score(cache_data[W], cols, score_function,
                                                                             weights=cache_weights[W], alpha=alpha)
                            score_cur = cache_score[y][W][parents_cur]
                            diff_temp = score_new - score_cur
                            if diff_temp > diff:
                                diff = diff_temp
                                operator_candidate = [x, y, H]
            if diff:
                if operator_candidate[0] in cpdag[operator_candidate[1]]['par']:
                    cpdag[operator_candidate[1]]['par'].remove(operator_candidate[0])
                else:
                    cpdag[operator_candidate[1]]['nei'].remove(operator_candidate[0])
                    cpdag[operator_candidate[0]]['nei'].remove(operator_candidate[1])
                for h in operator_candidate[2]:
                    cpdag[h]['nei'].remove(operator_candidate[1])
                    cpdag[operator_candidate[1]]['nei'].remove(h)
                    cpdag[h]['par'].append(operator_candidate[1])
                    if h in cpdag[operator_candidate[0]]['nei']:
                        cpdag[h]['nei'].remove(operator_candidate[0])
                        cpdag[operator_candidate[0]]['nei'].remove(h)
                        cpdag[h]['par'].append(operator_candidate[0])
                cpdag = dag2cpdag(cpdag)
            else:
                break
    time_total = time.time() - time_total
    if debug:
        print('total cost:', time_total, 'seconds')
        # print('compute score cost: %.2f%%' % (time_score / time_total * 100))
    return post_process(cpdag, dc)


def all_subsets(ss):
    return chain(*map(lambda x: combinations(ss, x), range(0, len(ss) + 1)))


def validity_test(cpdag, X, Y, Z, type):
    NA = [x for x in cpdag[Y]['nei'] if x in set().union(*cpdag[X].values()) or X in cpdag[x]['par']]
    if type == 'insert':
        NAZ = NA + Z
        if not clique_check(cpdag, NAZ):
            return False

        underchecked = list(set().union(*cpdag[X].values()))
        checked = []
        while underchecked:
            underchecked_copy = list(underchecked)
            for vk in underchecked_copy:
                if set().union(*cpdag[vk].values()):
                    if Y in set().union(*cpdag[vk].values()):
                        if vk not in NAZ:
                            return False
                    else:
                        for key in set().union(*cpdag[vk].values()):
                            if key not in checked + underchecked:
                                underchecked.append(key)
                underchecked.remove(vk)
                checked.append(vk)
        return True
    else:
        NAwZ = [x for x in NA if x not in Z]
        return clique_check(cpdag, NAwZ)


def clique_check(cpdag, vars):
    if len(vars) > 1:
        for i in range(len(vars)):
            for j in range(i + 1, len(vars)):
                if vars[i] not in set().union(*cpdag[vars[j]].values()) and vars[j] not in cpdag[vars[i]]['par']:
                    return False
    return True


def dag_update(dag, edge_candidate, candidate, diff, debug):
    '''
    Args:
        dag: current dag
        edge_candidate: best edge operation
        candidate: candidate parents for each variable
        diff: difference in score between the best seaching dag and the current dag
        debug: whether output debug information

    Returns:
        dag: updated dag
        candidate: updated candidate
    '''
    if edge_candidate:
        # print(edge_candidate, diff)
        if edge_candidate[-1] == 'a':
            dag[edge_candidate[1]]['par'] = sorted(dag[edge_candidate[1]]['par'] + [edge_candidate[0]])
            candidate[edge_candidate[0]].remove(edge_candidate[1])
            candidate[edge_candidate[1]].remove(edge_candidate[0])
        elif edge_candidate[-1] == 'r':
            dag[edge_candidate[1]]['par'] = sorted(dag[edge_candidate[1]]['par'] + [edge_candidate[0]])
            dag[edge_candidate[0]]['par'].remove(edge_candidate[1])
        elif edge_candidate[-1] == 'd':
            dag[edge_candidate[1]]['par'].remove(edge_candidate[0])
            candidate[edge_candidate[0]].append(edge_candidate[1])
            candidate[edge_candidate[1]].append(edge_candidate[0])
        if debug:
            print('best operation is:', edge_candidate, diff)
    return dag, candidate