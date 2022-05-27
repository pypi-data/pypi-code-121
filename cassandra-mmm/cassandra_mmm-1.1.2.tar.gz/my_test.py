#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Imports
import pandas as pd
import numpy as np
import nevergrad as ng

from sklearn.linear_model import Ridge
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor

from src.cassandra.model.linear import *
from src.cassandra.model.logLinear import *
from src.cassandra.model.logLog import *
from src.cassandra.model.mlpRegressor import *
from src.cassandra.model.nevergrad.nevergrad import *
from src.cassandra.model.nevergrad.utils import *
from src.cassandra.model.ridge import *
from src.cassandra.model.modelEvaluation.plot import *
from src.cassandra.model.nestedModel import *
from src.cassandra.data.dataProcessing.prophet import *
from src.cassandra.data.trasformations.trasformations import *
from src.cassandra.model.modelEvaluation.evaluation import *
from src.cassandra.model.nevergrad import *
from src.cassandra.data.dataAnalysis.plot import *
from src.cassandra.data.dataProcessing.clean_and_format import *
from src.cassandra.data.featureSelection.ols import *
from src.cassandra.budgetAllocator.budget_allocator import *
from src.cassandra.budgetAllocator.utils import *
from src.cassandra.utils.save import *

# In[2]:


# pip install cassandra-mmm --upgrade


# In[25]:


subset_columns = ['date', 'conversions', 'fb_pr_spend', 'fb_re_spend',
                  'g_discovery_spend', 'g_display_spend', 'g_performance_max_spend', 'g_search_spend', 'g_video_spend',
                  'tiktok_learn_spend', 'influencer_spend', 'email_campaigns_sessions',
                  's_organic', 's_referral', 's_influencer', 's_affiliate', 's_direct', 's_partner', 's_mediapartner',
                  'adopta_albero_impressions', 'regalar_arbol_impressions', 'regala_arbol_impressions',
                  'plantar_arbol_impressions', 'treedom_impressions',
                  # 'avg_p_cacao', 'avg_p_baobab', 'avg_p_asc2020', 'avg_p_pt2020', 'avg_p_ft_ag',
                  'tickets_count']
csv_data = create_dataset('D:/workspace_cassandra/mmm/treedom/ES/treedom-es - modifiche.csv', subset_columns=subset_columns)

# csv_data = create_data_columns(csv_data, 'date', national_holidays_abbreviation = 'ES')

# csv_data.drop(csv_data[csv_data['date'] < '2021-02-28'].index, inplace=True)
# csv_data.drop(csv_data[csv_data['conversions'] < 1].index, inplace=True)
# csv_data.drop(csv_data[csv_data['conversions'] > 55].index, inplace=True)

# pd.set_option("display.max_rows", None)
# pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", 20)
pd.set_option("display.max_columns", 20)
csv_data.fillna(method='bfill', inplace=True)
csv_data.fillna(method='ffill', inplace=True)
csv_data.fillna(0, inplace=True)
csv_data

# # Data Preparation

# In[26]:


keyword_cols_aggregate = ['adopta_albero_impressions', 'regalar_arbol_impressions', 'regala_arbol_impressions',
                          'plantar_arbol_impressions', 'treedom_impressions']
csv_data['keywords_impressions'] = csv_data[keyword_cols_aggregate].sum(axis=1)

csv_data.drop(keyword_cols_aggregate, axis=1, inplace=True)

s_mediapartner_aggregate = ['s_mediapartner', 's_partner']
csv_data['s_partners'] = csv_data[s_mediapartner_aggregate].sum(axis=1)

csv_data.drop(s_mediapartner_aggregate, axis=1, inplace=True)

s_influencer_aggregate = ['s_influencer', 's_affiliate']
csv_data['s_influencers'] = csv_data[s_influencer_aggregate].sum(axis=1)

csv_data.drop(s_influencer_aggregate, axis=1, inplace=True)

s_other_aggregate = ['email_campaigns_sessions', 's_partners']
csv_data['s_others'] = csv_data[s_other_aggregate].sum(axis=1)

csv_data.drop(s_other_aggregate, axis=1, inplace=True)

# products_vars = [col for col in df.columns if 'avg' in col]

# for p in products_vars:
# for index, row in csv_data.iterrows():
# if row[p] != 0:
# csv_data.at[index, p] = 1
# else:
# csv_data.at[index, p] = 0


