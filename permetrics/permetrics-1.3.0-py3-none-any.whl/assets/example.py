#!/usr/bin/env python
# Created by "Thieu" at 15:49, 02/04/2022 ----------%                                                                               
#       Email: nguyenthieu2102@gmail.com            %                                                    
#       Github: https://github.com/thieu1995        %                         
# --------------------------------------------------%

import pandas as pd
from permetrics.regression import RegressionMetric
import numpy as np
from copy import deepcopy


y1 = np.array([2, 3, 1, 5, 6])
y2 = np.array([200000, -30000, -2, -500000, -6.50000])

# EVS = evs = explained_variance_score
# ME = me = max_error
# MBE = mbe = mean_bias_error
# MAE = mae = mean_absolute_error
# MSE = mse = mean_squared_error
# RMSE = rmse = root_mean_squared_error
# MSLE = msle = mean_squared_log_error
# MedAE = medae = median_absolute_error
# MRE = mre = MRB = mrb = mean_relative_bias = mean_relative_error
# MPE = mpe = mean_percentage_error
# MAPE = mape = mean_absolute_percentage_error
# SMAPE = smape = symmetric_mean_absolute_percentage_error
# MAAPE = maape = mean_arctangent_absolute_percentage_error
# MASE = mase = mean_absolute_scaled_error
# NSE = nse = nash_sutcliffe_efficiency
# NNSE = nnse = normalized_nash_sutcliffe_efficiency
# WI = wi = willmott_index
# R = r = PCC = pcc = pearson_correlation_coefficient
# AR = ar = APCC = apcc = absolute_pearson_correlation_coefficient
# R2s = r2s = pearson_correlation_coefficient_square
# CI = ci = confidence_index
# COD = cod = R2 = r2 = coefficient_of_determination
# ACOD = acod = AR2 = ar2 = adjusted_coefficient_of_determination
# DRV = drv = deviation_of_runoff_volume
# KGE = kge = kling_gupta_efficiency
# GINI = gini = gini_coefficient
# GINI_WIKI = gini_wiki = gini_coefficient_wiki
# PCD = pcd = prediction_of_change_in_direction
# CE = ce = cross_entropy
# KLD = kld = kullback_leibler_divergence
# JSD = jsd = jensen_shannon_divergence
# VAF = vaf = variance_accounted_for
# RAE = rae = relative_absolute_error
# A10 = a10 = a10_index
# A20 = a20 = a20_index
# A30 = a30 = a30_index
# NRMSE = nrmse = normalized_root_mean_square_error
# RSE = rse = residual_standard_error
#
# RE = re = RB = rb = single_relative_bias = single_relative_error
# AE = ae = single_absolute_error
# SE = se = single_squared_error
# SLE = sle = single_squared_log_error


# data = pd.read_csv("assets/data_test.csv", usecols=["y_test_true_scaled", "y_test_true_unscaled", "y_test_pred_scaled", "y_test_pred_unscaled"])
# y_true = data[["y_test_true_scaled", "y_test_true_unscaled"]].values
# y_pred = data[["y_test_pred_scaled", "y_test_pred_unscaled"]].values


METRICS = ["R", "R2", "AR", "A30", "MBE", "MPE"]

model = RegressionMetric(y1, y2, decimal=5)
result = model.get_metrics_by_list_names(METRICS)
print(result)

model = RegressionMetric(y1, y2, decimal=5)
print(model.AR2(y1, y2, (100, 2)))