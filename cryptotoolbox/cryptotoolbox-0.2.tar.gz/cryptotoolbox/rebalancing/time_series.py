from cryptotoolbox.rebalancing import rolling

from sklearn.metrics import mean_squared_error
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix

from cryptotoolbox.signal import signal_utility


import pandas as pd
import numpy as np



def rolling_mixing(forecasting_model, X, y, n=252, s=63, s_eval= None, calibration_step=None, display = False, **kwargs):
    assert X.shape[0] == y.shape[0]
    idx = X.index
    forecasting_series = pd.Series(index=idx, name='prediction')
    discrete_three_states_forecasting_series = pd.Series(index=idx, name='prediction')
    discrete_three_states_forecasting_series_lo = pd.Series(index=idx, name='prediction')
    discrete_two_states_forecasting_series = pd.Series(index=idx, name='prediction')
    discrete_two_states_forecasting_series_lo = pd.Series(index=idx, name='prediction')

    if n is None and s_eval is None:
        roll = rolling._ExpandingRollingMechanism(idx, s=s)
    if n is None and s_eval is not None:
        roll = rolling._ExpandingEvalRollingMechanism(idx, s=s, s_eval = s_eval)
    if n is not None and s_eval is None :
        roll = rolling._RollingMechanism(idx, n=n, s=s)
    if n is not None and s_eval is not None:
        roll = rolling._EvalRollingMechanism(idx, n=n, s=s, s_eval = s_eval)
    features_names = list(X.columns)
    features_importances = []
    iteration_counter = 0
    for slice_n, slice_s, slice_s_eval in roll():
        # Select X
        X_train = X.loc[slice_n].copy()
        y_train = y.loc[slice_n].copy()

        X_test = X.loc[slice_s].copy()
        y_test = y.loc[slice_s].copy()
        if calibration_step >0:
            if (iteration_counter>0 and iteration_counter%calibration_step == 0):
                # print('launching calibration '+str(iteration_counter))
                forecasting_model.calibrate(X_train, y_train)
                # print('endiing calibration ' + str(iteration_counter))

        if slice_s_eval is not None:
            X_eval = X.loc[slice_s_eval].copy()
            y_eval = y.loc[slice_s_eval].copy()
            forecasting_model.fit(X_train, y_train, X_eval, y_eval)
        else :
            forecasting_model.fit(X_train, y_train, X_train, y_train)

        y_pred = forecasting_model.predict(X_test)
        y_train_pred = forecasting_model.predict(X_train)

        #### three states discretization
        lower_quantile_threshold, upper_quantile_threshold, lower_threshold, upper_threshold, sharpe_strat, sharpe_under = signal_utility.find_best_three_states_discretization(y_train_pred,y_train)

        y_pred_three_space_discrete = signal_utility.apply_discretization_three_states(y_pred, upper_threshold,lower_threshold)
        y_test_three_space_discrete = signal_utility.apply_discretization_three_states(y_test, upper_threshold,lower_threshold)

        #### three states discretization long only
        lower_quantile_threshold_lo, upper_quantile_threshold_lo, lower_threshold_lo, upper_threshold_lo, sharpe_strat_lo, sharpe_under_lo = signal_utility.find_best_three_states_discretization_lo(y_train_pred, y_train)


        y_pred_three_space_discrete_lo = signal_utility.apply_discretization_three_states_lo(y_pred, upper_threshold_lo,lower_threshold_lo)
        y_test_three_space_discrete_lo =signal_utility. discretize_three_states_lo(y_test, upper_threshold_lo,lower_threshold_lo)


        #### two states discretization


        splitting_quantile_threshold, splitting_threshold, sharpe_strat, sharpe_under = signal_utility.find_best_two_states_discretization(y_train_pred,y_train)
        y_pred_two_space_discrete = signal_utility.apply_discretization_two_states(y_pred, splitting_threshold)
        y_test_two_space_discrete = signal_utility.apply_discretization_two_states(y_test, splitting_threshold)

        #### two states discretization long only
        splitting_quantile_threshold_lo, splitting_threshold_lo, sharpe_strat_lo, sharpe_under_lo = signal_utility.find_best_two_states_discretization(y_train_pred,y_train)
        y_pred_two_space_discrete_lo = signal_utility.apply_discretization_two_states_lo(y_pred, splitting_threshold_lo)
        y_test_two_space_discrete_lo = signal_utility.apply_discretization_two_states_lo(y_test, splitting_threshold_lo)

        run_importances=forecasting_model.get_features_importance(features_names)
        features_importances.append(run_importances)
        # no leverage for the moment
        forecasting_series.loc[slice_s] = y_pred.ravel()
        discrete_three_states_forecasting_series.loc[slice_s] = y_pred_three_space_discrete.ravel()
        discrete_two_states_forecasting_series.loc[slice_s] = y_pred_two_space_discrete.ravel()
        discrete_three_states_forecasting_series_lo.loc[slice_s] = y_pred_three_space_discrete_lo.ravel()
        discrete_two_states_forecasting_series_lo.loc[slice_s] = y_pred_two_space_discrete_lo.ravel()

        rmse = mean_squared_error(y_test, y_pred)
        matrix_three = confusion_matrix(y_test_three_space_discrete, y_pred_three_space_discrete)
        accuracy_three = accuracy_score(y_test_three_space_discrete, y_pred_three_space_discrete)
        # matrix_three_lo = confusion_matrix(y_test_three_space_discrete_lo, y_pred_three_space_discrete_lo)
        # accuracy_three_lo = accuracy_score(y_test_three_space_discrete_lo, y_pred_three_space_discrete_lo)
        matrix_two = confusion_matrix(y_test_two_space_discrete, y_pred_two_space_discrete)
        accuracy_two = accuracy_score(y_test_two_space_discrete, y_pred_two_space_discrete)
        matrix_two_lo = confusion_matrix(y_test_two_space_discrete_lo, y_pred_two_space_discrete_lo)
        accuracy_two_lo = accuracy_score(y_test_two_space_discrete_lo, y_pred_two_space_discrete_lo)

        if display:
            print('training slice ' + str(slice_n))
            print('testing slice ' + str(slice_s))
            print('rmse for slice : '+str(rmse))
            print('accuracy three states')
            print(accuracy_three)
            print('confusion matrix three states')
            print(matrix_three  )
            print('accuracy two states')
            print(accuracy_two)
            print('confusion matrix two states')
            print(matrix_two)
        iteration_counter = iteration_counter+1

    features_importances = pd.DataFrame(features_importances)
    return forecasting_series, features_importances, discrete_two_states_forecasting_series, discrete_two_states_forecasting_series_lo, discrete_three_states_forecasting_series, discrete_three_states_forecasting_series_lo