# # Prophet

# In[27]:


df = prophet(csv_data, 'date', 'conversions', window_start='2021-02-28', national_holidays_abbreviation='ES',
             future_dataframe_periods=365, plot_prophet=True, daily_seasonality=False)

# In[28]:


df

# # Spends

# In[7]:


medias_google = [col for col in df.columns if 'spend' in col if 'g_' in col]
medias_fb = [col for col in df.columns if 'spend' in col if 'fb_' in col]
medias_others = [col for col in df.columns if 'spend' in col if 'fb_' not in col if 'g_' not in col]

media = medias_google + medias_fb + medias_others

spends_df = spend_to_dataset(df, media)
spends_df

# In[8]:


spends, response_get_budget = getBudget(df, 'date', 'conversions', media, '2022-02-28')
print(spends, np.sum(spends), response_get_budget)

# # Correlation

# In[29]:


pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
df.corr()

# In[51]:


organic = ['s_organic', 's_referral', 's_influencers', 's_direct', 's_others', 'keywords_impressions']
context = ['tickets_count']

# product_vars = [col for col in df.columns if 'avg' in col]

prophet_vars = ['trend', 'yearly', 'monthly', 'weekly', 'holidays']
# prophet_vars = ['day_week', 'month', 'festivo']

all_features = media + organic + context + prophet_vars  # + product_vars

# In[52]:


X = df[all_features]
y = df['conversions']

result_ols, model_ols = ols(X, y, constant=True)

# # Nested Model

# In[32]:


# Sub-model describes Keywords Impressions using Google and Facebook's Media Spents
# Mail model uses all other variables and the sub-model to describe conversions
# medias_main = medias_google + medias_fb

# result, model, metrics_values, sub_result, sub_model, sub_metric_values = mainNestedModel(df, medias_main, 'keywords_impressions', all_variables, 'conversions', sub_model_regression = 'linear', sub_metric = ['rsq', 'nrmse', 'mape'], return_sub_metric = True, model_regression = 'ridge', metric = ['rsq', 'nrmse', 'mape'], return_metric = True)


# # Ridge Regression

# In[53]:


#result_ridge, model_ridge = ridge(df, X.columns, 'conversions', 'Ridge', ridge_number=21,
                                  #metric=['rsq', 'nrmse', 'mape'])

# In[55]:


#show_prediction_vs_actual_graph_with_error(result_ridge, result_ridge['conversions'], result_ridge['prediction'],
                                           #'date', 'revenue', name_model='')

# In[56]:


#show_coefficients(all_features, model_ridge, 'Ridge')

# # Linear Regression

# In[36]:


result_linear, model_linear = linear(df, X.columns, 'conversions', 'Linear', metric=['rsq', 'nrmse', 'mape'])

# In[37]:


#show_prediction_vs_actual_graph_with_error(result_linear, result_linear['conversions'], result_linear['prediction'],
                                           #'date', 'conversions', name_model='')

# In[38]:


#show_coefficients(all_features, model_linear, 'Linear')

# # LogLog Linear Regression

# In[39]:


#trasformations_log_columns = media + organic
#not_log_columns = prophet_vars + context

# In[40]:


#result_logLog_linear, model_logLog_linear = logLog(df, trasformations_log_columns, not_log_columns, 'conversions',
                                                   #'logLog', model_regression='linear', metric=['rsq', 'nrmse', 'mape'])

# In[41]:


# show_prediction_vs_actual_graph(result_logLog, 'date', 'conversions', 'prediction')


# In[42]:


#show_prediction_vs_actual_graph_with_error(result_logLog_linear, result_logLog_linear['conversions'],
                                           #result_logLog_linear['prediction'], 'date', 'conversions', name_model='')

# In[43]:


#show_coefficients(all_features, model_logLog_linear, 'Log Log')

# # LogLog Ridge Regression

# In[44]:


#result_logLog_ridge, model_logLog_ridge = logLog(df, trasformations_log_columns, not_log_columns, 'conversions',
                                                 #'logLog', model_regression='ridge', metric=['rsq', 'nrmse', 'mape'])

# In[45]:


#show_prediction_vs_actual_graph_with_error(result_logLog_ridge, result_logLog_ridge['conversions'],
                                           #result_logLog_ridge['prediction'], 'date', 'conversions', name_model='')

# In[46]:


