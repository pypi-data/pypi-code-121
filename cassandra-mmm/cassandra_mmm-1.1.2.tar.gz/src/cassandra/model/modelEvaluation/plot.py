import pandas as pd
import numpy as np
import plotly.express as px
from cassandra.model.modelEvaluation.evaluation import saturation_to_dataset
from sklearn import metrics
import plotly.graph_objects as go
import math


def show_nrmse(y_actual, y_pred, verbose=False):
    value = np.sqrt(np.mean((y_actual - y_pred) ** 2)) / (max(y_actual) - min(y_actual))
    passed = "✔️" if value < 0.15 else "❌"
    if verbose:
        return value, passed
    else:
        return value


def show_mape(y_actual, y_pred, verbose=False):
    # mean absolute percentage error
    x = np.abs((y_actual - y_pred) / y_actual)
    value = np.mean(x[~np.isinf(x)])
    passed = "✔️" if value < 0.15 else "❌"
    if verbose:
        return value, passed
    else:
        return value


def show_rsquared(y_actual, y_pred, verbose=False):
    # r squared
    value = round(metrics.r2_score(y_actual, y_pred), 3)
    passed = "✔️" if value > 0.8 else "❌"
    if verbose:
        return value, passed
    else:
        return value


def show_nrmse_old(y_actual, y_pred, verbose=False):
    # normalized root mean square error
    value = round(np.sqrt(metrics.mean_squared_error(y_actual, y_pred)) / np.mean(y_actual), 3)
    passed = "✔️" if value < 0.15 else "❌"
    if verbose:
        return value, passed
    else:
        return value


def show_mape_old(y_actual, y_pred, verbose=False):
    # mean absolute percentage error
    value = round(metrics.mean_absolute_error(y_actual, y_pred) / np.mean(y_actual), 3)
    passed = "✔️" if value < 0.15 else "❌"
    if verbose:
        return value, passed
    else:
        return value


def show_rssd(df, coefs, verbose=False):

    media = [col for col in df.columns if '_spend' in col]

    def get_effect_share(df, coefs):
        def effect_share(contribution_df):
            return (contribution_df.sum() / contribution_df.sum().sum()).values

        contr_df = {}

        for m in media:
            contr_df[m] = df[m] * coefs[media.index(m)]

        contr_df = pd.DataFrame.from_dict(contr_df)
        ef_share = effect_share(contr_df)

        return ef_share

    def get_spend_share(df):
        def spend_share(X_df):
            return (X_df.sum() / X_df.sum().sum()).values

        spend_df = {}

        for m in media:
            spend_df[m] = df[m]

        spend_df = pd.DataFrame.from_dict(spend_df)
        ss_share = spend_share(spend_df)

        return ss_share

    value = round(np.sqrt(sum((np.array(get_effect_share(df, coefs)) - np.array(get_spend_share(df))) ** 2)), 3)
    passed = "✔️" if value < 0.15 else "❌"

    if verbose:
        return value, passed
    else:
        return value


def show_rssd_aggregated(df_aggregated, medias, verbose=False):
    # mean absolute percentage error
    df_result = pd.DataFrame()

    for index, row in df_aggregated.iterrows():
        if row['canale'] in medias:
            df_result.at[index, 'share'] = (df_aggregated.at[index, 'effect_share'] - df_aggregated.at[
                index, 'spend_share']) ** 2

    value = math.sqrt(df_result.sum())

    passed = "✔️" if value < 0.15 else "❌"
    if verbose:
        return value, passed
    else:
        return value



def show_coefficients(features, model, name_model, graph=True):
    # Given model = LinearRegression() model already executed

    # Create an array of the variables you want to check coeffs
    # features = ['g_display_cost', 'g_shopping_cost', 'g_video_cost', 'g_search_brand_cost', 'g_search_no_brand_cost',
    #             'fb_cost', 'pinterest_cost', 'b_audience_cost', 'b_search_cost', 'avg_price',
    #             'solostove_organic_traffic', 'solostove_paid_traffic', 'trend_smokeless_fire_pit']

    coeffs = model.coef_.copy()
    new_features = features.copy()

    if model.intercept_:
        coeffs = np.append(coeffs, model.intercept_)
        new_features = np.append(new_features, 'intercept')

    roas = pd.DataFrame(data=coeffs, index=new_features, columns=['contribution'])
    title_graph = name_model + " Model Coefficients graph"
    if graph == True:

        fig = go.Figure(
            data=[go.Bar(x=roas.index, y=roas['contribution'])],
            layout=go.Layout(
                title=go.layout.Title(text=title_graph)
            )
        )

        fig.show()
        return coeffs
    else:
        return coeffs


