#!/usr/bin/env python
# Created by "Thieu" at 15:22, 18/05/2022 ----------%                                                                               
#       Email: nguyenthieu2102@gmail.com            %                                                    
#       Github: https://github.com/thieu1995        %                         
# --------------------------------------------------%

# https://stackabuse.com/classification-in-python-with-scikit-learn-and-pandas/

## Coronary heart disease (CHD) in South Africa

import pandas as pd
from sklearn.linear_model import LogisticRegression


heart = pd.read_csv('data/coronary_heart_disease.csv', sep=',', header=0)
print(heart.head())
print(heart.describe())
print(heart.info())

y = heart.iloc[:,10]
X = heart.iloc[:,1:10]

LR = LogisticRegression(random_state=0, solver='lbfgs', multi_class='ovr').fit(X, y)
LR.predict(X.iloc[460:,:])
print(round(LR.score(X,y), 4))