#show_coefficients(all_features, model_logLog_ridge, 'Log Log Ridge')

# # Modello Ridge

# In[47]:

#hyperparameters_dict = instrum_variables_nevergrad(media, organic + prophet_vars + context, force_coeffs=True, use_intercept=True, use_adstock=True,
                                                   #use_saturation=True, adstock_type='weibull')
# hyperparameters_dict['ridge_number'] = {'lower': 0, 'upper': None}
# hyperparameters_dict['s_organic'] = {'lower': 0, 'upper': None}
# hyperparameters_dict['s_referral'] = {'lower': 0, 'upper': None}
# hyperparameters_dict['s_influencers'] = {'lower': 0, 'upper': None}
# hyperparameters_dict['s_direct'] = {'lower': 0, 'upper': None}
# hyperparameters_dict['s_others'] = {'lower': 0, 'upper': None}
# hyperparameters_dict['keywords_impressions'] = {'lower': 0, 'upper': None}
#
# metric, result, model, coeff, metric_array = nevergrad_model(df, hyperparameters_dict, media, organic + prophet_vars + context, 'conversions',
#                                                              model_regression='logLog', X_transformations_columns = media + organic, model_regression_log_log='ridge',
#                                                              ridge_number=11, metric_return='mape', force_coeffs=True,   budget=1000)
#,
#metric, result, model, coeff, metric_array = nevergrad_model(df, hyperparameters_dict, media, organic + prophet_vars + context, 'conversions',
                                                             #model_regression='ridge',
                                                             #ridge_number=11, metric_return='mape', force_coeffs=True, budget=500)
#print(coeff)
#print(model.coef_)

