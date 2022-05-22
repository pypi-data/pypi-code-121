import os

import pandas as pd
import torch
os.chdir(os.path.dirname(os.path.abspath(__file__)))


if __name__ == '__main__':    
    model = torch.load('no_cython_model.th')
    df = pd.read_csv('test_data/0.zip', nrows=32)
    print(model(df))