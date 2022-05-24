from miacag.utils.sql_utils import getDataFromDatabase
from sklearn.metrics import f1_score, accuracy_score
import pandas as pd


def map_labels_to_OneTwoThree():
    labels_dict = {0: 0,
                   1: 1,
                   2: 2,
                   3: 2,
                   4: 2,
                   6: 2,
                   7: 2,
                   8: 2,
                   9: 0,
                   10: 2,
                   11: 2,
                   12: 2,
                   13: 1,
                   14: 2,
                   15: 2,
                   16: 2,
                   17: 2,
                   18: 2,
                   19: 2,
                   20: 2}
    return labels_dict


def appendDataFrame(sql_config, df_results, experiment_name):
    df, _ = getDataFromDatabase(sql_config)
    for label_name in sql_config["labels_names"]:
        f1_test_transformed = f1_score(
          df[label_name], df[label_name + '_predictions'], average='macro')

        df = df.replace(
          {label_name + '_predictions': map_labels_to_OneTwoThree()})

        df = df.replace(
          {label_name: map_labels_to_OneTwoThree()})

        f1_test = f1_score(
          df[label_name],
          df[label_name + '_predictions'], average='macro')

        acc_test = accuracy_score(
            df[label_name],
            df[label_name + '_predictions'])

        dictionary = {
          'Experiment name': [experiment_name],
          'Test F1 score on data labels transformed_{}'.format(
            label_name): [f1_test_transformed],
          'Test F1 score on three class labels_{}'.format(
            label_name): [f1_test],
          'Test acc on three class labels_{}'.format(
            label_name): [acc_test]
           }
        results_new = pd.DataFrame(dictionary)
        df_results = pd.concat([df_results, results_new])

    return df_results