# def build_model(b1, b2, b3, b4, b5, b6, b7, b8, b11, b13, b14, b15, b16, b17, b18, b19,
#                 b20, b21, b22, b23, b24, b0,  # b26, b27, b28, b29, b30, b31, b32, b33,
#                 g_discovery_spend_scale, g_discovery_spend_shape, g_discovery_spend_beta,
#                 g_display_spend_scale, g_display_spend_shape, g_display_spend_beta,
#                 g_performance_max_spend_scale, g_performance_max_spend_shape, g_performance_max_spend_beta,
#                 g_search_spend_scale, g_search_spend_shape, g_search_spend_beta,
#                 g_video_spend_scale, g_video_spend_shape, g_video_spend_beta,
#                 fb_re_spend_scale, fb_re_spend_shape, fb_re_spend_beta,
#                 fb_pr_spend_scale, fb_pr_spend_shape, fb_pr_spend_beta,
#                 tiktok_learn_spend_scale, tiktok_learn_spend_shape, tiktok_learn_spend_beta,
#                 # microsoft_spend_scale, microsoft_spend_shape, microsoft_spend_beta,
#                 # linkedin_spend_scale, linkedin_spend_shape, linkedin_spend_beta,
#                 influencer_spend_scale, influencer_spend_shape, influencer_spend_beta):
#     # Google
#     x1 = df['g_discovery_spend']
#     x2 = df['g_display_spend']
#     x3 = df['g_performance_max_spend']
#     x4 = df['g_search_spend']
#     x5 = df['g_video_spend']
#
#     x1_adstock = adstock_weibull(x1, g_discovery_spend_scale, g_discovery_spend_shape).replace([np.inf, -np.inf], 0)
#     x2_adstock = adstock_weibull(x2, g_display_spend_scale, g_display_spend_shape).replace([np.inf, -np.inf], 0)
#     x3_adstock = adstock_weibull(x3, g_performance_max_spend_scale, g_performance_max_spend_shape).replace(
#         [np.inf, -np.inf], 0)
#     x4_adstock = adstock_weibull(x4, g_search_spend_scale, g_search_spend_shape).replace([np.inf, -np.inf], 0)
#     x5_adstock = adstock_weibull(x5, g_video_spend_scale, g_video_spend_shape).replace([np.inf, -np.inf], 0)
#
#     x1 = saturation(x1_adstock, g_discovery_spend_beta)
#     x2 = saturation(x2_adstock, g_display_spend_beta)
#     x3 = saturation(x3_adstock, g_performance_max_spend_beta)
#     x4 = saturation(x4_adstock, g_search_spend_beta)
#     x5 = saturation(x5_adstock, g_video_spend_beta)
#
#     # Facebook
#     x6 = df['fb_re_spend']
#     x7 = df['fb_pr_spend']
#
#     x6_adstock = adstock_weibull(x6, fb_re_spend_scale, fb_re_spend_shape).replace([np.inf, -np.inf], 0)
#     x7_adstock = adstock_weibull(x7, fb_pr_spend_scale, fb_pr_spend_shape).replace([np.inf, -np.inf], 0)
#
#     x6 = saturation(x6_adstock, fb_re_spend_beta)
#     x7 = saturation(x7_adstock, fb_pr_spend_beta)
#
#     # Other Medias
#     x8 = df['tiktok_learn_spend']
#     # x9 = df['microsoft_spend']
#     # x10 = df['linkedin_spend']
#     x11 = df['influencer_spend']
#
#     x8_adstock = adstock_weibull(x8, tiktok_learn_spend_scale, tiktok_learn_spend_shape).replace([np.inf, -np.inf], 0)
#     # x9_adstock = adstock_weibull(x9, microsoft_spend_scale, microsoft_spend_shape).replace([np.inf, -np.inf], 0)
#     # x10_adstock = adstock_weibull(x10, linkedin_spend_scale, linkedin_spend_shape).replace([np.inf, -np.inf], 0)
#     x11_adstock = adstock_weibull(x11, influencer_spend_scale, influencer_spend_shape).replace([np.inf, -np.inf], 0)
#
#     x8 = saturation(x8_adstock, tiktok_learn_spend_beta)
#     # x9 = saturation(x9_adstock, microsoft_spend_beta)
#     # x10 = saturation(x10_adstock, linkedin_spend_beta)
#     x11 = saturation(x11_adstock, influencer_spend_beta)
#
#     # Google
#     df_transf['g_discovery_spend'] = x1
#     df_transf['g_display_spend'] = x2
#     df_transf['g_performance_max_spend'] = x3
#     df_transf['g_search_spend'] = x4
#     df_transf['g_video_spend'] = x5
#
#     # Facebook
#     df_transf['fb_re_spend'] = x6
#     df_transf['fb_pr_spend'] = x7
#
#     # Other Medias
#     df_transf['tiktok_learn_spend'] = x8
#     # df_transf['microsoft_spend'] = x9
#     # df_transf['linkedin_spend'] = x10
#     df_transf['influencer_spend'] = x11
#
#     X = df_transf[all_features]
#     y = df_transf['conversions']
#
#     X_train, X_test, y_train, y_test = train_test_split(X, y)
#
#     model = Ridge(22)
#
#     model.fit(X_train, y_train)
#
#     coefs = [b1] + [b2] + [b3] + [b4] + [b5] + [b6] + [b7] + [b8] + [b11] + [b13] + [b14] + [b15] + [b16] + [b17] + [
#         b18] + [b19] + [b20] + [b21] + [b22] + [b23] + [b24]
#     model.coef_ = np.array(coefs)
#     model.intercept_ = b0
#
#     # Setting the Result Dataset
#     result = df_transf.copy()
#
#     result['prediction'] = model.predict(X)
#
#     nrmse_val = show_nrmse(result['conversions'], result['prediction'])
#     mape_val = show_mape(result['conversions'], result['prediction'])
#     rsquared_val = show_rsquared(result['conversions'], result['prediction'])
#
#     print(rsquared_val, nrmse_val, mape_val)
#
#     mape_array.append(mape_val)
#
#     return mape_val
#
#
# # In[48]:
#
#
# instrum = ng.p.Instrumentation(
#     # alpha = ng.p.Scalar(lower=0),
#
#     b1=ng.p.Scalar(lower=0),
#     b2=ng.p.Scalar(lower=0),
#     b3=ng.p.Scalar(lower=0),
#     b4=ng.p.Scalar(lower=0),
#     b5=ng.p.Scalar(lower=0),
#     b6=ng.p.Scalar(lower=0),
#     b7=ng.p.Scalar(lower=0),
#     b8=ng.p.Scalar(lower=0),
#     # b9 = ng.p.Scalar(lower=0),
#     # b10 = ng.p.Scalar(lower=0),
#     b11=ng.p.Scalar(lower=0),
#
#     # b12 = ng.p.Scalar(),
#     b13=ng.p.Scalar(lower=0),
#     b14=ng.p.Scalar(lower=0),
#     b15=ng.p.Scalar(lower=0),
#     b16=ng.p.Scalar(lower=0),
#     b17=ng.p.Scalar(lower=0),
#     b18=ng.p.Scalar(lower=0),
#     b19=ng.p.Scalar(upper=0),
#     b20=ng.p.Scalar(),
#     b21=ng.p.Scalar(),
#     b22=ng.p.Scalar(),
#     b23=ng.p.Scalar(),
#     b24=ng.p.Scalar(),
#     # b25 = ng.p.Scalar(),
#     # b26 = ng.p.Scalar(),
#     # b27 = ng.p.Scalar(),
#     # b28 = ng.p.Scalar(),
#     # b29 = ng.p.Scalar(),
#     # b30 = ng.p.Scalar(),
#     # b31 = ng.p.Scalar(),
#     # b32 = ng.p.Scalar(),
#     # b33 = ng.p.Scalar(),
#
#     b0=ng.p.Scalar(),
#
#     g_discovery_spend_scale=ng.p.Scalar(lower=0, upper=0.1),
#     g_discovery_spend_shape=ng.p.Scalar(lower=0, upper=2),
#     g_discovery_spend_beta=ng.p.Scalar(lower=0, upper=1),
#     g_display_spend_scale=ng.p.Scalar(lower=0, upper=0.1),
#     g_display_spend_shape=ng.p.Scalar(lower=0, upper=2),
#     g_display_spend_beta=ng.p.Scalar(lower=0, upper=1),
#     g_performance_max_spend_scale=ng.p.Scalar(lower=0, upper=0.1),
#     g_performance_max_spend_shape=ng.p.Scalar(lower=0, upper=2),
#     g_performance_max_spend_beta=ng.p.Scalar(lower=0, upper=1),
#     g_search_spend_scale=ng.p.Scalar(lower=0, upper=0.1),
#     g_search_spend_shape=ng.p.Scalar(lower=0, upper=2),
#     g_search_spend_beta=ng.p.Scalar(lower=0, upper=1),
#     g_video_spend_scale=ng.p.Scalar(lower=0, upper=0.1),
#     g_video_spend_shape=ng.p.Scalar(lower=0, upper=2),
#     g_video_spend_beta=ng.p.Scalar(lower=0, upper=1),
#
#     fb_re_spend_scale=ng.p.Scalar(lower=0, upper=0.1),
#     fb_re_spend_shape=ng.p.Scalar(lower=0, upper=2),
#     fb_re_spend_beta=ng.p.Scalar(lower=0, upper=1),
#     fb_pr_spend_scale=ng.p.Scalar(lower=0, upper=0.1),
#     fb_pr_spend_shape=ng.p.Scalar(lower=0, upper=2),
#     fb_pr_spend_beta=ng.p.Scalar(lower=0, upper=1),
#
#     tiktok_learn_spend_scale=ng.p.Scalar(lower=0, upper=0.1),
#     tiktok_learn_spend_shape=ng.p.Scalar(lower=0, upper=2),
#     tiktok_learn_spend_beta=ng.p.Scalar(lower=0, upper=1),
#
#     # microsoft_spend_scale = ng.p.Scalar(lower=0, upper=0.1),
#     # microsoft_spend_shape = ng.p.Scalar(lower=0, upper=2),
#     # microsoft_spend_beta = ng.p.Scalar(lower=0, upper=1),
#
#     # linkedin_spend_scale = ng.p.Scalar(lower=0, upper=0.1),
#     # linkedin_spend_shape = ng.p.Scalar(lower=0, upper=2),
#     # linkedin_spend_beta = ng.p.Scalar(lower=0, upper=1),
#
#     influencer_spend_scale=ng.p.Scalar(lower=0, upper=0.1),
#     influencer_spend_shape=ng.p.Scalar(lower=0, upper=2),
#     influencer_spend_beta=ng.p.Scalar(lower=0, upper=1)
# )
#
# optimizer = ng.optimizers.TwoPointsDE(parametrization=instrum, budget=1000)
# recommendation = optimizer.minimize(build_model)
#
# # NGOpt
# # TwoPointsDE
# recommendation.value
#
#
# # In[49]:
#
#
# def build_model(b1, b2, b3, b4, b5, b6, b7, b8, b11, b13, b14, b15, b16, b17, b18, b19,
#                 b20, b21, b22, b23, b24, b0,  # b26, b27, b28, b29, b30, b31, b32, b33,
#                 g_discovery_spend_scale, g_discovery_spend_shape, g_discovery_spend_beta,
#                 g_display_spend_scale, g_display_spend_shape, g_display_spend_beta,
#                 g_performance_max_spend_scale, g_performance_max_spend_shape, g_performance_max_spend_beta,
#                 g_search_spend_scale, g_search_spend_shape, g_search_spend_beta,
#                 g_video_spend_scale, g_video_spend_shape, g_video_spend_beta,
#                 fb_re_spend_scale, fb_re_spend_shape, fb_re_spend_beta,
#                 fb_pr_spend_scale, fb_pr_spend_shape, fb_pr_spend_beta,
#                 tiktok_learn_spend_scale, tiktok_learn_spend_shape, tiktok_learn_spend_beta,
#                 # microsoft_spend_scale, microsoft_spend_shape, microsoft_spend_beta,
#                 # linkedin_spend_scale, linkedin_spend_shape, linkedin_spend_beta,
#                 influencer_spend_scale, influencer_spend_shape, influencer_spend_beta):
#     # Google
#     x1 = df['g_discovery_spend']
#     x2 = df['g_display_spend']
#     x3 = df['g_performance_max_spend']
#     x4 = df['g_search_spend']
#     x5 = df['g_video_spend']
#
#     x1_adstock = adstock_weibull(x1, g_discovery_spend_scale, g_discovery_spend_shape).replace([np.inf, -np.inf], 0)
#     x2_adstock = adstock_weibull(x2, g_display_spend_scale, g_display_spend_shape).replace([np.inf, -np.inf], 0)
#     x3_adstock = adstock_weibull(x3, g_performance_max_spend_scale, g_performance_max_spend_shape).replace(
#         [np.inf, -np.inf], 0)
#     x4_adstock = adstock_weibull(x4, g_search_spend_scale, g_search_spend_shape).replace([np.inf, -np.inf], 0)
#     x5_adstock = adstock_weibull(x5, g_video_spend_scale, g_video_spend_shape).replace([np.inf, -np.inf], 0)
#
#     x1 = saturation(x1_adstock, g_discovery_spend_beta)
#     x2 = saturation(x2_adstock, g_display_spend_beta)
#     x3 = saturation(x3_adstock, g_performance_max_spend_beta)
#     x4 = saturation(x4_adstock, g_search_spend_beta)
#     x5 = saturation(x5_adstock, g_video_spend_beta)
#
#     # Facebook
#     x6 = df['fb_re_spend']
#     x7 = df['fb_pr_spend']
#
#     x6_adstock = adstock_weibull(x6, fb_re_spend_scale, fb_re_spend_shape).replace([np.inf, -np.inf], 0)
#     x7_adstock = adstock_weibull(x7, fb_pr_spend_scale, fb_pr_spend_shape).replace([np.inf, -np.inf], 0)
#
#     x6 = saturation(x6_adstock, fb_re_spend_beta)
#     x7 = saturation(x7_adstock, fb_pr_spend_beta)
#
#     # Other Medias
#     x8 = df['tiktok_learn_spend']
#     # x9 = df['microsoft_spend']
#     # x10 = df['linkedin_spend']
#     x11 = df['influencer_spend']
#
#     x8_adstock = adstock_weibull(x8, tiktok_learn_spend_scale, tiktok_learn_spend_shape).replace([np.inf, -np.inf], 0)
#     # x9_adstock = adstock_weibull(x9, microsoft_spend_scale, microsoft_spend_shape).replace([np.inf, -np.inf], 0)
#     # x10_adstock = adstock_weibull(x10, linkedin_spend_scale, linkedin_spend_shape).replace([np.inf, -np.inf], 0)
#     x11_adstock = adstock_weibull(x11, influencer_spend_scale, influencer_spend_shape).replace([np.inf, -np.inf], 0)
#
#     x8 = saturation(x8_adstock, tiktok_learn_spend_beta)
#     # x9 = saturation(x9_adstock, microsoft_spend_beta)
#     # x10 = saturation(x10_adstock, linkedin_spend_beta)
#     x11 = saturation(x11_adstock, influencer_spend_beta)
#
#     # Google
#     df_transf['g_discovery_spend'] = x1
#     df_transf['g_display_spend'] = x2
#     df_transf['g_performance_max_spend'] = x3
#     df_transf['g_search_spend'] = x4
#     df_transf['g_video_spend'] = x5
#
#     # Facebook
#     df_transf['fb_re_spend'] = x6
#     df_transf['fb_pr_spend'] = x7
#
#     # Other Medias
#     df_transf['tiktok_learn_spend'] = x8
#     # df_transf['microsoft_spend'] = x9
#     # df_transf['linkedin_spend'] = x10
#     df_transf['influencer_spend'] = x11
#
#     X = df_transf[all_features]
#     y = df_transf['conversions']
#
#     X_train, X_test, y_train, y_test = train_test_split(X, y)
#
#     model = Ridge(22)
#
#     model.fit(X_train, y_train)
#
#     coefs = [b1] + [b2] + [b3] + [b4] + [b5] + [b6] + [b7] + [b8] + [b11] + [b13] + [b14] + [b15] + [b16] + [b17] + [
#         b18] + [b19] + [b20] + [b21] + [b22] + [b23] + [b24]
#     model.coef_ = np.array(coefs)
#     model.intercept_ = b0
#
#     # Setting the Result Dataset
#     result = df_transf.copy()
#
#     result['prediction'] = model.predict(X)
#
#     nrmse_val = show_nrmse(result['conversions'], result['prediction'])
#     mape_val = show_mape(result['conversions'], result['prediction'])
#     rsquared_val = show_rsquared(result['conversions'], result['prediction'])
#
#     print('RSQUARED: ', rsquared_val)
#     print('NRMSE: ', nrmse_val)
#     print('MAPE: ', mape_val)
#
#     return result, model
#
#
# result, model = build_model(**recommendation.value[1])

