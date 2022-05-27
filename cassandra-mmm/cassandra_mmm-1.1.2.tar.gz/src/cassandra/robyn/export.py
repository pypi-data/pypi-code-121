import pandas as pd
import numpy as np
from scipy.stats import dweibull
import matplotlib.pyplot as plt
import plotly.express as px


def create_df_adstock_weibull(df, adstock_type, weibull_type='pdf', max_y=1, max_x=100, graph=False):
    df_dict = df.to_dict()
    new_dict = {}
    for key, value in df_dict.items():
        new_dict[key] = value['Initial Model']

    if adstock_type == 'weibull':
        result_df = pd.DataFrame()
        adstock_columns = [col.replace('_shapes', '') for col in new_dict.keys() if 'shapes' in col]

        for m in adstock_columns:
            shape_name = m + '_shapes'
            scale_name = m + '_scales'
            shape = new_dict[shape_name]
            scale = new_dict[scale_name]

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
            result_df = pd.concat([result_df, df_media])

        shapes = [col for col in new_dict.keys() if 'shapes' in col]
        adstocked_shapes = {key: new_dict[key] for key in shapes}
        scales = [col for col in new_dict.keys() if 'scales' in col]
        adstocked_scales = {key: new_dict[key] for key in scales}

        adstock_shapes_df = pd.DataFrame(list(adstocked_shapes.items()))
        adstock_shapes_df.rename(
            columns={adstock_shapes_df.columns[0]: 'canale', adstock_shapes_df.columns[1]: 'adstock_shapes'},
            inplace=True)
        adstock_shapes_df['canale'] = adstock_shapes_df.canale.str.replace('_shapes', '')

        adstock_scales_df = pd.DataFrame(list(adstocked_scales.items()))
        adstock_scales_df.rename(
            columns={adstock_scales_df.columns[0]: 'canale', adstock_scales_df.columns[1]: 'adstock_scales'},
            inplace=True)
        adstock_scales_df['canale'] = adstock_scales_df.canale.str.replace('_scales', '')

        adstock_df = pd.merge(left=adstock_shapes_df, right=adstock_scales_df, left_on='canale',
                              right_on='canale')

    if adstock_type == 'weibull':
        return adstock_df, result_df


def create_df_saturation(df_hyperparameters, df_spend_response, df_aggregated, graph=True):
    df_dict = df_hyperparameters.to_dict()
    new_dict = {}
    for key, value in df_dict.items():
        new_dict[key] = value['Initial Model']

    result_df = pd.DataFrame()
    saturation_columns = list(df_spend_response['canale'].unique())

    for m in saturation_columns:
        alpha_name = m + '_alphas'
        gamma_name = m + '_gammas'
        alpha = new_dict[alpha_name]
        gamma = new_dict[gamma_name]
        coef = df_aggregated['coef'].copy().loc[df_aggregated['rn'] == m][0]

        range_x = list(df_spend_response['spend'].copy().loc[df_spend_response['canale'] == m])
        max_x = max(range_x)
        min_x = min(range_x)

        range_y = list(df_spend_response['response'].copy().loc[df_spend_response['canale'] == m])
        max_y = max(range_y)

        gamma_trans = round(np.quantile(np.linspace(start=min_x, stop=max_x, num=100), gamma), 4)

        y_res = []
        for x in range_x:
            y_res.append((x ** alpha / (x ** alpha + gamma_trans ** alpha)) * coef)

        max_y_res = max(y_res)
        min_y_res = min(y_res)

        data = plt.plot(range_x, y_res)[0].get_data()
        df_new = pd.DataFrame(data).T
        df_new.rename(columns={df_new.columns[0]: 'x', df_new.columns[1]: 'y'},
                      inplace=True)

        for index, row in df_new.iterrows():
            df_new.at[index, 'y'] = ((df_new.at[index, 'y'] - df_new['y'].min()) / (
                    df_new['y'].max() - df_new['y'].min())) * (max_y_res - min_y_res) + min_y_res
            df_new.at[index, 'x'] = ((df_new.at[index, 'x'] - df_new['x'].min()) / (
                    df_new['x'].max() - df_new['x'].min())) * (max_x - min_x) + min_x

        if graph == True:
            title_graph = 'Saturation ' + m
            fig2 = px.line(x=df_new['x'], y=df_new['y'], title=title_graph)

            fig2.update_layout(
                xaxis_title=m + ' spend',
                yaxis_title=m + ' response')

            # TODO
            # fig2.add_trace(
            # go.Scatter(
            # mode='markers',
            # x=[df_new['x'].mean()],
            # marker=dict(
            # size=12),
            # name='mean spend'
            # )
            # )
            fig2.show()

        df_new['canale'] = m
        result_df = pd.concat([result_df, df_new])

    return result_df

def new_create_df_adstock_weibull(df, adstock_type, weibull_type='pdf', max_y=1, max_x=100, graph=False):
    df_dict = df.to_dict()
    new_dict = {}
    for key, value in df_dict.items():
        new_dict[key] = value['Initial Model']

    if adstock_type == 'weibull':
        result_df = pd.DataFrame()
        adstock_columns = [col.replace('_shapes', '') for col in new_dict.keys() if 'shapes' in col]

        for m in adstock_columns:
            shape_name = m + '_shapes'
            scale_name = m + '_scales'
            shape = new_dict[shape_name]
            scale = new_dict[scale_name]

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
            result_df = pd.concat([result_df, df_media])

        shapes = [col for col in new_dict.keys() if 'shapes' in col]
        adstocked_shapes = {key: new_dict[key] for key in shapes}
        scales = [col for col in new_dict.keys() if 'scales' in col]
        adstocked_scales = {key: new_dict[key] for key in scales}

        adstock_shapes_df = pd.DataFrame(list(adstocked_shapes.items()))
        adstock_shapes_df.rename(
            columns={adstock_shapes_df.columns[0]: 'canale', adstock_shapes_df.columns[1]: 'adstock_shapes'},
            inplace=True)
        adstock_shapes_df['canale'] = adstock_shapes_df.canale.str.replace('_shapes', '')

        adstock_scales_df = pd.DataFrame(list(adstocked_scales.items()))
        adstock_scales_df.rename(
            columns={adstock_scales_df.columns[0]: 'canale', adstock_scales_df.columns[1]: 'adstock_scales'},
            inplace=True)
        adstock_scales_df['canale'] = adstock_scales_df.canale.str.replace('_scales', '')

        adstock_df = pd.merge(left=adstock_shapes_df, right=adstock_scales_df, left_on='canale',
                              right_on='canale')

    if adstock_type == 'weibull':
        return adstock_df, result_df
