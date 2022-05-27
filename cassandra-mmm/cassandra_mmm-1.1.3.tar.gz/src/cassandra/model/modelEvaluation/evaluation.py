import pandas as pd
import numpy as np
from cassandra.data.trasformations.trasformations import saturation, saturation_hill
from scipy.stats import dweibull
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go


# def saturation_to_dataset(df, df_adstock_saturation):
#     df_saturation = df.copy()
#
#     for index, row in df.iterrows():
#         for m in list(df_adstock_saturation['canale']):
#             df_saturation.at[index, m] = saturation(df_saturation.at[index, m], df_adstock_saturation.loc[
#                 df_adstock_saturation['canale'] == m, 'saturation'].iloc[0])
#
#     return df_saturation


def response_regression_to_dataset(df, name_date_column, name_target_colum, name_prediction_column, coef_dict):
    df['intercept'] = 1
    new_dict = {}

    for key, value in coef_dict.items():
        new_dict[key] = df[key] * coef_dict[key]

    response_df = df[[name_date_column, name_target_colum, name_prediction_column]].join(pd.DataFrame(new_dict))
    return response_df


def decomposition_to_dataset(df, coef_dict, medias, spend_df, name_date_column, name_target_colum,
                             name_prediction_column, df_adstock_saturation, saturation_type='hill'):
    df_all_decomp = response_regression_to_dataset(df, name_date_column, name_target_colum, name_prediction_column,
                                                   coef_dict)

    coef_df = pd.DataFrame(list(coef_dict.items()))
    coef_df.rename(columns={coef_df.columns[0]: 'canale', coef_df.columns[1]: 'coef'}, inplace=True)

    decomp_agg_df = pd.DataFrame(df_all_decomp[coef_dict.keys()].sum(axis=0))
    decomp_agg_df.reset_index(inplace=True)
    decomp_agg_df.rename(columns={decomp_agg_df.columns[0]: 'canale', decomp_agg_df.columns[1]: 'xDecompAgg'},
                         inplace=True)

    decomp_mean_df = pd.DataFrame(df_all_decomp[coef_dict.keys()][df_all_decomp[coef_dict.keys()] > 0].mean(axis=0))
    decomp_mean_df.reset_index(inplace=True)
    decomp_mean_df.rename(columns={decomp_mean_df.columns[0]: 'canale', decomp_mean_df.columns[1]: 'xDecompMeanNon0'},
                          inplace=True)

    decomp_df = pd.merge(left=decomp_agg_df, right=decomp_mean_df, left_on='canale', right_on='canale')

    response_decomp_df = pd.merge(left=decomp_df, right=coef_df, left_on='canale', right_on='canale')

    response_decomp_df['xDecompPerc'] = response_decomp_df['xDecompAgg'] / response_decomp_df['xDecompAgg'].sum()
    response_decomp_df['xDecompMeanNon0Perc'] = response_decomp_df['xDecompMeanNon0'] / response_decomp_df[
        'xDecompMeanNon0'].sum()

    df_aggregated = pd.merge(how='left', left=response_decomp_df, right=spend_df, left_on='canale',
                             right_on='canale')

    df_aggregated = pd.merge(how='left', left=df_aggregated, right=df_adstock_saturation, left_on='canale',
                             right_on='canale')

    xDecompPercSum = 0

    for index, row in df_aggregated.iterrows():
        if row['canale'] in medias:
            xDecompPercSum = xDecompPercSum + row['xDecompPerc']

    for index, row in df_aggregated.iterrows():
        if row['canale'] in medias:
            df_aggregated.at[index, 'effect_share'] = (df_aggregated.at[index, 'xDecompPerc'] / xDecompPercSum) * 100
            df_aggregated.at[index, 'roi'] = (df_aggregated.at[index, 'xDecompAgg'] / df_aggregated.at[
                index, 'spesa']) * 100
            df_aggregated.at[index, 'cpa'] = df_aggregated.at[index, 'spesa'] / df_aggregated.at[
                index, 'xDecompAgg']
            if saturation_type == 'hill':
                df_aggregated.at[index, 'response_media'] = df_aggregated.at[index, 'coef'] * saturation_hill(
                    df_aggregated.at[
                        index, 'xDecompMeanNon0'],
                    df_aggregated.at[
                        index, 'saturation_alpha'], df_aggregated.at[
                        index, 'saturation_gamma'])
            else:
                df_aggregated.at[index, 'response_media'] = df_aggregated.at[index, 'coef'] * saturation(
                    df_aggregated.at[
                        index, 'xDecompMeanNon0'],
                    df_aggregated.at[
                        index, 'saturation_theta'])
            df_aggregated.at[index, 'roi_medio'] = (df_aggregated.at[index, 'response_media'] / df_aggregated.at[
                index, 'spesa_media']) * 100

    # TODO
    # df_aggregated = df_aggregated[['canale', 'xDecompAgg', 'xDecompMeanNon0', 'xDecompPerc', 'xDecompMeanNon0Perc', 'spesa', 'spesa_media',
    # 'spend_share', 'effect_share', 'spesa_totale', 'roi', 'roi_medio', 'cpa', 'response_media']]

    return df_aggregated, df_all_decomp


