import pandas as pd

def dfAppend(df:pd.DataFrame, dicKey:int, row:int):

    """ 
    dataframeに行を追加(appendの代替)

    Parameters
    ----------
    df : pd.DataFrame
        pandas DataFrame
    dicKey : int
        ディクショナリキー
    row : int
        行番号

    """

    # 追加用のディクショナリを宣言
    dict_tmp = {}

    # ディクショナリに行番号をセット
    dict_tmp[dicKey] = row

    # キー値を加算
    dicKey += 1

    # 戻り値を返す
    return df.from_dict(dict_tmp, orient="index"), dicKey

def convertToList(targetDataFrame:pd.DataFrame, targetColumnName:str, dupRowDel:bool = True):
    
    """
    DataFrameから特定列を抽出して値をリスト化する
    
    Parameters
    ----------
    targetDataFrame : pd.DataFrame
        対象DataFrame
    targetColumnName : str
        抽出対象列名
    dupRowDel : bool
        重複行削除フラグ
        
    """
    
    # 特定列のみ抽出
    dfCol:pd.DataFrame = targetDataFrame.loc[:,[targetColumnName]]
    
    # 重複除去
    if dupRowDel:
        dfCol = dfCol.drop_duplicates()
    
    # 抽出列をループしてリストに格納
    result:list = list()
    for columnName, row in dfCol.iterrows():
        result.append(row[targetColumnName])
    
    return result