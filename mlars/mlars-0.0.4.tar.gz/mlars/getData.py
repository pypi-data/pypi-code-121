from sklearn.model_selection import train_test_split
from colorama import Fore, Back, Style
import pandas as pd


def getData(df, name: str, unique, test_size: float = 0.2) :
    for i in range(len(unique)):
        df[name] = df[name].replace(unique[i], i)
    for col in df.select_dtypes(include=['bool']):
        df[col] = df[col].astype('int')
    #datetime to int
    for col in df.select_dtypes(include=['datetime64[ns]']):
        df[col] = df[col].apply(lambda x: x.value)
    for col in df.select_dtypes(include=['object']):
        if len(df[col].unique()) < 40:
            one_hot = pd.get_dummies(df[col],prefix=[col])
            df = df.drop(col,axis = 1)
            df = df.join(one_hot)
        # df[col] = df[col].astype('int')/ 10**9
    print(df.shape)
    df = df.select_dtypes(include=['float64', 'int64', 'int32', 'int16', 'int8', 'float32','uint8', 'float16','datetime64[ns]'])
    print (Fore.YELLOW + "with dataframe of shape: {} {}".format(df.shape[0], df.shape[1]))
    X = df.drop(name, axis=1)
    y = df[name]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size)
    return [X_train, X_test, y_train, y_test]

def clearData(df):
    length = len(df)
    some = df.isnull().sum()
    for id,item in enumerate(some):
        if (item/length)*100 > 30:
            df.drop(df.columns[id],1) 
    df.dropna()
    return df