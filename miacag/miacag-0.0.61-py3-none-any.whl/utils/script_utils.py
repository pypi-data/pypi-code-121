import os
import pandas as pd


def mkFolder(dir):
    os.makedirs(dir, exist_ok=True)


def get_open_port():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


def create_empty_csv(output_csv_test, label_names):
    keys = ['Test F1 score on data labels transformed_',
            'Test F1 score on three class labels_',
            'Test acc on three class labels_']
    keys_ = []
    for key in keys:
        for label_name in label_names:
            keys_.append(key+label_name)

    keys_ = ['Experiment name'] + keys_
    values = [[] for i in range(0, len(keys_))]
    df = dict(zip(keys_, values))
    df_csv = pd.DataFrame.from_dict(df)
    df_csv.to_csv(output_csv_test)
    return df_csv