# TODO
def decomposition_without_hyperparameters_to_dataset(df, coef_dict, medias, spend_df, name_date_column,
                                                     name_target_colum,
                                                     name_prediction_column):
    df_all_decomp = response_regression_to_dataset(df, name_date_column, name_target_colum, name_prediction_column,
                                                   coef_dict)

    coef_df = pd.DataFrame(list(coef_dict.items()))
    coef_df.rename(columns={coef_df.columns[0]: 'canale', coef_df.columns[1]: 'coef'}, inplace=True)

    decomp_agg_df = pd.DataFrame(df_all_decomp[coef_dict.keys()].sum(axis=0))
    decomp_agg_df.reset_index(inplace=True)
    decomp_agg_df.rename(columns={decomp_agg_df.columns[0]: 'canale', decomp_agg_df.columns[1]: 'xDecompAgg'},
                         inplace=True)

    decomp_mean_df = pd.DataFrame(df_all_decomp[coef_dict.keys()][df_all_decomp[coef_dict.keys()] > 0].mean(axis=0))
    decomp_mean_df.reset_index(inplace=True)
    decomp_mean_df.rename(columns={decomp_mean_df.columns[0]: 'canale', decomp_mean_df.columns[1]: 'xDecompMeanNon0'},
                          inplace=True)

    decomp_df = pd.merge(left=decomp_agg_df, right=decomp_mean_df, left_on='canale', right_on='canale')

    response_decomp_df = pd.merge(left=decomp_df, right=coef_df, left_on='canale', right_on='canale')

    response_decomp_df['xDecompPerc'] = response_decomp_df['xDecompAgg'] / response_decomp_df['xDecompAgg'].sum()
    response_decomp_df['xDecompMeanNon0Perc'] = response_decomp_df['xDecompMeanNon0'] / response_decomp_df[
        'xDecompMeanNon0'].sum()

    df_aggregated = pd.merge(how='left', left=response_decomp_df, right=spend_df, left_on='canale',
                             right_on='canale')

    xDecompPercSum = 0

    for index, row in df_aggregated.iterrows():
        if row['canale'] in medias:
            xDecompPercSum = xDecompPercSum + row['xDecompPerc']

    for index, row in df_aggregated.iterrows():
        if row['canale'] in medias:
            df_aggregated.at[index, 'effect_share'] = (df_aggregated.at[index, 'xDecompPerc'] / xDecompPercSum) * 100
            df_aggregated.at[index, 'roi'] = (df_aggregated.at[index, 'xDecompAgg'] / df_aggregated.at[
                index, 'spesa']) * 100
            df_aggregated.at[index, 'cpa'] = df_aggregated.at[index, 'spesa'] / df_aggregated.at[
                index, 'xDecompAgg']

    return df_aggregated, df_all_decomp


