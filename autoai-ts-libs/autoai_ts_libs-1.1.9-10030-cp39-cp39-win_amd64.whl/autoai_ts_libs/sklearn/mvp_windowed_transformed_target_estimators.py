################################################################################
# IBM Confidential
# OCO Source Materials
# 5737-H76, 5725-W78, 5900-A1R
# (c) Copyright IBM Corp. 2020, 2022. All Rights Reserved.
# The source code for this program is not published or otherwise divested of its trade secrets,
# irrespective of what has been deposited with the U.S. Copyright Office.
################################################################################
from typing import Union, List

from autoai_ts_libs.sklearn.small_data_window_transformers import (
    SmallDataWindowTargetTransformer,
)
from autoai_ts_libs.sklearn.small_data_standard_row_mean_center_transformers import (
    WindowTransformerMTS,
)
from autoai_ts_libs.sklearn.small_data_standard_row_mean_center_transformers import (
    StandardRowMeanCenterMTS,
)
from autoai_ts_libs.utils.messages.messages import Messages
from sklearn.compose import TransformedTargetRegressor
from sklearn.impute import SimpleImputer
from sklearn.utils.validation import check_array
import numpy as np
from autoai_ts_libs.utils.messages.messages import Messages
import logging
LOGGER = logging.getLogger(__name__)


def get_future_exogenous_input(imputer: object, future_exogenous: Union[np.ndarray, None], X: np.ndarray, exogenous_indices: List, prediction_horizon: int ) -> np.ndarray:
    """Helper function to handle missing or incomplete future exogenous input

    Args:
        imputer (Object): Imputer object to impute any missing exogenous
        future_exogenous (Union[np.ndarray, None]): Any provided future exogenous, can be None. If provided, 
            it is assumed to have the proper number of columns. If it does not contain enough rows, rows are
            added to the end to match prediction length.
        X (np.ndarray): Available history of X, where X contains all the features provided during fit.
        exogenous_indices (List): Indices into X which indicate exogenous columns
        prediction_horizon (int): Prediction horizon

    Returns:
        ndarray: Future exogenous of size prediction horizon x number of exogenous
    """
    if future_exogenous is None:
        fut_exog = np.NaN*np.ones((prediction_horizon, len(exogenous_indices)))
    else:
        assert future_exogenous.shape[1] == len(exogenous_indices), "future_exogenous provided, but future_exogenous.shape[1] is incorrect"
        pad_len = prediction_horizon - future_exogenous.shape[0]
        if pad_len > 0:
            fut_exog = np.pad(future_exogenous, ((0, pad_len), (0, 0)), "constant", constant_values=np.NaN)
        else:
            fut_exog = future_exogenous[:prediction_horizon,:]

    fut_exog = imputer.transform( np.vstack((X[:,exogenous_indices],fut_exog )) )
    fut_exog = fut_exog[-prediction_horizon:,]

    return fut_exog

