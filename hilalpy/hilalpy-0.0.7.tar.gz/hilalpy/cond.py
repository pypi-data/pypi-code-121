def cond (figure,errorratetotal,x,y,conditionx,conditiony,limitx,limity): 
    
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

    #Change Style

    sns.set_theme(style="darkgrid")

    #Format Plot for Whole

    plt.figure(figsize=(10,6))
    a=sns.relplot(x=df[x], y=df[y],style=df['V'],color='black', s=20,linewidth=0.1)

    a.ax.hlines(y=conditiony, xmin=conditionx, xmax=limitx)
    a.ax.vlines(x=conditionx, ymin=conditiony, ymax=limity)
    
    a.savefig(figure)

    #Condition Test on Whole

    dfx=df[(df[x] >= conditionx)]
    dfypos=dfx[(dfx[y] >= conditiony)]
    dfy_visible = dfypos[dfypos['V'] =='I']
    df_visible = dfypos[dfypos['V'] =='V']

    xpos_whole=abs((len(dfypos[x])-len(dfy_visible[x])))
    positive_errorrate_whole = abs(((xpos_whole/(len(dfypos)))*100)-100)

    dfx=df[(df[x] <= conditionx)]
    dfyneg=dfx[(dfx[y] <= conditiony)]
    dfy_invisible = dfyneg[dfyneg['V'] =='V']
    df_invisible = dfyneg[dfyneg['V'] =='I']

    xneg_whole=abs((len(dfyneg[x])-len(dfy_invisible[x])))
    negative_errorrate_whole = abs(((xneg_whole/(len(dfyneg[x])))*100)-100)
    
    #Combine Dataframe
    dfy_visible.to_csv( poserrorratedata, index=False, encoding='utf-8-sig')
    dfy_invisible.to_csv( negerrorratedata, index=False, encoding='utf-8-sig')


    #Condition Test on Naked Eye

    dfn = df[df['M'] =='NE']


    dfx=dfn[(dfn[x] >= conditionx)]
    dfy=dfx[(dfx[y] >= conditiony)]
    dfy_visible = dfy[dfy['V'] =='I']
    df_visible = dfy[dfy['V'] =='V']

    xpos_nakedye=abs((len(dfy[x])-len(dfy_visible[x])))
    positive_errorrate_nakedeye = abs(((abs(len(dfx[x])-len(dfy_visible[x]))/(len(dfy[x])))*100-100))

    dfx=dfn[(dfn[x] <= conditionx)]
    dfy=dfx[(dfx[y] <= conditiony)]
    dfy_invisible = dfy[dfy['V'] =='V']
    df_invisible = dfy[dfy['V'] =='I']


    xneg_nakedeye=abs((len(dfy[x])-len(dfy_invisible[x])))
    negative_errorrate_nakedeye = abs((abs((len(dfy[x])-len(dfy_invisible[x]))/(len(dfy[x])))*100-100))

    #Conditional Test on Optical Aided
    dfb= df[df['M'] =='OA']
    dfx=dfb[(dfb[x] >= conditionx)]
    dfyv=dfx[(dfx[y] >= conditiony)]
    dfy_visible = dfyv[dfyv['V'] =='I']
    df_visible = dfyv[dfyv['V'] =='V']


    xpos_opticalaided=abs((len(dfb[x])-len(dfy_visible[x])))
    positive_errorrate_opticalaided = abs(((abs(len(dfb[x])-len(dfy_visible[x]))/(len(dfb[x])))*100-100))

    dfx=dfb[(dfb[x] <= conditionx)]
    dfyi=dfx[(dfx[y] <= conditiony)]
    dfy_invisible = dfyi[dfyi['V'] =='V']
    df_invisible = dfyi[dfyi['V'] =='I']

    #def negative_errorrate(n, d):
    #    return ((d-n)/n) if n else 0

    xneg_opticalaided=abs((len(dfb[x])-len(dfy_invisible[x])))
    negative_errorrate_opticalaided = abs(((abs(len(dfb[x])-len(dfy_invisible[x]))/(len(dfb[x])))*100-100))
    

    #Error Rate Combine
    df = pd.merge(dfy_visible, df_visible, how='outer', indicator=True).query("_merge != 'both'").drop('_merge', axis=1).reset_index(drop=True)
    dfccd = df[df['I'] =='CCD']
    dfNU = df[df['I'] =='NU']
    dfT = df[df['I'] =='T']

    condition_test_result = {'Parameter': ['Whole (%)','Naked Eye (%)','Optical Aided (%)'],
            'Positive': [positive_errorrate_whole,positive_errorrate_nakedeye,positive_errorrate_opticalaided],
            'Negative': [negative_errorrate_whole,negative_errorrate_nakedeye,negative_errorrate_opticalaided]
                            }
    df_cond_result = pd.DataFrame(condition_test_result, columns = ['Parameter', 'Positive','Negative'])
    df=df_cond_result.round(2)
    #print(a)
    print (df_cond_result)

    df.to_csv( errorratetotal, index=False, encoding='utf-8-sig')