def adstock_weibull_to_dataset(nevergrad_dict, media, weibull_type='pdf', max_y=1, max_x=100, graph=True):
    result_adstock_df = pd.DataFrame()
    adstock_columns = media

    for m in adstock_columns:
        shape_name = m + '_shape'
        scale_name = m + '_scale'
        shape = nevergrad_dict[shape_name]
        scale = nevergrad_dict[scale_name]

        x_array = np.array([1])
        x = np.repeat(x_array, 100, axis=0)  # see to del
        range_x = [x / 100 for x in range(1, 101)]

        if weibull_type == 'pdf':
            y = dweibull.pdf(range_x, shape, scale=scale)
        else:
            y = dweibull.cdf(range_x, shape, scale=scale)

        data = plt.plot(range(1, 101), y)[0].get_data()

        df_media = pd.DataFrame(data).T

        df_media.rename(columns={df_media.columns[0]: 'x', df_media.columns[1]: 'y'},
                        inplace=True)

        for index, row in df_media.iterrows():
            df_media.at[index, 'y'] = ((df_media.at[index, 'y'] - df_media['y'].min()) / (
                    df_media['y'].max() - df_media['y'].min())) * (max_y - 0) + 0
            df_media.at[index, 'x'] = ((df_media.at[index, 'x'] - df_media['x'].min()) / (
                    df_media['x'].max() - df_media['x'].min())) * (max_x - 0) + 0
        if graph == True:
            title_graph = 'Adstock weibull ' + m
            fig2 = px.line(x=df_media['x'], y=df_media['y'], title=title_graph)
            fig2.show()

        df_media['canale'] = m
        result_adstock_df = pd.concat([result_adstock_df, df_media])

    shapes = [col for col in nevergrad_dict.keys() if 'shape' in col]
    adstocked_shapes = {key: nevergrad_dict[key] for key in shapes}
    scales = [col for col in nevergrad_dict.keys() if 'scale' in col]
    adstocked_scales = {key: nevergrad_dict[key] for key in scales}

    adstock_shapes_df = pd.DataFrame(list(adstocked_shapes.items()))
    adstock_shapes_df.rename(
        columns={adstock_shapes_df.columns[0]: 'canale', adstock_shapes_df.columns[1]: 'adstock_shape'},
        inplace=True)
    adstock_shapes_df['canale'] = adstock_shapes_df.canale.str.replace('_shape', '')

    adstock_scales_df = pd.DataFrame(list(adstocked_scales.items()))
    adstock_scales_df.rename(
        columns={adstock_scales_df.columns[0]: 'canale', adstock_scales_df.columns[1]: 'adstock_scale'},
        inplace=True)
    adstock_scales_df['canale'] = adstock_scales_df.canale.str.replace('_scale', '')

    adstock_df = pd.merge(left=adstock_shapes_df, right=adstock_scales_df, left_on='canale',
                          right_on='canale')
    return adstock_df, result_adstock_df


def adstock_geometric_to_dataset(nevergrad_dict, graph=True):
    thetas = [col for col in nevergrad_dict.keys() if 'theta' in col]
    adstocked = {key: nevergrad_dict[key] for key in thetas}

    adstock_df = pd.DataFrame(list(adstocked.items()))
    adstock_df.rename(columns={adstock_df.columns[0]: 'canale', adstock_df.columns[1]: 'adstock_theta'},
                      inplace=True)
    adstock_df['canale'] = adstock_df.canale.str.replace('_theta', '')

    if graph == True:
        fig = go.Figure(go.Bar(
            x=round(adstock_df['adstock_theta'] * 100, 2),
            y=adstock_df['canale'],
            orientation='h'),
            layout=dict(height=700, width=1000, xaxis_title='adstock geometric (%)', yaxis_title='canale',
                        title='Geometric Adstock', legend_title='Legend')
        )

        fig.show()
    return adstock_df


