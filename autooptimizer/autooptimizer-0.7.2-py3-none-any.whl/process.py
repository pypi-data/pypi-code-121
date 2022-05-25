import numpy as np
import matplotlib.pyplot as plt

def outlier_removal(dataset):
    Q1 = np.quantile(dataset, 0.25)
    Q3 = np.quantile(dataset, 0.75)
    IQR = Q3 - Q1
    lower_extreme = Q1 - (1.5 * IQR)
    upper_extreme = Q3 + (1.5 * IQR)
    new_dataset = np.delete(dataset,np.where((dataset < lower_extreme) | (dataset > upper_extreme)))
    outliers = []
    for i in dataset:
        if (i < lower_extreme) | ( i > upper_extreme):
            outliers.append(i)
    print('Outliers are',outliers)
    return new_dataset

def plot_outlier_removal(dataset):
    Q1 = np.quantile(dataset, 0.25)
    Q3 = np.quantile(dataset, 0.75)
    IQR = Q3 - Q1
    lower_extreme = Q1 - (1.5 * IQR)
    upper_extreme = Q3 + (1.5 * IQR)
    outliers = []
    for i in dataset:
        if (i < lower_extreme) | ( i > upper_extreme):
            outliers.append(i)
    new_dataset = np.delete(dataset,np.where((dataset < lower_extreme) | (dataset > upper_extreme)))
    plt.figure(figsize=(12,5))
    plt.subplot(1,2,1)
    for i in outliers:
        plt.annotate('Outlier',xytext=(1.1,i+2),xy=(1.01,i+1),fontsize=10,
                     arrowprops={'color':'violet','width':2,'headwidth':9})
    plt.title('Un-preprocessed dataset')
    plt.boxplot(dataset)
    plt.subplot(1,2,2)
    plt.title('Cleaned dataset')
    plt.boxplot(new_dataset)
    plt.show()
    print('Outliers are',outliers)
    return new_dataset
