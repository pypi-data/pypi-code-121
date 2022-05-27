from cassandra.data.dataAnalysis.correlation import *
from cassandra.data.dataProcessing.prophet import *
from cassandra.data.featureSelection.ols import *
from cassandra.data.dataAnalysis.exploration.utils import show_media, show_no_media, create_df, define_features, show_correlation_network_graph
from cassandra.data.featureSelection.multicollinearity import check_multicollinearity
import pandas as pd
from IPython.core.display import display
from cassandra.model.modelEvaluation.plot import show_seasonality


def exploration(csv, name_date_column, name_target_column, dict_columns_aggregate={}, window_start='',
                window_end='', national_holidays_abbreviation='IT', future_dataframe_periods=14, plot_prophet=False,
                trend_seasonality=True, holidays_seasonality=True,
                daily_seasonality=True, weekly_seasonality=True, monthly_seasonality=True,
                yearly_seasonality=True, seasonality_mode='additive',
                media_split=True, show_graph_media=True, show_graph_no_media=True, method_corr='pearson',
                min_periods_corr=1, min_correlation=0.6, plot_for_line=5, show_only_one='',
                constant_ols=True):
    # create csv
    if dict_columns_aggregate:
        df = create_df(csv, dict_columns_aggregate)
    else:
        df = csv

    display(Markdown(f"# Dataset"))
    display(df)

    # create df with seasonality variables
    new_df = prophet(df=df, name_date_column=name_date_column, name_target_column=name_target_column,
                     window_start=window_start, window_end=window_end,
                     national_holidays_abbreviation=national_holidays_abbreviation,
                     future_dataframe_periods=future_dataframe_periods, plot_prophet=plot_prophet,
                     trend_seasonality=trend_seasonality, holidays_seasonality=holidays_seasonality,
                     daily_seasonality=daily_seasonality, weekly_seasonality=weekly_seasonality,
                     monthly_seasonality=monthly_seasonality, yearly_seasonality=yearly_seasonality,
                     seasonality_mode=seasonality_mode)

    # define variables and show graph each other
    if media_split:
        everything, media, organic, price, seasonality, other, no_media, no_organic, no_price, no_seasonality, media_google, media_fb, media_others = define_features(
            df=new_df, media_split=media_split, name_date_column=name_date_column, name_target_column=name_target_column)

        if show_graph_media:
            show_media(new_df, name_date_column, name_target_column, media, media_google, media_fb, media_others)
        if show_graph_no_media:
            show_no_media(new_df, name_date_column, name_target_column, organic, price, seasonality, other)

    else:
        everything, media, organic, price, seasonality, other, no_media, no_organic, no_price, no_seasonality = define_features(
            df=new_df, media_split=media_split, name_date_column=name_date_column, name_target_column=name_target_column)
        if show_graph_media:
            show_media(new_df, name_date_column, name_target_column, media)
        if show_graph_no_media:
            show_no_media(new_df, name_date_column, name_target_column, organic, price, seasonality, other)

    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    new_df.fillna(value=0, inplace=True)
    # df.fillna(method = 'bfill', inplace=True)
    # df.fillna(method = 'ffill', inplace=True)

    display(Markdown(f"# Modeling Seasonality"))
    seasonality_df = show_seasonality(new_df, seasonality, name_date_column)

    display(Markdown(f"## Check Pearson Correlation Metric to check various possible correlations"))
    corr = new_df.corr(method=method_corr, min_periods=min_periods_corr)
    display(corr)

    display(Markdown(f"## Network for Correlation"))
    show_correlation_network_graph(corr, min_correlation=min_correlation)

    display(Markdown(
        f"## Show through a scatterplot the relationship between each input variable and {name_target_column}"))
    show_relationship_between_variables(new_df, plot_for_line=plot_for_line, show_only_one=show_only_one)

    # Features Selection
    X = new_df[everything]
    y = new_df[name_target_column]

    # OLS model
    display(Markdown(f"## OLS Model"))
    result_ols, model_ols = ols(X, y, constant=constant_ols)

    # check for multicollinearity
    display(Markdown(f"## Check for multicollinearity"))
    check_multicollinearity(X)

    pd.set_option("display.max_rows", 20)
    pd.set_option("display.max_columns", 20)

    return new_df