def saturation_hill_to_dataset(nevergrad_dict, media, graph=True):
    saturation_columns = media
    result_saturation_df = pd.DataFrame()

    for m in saturation_columns:
        alpha_name = m + '_alpha'
        gamma_name = m + '_gamma'
        alpha = nevergrad_dict[alpha_name]
        gamma = nevergrad_dict[gamma_name]
        hillCollect = pd.DataFrame()

        range_x = [x for x in range(1, 101)]

        hillCollect['x'] = range_x
        for index, row in hillCollect.iterrows():
            hillCollect.at[index, 'y'] = row['x'] ** alpha / (row['x'] ** alpha + (gamma * 100) ** alpha)

        if graph:
            title_graph = 'Saturation Hill Alpha' + m
            fig_sat_alpha = px.line(x=hillCollect['x'], y=hillCollect['y'], title=title_graph)
            fig_sat_alpha.show()

        hillCollect['canale'] = m

        result_saturation_df = pd.concat([result_saturation_df, hillCollect])

    alphas = [col for col in nevergrad_dict.keys() if 'alpha' in col]
    saturationed_alphas = {key: nevergrad_dict[key] for key in alphas}
    gammas = [col for col in nevergrad_dict.keys() if 'gamma' in col]
    saturationed_gammas = {key: nevergrad_dict[key] for key in gammas}

    saturation_alphas_df = pd.DataFrame(list(saturationed_alphas.items()))
    saturation_alphas_df.rename(
        columns={saturation_alphas_df.columns[0]: 'canale',
                 saturation_alphas_df.columns[1]: 'saturation_alpha'},
        inplace=True)
    saturation_alphas_df['canale'] = saturation_alphas_df.canale.str.replace('_alpha', '')

    saturation_gammas_df = pd.DataFrame(list(saturationed_gammas.items()))
    saturation_gammas_df.rename(
        columns={saturation_gammas_df.columns[0]: 'canale',
                 saturation_gammas_df.columns[1]: 'saturation_gamma'},
        inplace=True)
    saturation_gammas_df['canale'] = saturation_gammas_df.canale.str.replace('_gamma', '')

    saturation_df = pd.merge(left=saturation_alphas_df, right=saturation_gammas_df, left_on='canale',
                             right_on='canale')

    return saturation_df, result_saturation_df


def saturation_to_dataset(nevergrad_dict):
    betas = [col for col in nevergrad_dict.keys() if 'beta' in col]
    saturationed = {key: nevergrad_dict[key] for key in betas}
    saturation_df = pd.DataFrame(list(saturationed.items()))
    saturation_df.rename(columns={saturation_df.columns[0]: 'canale', saturation_df.columns[1]: 'saturation'},
                         inplace=True)
    saturation_df['canale'] = saturation_df.canale.str.replace('_beta', '')

    return saturation_df


def adstock_saturation_to_dataset(nevergrad_dict, use_adstock=True, adstock_type='weibull', weibull_type='pdf',
                                  use_saturation=True, saturation_type='hill', max_y=1, max_x=100, graph=True):
    media = [col for col in nevergrad_dict.keys() if '_spend' in col if not '_spend_' in col]
    if use_adstock:
        if adstock_type == 'weibull':
            adstock_df, result_adstock_df = adstock_weibull_to_dataset(nevergrad_dict, media, weibull_type, max_y,
                                                                       max_x, graph)

        elif adstock_type == 'geometric':
            adstock_df = adstock_geometric_to_dataset(nevergrad_dict, graph)

    else:
        adstock_df = pd.DataFrame({'canale': media})
    if use_saturation:
        if saturation_type == 'hill':
            saturation_df, result_saturation_df = saturation_hill_to_dataset(nevergrad_dict, media, graph)

        else:
            saturation_df = saturation_to_dataset(nevergrad_dict)
    else:
        saturation_df = pd.DataFrame({'canale': media})

    df_adstock_saturation = pd.merge(left=adstock_df, right=saturation_df, left_on='canale',
                                     right_on='canale')

    if use_adstock:
        if adstock_type == 'weibull':
            if saturation_type == 'hill':
                return df_adstock_saturation, result_adstock_df, result_saturation_df
            else:
                return df_adstock_saturation, result_adstock_df

        elif adstock_type == 'geometric':
            if saturation_type == 'hill':
                return df_adstock_saturation, result_saturation_df
            else:
                return df_adstock_saturation
    else:
        if use_saturation:
            if saturation_type == 'hill':
                return df_adstock_saturation, result_saturation_df
            else:
                return df_adstock_saturation
        else:
            return df_adstock_saturation


def spend_to_dataset(df, medias):
    total_spend_dict = {key: df[key].sum() for key in medias}
    total_spend_df = pd.DataFrame(list(total_spend_dict.items()))
    total_spend_df.rename(columns={total_spend_df.columns[0]: 'canale', total_spend_df.columns[1]: 'spesa'},
                          inplace=True)

    mean_spend_dict = {key: df[key].mean() for key in medias}
    mean_spend_df = pd.DataFrame(list(mean_spend_dict.items()))
    mean_spend_df.rename(columns={mean_spend_df.columns[0]: 'canale', mean_spend_df.columns[1]: 'spesa_media'},
                         inplace=True)

    result_df = pd.merge(left=total_spend_df, right=mean_spend_df, left_on='canale',
                         right_on='canale')

    result_df['spesa_totale'] = sum(total_spend_dict.values())
    result_df['spend_share'] = (result_df['spesa'] * 100) / result_df['spesa_totale']

    return result_df


