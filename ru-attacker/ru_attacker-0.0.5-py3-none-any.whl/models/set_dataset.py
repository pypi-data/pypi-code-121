import jsonlines
import pandas as pd


def get_data(filename):
    data = []
    with jsonlines.open(filename) as reader:
        for obj in reader:
            data.append(obj)
    df = pd.DataFrame(data)
    df["label"] = df["label"].map({'entailment': 1, 'not_entailment': 0})
    return df
