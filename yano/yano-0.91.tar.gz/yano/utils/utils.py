from sklearn.metrics import roc_auc_score
from copy import copy

from ..helper import seed_once
from ..stats import Stats


def run_algo_sklearn(algo, train, seed=42):
    algo=copy(algo)
    algo.random_state=seed
    algo.fit(train)
    return lambda x,model=algo: model.score_samples(x)

def run_algo_pyod(algo, train, seed=42):
    algo=copy(algo)
    algo.random_state=seed
    algo.fit(train)
    return lambda x,model=algo: model.decision_function(x)

@seed_once
def run_algo_callable(algo, train, *args, **kwargs):
    return algo(train,*args,**kwargs)





def run_algo(algo, train, *args,seed=42, **kwargs):
    if callable(algo):
        return run_algo_callable(algo, train, *args,seed=seed, **kwargs)
    if hasattr(algo, 'fit') and hasattr(algo, 'score_samples'):
        return run_algo_sklearn(algo, train, seed=seed)
    if hasattr(algo, 'fit') and hasattr(algo, 'decision_function'):
        return run_algo_pyod(algo, train, seed=seed)

def eval_func(func, test, testy, method="roc_auc"):
    if type(func) is list:
        preds=[]
        for f in func:
            preds.append(f(test))
        return Stats(pred)
    pred=func(test)
    if method=="roc_auc":
        return roc_auc_score(testy, pred)
    else:
        raise ValueError("Unknown method: {}".format(method))

def test_algo(algo, train, test, testy, *args, method="roc_auc",seed=42, **kwargs):
    func=run_algo(algo, train, *args,seed=seed, **kwargs)
    pred=func(test)
    return eval_func(func, test, testy)

def test_algo_n(algo, train, test, testy, *args, method="roc_auc", n=10, **kwargs):
    scores=[]
    for i in range(n):
        scores.append(test_algo(algo, train, test, testy, *args, method=method, seed=i, **kwargs))
    return Stats(scores)

def run_algo_folds(algo, folds, *args, seed=42, **kwargs):
    funcs=[]
    for x,tx,ty in folds:
        funcs.append(run_algo(algo, x, *args, seed=seed, **kwargs))
    return funcs

def run_algo_n(algo, train, *args, n=10, **kwargs):
    funcs=[]
    for i in range(n):
        funcs.append(run_algo(algo, train, *args, seed=i, **kwargs))
    return funcs