def saturation_to_dataset(df, df_adstock_saturation, coeffs, features, saturation_type='hill'):
    df_saturation = df.copy()

    if saturation_type == 'hill':
        for index, row in df_saturation.iterrows():
            for m in list(df_adstock_saturation['canale']):
                df_saturation.at[index, m] = saturation_hill(df_saturation.at[index, m], df_adstock_saturation.loc[
                    df_adstock_saturation['canale'] == m, 'saturation_alpha'].iloc[0], df_adstock_saturation.loc[
                                                                 df_adstock_saturation[
                                                                     'canale'] == m, 'saturation_gamma'].iloc[0])
    else:
        for index, row in df_saturation.iterrows():
            for m in list(df_adstock_saturation['canale']):
                df_saturation.at[index, m] = saturation(df_saturation.at[index, m], df_adstock_saturation.loc[
                    df_adstock_saturation['canale'] == m, 'saturation_theta'].iloc[0])

    coef_array = coeffs.copy()
    new_dict = {}

    for x in range(len(coef_array) - 1):
        new_dict[features[x]] = df_saturation[features[x]] * coef_array[x]

    df_saturation_response = pd.DataFrame(new_dict)
    return df_saturation_response


def create_coefs_dict(raccomendation_value):
    keys = [key for key, value in raccomendation_value.items() if '_spend_' not in key]
    values = [value for key, value in raccomendation_value.items() if '_spend_' not in key]

    coefs_dict = dict(zip(keys, values))

    return coefs_dict

# def decomposition_to_dataset(df, coef_dict, features, spend_df, medias, name_date_column, name_target_colum,
#                              name_prediction_column):
#     columns = features
#     coef_array = list(coef_dict.values())
#     result = df[columns].copy()
#
#     result['intercept'] = coef_array[-1]
#
#     coef_dict = {}
#
#     for x in range(len(coef_array) - 1):
#         coef_dict[columns[x]] = coef_array[x]
#
#     coef_dict['intercept'] = coef_array[-1]
#
#     df_all_decomp = response_regression_to_dataset(df, name_date_column, name_target_colum, name_prediction_column,
#                                                    coef_dict, features)
#
#     coef_df = pd.DataFrame(list(coef_dict.items()))
#     coef_df.rename(columns={coef_df.columns[0]: 'canale', coef_df.columns[1]: 'coef'}, inplace=True)
#
#     decomp_df = pd.DataFrame(df_all_decomp[result.keys()].sum(axis=0))
#     decomp_df.reset_index(inplace=True)
#     decomp_df.rename(columns={decomp_df.columns[0]: 'canale', decomp_df.columns[1]: 'xDecompAgg'},
#                      inplace=True)
#
#     response_decomp_df = pd.merge(left=decomp_df, right=coef_df, left_on='canale', right_on='canale')
#
#     response_decomp_df['xDecompPerc'] = response_decomp_df['xDecompAgg'] / response_decomp_df['xDecompAgg'].sum()
#
#     df_aggregated = pd.merge(how='left', left=response_decomp_df, right=spend_df, left_on='canale',
#                              right_on='canale')
#
#     xDecompPercSum = 0
#
#     for index, row in df_aggregated.iterrows():
#         if row['canale'] in medias:
#             xDecompPercSum = xDecompPercSum + row['xDecompPerc']
#
#     for index, row in df_aggregated.iterrows():
#         if row['canale'] in medias:
#             df_aggregated.at[index, 'effect_share'] = df_aggregated.at[index, 'xDecompPerc'] / xDecompPercSum
#             df_aggregated.at[index, 'roi'] = df_aggregated.at[index, 'xDecompAgg'] / df_aggregated.at[
#                 index, 'spesa_totale']
#
#     return df_aggregated, df_all_decomp