class AutoaiWindowTransformedTargetRegressor(TransformedTargetRegressor):
    """[summary]

    Args:
        feature_columns ([type], optional): [description]. Defaults to None.
        target_columns ([type], optional): [description]. Defaults to None.
        regressor ([type], optional): [description]. Defaults to None.
        lookback_window (int, optional): [description]. Defaults to 10.
        prediction_horizon (int, optional): [description]. Defaults to 1.
        scaling_func ([type], optional): [description]. Defaults to None.
        inverse_scaling_func ([type], optional): [description]. Defaults to None.
        check_inverse (bool, optional): [description]. Defaults to False.
        short_name (str, optional): [description]. Defaults to "".
        one_shot (bool, optional): [description]. Defaults to False.
        row_mean_center (bool, optional): [description]. Defaults to False.
        estimator_prediction_type (str, optional): [description]. Defaults to "forecast".
        time_column (int, optional): [description]. Defaults to -1.
        random_state (int, optional): [description]. Defaults to 42.
    """
    def __init__(
        self,
        feature_columns=None,
        target_columns=None,
        regressor=None,
        lookback_window=10,
        prediction_horizon=1,
        scaling_func=None,
        inverse_scaling_func=None,
        check_inverse=False,
        short_name="",
        one_shot=False,
        row_mean_center=False,
        estimator_prediction_type="forecast",
        time_column=-1,
        random_state=42,
    ):

        self.prediction_horizon = prediction_horizon
        self.lookback_window = lookback_window
        self.one_shot = one_shot
        self.row_mean_center = row_mean_center
        self.estimator_prediction_type = estimator_prediction_type
        self.cached_last_window_train_set_ = None

        # A pipeline could not be cloned because this init changed these input parameters. For now, we do not need them.
        # if func is None:
        #     self.func = self.function
        # else:
        #     self.func = func
        # if inverse_func is None:
        #     self.inverse_func = self.inverse_function
        # else:
        #     self.inverse_func = inverse_func

        self.scaling_func = scaling_func
        self.inverse_scaling_func = inverse_scaling_func
        # self.target_transformer = None
        self.short_name = short_name
        # self.ymean = None  # used in inverse_function to fill in inf/-inf and nan value
        self.forecasts_ = None  # used to keep forecasts of trainset

        self.feature_columns = feature_columns
        self.target_columns = target_columns
        self.time_column = time_column

        self.random_state = random_state

        if self.feature_columns and self.target_columns:
            self.is_exogenous_pipeline_ = set(self.feature_columns) != set(self.target_columns)
        else:
            self.is_exogenous_pipeline_ = False
        self.debug=False

        if self.debug:
            print(f"autoai builing an exogenous pipeline: {self.is_exogenous_pipeline_ }")

        self.exogenous_imputer = None

        # use_target_columns: If false use the provided y during fit (old method) otherwise
        # the provided target columns will be used during fit
        self.use_target_columns_ = True

        super().__init__(
            regressor=regressor,
            transformer=None,
            func=self.function,
            inverse_func=self.inverse_function,
            check_inverse=check_inverse,
        )
        self._check_args()

    def _check_args(self):
        if self.time_column != -1:
            raise Exception(Messages.get_message(message_id="AUTOAITSLIBS0058E"))
        
        if self.row_mean_center and self.is_exogenous_pipeline_:
            raise RuntimeError("Row mean center is not supported for exogenous use cases.")

    def __repr__(self):
        return f"{self.regressor}"

    def function(self, y):
        if not self.row_mean_center:
            # Note, prediction horizon of 1 is correct since we are building 1-step ahead model
            y = SmallDataWindowTargetTransformer(prediction_horizon=1).transform(X=y)
            y = SimpleImputer().fit_transform(y)

        return y

        # if self.one_shot:
        #     y = SmallDataWindowTargetTransformer(prediction_horizon=self.prediction_horizon).transform(X=y)
        # else:
        #     y = SmallDataWindowTargetTransformer(prediction_horizon=1).transform(X=y)
        #
        # y = SimpleImputer().fit_transform(y)
        #
        # # if self.scaling_func:  # transform the target y
        # #     power_transformer = PowerTransformer()
        # #     y2 = y
        # #     if y.ndim == 1:
        # #         y2 = y.reshape(y.shape[0], -1)
        # #     self.power_transformer = power_transformer.fit(X=y2)
        # #     transformed_y = self.power_transformer.transform(X=y2)
        # #     if y.ndim == 1:
        # #         y = transformed_y.flatten()
        # #     else:
        # #         y = transformed_y
        #
        # if self.scaling_func is None:
        #     return y
        #
        # y2 = y
        # self.ymean = np.mean(y2, axis=0)  # keep a vector of means, row-wise, or each column has one mean
        #
        # if y.ndim == 1:
        #     y2 = y.reshape(y.shape[0], 1)
        #
        # # first use PowerTransformer
        # self.target_transformer = PowerTransformer()
        # self.target_transformer.fit(X=y2)  # fit the transformer
        # transformed_y = self.target_transformer.transform(X=y2)
        #
        # if (np.count_nonzero(transformed_y) == 0) or (np.any(np.isinf(transformed_y))):
        #     # if all elements are 0 OR at least one element is inf or -inf
        #     self.target_transformer = StandardScaler()
        #     self.target_transformer.fit(X=y2)  # fit the transformer
        #
        #     transformed_y = self.target_transformer.transform(X=y2)
        #     if y.ndim == 1:
        #         y = transformed_y.flatten()
        #     else:
        #         y = transformed_y
        #
        #     return y
        # else:
        #     # if exists at least one none-zero elements OR none of inf or -inf elements
        #     if y.ndim == 1:
        #         y = transformed_y.flatten()
        #     else:
        #         y = transformed_y
        #
        #     return y

    def inverse_function(self, y):
        # Attention: this is not a precise inverse of the Windowing transformer
        # if self.inverse_scaling_func:
        #     y = self.inverse_scaling_func(y)

        return y

        # if self.inverse_scaling_func is None or self.target_transformer is None:
        #     return y
        #
        # y2 = y
        # if y.ndim == 1:
        #     y2 = y.reshape(y.shape[0], 1)
        #
        # inverse_y = self.target_transformer.inverse_transform(X=y2)
        # # check for inf and nan values
        # if (np.any(np.isinf(inverse_y)) or np.any(np.isnan(inverse_y))) and self.ymean is not None:
        #     df = pd.DataFrame(inverse_y)  # use DataFrame utility
        #     for idx, col in enumerate(df.columns):
        #         df[col].replace(inf, self.ymean[idx], inplace=True)
        #         df[col].replace(-inf, self.ymean[idx], inplace=True)
        #         df[col].replace(np.nan, self.ymean[idx], inplace=True)
        #
        #     inverse_y = df.values
        #
        # if y.ndim == 1:
        #     y = inverse_y.flatten()
        # else:
        #     y = inverse_y
        #
        # return y

    def _input_data_transformation(self, X):
        """
        Used to extract the proper columns of X, corresponding to features.
        
        Args:
            X : numpy array.
        """
        if hasattr(self, "feature_columns") and self.feature_columns:
            return X[:, self.feature_columns]
        return X

    def _output_data_transformation(self, X):
        """
        Used to extract the proper columns of X to create y, the target columns.
        
        Args:
            X : numpy array.
        """
        if hasattr(self, "target_columns") and self.target_columns:
            return X[:, self.target_columns]
        return X

    def _adjust_indices(self, target_columns: List[int]=[], feature_columns: List[int]=[]):
        """Adjusts feature and target columns as specified. This is intended to be used on
        non-exogenous pipelines so that only the required columns are needed in calls to fit/predict.

        Args:
            target_columns (List[int], optional): New target columns to use. Defaults to [].
            feature_columns (List[int], optional): New feature columns to use. Defaults to [].
        """
        self.target_columns = target_columns
        self.feature_columns = feature_columns

        # should not be needed
        # if hasattr(self.regressor, "_adjust_indices") and callable(self.regressor._adjust_indices):
        #     self.regressor._adjust_indices(target_columns=target_columns, feature_columns=feature_columns)

    def _check_features_targets(self, X):
        """Check to make sure features and targets are meaningful. If they are 
        none, all columns will be used for both (original behavior)

        Args:
            X (numpy.ndarray]): Input data

        Raises:
            ValueError: Either both feature and target columns should be none 
                (original behavior) or they should both be specified.
        """
        if (self.feature_columns and not self.target_columns) or (not self.feature_columns and self.target_columns):
            raise ValueError("If one of feature or target columns is specified, they must both be specified.")
        
        if not self.feature_columns and not self.target_columns:
            self.feature_columns = [i for i in range(X.shape[1]) if i != self.time_column]
            self.target_columns = self.feature_columns

    def _check_future_exogenous(self, Z: object):
        if not isinstance(Z, np.ndarray):
            raise ValueError(Messages.get_message(message_id='AUTOAITSLIBS0090E'))

        exo = set(self.feature_columns) - set(self.target_columns)
        if (Z.shape[0] != self.prediction_horizon) or (Z.shape[1] != len(exo)):
            LOGGER.warning(Messages.get_message(self.prediction_horizon,len(exo), message_id='AUTOAITSLIBS0008W'))
            return False
        return True

    def fit(self, X, y):
        # Original assumption was that X == y? Or at least that X.shape == y.shape
        # Because of need for imputation (which modifies X) we sometimes need to derive y from X using
        # target columns.
        #
        # If self.use_target_columns is True then:
        #     If target_columns is not None these will be used, otherwise all columns of X are used.
        # If feature_columns is not None these will be used to determine the X used in training, otherwise
        # all columns of X are used.
        #
        # These options are provided to ensure consistency with original behavior.
        #
        # X2 = X
        # if self.row_mean_center:
        #     window_transformer = WindowTransformerMTS(lookback_window=self.lookback_window)
        #     rowmean_transformer = StandardRowMeanCenterMTS(lookback_window=self.lookback_window)
        #     (Xw, yw) = window_transformer.fit_transform(X, y)
        #     (X, y) = rowmean_transformer.fit_transform(Xw, yw)
        #
        # super().fit(X, y)  # set internal states
        #
        # # create forecasts immediately beyond training set
        # if X2.shape[0] > 2 * self.lookback_window:
        #     self.forecasts_ = self.predict_rowwise_2d(X=X2[-2 * self.lookback_window:, ])
        # else:
        #     self.forecasts_ = self.predict_rowwise_2d(X=X2)
        #
        # self.forecasts_ = self.forecasts_[-1:, ]  # keep only predictions of the last row
        # return self

        # clm_index = list(set(self.feature_columns + self.target_columns))

        # num_time_series = X.shape[1]  # number of time series

        self._check_features_targets(X)
        random_state = getattr(self, "random_state", None)
        num_time_series = len(self.target_columns)

        # keep last window in train set
        if X.shape[0] > self.lookback_window:
            self.cached_last_window_train_set_ = X[
                -self.lookback_window :,
            ]
        else:
            self.cached_last_window_train_set_ = X

        # get the right X y
        if not hasattr(self, "use_target_columns_") or (hasattr(self, "use_target_columns_") and self.use_target_columns_):
            y = self._output_data_transformation(X)
        X = self._input_data_transformation(X)

        if self.row_mean_center:
            # to do: row_mean_center, StandardRowMeanCenterMTS should be
            # updated to support the case when X.shape[1] != y.shape[1]
            window_transformer = WindowTransformerMTS(
                lookback_window=self.lookback_window
            )
            rowmean_transformer = StandardRowMeanCenterMTS(
                lookback_window=self.lookback_window,
                random_state=random_state
            )
            (Xw, yw) = window_transformer.fit_transform(X, y)
            (X, y) = rowmean_transformer.fit_transform(Xw, yw)

        super().fit(X, y)  # set internal states

        # if the pipeline is exogenous, we fit an imputer if exogenous are not provided
        if hasattr(self, "is_exogenous_pipeline_") and self.is_exogenous_pipeline_:
            self.exogenous_imputer = SimpleImputer()
            # from autoai_ts_libs.srom.imputers.interpolators import InterpolateImputer
            # self.exogenous_imputer = InterpolateImputer(enable_fillna=False, method="ffill")
            exogenous_indices = [i for i, c in enumerate(self.feature_columns) if c not in self.target_columns]

            self.exogenous_imputer.fit(X[:, exogenous_indices])
            fut_exog = get_future_exogenous_input(self.exogenous_imputer, None, X, exogenous_indices, self.prediction_horizon)
        else:
            fut_exog = None

        # create forecasts immediately beyond training set
        X_cached = self.cached_last_window_train_set_

        self.forecasts_ = self.predict_rowwise_2d(X=X_cached, future_exogenous=fut_exog)
        self.forecasts_ = self.forecasts_[
            -1:,
        ]  # keep only predictions of the last row
        self.forecasts_ = self.forecasts_.reshape(
            -1, num_time_series
        )  # reshape to h x k, where k is number of time series, h is prediction horizon

        return self

    # prediction_type: forecast, rowwise, rowwise_2d
    def predict(self, X=None, prediction_type=None, future_exogenous: np.ndarray=None):
        # hack to pass save/load test
        if not hasattr(self, "debug"):
            self.debug = False

        has_future = False
        if future_exogenous is not None:
            has_future = self._check_future_exogenous(future_exogenous)

        if X is not None:
            X = check_array(X, dtype=np.float64, force_all_finite=False, ensure_2d=False, ensure_min_samples=0)
            if np.count_nonzero(np.isnan(X)) > 0:
                raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0067E'))

        if prediction_type is None:
            prediction_type = self.estimator_prediction_type

        expected_method_name = f"predict_{prediction_type}"
        method = getattr(self, expected_method_name, None)
        if not method:
            raise ValueError(
                Messages.get_message({prediction_type}, message_id="AUTOAITSLIBS0011E")
            )
        if has_future:
            return method(X=X, future_exogenous=future_exogenous)
        else:
            return method(X=X)

    def predict_forecast(self, X=None, future_exogenous=None):
        has_future = False
        if future_exogenous is not None:
            has_future = self._check_future_exogenous(future_exogenous)

        if X is None and not (future_exogenous is not None and self.is_exogenous_pipeline_):
            # if X is none, we can use pre-cached forecasts
            # but we should only do that for exogenous pipelines if exgoenous is not provided
            return self.forecasts_
        try:
            num_time_series = len(self.target_columns) if hasattr(self, "target_columns") else X.shape[1]
            # prepend the last window of train set
            if X is not None:
                Xnew = np.concatenate((self.cached_last_window_train_set_, X), axis=0)
            else:
                Xnew = self.cached_last_window_train_set_
        except Exception as e:
            raise Exception(
                Messages.get_message(str(e), message_id="AUTOAITSLIBS0055E")
            )
        # take only the last window
        Xnew = Xnew[
            -self.lookback_window :,
        ]
        # call row prediction
        if has_future:
            y_pred = self.predict_rowwise_2d(X=Xnew, future_exogenous=future_exogenous)
        else:
            y_pred = self.predict_rowwise_2d(X=Xnew)
        # take the last row of y_pred
        y_pred = y_pred[
            -1:,
        ]
        # return correct shape of h x k
        return y_pred.reshape(
            -1, num_time_series
        )  # reshape to h x k, where k is number of time series, h is prediction horizon

    # This method is responsible for:
    # 1. prepend last window of train set to input X
    # 2. call _predict_rowwise_2d
    # 3. remove predictions for the cached train set
    # 4. reshape output to the required m x h x k format
    def predict_rowwise(self, X, future_exogenous=None):
        has_future = False
        if future_exogenous is not None:
            has_future = self._check_future_exogenous(future_exogenous)

        if X is None:
            raise ValueError(Messages.get_message(message_id="AUTOAITSLIBS0012E"))

        num_time_series = len(self.target_columns) if hasattr(self, "target_columns") else X.shape[1]
        # prepend last window of train set
        Xnew = np.concatenate((self.cached_last_window_train_set_, X), axis=0)
        # Xnew = self._input_data_transformation(Xnew)
        # call row prediction
        if has_future:
            y_pred = self.predict_rowwise_2d(X=Xnew, future_exogenous=future_exogenous)
        else:
            y_pred = self.predict_rowwise_2d(X=Xnew)
        # remove the prediction for the cached train set
        y_pred = y_pred[
            self.cached_last_window_train_set_.shape[0] :,
        ]
        # reshape to m x h x k, m is number of rows in input X, h is prediction horizon, k is number of time series
        y_pred = y_pred.reshape(y_pred.shape[0], -1, num_time_series)
        return y_pred

    # X: raw time series
    # This method returns the prediction for each row in X
    # We do not prepend last window of train set to X here, because it has been done alreeady
    def predict_rowwise_2d(self, X, future_exogenous=None):
        has_future = False
        if future_exogenous is not None:
            has_future = self._check_future_exogenous(future_exogenous)

        X = self._input_data_transformation(X)
        if self.row_mean_center:
            # should not be an exogenous case
            pipeline = self.regressor_
            if len(pipeline.steps) != 1:
                raise ValueError(Messages.get_message(message_id="AUTOAITSLIBS0013E"))

            # create a new transformer
            transformer = WindowTransformerMTS(lookback_window=self.lookback_window)
            # window and transform the data ONLY ONCE, right most column is latest in temporal order
            (Xw, _) = transformer.fit_transform(X)

            estimator = pipeline.steps[-1][-1]  # take the final estimator of the pipeline
            y_pred = self._predict_rolling_recursive(
                X=Xw,
                model=estimator,
                remaining_prediction_horizon=self.prediction_horizon
            )
        else:
            if hasattr(self, "is_exogenous_pipeline_") and self.is_exogenous_pipeline_:
                if has_future:
                    y_pred = self._predict_rolling_exog(X, future_exogenous=future_exogenous)
                else:
                    y_pred = self._predict_rolling_exog(X)
            else:
                y_pred = self._predict_rolling(X)

        return y_pred

    # X is in windowed and unscaled space
    # X contains only feature columns
    # note, _predict_rolling_recursive is only called when row_mean_center is called
    # which is only true when we have univariate case -- no exogenous support below
    def _predict_rolling_recursive(self, X, model=None, remaining_prediction_horizon=0):
        # create a new transformer
        random_state = getattr(self, "random_state", None)
        rowmean_transformer = StandardRowMeanCenterMTS(
            lookback_window=self.lookback_window,
            random_state=random_state
        )
        # fit and transform X to the transformed space
        (Xt, _) = rowmean_transformer.fit_transform(X=X)
        # call 1-step ahead prediction, yt in scaled space
        yt = model.predict(Xt)
        if yt.ndim == 1:
            yt = yt.reshape(yt.shape[0], 1)

        # y_pred in raw space
        y_pred = rowmean_transformer.inverse_transform(yt)

        # replace previous columns with predicted columns
        for i in range(1, y_pred.shape[1]):
            X[:, i * self.lookback_window] = y_pred[:, i - 1]

        # remove the first column of X, append the last column of y_pred to right most of X
        X = np.concatenate((X[:, 1:], y_pred[:, -1].reshape(-1, 1)), axis=1)

        if remaining_prediction_horizon > 1:
            yp = self._predict_rolling_recursive(
                X=X,
                model=model,
                remaining_prediction_horizon=remaining_prediction_horizon - 1,
            )
            y_pred = np.concatenate((y_pred, yp), axis=1)

        return y_pred

    # X: (originally) raw time series
    # X contains only feature columns
    def _predict_rolling(self, X, future_exogenous: np.ndarray=None):
        # to handle exogenous appropriately we need some indices
        exog_columns = [i for i in self.feature_columns if i not in self.target_columns]
        # need indices into X (which contains only features)
        # these are indices into features!
        target_indices = [i for i, c in enumerate(self.feature_columns) if c in self.target_columns]
        # target_indices = [self.feature_columns.index(t) for t in self.target_columns if t in self.feature_columns]
        exogenous_indices = [i for i, c in enumerate(self.feature_columns) if c in exog_columns]
        # exogenous_indices = [self.feature_columns.index(t) for t in exog_columns if t in self.feature_columns]
        num_features = len(self.feature_columns)  # input size of model

        # impute future exogenous once
        if exogenous_indices:
            future_exogenous = get_future_exogenous_input(self.exogenous_imputer, future_exogenous, X, exogenous_indices, self.prediction_horizon)
        else:
            future_exogenous = None

        if self.debug:
            print("targets:", target_indices)
            print("exogenous:", exogenous_indices)

        # Warning: code is very brittle -- depends on precise pipeline steps
        # three or four step pipeline, step three only used if estimator is SVR

        pipeline = self.regressor_
        # trained windowing transformer
        window_transformer = pipeline.steps[0][1]
        # trained final estimator
        estimator = pipeline.steps[-1][-1]

        # only window the data once, each row is one time step, right most side is latest in time
        Xt = window_transformer.transform(X)
        # calling imputer (if exists)
        Xt = pipeline.steps[1][1].transform(Xt)

        X4_svr = (
            Xt  # only use for SVR pipeline, keep a copy of windowed and unscaled data
        )

        y_pred = None
        # prediction, keep same rows, extending to the right
        for k in range(self.prediction_horizon):
            if "SVR" in self.short_name:  # scale data
                Xt = pipeline.steps[2][1].transform(X4_svr)
            # Xt input needed for estimator
            # call 1-step ahead prediction
            yt = estimator.predict(Xt)
            if yt.ndim == 1:
                yt = yt.reshape(yt.shape[0], 1)

            if self.debug:
                print("Xt:", Xt.shape)
                print("Xt:", Xt)
                print("yt", yt.shape)

            # yt has targets only

            # keep prediction results, for prediction horizon k
            if y_pred is None:
                y_pred = yt
            else:
                y_pred = np.concatenate((y_pred, yt), axis=1)

            # append predicted results to the right most columns, remove left most columns (older in time)
            # continue prediction for the same time step, using predicted values only
            # for each row, keep same ground-truth data during prediction

            if "SVR" in self.short_name:
                Xnext = X4_svr
            else:
                Xnext = Xt

            # Xtmp: temporary matrix to hold new values to concatenate to the right of X4_svr/Xt
            Xtmp = np.ones((Xnext.shape[0], num_features))*np.NaN
            if target_indices:
                Xtmp[:, target_indices] = yt
            if exogenous_indices:
                Xtmp[:-1, exogenous_indices] = Xnext[1:, -num_features:][:, exogenous_indices]  # values from next row are future exogenous that are already in X
                # if future_exogenous is not None:
                #     Xtmp[-1:, exogenous_indices] = future_exogenous[k, :]  # last row is always future exogenous from future_exogenous parameter
                # else:
                #     # case when no future exogenous were provided, fallback method
                #     Xtmp[:, exogenous_indices] = self.exogenous_imputer.transform(Xtmp[:, exogenous_indices])
                Xtmp[-1:, exogenous_indices] = future_exogenous[k, :]

            if "SVR" in self.short_name:
                X4_svr = np.concatenate((Xnext[:, num_features:], Xtmp), axis=1)
            else:
                Xt = np.concatenate((Xnext[:, num_features:], Xtmp), axis=1)

        return y_pred

    def _predict_rolling_exog(self, X, future_exogenous: np.ndarray=None):
        # attempt to be less dependent on internal windowing structure
        # enabling non-uniform windows across features
        # self.debug = True

        # eliminate this message since there are prior messages
        # if future_exogenous is not None and (future_exogenous.shape[0] != self.prediction_horizon):
        #     raise ValueError("Provided future exogenous should be None or equal in length to the prediction horizon.")

        # to handle exogenous appropriately we need some indices
        exog_columns = [i for i in self.feature_columns if i not in self.target_columns]
        # need indices into X (which contains only features)
        # these are indices into features!
        target_indices = [i for i, c in enumerate(self.feature_columns) if c in self.target_columns]
        # target_indices = [self.feature_columns.index(t) for t in self.target_columns if t in self.feature_columns]
        exogenous_indices = [i for i, c in enumerate(self.feature_columns) if c in exog_columns]
        # exogenous_indices = [self.feature_columns.index(t) for t in exog_columns if t in self.feature_columns]
        num_features = len(self.feature_columns)  # input size of model

        # impute future exogenous once
        if exogenous_indices:
            future_exogenous = get_future_exogenous_input(self.exogenous_imputer, future_exogenous, X, exogenous_indices, self.prediction_horizon)
        else:
            future_exogenous = None

        if self.debug:
            print("targets:", target_indices)
            print("exogenous:", exogenous_indices)

        # Warning: code is very brittle -- depends on precise pipeline steps
        # three or four step pipeline, step three only used if estimator is SVR

        pipeline = self.regressor_
        # trained windowing transformer
        window_transformer = pipeline.steps[0][1]
        # trained final estimator
        estimator = pipeline.steps[-1][-1]

        # only window the data once, each row is one time step, right most side is latest in time
        Xt = window_transformer.transform(X)
        # calling imputer (if exists)
        imputer = pipeline.steps[1][1]
        Xt = imputer.transform(Xt)

        # For SVR, we have a scaler
        # In either case Xt represents input data to model
        if "SVR" in self.short_name:
            scaler = pipeline.steps[2][1]
            Xt = scaler.transform(Xt)
        else:
            scaler = None

        y_pred = None
        # track separate segments of the raw timeseries, which we will add the
        # rolling predictions to
        # one tracking matrix is required for each row in X
        # we limit memory usage by fixing the size of these windows
        # key requirement is that applying window transformer to data in each Xseg
        # should give you proper Xt elements
        # this means we need future exogenous to be added to the windows
        # if the models have lookahead

        # need lookahead to get offset properly
        lookahead = getattr(window_transformer, "lookahead_window", 0)
        # print("lookahead is:", lookahead)
        # print("shape of X", X.shape)
        # protect from invalid lookahead
        if lookahead > 1:
            raise ValueError("Features based on lookahead greater than one is not supported for one step ahead models.")

        maxwin = self.lookback_window + 1 + lookahead

        Xseg = np.NaN*np.ones((X.shape[0], maxwin, X.shape[1]))
        # l indexes the time point (time corresponding to initial feature)
        for l in range(0, X.shape[0]):
            # use min to deal with short data
            if l < min(maxwin-lookahead, X.shape[0]-lookahead):
                # if l < maxwin-lookahead:
                # get partial window plus complete lookahead
                Xseg[l,-l-lookahead-1:,:] = X[:l+lookahead+1,:]
            elif l >= X.shape[0]-lookahead:
                # near end of input data we need to have empty rows for lookahead
                # -lookahead, l-maxwin+lookahead
                lookahead_offset = l - X.shape[0] + (maxwin-lookahead) + 1
                # print("la offset:", lookahead_offset)
                # Xseg[l,: lookahead_offset,:] = X[l-maxwin+lookahead+1:l+1,:]
                Xseg[l,: lookahead_offset,:] = Xseg[l-1, 1: ,:]
            else:
                # else complete window with lookahead
                Xseg[l,:,:] = X[l-maxwin+1+lookahead:l+lookahead+1,:]

        # with lookahead the first Xt may not be correct
        # i.e., we may have some future exogenous to fill
        # whereas xt will be partially imputed because of imputation done on windows
        if exogenous_indices and lookahead > 0:
            # we only support lookahead == 1
            # so only last row of last Xseg is affected
            # if future_exogenous is not None:
            Xseg[-1,-1,exogenous_indices] = future_exogenous[0,:]
            # else:
            #     raise RuntimeError("Future exogenous should not be empty")
            #     Xseg[-1,-1,exogenous_indices] = self.exogenous_imputer.transform(Xseg[-1,-1,exogenous_indices].reshape(1,-1))

        def make_Xt_from_Xseg(Xseg):
            # generate the new Xt from the updated segments by applying
            # necessary pipeline steps
            for j, Xtmp in enumerate(Xseg):
                tmp = window_transformer.transform(Xtmp)
                tmp = imputer.transform(tmp)
                if scaler:
                    tmp = scaler.transform(tmp)
                Xt[j,:] = tmp[-1-lookahead,:] # need to account for lookahead here as Xseg is offset
            return Xt

        Xt = make_Xt_from_Xseg(Xseg)

        # prediction, for each prediction we need to update each segment
        for k in range(self.prediction_horizon):
            # call 1-step ahead prediction
            yt = estimator.predict(Xt)
            if yt.ndim == 1:
                yt = yt.reshape(yt.shape[0], 1)
            if self.debug:
                print("Xt:", Xt.shape)
                print("Xt:", Xt)
                print("yt", yt.shape)
                print("yt:", yt)
            # yt has targets only
            # keep prediction results, for prediction horizon k
            if y_pred is None:
                y_pred = yt
            else:
                y_pred = np.concatenate((y_pred, yt), axis=1)

            if k == self.prediction_horizon - 1:
                # no need to update Xseg/Xt after last prediction
                break
            # Update all the segments with their new predictions
            # print("Xseg:", Xseg)
            # print("Xseg shape:", Xseg.shape)
            for i in range(Xseg.shape[0]):
                # index in second dimension of Xseg which contains that segment's
                # current time
                last_index = -1-lookahead
                # for each segment shift up by one to advance time
                Xseg[i,:-1,:] = Xseg[i,1:,:].copy()
                # add new values for targets
                if target_indices:
                    Xseg[i,last_index,target_indices] = yt[i,:]
                # add new values for features
                if exogenous_indices:
                    if i < Xseg.shape[0] - 1:
                        Xseg[i, -1, exogenous_indices] = Xseg[i+1,-1,exogenous_indices].copy()
                    else:
                        # # reset the exogenous so imputation works
                        # Xseg[i,-1,exogenous_indices] = np.NaN
                        # # future exogenous is not empty (imputed once at the beginning)
                        # if future_exogenous is not None:
                        #     Xseg[i,-1, exogenous_indices] = future_exogenous[k+lookahead, :]
                        # else:
                        #     # case when no future exogenous were provided, fallback method
                        #     # means = np.nanmean(Xseg[i,:-1][:, exogenous_indices], axis=0)
                        #     # print(Xseg[i,:-1][:,exogenous_indices], Xseg[i,:-1][:, exogenous_indices].shape)
                        #     # print("means:", means)
                        #     # below is always one sample
                        #     # print("Last element of xseg:", Xseg[i,-1, exogenous_indices])
                        #     raise RuntimeError("Future exogenous should not be empty")
                        #     Xseg[i,-1, exogenous_indices] = self.exogenous_imputer.transform(Xseg[i,-1, exogenous_indices].reshape(1, -1))
                        Xseg[i,-1, exogenous_indices] = future_exogenous[k+lookahead, :]
            Xt = make_Xt_from_Xseg(Xseg)
        return y_pred


    # attempt to have a uniform interface for returning the internal estimator from our metaestimators
    @property
    def get_estimators(self):
        return [getattr(self, "regressor", None)]

