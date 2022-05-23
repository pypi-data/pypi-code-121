import os
import numpy as np
import pandas as pd

from kolibri.config import TaskType
from sklearn.model_selection._split import _BaseKFold
from copy import deepcopy
from sklearn.model_selection import KFold, StratifiedKFold, BaseCrossValidator

def construct_learner_name(fold, repeat, repeats):
    repeat_str = f"_repeat_{repeat}" if repeats > 1 else ""
    return f"learner_fold_{fold}{repeat_str}"


def intersect(d):
    result = set(d[0]).intersection(*d[1:])
    return result

def log10p(x, offset=100):
    print(offset)
    return np.log10(offset + x)

def is_tree(estimator):
    from sklearn.tree import BaseDecisionTree
    from sklearn.ensemble._forest import BaseForest

    if "final_estimator" in estimator.get_params():
        estimator = estimator.final_estimator
    if "base_estimator" in estimator.get_params():
        estimator = estimator.base_estimator
    if isinstance(estimator, BaseForest) or isinstance(estimator, BaseDecisionTree):
        return True

def get_cv_splitter(fold, default, seed: int, shuffle: bool, int_default: str = "kfold"):
    if not fold:
        return default
    if hasattr(fold, "split"):
        return fold
    if type(fold) is int:
        if default is not None:
            if isinstance(default, _BaseKFold) and fold <= 1:
                raise ValueError(
                    "k-fold cross-validation requires at least one"
                    " train/test split by setting n_splits=2 or more,"
                    f" got n_splits={fold}."
                )
            try:
                default_copy = deepcopy(default)
                default_copy.n_splits = fold
                return default_copy
            except:
                raise ValueError(f"Couldn't set 'n_splits' to {fold} for {default}.")
        else:
            fold_seed = seed if shuffle else None
            if int_default == "kfold":
                return KFold(fold, random_state=fold_seed, shuffle=shuffle)
            elif int_default == "stratifiedkfold":
                return StratifiedKFold(fold, random_state=fold_seed, shuffle=shuffle)
            else:
                raise ValueError(
                    "Wrong value for int_default param. Needs to be either 'kfold' or 'stratifiedkfold'."
                )
    raise TypeError(
        f"{fold} is of type {type(fold)} while it needs to be either a CV generator or int."
    )

def get_groups( groups, data = None, fold_groups=None):

    if groups is None:
        return fold_groups
    if isinstance(groups, str):
        if groups not in data.columns:
            raise ValueError(
                f"Column {groups} used for groups is not present in the dataset."
            )
        groups = data[groups]
    else:
        if groups.shape[0] != data.shape[0]:
            raise ValueError(
                f"groups has lenght {groups.shape[0]} which doesn't match X_train length of {len(data)}."
            )
    return groups


def is_unsupervised(ml_task):
    return ml_task == TaskType.CLUSTERING or ml_task == TaskType.ANOMALY_DETECTION


def get_target_type(target_ds):
    if not isinstance(target_ds, pd.Series):
        raise Exception("get_target_type function argument is not a pandas Series object")
    unique_values=list(target_ds.unique())
    if len(unique_values)==2:
        return "Binary Classes"
    elif len(unique_values)>2 and target_ds.dtype == 'object':
        return "Multi Classes"
    elif len(unique_values)<50 and target_ds.dtype in['int64', 'int32']:
        return "Multi Classes"
    elif len(unique_values)>=50 and not target_ds== 'object':
        return "Numrical"
    else:
        return "Unknown"
def is_multiclass(ml_task, y) -> bool:
    """
    Method to check if the problem is multiclass.
    """
    try:
        return ml_task == TaskType.CLASSIFICATION and y.value_counts().count() > 2
    except:
        return False

def is_int(x):
    """Check if x is of integer type, but not boolean"""
    # boolean are subclasses of integers in Python, so explicitly exclude them
    return isinstance(x, (int, np.integer)) and not isinstance(x, bool)


def is_float(x):
    """Check if x is of float type"""
    return isinstance(x, (float, np.floating))


def check_n_jobs(n_jobs):
    """Check `n_jobs` parameter according to the scikit-learn convention.

    Parameters
    ----------
    n_jobs : int, positive or -1
        The number of jobs for parallelization.

    Returns
    -------
    n_jobs : int
        Checked number of jobs.
    """
    # scikit-learn convention
    # https://scikit-learn.org/stable/glossary.html#term-n-jobs
    if n_jobs is None:
        return 1
    elif not is_int(n_jobs):
        raise ValueError(f"`n_jobs` must be None or an integer, but found: {n_jobs}")
    elif n_jobs < 0:
        return os.cpu_count() - n_jobs + 1
    else:
        return n_jobs


def infer_task_type(y):
    c1 = "int" in y.dtype.name
    c2 = y.nunique() <= 20
    c3 = y.dtype.name in ["object", "bool", "category"]

    if (c1 and c2) or c3:
        ml_task = TaskType.CLASSIFICATION
    else:
        ml_task = TaskType.REGRESSION

    if y.nunique() > 2 and ml_task != TaskType.REGRESSION:
        ml_task = TaskType.MULTI_TARGET_CLASSIFICATION
    else:
        ml_task = TaskType.BINARY_CLASSIFICATION
    return ml_task

def prepare_names_for_json(df):
    return df.columns.str.replace(r"[\,\}\{\]\[\:\"\']", "")

def learner_name_to_fold_repeat(name):
    fold, repeat = None, None
    arr = name.split("_")
    fold = int(arr[2])
    if "repeat" in name:
        repeat = int(arr[4])
    return fold, repeat


def get_fold_repeat_cnt(model_path):
    training_logs = [f for f in os.listdir(model_path) if "_training.log" in f]
    fold_cnt, repeat_cnt = 0, 0
    for fname in training_logs:
        fold, repeat = learner_name_to_fold_repeat(fname)
        if fold is not None:
            fold_cnt = max(fold_cnt, fold)
        if repeat is not None:
            repeat_cnt = max(repeat_cnt, repeat)

    fold_cnt += 1  # counting from 0
    repeat_cnt += 1

    return fold_cnt, repeat_cnt


def get_learners_names(model_path):
    postfix = "_training.log"
    learner_names = [
        f.repleace(postfix, "") for f in os.listdir(model_path) if postfix in f
    ]
    return learner_names


def estimate_weight(error):
    """
    to estimate weights for base estimators based on the error rates
    :param error: error rates
    :return:
    """
    if error < 0.0000001:
        error = 0.0000001
    if error == 1:
        error = 0.9999999
    return 0.5*np.log((1-error)/error)
