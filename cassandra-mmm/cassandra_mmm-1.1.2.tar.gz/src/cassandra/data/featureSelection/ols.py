import statsmodels.api as sm
from IPython.core.display import display


def ols(X, y, constant=True):
    features = X.copy()

    if constant:
        features = sm.add_constant(features)

    model = sm.OLS(y, features)

    result = model.fit()
    display(result.summary())

    return result, model
