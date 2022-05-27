import  numpy as np
import pandas as pd
from hbshare.fe.XZ import  functionality
from hbshare.fe.XZ import db_engine as dbeng

util=functionality.Untils()
hbdb=dbeng.HBDB()
localdb=dbeng.PrvFunDB().engine

def create_stock_shift_ratio():

    hsl=pd.read_excel(r"E:\GitFolder\hbshare\fe\factor_analysis\换手率.xlsx")
    date_col=hsl.columns.tolist()
    date_col.remove('证券简称')
    date_col.remove('证券代码')
    new_date_col=[]
    date_map=dict()
    hsl['jjdm'] = hsl['证券代码'].str[0:6]
    for i in range(len(date_col)):
        new_date_col.append(date_col[i].replace('H1','0630').replace(' ','').replace('H2', '1231'))

    date_map = dict(zip(date_col,new_date_col))

    outputdf=pd.DataFrame()
    tempdf=pd.DataFrame()
    tempdf['jjdm']=util.get_mutual_stock_funds('20211231')
    tempdf=pd.merge(tempdf,hsl,how='left',on='jjdm')

    for date in date_col:
        tempdf2=tempdf[['jjdm',date]]
        tempdf2['date']=date_map[date]
        tempdf2.rename(columns={date:'hsl'},inplace=True)
        outputdf=pd.concat([outputdf,tempdf2],axis=0)

    outputdf=outputdf[outputdf['hsl'].notnull()]

    outputdf.to_sql('factor_hsl',con=localdb,index=False,if_exists='append')

def read_factors(table_name):

    sql="select * from {}".format(table_name)
    df=pd.read_sql(sql,con=localdb)

    return  df

def bhar(arr):
    return 100 * (np.power(np.cumprod((arr + 100) / 100).tolist()[-1], 1 / len(arr)) - 1)


def hsl_rank2db(dir):

    #get the hsl raw data first
    # sql="select * from factor_hsl  "
    # df=pd.read_sql(sql,con=localdb)
    df=pd.read_csv(dir)
    df['hsl_rank']=df.groupby('date').rank(method='min')
    count=df.groupby('date', as_index=False).count()[['date', 'jjdm']]
    count.rename(columns={'jjdm':'count'},inplace=True)
    df=pd.merge(df,count,how='left',on='date')
    df['hsl_rank']=df['hsl_rank']/df['count']
    df.to_sql('factor_hsl',con=localdb,index=False,if_exists='append')


if __name__ == '__main__':

    df=read_factors('factor_hsl')
    df=df.groupby('jjdm').min()
    df=df[df['hsl'] >= 350]

    jjdm_list=df.index.tolist()
    jjdm_con=util.list_sql_condition(jjdm_list)

    sql="""select jjdm,hb1n,rqzh from st_fund.t_st_gm_nhb 
    where hb1n!=99999 and jjdm in ({0}) and tjnf in ('2015','2016','2017','2018','2019','2020','2021')"""\
        .format(jjdm_con)
    ret=hbdb.db2df(sql,db='funduser')
    ret=ret.groupby('jjdm')['hb1n'].apply(bhar)
    ret.to_csv('hlsret.csv',encoding='gbk')
    print('')