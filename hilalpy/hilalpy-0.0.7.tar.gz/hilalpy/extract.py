def extract (largerthandata,smallerthandata,x,y,conditionx,conditiony,limitx,limity): 
    
    import os,glob, pandas as pd
    import numpy as np  
    import pandas as pd  
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    #convert all varible to positive.
    url = 'https://raw.githubusercontent.com/msyazwanfaid/hilalpy/main/Final.csv'
    df = pd.read_csv(url, index_col=0)
    df[x] = df[x].abs()
    df[y] = df[y].abs()

    #Set Limit

    df=df[(df[x] <= limitx)]
    df=df[(df[y] <= limity)]

    #Largerthan Data Extract

    dfx=df[(df[x] >= conditionx)]
    dfypos=dfx[(dfx[y] >= conditiony)]
    dfypos.to_csv( largerthandata, index=False, encoding='utf-8-sig')

    
    dfx=df[(df[x] <= conditionx)]
    dfyneg=dfx[(dfx[y] <= conditiony)]
    dfyneg.to_csv( smallerthandata, index=False, encoding='utf-8-sig')