# In[24]:


show_mape_trend(metric_array)

# In[41]:

#
# metric = {}
# metric['rsq'] = 0.897
# metric['nrmse'] = 0.413
# metric['mape'] = 0.239
#
# # In[42]:
#
#
# save_metric_to_csv(metric, 'C:/Users/Federico/Downloads/KPIs.csv')
#
# # In[44]:
#
#
# coefficenti = show_coefficients(all_features, model, 'Ridge', graph=True)
#
# # In[23]:
#
#
# show_prediction_vs_actual_graph(result, 'date', 'conversions', 'prediction')
#
# # In[24]:
#
#
# pd.set_option("display.max_rows", 20)
# pd.set_option("display.max_columns", 20)
# result
#
# # In[25]:
#
#
# df_adstock_saturation, result_df_adstock = adstock_saturation_to_dataset(recommendation.value[1], 'weibull')
# save_dataset_to_csv(df_adstock_saturation, 'C:/Users/Federico/Downloads/treddom_ES_Adstock_Saturation.csv')
# df_adstock_saturation
#
# # In[27]:
#
#
# coefficenti_dict = {}
# for index, value in enumerate(coefficenti):
#     coefficenti_dict[index] = value
# coefficenti_dict['b0'] = model.intercept_
#
# # In[67]:
#
#
# # coefficenti = recommendation.value[1].copy()
# # del coefficenti['alpha']
# columns_coef = ['g_discovery_spend', 'g_display_spend', 'g_performance_max_spend', 'g_search_spend', 'g_video_spend',
#                 'fb_pr_spend', 'fb_re_spend', 'tiktok_learn_spend', 'influencer_spend',
#                 's_organic', 's_referral', 's_influencers', 's_direct', 's_others', 'keywords_impressions',
#                 # 'avg_p_cacao', 'avg_p_baobab', 'avg_p_asc2020', 'avg_p_pt2020', 'avg_p_ft_ag',
#                 'tickets_count', 'trend', 'yearly', 'monthly', 'weekly', 'holidays']
#
# # In[73]:
#
#
# df_saturation = df.copy()
#
# for index, row in df_saturation.iterrows():
#     for m in list(df_adstock_saturation['canale']):
#         df_saturation.at[index, m] = saturation(df_saturation.at[index, m], df_adstock_saturation.loc[
#             df_adstock_saturation['canale'] == m, 'saturation'].iloc[0])
#
# coef_array = coefficenti
# new_dict = {}
#
# for x in range(len(coef_array) - 1):
#     new_dict[columns_coef[x]] = df_saturation[columns_coef[x]] * coef_array[x]
#
# new_dict['intercept'] = coef_array[-1]
#
# pd.set_option("display.max_rows", 20)
# pd.set_option("display.max_columns", 20)
# df_saturation_response = pd.DataFrame(new_dict)