def show_response_curves(df, df_adstock_saturation, coeffs, features, medias, saturation_type = 'hill'):
    df_response_curves = saturation_to_dataset(df, df_adstock_saturation, coeffs, features, saturation_type=saturation_type)

    for m in medias:
        s_df = pd.merge(df[m], df_response_curves[m], left_index=True, right_index=True)

        # For each media remove all the 0 spend values as Log(0) can't be calculated
        s_df[m + '_x'] = s_df[m + '_x'][s_df[m + '_x'] != 0]
        s_df[m + '_y'] = s_df[m + '_y'][s_df[m + '_y'] != 0]

        # Create a Scatter Plot
        fig = px.line(
            # Spends Media channel's name
            x=s_df[m + '_x'].sort_values(),
            # Response Media channel's name
            y=s_df[m + '_y'].sort_values()
        )
        fig.update_layout(
            xaxis_title=m + ' spend',
            yaxis_title=m + ' response')
        # Print Figure
        fig.show()

    return df_response_curves


def show_effect_share_vs_spend_share(df_aggregated, show_cpa=True):
    df_spend_var = df_aggregated.copy().dropna()
    fig = go.Figure()

    fig.add_bar(x=df_spend_var['canale'], y=round(df_spend_var['spend_share'], 2), name='spend_share',
                marker=dict(color="Purple"))
    fig.add_bar(x=df_spend_var['canale'], y=round(df_spend_var['effect_share'], 2), name='effect_share',
                marker=dict(color="MediumPurple"))

    if show_cpa:
        fig.add_scatter(x=df_spend_var['canale'], y=round(df_aggregated['cpa'], 2), mode="markers",
                        name='cpa',
                        marker=dict(size=20, color="LightSeaGreen"))
    else:
        fig.add_scatter(x=df_spend_var['canale'], y=round(df_spend_var['roi'], 2), mode="markers", name='roi',
                        marker=dict(size=20, color="LightSeaGreen"))

    fig.show()


def show_all_decomp_response(df_all_decomp, name_date_column, features, show_target=False, target='conversions',
                             show_target_prediction=False, name_prediction_column='prediction', nbins=None, bargap=0.2):
    if nbins:
        nbins = len(df_all_decomp)
    if show_target:
        features.append(target)
    if show_target_prediction:
        features.append(name_prediction_column)

    fig = px.histogram(df_all_decomp, x=name_date_column, y=features, nbins=nbins)
    fig.update_layout(bargap=bargap)
    fig.show()


def show_seasonality(df, seasonality_columns, name_date_column):
    df_seasonality = df.copy()[seasonality_columns]

    for s in seasonality_columns:
        if s == 'trend':
            trend_df = df.copy().drop_duplicates(keep='first', subset=[name_date_column])
            fig = px.line(
                x=trend_df[name_date_column],
                y=trend_df['trend'])
            fig.update_layout(
                xaxis_title='Date',
                yaxis_title='Trend')
            fig.show()

        if s == 'holidays':
            fig = px.line(
                x=pd.to_datetime(df[name_date_column]),
                y=df['holidays'])
            fig.update_layout(
                xaxis_title='Date',
                yaxis_title='Holidays')
            fig.show()

        if s == 'yearly':
            yearly_df = df.copy()
            yearly_df[name_date_column] = pd.to_datetime(yearly_df[name_date_column]).dt.dayofyear
            yearly_df = yearly_df.drop_duplicates(keep='first', subset=[name_date_column])
            fig = px.line(
                x=yearly_df[name_date_column].sort_values(),
                y=yearly_df['yearly'])
            fig.update_layout(
                xaxis_title='Day of year',
                yaxis_title='Yearly')
            fig.show()

        if s == 'monthly':
            monthly_df = df.copy()
            monthly_df[name_date_column] = pd.to_datetime(monthly_df[name_date_column]).dt.day
            monthly_df = monthly_df.drop_duplicates(keep='first', subset=[name_date_column])
            fig = px.line(
                x=monthly_df[name_date_column].sort_values(),
                y=monthly_df['monthly'])
            fig.update_layout(
                xaxis_title='Day of month',
                yaxis_title='Montly')
            fig.show()

        if s == 'weekly':
            weekly_df = df.copy()
            weekly_df[name_date_column] = pd.to_datetime(weekly_df[name_date_column]).dt.day_name()
            weekly_df = weekly_df.drop_duplicates(keep='first', subset=[name_date_column])
            fig = px.line(
                x=weekly_df[name_date_column],
                y=weekly_df['weekly'])
            fig.update_layout(
                xaxis_title='Days',
                yaxis_title='Weekly')
            fig.show()

        if s == 'daily':
            daily_df = df.copy()
            daily_df[name_date_column] = pd.to_datetime(daily_df[name_date_column]).dt.time
            daily_df = daily_df.drop_duplicates(keep='first', subset=[name_date_column])
            fig = px.line(
                x=daily_df[name_date_column],
                y=daily_df['daily'])
            fig.update_layout(
                xaxis_title='Hour of Day',
                yaxis_title='Daily')
            fig.show()

    return df_seasonality

# def show_geometric_adstock(df_adstock_saturation):
#     fig = go.Figure(go.Bar(
#         x=round(df_adstock_saturation['adstock'] * 100, 2),
#         y=df_adstock_saturation['canale'],
#         orientation='h'),
#         layout=dict(height=700, width=1000, xaxis_title='adstock geometric (%)', yaxis_title='canale',
#                     title='Geometric Adstock', legend_title='Legend')
#     )
#
#     fig.show()
