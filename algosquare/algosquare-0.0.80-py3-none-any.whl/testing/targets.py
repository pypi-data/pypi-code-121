import numpy as np
import pandas as pd

def create_classification_target(index, n_cols, categories, seed = 0):
    def transform(x):
        if pd.isnull(x):
            return x
        return categories[x]

    rng = np.random.default_rng(seed = seed)
    return pd.DataFrame(rng.integers(0, len(categories), (len(index), n_cols)), index = index, columns = [f'T{i}' for i in range(n_cols)]).applymap(transform)


def create_regression_target(index, n_cols, seed = 0):
    rng = np.random.default_rng(seed = seed)
    return pd.DataFrame(rng.normal(size = (len(index), n_cols)) ** 2 + np.arange(1, n_cols+1), index = index, columns = [f'T{i}' for i in range(n_cols)])