# In[144]:


# s_df = pd.merge(df['g_discovery_spend'], df_saturation_response['g_discovery_spend'], left_index=True, right_index=True)
# pd.set_option("display.max_rows", None)
# pd.set_option("display.max_columns", None)
# s_df


# In[145]:

#
# import plotly.express as px
#
# for m in media:
#     s_df = pd.merge(df[m], df_saturation_response[m], left_index=True, right_index=True)
#
#     # For each media remove all the 0 spend values as Log(0) can't be calculated
#     s_df[m + '_x'] = s_df[m + '_x'][s_df[m + '_x'] != 0]
#     s_df[m + '_y'] = s_df[m + '_y'][s_df[m + '_y'] != 0]
#     # saturation_df = saturation_df[(saturation_df[[media]] != 0).all(axis=1)]
#
#     # Create a Scatter Plot
#     fig = px.scatter(
#         # Our temporary DF with no 0 values
#         s_df,
#         # Media channel's name
#         x=m + '_x',
#         # Our output variable (Sales or Conversion)
#         y=m + '_y',
#         # Specify the type of trendline you want to show, use OLS if not sure
#         trendline="ols",
#         # Define the trendline as logarithmic, this will return curved functions
#         trendline_options=dict(log_x=True)
#     )
#     # Print Figure
#     fig.show()
#
# # In[158]:
#
#
# import plotly.express as px
#
# for m in media:
#     s_df = pd.merge(df[m], df_saturation_response[m], left_index=True, right_index=True)
#
#     # For each media remove all the 0 spend values as Log(0) can't be calculated
#     s_df[m + '_x'] = s_df[m + '_x'][s_df[m + '_x'] != 0]
#     s_df[m + '_y'] = s_df[m + '_y'][s_df[m + '_y'] != 0]
#     # saturation_df = saturation_df[(saturation_df[[media]] != 0).all(axis=1)]
#
#     # Create a Scatter Plot
#     fig = px.line(
#         # Our temporary DF with no 0 values
#         s_df,
#         # Media channel's name
#         x=m + '_x',
#         # Our output variable (Sales or Conversion)
#         y=m + '_y',
#         # Specify the type of trendline you want to show, use OLS if not sure
#         marker=True,
#         # Define the trendline as logarithmic, this will return curved functions
#         # trendline_options=dict(log_x=True)
#     )
#     # Print Figure
#     fig.show()
#
# # In[93]:
#
#
# df_aggregated, df_all_decomp = decomposition_to_dataset(result, coefficenti_dict, columns_coef, spends_df, media,
#                                                         'date', 'conversions', 'prediction')
# save_dataset_to_csv(df_all_decomp, 'C:/Users/Federico/Downloads/treddom_ES_Timeseries.csv')
#
# df_aggregated = pd.merge(how='left', left=df_aggregated, right=df_adstock_saturation, left_on='canale',
#                          right_on='canale')
# save_dataset_to_csv(df_aggregated, 'C:/Users/Federico/Downloads/treddom_ES_Decomposition.csv')
# df_aggregated
#
# # In[94]:
#
#
# df_all_decomp
#
# # In[95]:
#
#
# # lower_bounds = [100, spends[1]*0.6, spends[2]*0.6, spends[3]*0.6, spends[4]*0.6, spends[5]*0.6, spends[6]*0.6,
# # spends[7]*0.6, spends[8]*0.6]
# # upper_bounds = [spends[0]*1.5, spends[1]*1.5, spends[2]*1.5, spends[3]*1.5, spends[4]*1.5, spends[5]*1.5, spends[6]*1.5,
# # spends[7]*1.5, spends[8]*1.5]
#
# lower_bounds = [100, 0, 0, 50, 20, 50, 0, 0, 0]
# upper_bounds = [165, 60, 60, 165, 165, 165, 60, 60, 60]
#
# budget_allocator_df = budget_allocator(result, 'date', media, all_features, '2022-02-28',
#                                        model, spends, response_get_budget, lower_bounds, upper_bounds, 5000,
#                                        df_aggregated, algoritm='GN_ISRES')
# save_dataset_to_csv(budget_allocator_df, 'C:/Users/Federico/Downloads/treddom_ES_budget_allocator.csv')
# budget_allocator_df
#
# # In[ ]:
#
#
# # In[ ]:
#
#


