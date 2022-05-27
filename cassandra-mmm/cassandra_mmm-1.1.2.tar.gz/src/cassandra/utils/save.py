import pandas as pd
from cassandra.model.modelEvaluation.evaluation import response_regression_to_dataset, decomposition_to_dataset, adstock_saturation_to_dataset, spend_to_dataset


def save_metric_to_csv(metric_dictionary, path_file_to_save):
    my_dict = [metric_dictionary]
    df = pd.DataFrame.from_dict(my_dict)
    df.to_csv(path_file_to_save, index = False, header=True)

def save_timeseries_to_csv(df, name_date_column, name_target_colum, name_prediction_column, coef_dict, features, path_file_to_save):
    response_df = response_regression_to_dataset(df, name_date_column, name_target_colum, name_prediction_column, coef_dict,
                                   features)
    response_df.to_csv(path_file_to_save, index = False, header=True)

def save_decomposition_to_csv(df, coef_dict, features, spend_df, medias, path_file_to_save):
    response_df = decomposition_to_dataset(df, coef_dict, features, spend_df, medias)
    response_df.to_csv(path_file_to_save, index = False, header=True)

def save_adstock_saturation_to_csv(dict_theta_and_beta, path_file_to_save):
    response_df = adstock_saturation_to_dataset(dict_theta_and_beta)
    response_df.to_csv(path_file_to_save, index = False, header=True)

def save_spend_to_csv(df, medias, path_file_to_save):
    response_df = spend_to_dataset(df, medias)
    response_df.to_csv(path_file_to_save, index = False, header=True)

def save_dataset_to_csv(df, path_file_to_save):
    df.to_csv(path_file_to_save, index = False, header=True)