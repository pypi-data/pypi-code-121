import os
import pandas as pd

def load_holidays():
    path = os.path.join(os.path.dirname(__file__), "dataset_holidays.csv")
    df = pd.read_csv(path, on_bad_lines='skip')
    return df