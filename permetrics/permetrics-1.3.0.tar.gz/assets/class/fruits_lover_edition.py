#!/usr/bin/env python
# Created by "Thieu" at 08:12, 18/05/2022 ----------%                                                                               
#       Email: nguyenthieu2102@gmail.com            %                                                    
#       Github: https://github.com/thieu1995        %                         
# --------------------------------------------------%

import pandas as pd
import matplotlib.pyplot as plt


fruits = pd.read_table('fruit_data_with_colors.txt')
print(fruits.head())
print(fruits.shape)
print(fruits['fruit_name'].unique())
print(fruits.groupby('fruit_name').size())

import seaborn as sns
sns.countplot(fruits['fruit_name'], label="Count")
plt.show()


fruits.drop('fruit_label', axis=1).plot(kind='box', subplots=True, layout=(2,2),
                                        sharex=False, sharey=False, figsize=(9,9),
                                        title='Box Plot for each input variable')
plt.savefig('fruits_box')
plt.show()
