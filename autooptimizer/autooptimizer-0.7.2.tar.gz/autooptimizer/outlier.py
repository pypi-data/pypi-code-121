import numpy as np
import matplotlib.pyplot as plt

def interquartile_outlier_removal(array):
    Q1 = np.quantile(array, 0.25)
    Q3 = np.quantile(array, 0.75)
    IQR = Q3 - Q1
    lower_extreme = Q1 - (1.5 * IQR)
    upper_extreme = Q3 + (1.5 * IQR)
    new_array = np.delete(array, np.where((array < lower_extreme) | (array > upper_extreme)))
    outliers = [i for i in array if i < lower_extreme or i > upper_extreme]
    if len(outliers) == 0:
        print('No outlier')
    else:
        print('Outliers are {}'.format(outliers))
    return new_array

def plot_interquartile_outlier_removal(array):
    Q1 = np.quantile(array, 0.25)
    Q3 = np.quantile(array, 0.75)
    IQR = Q3 - Q1
    lower_extreme = Q1 - (1.5 * IQR)
    upper_extreme = Q3 + (1.5 * IQR)
    outliers = [i for i in array if (i < lower_extreme) | ( i > upper_extreme)]
    new_array = np.delete(array,np.where((array < lower_extreme) | (array > upper_extreme)))
    plt.rcParams.update({'font.family':'times new roman', 'font.size': 11.5, 'text.color': 'darkblue'})
    plt.figure(figsize=(12,5))
    plt.suptitle('Interquartile Range Method', fontsize=16, color='black')
    plt.subplot(1,2,1)
    for i in outliers:
        plt.annotate('outlier', xytext=(1.1,i+2), xy=(1.01,i+1), fontsize=12,
                    arrowprops={'color':'violet', 'width':1.5, 'headwidth':7})
    plt.title('Un-preprocessed dataset')
    plt.boxplot(array)
    plt.subplot(1,2,2)
    plt.title('Cleaned dataset')
    plt.boxplot(new_array)
    plt.show()
    return np.array(new_array)

def zscore_outlier_removal(array):
    threshold = 3
    mean = np.mean(array)
    std = np.std(array, ddof=0)
    outliers = [i.astype(int) for i in array if abs((i - mean) / std) > threshold]
    new_array = [i for i in array if abs((i - mean) / std) < threshold]
    if len(outliers) == 0:
        print('No outlier')
    else:
        print('Outliers are {}'.format(outliers))
    return np.array(new_array)

def plot_zscore_outlier_removal(array):
    threshold = 3
    mean = np.mean(array)
    std = np.std(array, ddof=0)
    outliers = [i.astype(int) for i in array if abs((i - mean) / std) > threshold]
    new_array = [i for i in array if abs((i - mean) / std) < threshold]
    plt.rcParams.update({'font.family':'times new roman', 'font.size': 11.5, 'text.color':'darkblue'})
    plt.figure(figsize=(12,5))
    plt.suptitle('Z-Score Method', fontsize=16, color='black')
    plt.subplot(1,2,1)
    for i in outliers:
        plt.annotate('outlier', xytext=(1.1, i+2), xy=(1.01, i+1), fontsize=12,
                     arrowprops={'color':'violet','width':1.5,'headwidth':7})
    plt.title('Un-preprocessed dataset')
    plt.boxplot(array)
    plt.subplot(1,2,2)
    plt.title('Cleaned Dataset')
    plt.boxplot(new_array)
    plt.show()
    return np.array(new_array)
    
def std_outlier_removal(array, threshold=3):
    mean = np.mean(array)
    std = np.std(array, ddof=0)
    upper_limit = mean + threshold * std
    lower_limit = mean - threshold * std
    outliers = [i for i in array if i > upper_limit or i < lower_limit]
    new_array = [i for i in array if i < upper_limit and i > lower_limit]
    if len(outliers) == 0:
        print('No outlier')
    else:
        print('Outliers are {}'.format(outliers))
    return np.array(new_array)

def plot_std_outlier_removal(array, threshold=3):
    mean = np.mean(array)
    std = np.std(array, ddof=0)
    upper_limit = mean + threshold * std
    lower_limit = mean - threshold * std
    outliers = [i for i in array if i > upper_limit or i < lower_limit]
    new_array = [i for i in array if i < upper_limit and i > lower_limit]
    plt.rcParams.update({'font.family':'times new roman', 'font.size':11.5, 'text.color':'darkblue'})
    plt.figure(figsize=(12,5))
    plt.suptitle('Standard Deviation Method', fontsize=16, color='black')
    plt.subplot(1,2,1)
    for i in outliers:
        plt.annotate('outlier', xytext=(1.1, i+1), xy=(1.01, i+1), fontsize=12,
                    arrowprops=({'color':'violet', 'width':1.5, 'headwidth':7}))
    plt.title('Un-preprocessed dataset')
    plt.boxplot(array)
    plt.subplot(1,2,2)
    plt.title('Cleaned Dataset')
    plt.boxplot(new_array)
    plt.show()
    return new_array
