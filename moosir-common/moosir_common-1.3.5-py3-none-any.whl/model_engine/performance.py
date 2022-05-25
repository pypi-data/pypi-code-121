
from sklearn.metrics import mean_squared_error, mean_absolute_error, explained_variance_score
from scipy.stats import spearmanr

from .models import *


class RegressionPerformanceManager(IPerformanceSender):

    def calculate_performance(self, model: IModel, true_values: pd.DataFrame, predictions: pd.DataFrame):
        ic = spearmanr(true_values, predictions)[0]
        mse = mean_squared_error(true_values, predictions)
        mae = mean_absolute_error(true_values, predictions)
        exp_var_train = explained_variance_score(true_values, predictions)

        return {"ic": ic, "mse": mse, "mae": mae, "exp_var_train": exp_var_train}
