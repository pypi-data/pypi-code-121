from sklearn.model_selection import cross_val_score, GridSearchCV, RandomizedSearchCV
import pandas as pd
import statsmodels.api as sm

from itertools import product

from .model_validator import CustomTsCv
from .metrics import get_any_metric


class ParameterSearcher:
    """
        - todo: result in here will be used in research/reporting/shared, bad design, need to move to common!!!!
        - todo: copied from prob models but made some changes: bad design, need to be in common
        - todo: how to add custom metrics, such as bias and variance
        - todo: does not support multiple metrics cos of best model!!!
        - todo: doesnt have unit tests
    """

    def __init__(self):
        self.train_lengths_key = "train_lengths"
        self.test_lengths_key = "test_lengths"
        self.look_aheads_key = "look_aheads"
        self.train_shuffle_block_size = "train_shuffle_block_size"

    def search_params(self,
                      X: pd.DataFrame,
                      y: pd.DataFrame,
                      train_size: int,
                      test_size: int,
                      train_shuffle_block_size: int,
                      estimator,
                      param_grid: dict,
                      metrics,
                      is_get_best_model: bool,
                      return_train_score:bool):

        refit = False
        scoring = metrics
        if is_get_best_model:
            assert len(metrics) == 1
            scoring = metrics[0]
            refit = True

        obs_n = X.shape[0]

        cv = CustomTsCv(train_n=train_size,
                        test_n=test_size,
                        sample_n=obs_n,
                        train_shuffle_block_size=train_shuffle_block_size)

        grid = RandomizedSearchCV(estimator=estimator,
                                  param_distributions=param_grid,
                                  scoring=scoring,
                                  verbose=1,
                                  # n_jobs=-1,
                                  cv=cv,
                                  refit=refit,
                                  return_train_score=return_train_score)

        grid_result = grid.fit(X, y)

        cv_result = pd.DataFrame(grid_result.cv_results_)
        return cv_result, grid

    def run_parameter_search_multiple_cvs(self,
                                          X: pd.DataFrame,
                                          y: pd.DataFrame,
                                          estimator,
                                          param_grid,
                                          cv_params,
                                          metrics: list
                                          ):
        """
        :param X: x to pass to estimator
        :param y: target values
        :param estimator: estimator object. A object of that type is instantiated for each grid point
        :param param_grid: parameter dictionary to be passed to grid search
        :param metric: estimator One metrics (cos need to know best_estimator)
        :param cv_params: required for cross-validation,
                        - dictionary with "train_lengths", "test_lengths", "look_aheads" keys and values of arrays
                        - it searches for different train/test/lookaheads lengths
        :return: gridsearch cv_result + 3 columns for cv
        """

        grid_results = []
        # best_models = []

        scorers = get_any_metric(metrics=metrics)

        cv_params_grid = list(product(cv_params[self.train_lengths_key],
                                      cv_params[self.test_lengths_key],
                                      cv_params[self.look_aheads_key],
                                      cv_params[self.train_shuffle_block_size]
                                      ))

        # todo: wrong, no need for loop!!!!
        for train_size, test_size, look_ahead, train_shuffle_block_size in cv_params_grid:
            result, grid = self.search_params(X=X,
                                              y=y,
                                              train_size=train_size,
                                              test_size=test_size,
                                              train_shuffle_block_size=train_shuffle_block_size,
                                              # obs_n=obs_n,
                                              estimator=estimator,
                                              param_grid=param_grid,
                                              metrics=scorers,
                                              is_get_best_model=False,
                                              return_train_score=True
                                              )

            result[self.train_lengths_key] = train_size
            result[self.test_lengths_key] = test_size
            result[self.look_aheads_key] = look_ahead

            grid_results.append(result)

            # best_model = grid.best_estimator_
            # best_models.append(best_model)

        grid_results = pd.concat(grid_results).reset_index()
        _ = grid_results.pop("params")
        _ = grid_results.pop("index")

        # indx_max = grid_results["mean_test_score"].idxmax()
        # best_model_result = best_models[indx_max]

        return grid_results #, best_models
