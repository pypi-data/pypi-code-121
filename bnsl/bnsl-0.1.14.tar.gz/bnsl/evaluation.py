from .accessory import from_bnlearn, dag2cpdag


def shd(dag_true, dag_learned):
    '''
    :param dag_true: true CPDAG
    :param dag_learned: learned CPDAG
    :return: the separate SHD score of learned graph
    '''
    if type(dag_true) is str:
        dag_true = from_bnlearn(dag_true)
    elif type(dag_true) is not dict:
        raise Exception('The format of input true DAG is invalid.')
    if type(dag_learned) is str:
        dag_learned = from_bnlearn(dag_learned)
    elif type(dag_learned) is not dict:
        raise Exception('The format of input learned DAG is invalid.')
    cpdag_true = dag2cpdag(dag_true)
    cpdag_learned = dag2cpdag(dag_learned)
    add = 0
    remove = 0
    reorient = 0
    for key, value in cpdag_true.items():
        for par in value['par']:
            if par not in cpdag_learned[key]['par']:
                if par not in cpdag_learned[key]['nei'] and key not in cpdag_learned[par]['par']:
                    add += 1
                else:
                    reorient += 1
        for nei in value['nei']:
            if nei not in cpdag_learned[key]['nei']:
                if nei not in cpdag_learned[key]['par'] and key not in cpdag_learned[nei]['par']:
                    add += 0.5
                else:
                    reorient += 0.5
    for key, value in cpdag_learned.items():
        for par in value['par']:
            if (par not in cpdag_true[key]['par']) and (par not in cpdag_true[key]['nei']) and (
                    key not in cpdag_true[par]['par']):
                remove += 1
        for nei in value['nei']:
            if (nei not in cpdag_true[key]['nei']) and (nei not in cpdag_true[key]['par']) and (
                    key not in cpdag_true[nei]['par']):
                remove += 0.5
    return int(add + remove + reorient)


# evaluation methods
def compare(dag_true, dag_learned):
    '''
    :param dag_true: true DAG
    :param dag_learned: learned DAG
    :return: true positive, false positive and false negative of learned DAG based on the difference between the CPDAG of the learned and true DAG
    '''
    if type(dag_true) is str:
        dag_true = from_bnlearn(dag_true)
    elif type(dag_true) is not dict:
        raise Exception('The format of input true DAG is invalid.')
    if type(dag_learned) is str:
        dag_learned = from_bnlearn(dag_learned)
    elif type(dag_learned) is not dict:
        raise Exception('The format of input learned DAG is invalid.')
    cpdag_true = dag2cpdag(dag_true)
    cpdag_learned = dag2cpdag(dag_learned)
    tp = 0
    fp = 0
    fn = 0
    for var in cpdag_learned:
        for par in cpdag_learned[var]['par']:
            if par in cpdag_true[var]['par']:
                tp += 1
            else:
                fp += 1
        for nei in cpdag_learned[var]['nei']:
            if nei in cpdag_true[var]['nei']:
                tp += 0.5
            else:
                fp += 0.5
    for var in cpdag_true:
        for par in cpdag_true[var]['par']:
            if par not in cpdag_learned[var]['par']:
                fn += 1
        for nei in cpdag_true[var]['nei']:
            if nei not in cpdag_learned[var]['nei']:
                fn += 1
    return tp, fp, fn


# compute the F1 score of a learned graph given true graph
def f1(dag_true, dag_learned):
    '''
    :param dag_true: true DAG
    :param dag_learned: learned DAG
    :return: f1 score of learned DAG based on the difference between the CPDAG of the learned and true DAG
    '''
    tp, fp, fn = compare(dag_true, dag_learned)
    return tp * 2 / (tp * 2 + fp + fn)


# compute the precision of a learned graph given true graph
def precision(dag_true, dag_learned):
    '''
    :param dag_true: true DAG
    :param dag_learned: learned DAG
    :return: the precision score of learned DAG
    '''
    tp, fp, fn = compare(dag_true, dag_learned)
    return tp / (tp + fp)


# compute the recall of a learned graph given true graph
def recall(dag_true, dag_learned):
    '''
    :param dag_true: true DAG
    :param dag_learned: learned DAG
    :return: the recall score of learned DAG
    '''
    tp, fp, fn = compare(dag_true, dag_learned)
    return tp / (tp + fn)
