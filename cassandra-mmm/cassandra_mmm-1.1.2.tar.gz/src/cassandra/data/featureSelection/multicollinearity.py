from IPython.core.display import display
from statsmodels.stats.outliers_influence import variance_inflation_factor
import pandas as pd


def check_multicollinearity(X):
    df = pd.DataFrame()
    df['feature'] = X.columns
    # calculating VIF for each feature
    df['VIF'] = [variance_inflation_factor(X.values, i) for i in range(len(X.columns))]
    display(df)
