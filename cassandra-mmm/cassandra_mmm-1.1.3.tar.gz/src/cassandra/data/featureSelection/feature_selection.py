import numpy as np

#' Automatic function for the extraction of categorical variables
def categorical_columns(df):
    cat_vars = []
    for x in df.columns:
        values = list(df[x].value_counts().index)
        if values in [[0, 1], [1], [True, False], [True]]:
            cat_vars.append(x)

    return cat_vars

#' Automatic function for the extraction of numerical variables
def numerical_columns(df):
    return list(df.select_dtypes(include=[np.number]).columns.values)