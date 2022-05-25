def equa (a,b,equation,limita,limitb):

    import os,glob, pandas as pd
    import numpy as np  
    import pandas as pd  
    import matplotlib.pyplot as plt
    import seaborn as sns
    import numexpr as ne

    #convert all varible to positive.
    url = 'https://raw.githubusercontent.com/msyazwanfaid/hilalpy/main/Final.csv'
    df = pd.read_csv(url, index_col=0)
    df[a] = df[a].abs()
    df[b] = df[b].abs()

    #Set Limit

    df=df[(df[a] <= limita)]
    df=df[(df[b] <= limitb)]

    #Graph
    sns.set_theme(style="darkgrid")

    plt.figure(figsize=(10,6))
    z=sns.relplot(x=df[a], y=df[b],style=df['V'],color='black', s=20,linewidth=0.1)

    def graph(formula, x_range):
        x = np.array(x_range)
        y = eval(formula)
        plt.plot(x, y,'k')


    graph(equation, range(0, limita))

    plt.show()

    z.savefig(figure)

    #Condition on Whole
    x=df[a];
    df["test"]=ne.evaluate(equation)
    dfx=df[(df[b] >= df["test"])]
    dfy_visible = dfx[dfx['V'] =='I']
    df_visible = df[df['V'] =='V']

    xpos=abs((len(dfx)-len(dfy_visible)))
    positive_errorrate_whole = abs(((xpos/(len(dfx)))*100-100))

    dfx=df[(df[b] <= df["test"])]
    dfy_invisible = dfx[dfx['V'] =='V']
    df_invisible = df[df['V'] =='I']

    xneg=abs((len(dfx)-len(dfy_invisible)))
    negative_errorrate_whole = abs(((xneg/(len(dfx)))*100-100))
    
    #Combine Dataframe
    dfy_visible.to_csv( poserrorratedata, index=False, encoding='utf-8-sig')
    dfy_invisible.to_csv( negerrorratedata, index=False, encoding='utf-8-sig')


    #Condition Test on Naked Eye
    dfn = df[df['M'] =='NE']
    dfx=dfn[(dfn[b] >= dfn["test"])]
    dfy_visible = dfx[dfx['V'] =='I']
    df_visible = dfn[dfn['V'] =='V']

    xpos=abs((len(dfn)-len(dfy_visible)))
    positive_errorrate_nakedeye = abs(((xpos/(len(dfn)))*100-100))

    dfx=dfn[(dfn[b] <= dfn["test"])]
    dfy_invisible = dfx[dfx['V'] =='V']
    df_invisible = dfn[dfn['V'] =='I']

    xneg=abs((len(dfx)-len(dfy_invisible)))
    negative_errorrate_nakedeye = abs(((xneg/(len(dfx)))*100-100))

    #Condition on Optical Aided
    dfb = df[df['M'] =='OA']

    dfx=dfb[(dfb[b] >= dfb["test"])]
    dfy_visible = dfx[dfx['V'] =='I']
    df_visible = dfb[dfb['V'] =='V']

    xpos=abs((len(dfb)-len(dfy_visible)))
    positive_errorrate_opticalaided  = abs(((xpos/(len(dfb)))*100-100))

    dfx=dfb[(dfb[b] <= dfb["test"])]
    dfy_invisible = dfx[dfx['V'] =='V']
    df_invisible = dfx[dfx['V'] =='I']


    xneg_opticalaided=abs((len(df_invisible)-len(dfy_invisible)))
    negative_errorrate_opticalaided = abs(((abs(len(dfb)-len(dfy_invisible))/(len(dfb)))*100-100))

        
    #Merge Error Rate
    df = pd.merge(dfy_visible, df_visible, how='outer', indicator=True).query("_merge != 'both'").drop('_merge', axis=1).reset_index(drop=True)
    dfccd = df[df['I'] =='CCD']
    dfNU = df[df['I'] =='NU']
    dfT = df[df['I'] =='T']

    condition_test_result = {'Parameter': ['Whole','Naked Eye','Optical Aided'],
            'Positive': [positive_errorrate_whole,positive_errorrate_nakedeye,positive_errorrate_opticalaided],
            'Negative': [negative_errorrate_whole,negative_errorrate_nakedeye,negative_errorrate_opticalaided]
                            }
    df_cond_result = pd.DataFrame(condition_test_result, columns = ['Parameter', 'Positive','Negative'])
    df=df_cond_result.round(2)
    print (df_cond_result)
    df.to_csv( errorratetotal, index=False, encoding='utf-8-sig')