def rolling_forecasting(forecasting_model, X, y, n=252, s=63, s_eval= None, calibration_step=None, display = False, min_signal = -1., max_signal = 1., **kwargs):
    assert X.shape[0] == y.shape[0]
    idx = X.index
    forecasting_series = pd.Series(index=idx, name='prediction')
    discrete_three_states_forecasting_series = pd.Series(index=idx, name='prediction')
    discrete_three_states_forecasting_series_lo = pd.Series(index=idx, name='prediction')
    discrete_two_states_forecasting_series = pd.Series(index=idx, name='prediction')
    discrete_two_states_forecasting_series_lo = pd.Series(index=idx, name='prediction')

    if n is None and s_eval is None:
        roll = rolling._ExpandingRollingMechanism(idx, s=s)
    if n is None and s_eval is not None:
        roll = rolling._ExpandingEvalRollingMechanism(idx, s=s, s_eval = s_eval)
    if n is not None and s_eval is None :
        roll = rolling._RollingMechanism(idx, n=n, s=s)
    if n is not None and s_eval is not None:
        roll = rolling._EvalRollingMechanism(idx, n=n, s=s, s_eval = s_eval)
    features_names = list(X.columns)
    features_importances = []
    iteration_counter = 0
    for slice_n, slice_s, slice_s_eval in roll():
        # Select X
        X_train = X.loc[slice_n].copy()
        y_train = y.loc[slice_n].copy()

        X_test = X.loc[slice_s].copy()
        y_test = y.loc[slice_s].copy()
        if calibration_step >0:
            if (iteration_counter>0 and iteration_counter%calibration_step == 0):
                # print('launching calibration '+str(iteration_counter))
                forecasting_model.calibrate(X_train, y_train)
                # print('endiing calibration ' + str(iteration_counter))

        if slice_s_eval is not None:
            X_eval = X.loc[slice_s_eval].copy()
            y_eval = y.loc[slice_s_eval].copy()
            forecasting_model.fit(X_train, y_train, X_eval, y_eval)
        else :
            forecasting_model.fit(X_train, y_train, X_train, y_train)

        y_pred = forecasting_model.predict(X_test)
        y_train_pred = forecasting_model.predict(X_train)

        #### three states discretization
        lower_quantile_threshold, upper_quantile_threshold, lower_threshold, upper_threshold, sharpe_strat, sharpe_under = signal_utility.find_best_three_states_discretization(
            y_train_pred, y_train)

        y_pred_three_space_discrete = signal_utility.apply_discretization_three_states(y_pred, upper_threshold,
                                                                                       lower_threshold)
        y_test_three_space_discrete = signal_utility.apply_discretization_three_states(y_test, upper_threshold,
                                                                                       lower_threshold)

        #### three states discretization long only
        lower_quantile_threshold_lo, upper_quantile_threshold_lo, lower_threshold_lo, upper_threshold_lo, sharpe_strat_lo, sharpe_under_lo = signal_utility.find_best_three_states_discretization_lo(
            y_train_pred, y_train)

        y_pred_three_space_discrete_lo = signal_utility.apply_discretization_three_states_lo(y_pred, upper_threshold_lo,
                                                                                             lower_threshold_lo)
        y_test_three_space_discrete_lo = signal_utility.discretize_three_states_lo(y_test, upper_threshold_lo,
                                                                                   lower_threshold_lo)

        #### two states discretization

        splitting_quantile_threshold, splitting_threshold, sharpe_strat, sharpe_under = signal_utility.find_best_two_states_discretization(
            y_train_pred, y_train)
        y_pred_two_space_discrete = signal_utility.apply_discretization_two_states(y_pred, splitting_threshold)
        y_test_two_space_discrete = signal_utility.apply_discretization_two_states(y_test, splitting_threshold)

        #### two states discretization long only
        splitting_quantile_threshold_lo, splitting_threshold_lo, sharpe_strat_lo, sharpe_under_lo = signal_utility.find_best_two_states_discretization(
            y_train_pred, y_train)
        y_pred_two_space_discrete_lo = signal_utility.apply_discretization_two_states_lo(y_pred, splitting_threshold_lo)
        y_test_two_space_discrete_lo = signal_utility.apply_discretization_two_states_lo(y_test, splitting_threshold_lo)

        run_importances=forecasting_model.get_features_importance(features_names)
        features_importances.append(run_importances)
        # no leverage for the moment
        y_pred = np.clip(y_pred, a_min=min_signal, a_max=max_signal)
        forecasting_series.loc[slice_s] = y_pred.ravel()
        discrete_three_states_forecasting_series.loc[slice_s] = y_pred_three_space_discrete.ravel()
        discrete_two_states_forecasting_series.loc[slice_s] = y_pred_two_space_discrete.ravel()
        discrete_three_states_forecasting_series_lo.loc[slice_s] = y_pred_three_space_discrete_lo.ravel()
        discrete_two_states_forecasting_series_lo.loc[slice_s] = y_pred_two_space_discrete_lo.ravel()

        rmse = mean_squared_error(y_test, y_pred)
        matrix_three = confusion_matrix(y_test_three_space_discrete, y_pred_three_space_discrete)
        accuracy_three = accuracy_score(y_test_three_space_discrete, y_pred_three_space_discrete)
        # matrix_three_lo = confusion_matrix(y_test_three_space_discrete_lo, y_pred_three_space_discrete_lo)
        # accuracy_three_lo = accuracy_score(y_test_three_space_discrete_lo, y_pred_three_space_discrete_lo)
        matrix_two = confusion_matrix(y_test_two_space_discrete, y_pred_two_space_discrete)
        accuracy_two = accuracy_score(y_test_two_space_discrete, y_pred_two_space_discrete)
        matrix_two_lo = confusion_matrix(y_test_two_space_discrete_lo, y_pred_two_space_discrete_lo)
        accuracy_two_lo = accuracy_score(y_test_two_space_discrete_lo, y_pred_two_space_discrete_lo)

        if display:
            print('training slice ' + str(slice_n))
            print('testing slice ' + str(slice_s))
            print('rmse for slice : '+str(rmse))
            print('accuracy three states')
            print(accuracy_three)
            print('confusion matrix three states')
            print(matrix_three  )
            print('accuracy two states')
            print(accuracy_two)
            print('confusion matrix two states')
            print(matrix_two)
        iteration_counter = iteration_counter+1

    features_importances = pd.DataFrame(features_importances)
    return forecasting_series, features_importances, discrete_two_states_forecasting_series, discrete_two_states_forecasting_series_lo, discrete_three_states_forecasting_series, discrete_three_states_forecasting_series_lo

