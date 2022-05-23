import pandas as pd

def check_types(df: pd.DataFrame):
    """ verifica os tipos de df de cada coluna do geral.
    INPUT:
    df - o geral analisado
    OUTPUT:
    imprime uma linha com os nomes de cada coluna e seu tipo de df
    """
    for column in df.columns:
        print("coluna: {0}, tipo: {1}".format(column, type(df[column].iloc[0])))