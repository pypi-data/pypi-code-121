import datetime
import pandas as pd
import numpy as np
from hbshare.fe.xwq.analysis.orm.hbdb import HBDB
from hbshare.fe.XZ import db_engine
from hbshare.fe.XZ import functionality
from sklearn.linear_model import LinearRegression as LR
from scipy.optimize import shgo, minimize
import statsmodels.api as sm




localdb=db_engine.PrvFunDB().engine
hbdb=db_engine.HBDB()
util=functionality.Untils()


def get_monthly_jjnav(jjdm_list,start_date=None,end_date=None):

    jjdm_con = util.list_sql_condition(jjdm_list)

    if(start_date is not None):
        date_con1=" and tjyf>='{0}'".format(start_date[0:6])
    else:
        date_con1=''

    if(end_date is not None):
        date_con2 = " and tjyf<='{0}'".format(end_date[0:6])
    else:
        date_con2=''

    #get the nav ret  for given jjdm and time zone(already times 100)
    sql="select jjdm,tjyf,rqzh,hb1y from st_fund.t_st_gm_yhb where jjdm in ({0}) and rq1y!=99999 {1} {2} "\
        .format(jjdm_con,date_con1,date_con2)
    navdf=hbdb.db2df(sql, db='funduser')

    max_yearmonth=navdf['tjyf'].max()
    min_yearmonth=navdf['tjyf'].min()

    return navdf,max_yearmonth,min_yearmonth

def get_daily_jjnav(jjdm_list,start_date=None,end_date=None):

    jjdm_con=util.list_sql_condition(jjdm_list)

    if(start_date is not None):
        date_con1=" and jzrq>='{0}'".format(start_date)
    else:
        date_con1=''

    if(end_date is not None):
        date_con2 = " and jzrq<='{0}'".format(end_date)
    else:
        date_con2=''

    sql="select jjdm,jzrq,hbdr from st_fund.t_st_gm_rhb where jjdm in ({0}) and hbdr!=99999 and hbdr!=0 {1} {2}  "\
        .format(jjdm_con,date_con1,date_con2)
    navdf=hbdb.db2df(sql, db='funduser')

    return navdf

def get_weekly_jjnav(jjdm_list,start_date=None,end_date=None):

    jjdm_con=util.list_sql_condition(jjdm_list)

    if(start_date is not None):
        date_con1=" and tjrq>='{0}'".format(start_date)
    else:
        date_con1=''

    if(end_date is not None):
        date_con2 = " and tjrq<='{0}'".format(end_date)
    else:
        date_con2=''

    sql="select jjdm,tjrq,hb1z from st_fund.t_st_gm_zhb where jjdm in ({0}) and hb1z!=99999 and hb1z!=0 {1} {2}  "\
        .format(jjdm_con,date_con1,date_con2)
    navdf=hbdb.db2df(sql, db='funduser')

    return navdf

def get_monthly_index_ret(zqdm,start_date=None,end_date=None):

    if(start_date is not None):
        date_con1=" and tjyf>='{0}'".format(start_date[0:6])
    else:
        date_con1=''

    if(end_date is not None):
        date_con2 = " and tjyf<='{0}'".format(end_date[0:6])
    else:
        date_con2=''

    sql="select zqdm,tjyf,rqzh,hb1y from st_market.t_st_zs_yhb where zqdm='{0}' and abs(hb1y)!=99999 {1} {2}"\
        .format(zqdm,date_con1,date_con2)

    benchmark_ret=hbdb.db2df(sql, db='alluser')

    return  benchmark_ret

def get_weekly_index_ret(zqdm,start_date=None,end_date=None):

    if(start_date is not None):
        date_con1=" and tjrq>='{0}'".format(start_date)
    else:
        date_con1=''

    if(end_date is not None):
        date_con2 = " and tjrq<='{0}'".format(end_date)
    else:
        date_con2=''

    sql="select zqdm,tjrq,hb1z from st_market.t_st_zs_zhb where zqdm='{0}' and abs(hb1z)!=99999 {1} {2}"\
        .format(zqdm,date_con1,date_con2)

    benchmark_ret=hbdb.db2df(sql, db='alluser')

    return  benchmark_ret

def bhar(arr):
        return 100*(np.power(np.cumprod((arr+100)/100).tolist()[-1],1/len(arr))-1)

def ols_withcons_for_group(arr):
    y_col=arr.columns[0]
    x_col=arr.columns.tolist()
    x_col.remove(y_col)

    # result=util.my_general_linear_model_func(arr[x_col].values,
    #                                          arr[y_col].values)
    # # print(result['x'].sum())
    # # print(result['success'])
    # return result['x'].tolist()

    result = util.my_general_linear_model_func(arr[x_col].values,
                                             arr[y_col].values)
    return result

def ols_for_group(arr):

    y_col=arr.columns[0]
    x_col=arr.columns.tolist()
    x_col.remove(y_col)

    result=sm.OLS(arr[y_col].values, arr[x_col].values).fit()

    return result.params.tolist()

def get_barra_daily_ret(start_date=None,end_date=None):
    #barra return daily return
    sql='select factor_ret,factor_name,trade_date from st_ashare.r_st_barra_factor_return'
    test=hbdb.db2df(sql,db='alluser')
    factor_name_list=test['factor_name'].unique().tolist()
    factor_ret_df=pd.DataFrame()
    date_list=test['trade_date'].unique().tolist()
    date_list.sort()
    factor_ret_df['date']=date_list
    for factor in factor_name_list:
        factor_ret_df=pd.merge(factor_ret_df,test[test['factor_name']==factor][['factor_ret','trade_date']],
                               how='left',left_on='date',right_on='trade_date').drop('trade_date',axis=1)
        factor_ret_df.rename(columns={'factor_ret':factor},inplace=True)

    return factor_ret_df

def get_styleindex_ret(index_list,start_date=None,end_date=None):

    if(start_date is not None):
        start_date="and jyrq>='{}'".format(start_date)
    else:
        start_date=""

    if(end_date is not None):
        end_date="and jyrq<='{}'".format(end_date)
    else:
        end_date=""

    # style daily return
    style_ret=pd.DataFrame()
    for zqdm in index_list:

        #sql = "select spjg,zqmc,jyrq from st_market.t_st_zs_hqql where zqdm='{}' ".format(zqdm)
        sql= "select zqdm,jyrq,hbdr from st_market.t_st_zs_rhb where zqdm='{0}' and hbdr!=0 {1} {2} "\
            .format(zqdm,start_date,end_date)
        test = hbdb.db2df(sql=sql, db='alluser')
        #test['ret'] = test['spjg'].pct_change()
        test[zqdm]=test['hbdr']
        test.set_index('jyrq',inplace=True)
        style_ret=pd.concat([style_ret,test[zqdm]],axis=1)

    return style_ret

def get_barra_ret(col_list):

    theme_map = dict(zip(['Bank', 'RealEstate', 'Health', 'Transportation', 'Mining', 'NonFerMetal',
                               'HouseApp', 'LeiService', 'MachiEquip', 'BuildDeco', 'CommeTrade',
                               'CONMAT', 'Auto', 'Textile', 'FoodBever', 'Electronics',
                               'Computer', 'LightIndus', 'Utilities', 'Telecom', 'AgriForest',
                               'CHEM', 'Media', 'IronSteel', 'NonBankFinan', 'ELECEQP', 'AERODEF',
                               'Conglomerates'],
                              ['大金融', '大金融', '消费', '制造', '周期', '周期',
                               '周期', '消费', '制造', '周期', '消费',
                               '消费', '制造', '消费', '消费', 'TMT',
                               'TMT', '制造', '制造', 'TMT', '消费',
                               '周期', 'TMT', '周期', '大金融', '制造', '无',
                               '无']))
    col_con=util.list_sql_condition(col_list)

    sql="""select factor_ret,factor_name,trade_date from st_ashare.r_st_barra_factor_return where factor_name in 
    ({0}) and trade_date>='20171231'
       """.format(col_con)
    df=hbdb.db2df(sql,db='alluser')
    if(col_list==list(theme_map.keys())):
        df['factor_name']=[theme_map[x] for x in df['factor_name'] ]
    df = df.groupby(['trade_date', 'factor_name']).mean().unstack()*100
    df.columns = df.columns.get_level_values(1)
    df.drop('无',axis=1,inplace=True)

    return  df

def get_jj_daily_ret(jjdm_list):

    tempdf = get_daily_jjnav(jjdm_list)
    jj_ret = pd.DataFrame()
    jj_ret['date'] = tempdf.sort_values('jzrq')['jzrq']
    for jjdm in tempdf['jjdm'].unique():
        jj_ret=pd.merge(jj_ret,tempdf[tempdf['jjdm']==jjdm][['hbdr','jzrq']],
                        how='left',left_on='date',right_on='jzrq').drop('jzrq',axis=1)
        jj_ret.rename(columns={'hbdr':jjdm},inplace=True)
        # jj_ret[jjdm]=jj_ret[jjdm]/100

    jj_ret.set_index('date',drop=True,inplace=True)

    return jj_ret

def style_exp_foroutsideuser():


    for zqdm in ['399372', '399373', '399374', '399375', '399376', '399377', 'CBA00301']:

        sql="select spjg,jyrq from st_market.t_st_zs_hq where jyrq>='20100105' and zqdm='{}'"\
            .format(zqdm)
        temdf=hbdb.db2df(sql,db='alluser').rename(columns={'spjg':zqdm})
        if(zqdm=='399372'):
            style_index_ret=temdf.copy()
        else:
            style_index_ret=pd.merge(style_index_ret,temdf,how='left',on='jyrq')

    style_index_ret.set_index('jyrq',inplace=True)


    priv_pool=pd.read_excel(r"C:\Users\xuhuai.zhe\Downloads\私募跟踪池.xlsx")
    jjjc_con=util.list_sql_condition(priv_pool['基金简称'].values.tolist())
    pri_basis=hbdb.db2df("select jjdm,jjjc from st_hedge.t_st_jjxx where jjjc in ({})"
                         .format(jjjc_con),db='highuser')
    pri_basis.drop_duplicates('jjjc',keep='first',inplace=True)
    jjdm_list=pri_basis['jjdm'].values.tolist()

    output = []
    for jjdm in jjdm_list:
        #S64497

        jj_ret=hbdb.db2df("select hbdr,jzrq,fqdwjz from st_hedge.t_st_rhb where jjdm='{}' and hbdr!=0".format(jjdm)
                          ,db='highuser').rename(columns={'hbdr':jjdm})
        jj_ret['jzrq']=jj_ret['jzrq'].astype(int)
        jj_ret.set_index('jzrq',inplace=True)

        olsdf=pd.merge(jj_ret,style_index_ret,how='left',left_index=True,right_index=True).fillna(0)
        olsdf[['399372', '399373', '399374', '399375','399376', '399377', 'CBA00301']]=\
            olsdf[['399372', '399373', '399374', '399375','399376', '399377', 'CBA00301']].pct_change()*100

        olsdf['399374'] = (olsdf['399374'] + olsdf['399376']) / 2
        olsdf['399375'] = (olsdf['399375'] + olsdf['399377']) / 2
        olsdf.drop(['399376','399377'],axis=1,inplace=True)
        olsdf = olsdf[olsdf['399372'] < 9999]

        laster_half_year=olsdf.index[olsdf.index>=int((datetime.datetime.strptime(str(jj_ret.index[-1]),
                                                     '%Y%m%d')-datetime.timedelta(days=183)).strftime('%Y%m%d'))][0]
        last_year=olsdf.index[olsdf.index>=int((datetime.datetime.strptime(str(jj_ret.index[-1]),
                                                     '%Y%m%d')-datetime.timedelta(days=365)).strftime('%Y%m%d'))][0]
        last_oneandhalfyear=olsdf.index[olsdf.index>=int((datetime.datetime.strptime(str(jj_ret.index[-1]),
                                                     '%Y%m%d')-datetime.timedelta(days=365+182)).strftime('%Y%m%d'))][0]


        result1=util.my_general_linear_model_func(olsdf.loc[int(laster_half_year):][['399372', '399373', '399374', '399375','CBA00301']].values
                                                 , olsdf.loc[int(laster_half_year):][jjdm].values)
        result2=util.my_general_linear_model_func(olsdf.loc[int(last_year):][['399372', '399373', '399374', '399375','CBA00301']].values
                                                 , olsdf.loc[int(last_year):][jjdm].values)
        result3=util.my_general_linear_model_func(olsdf.loc[int(last_oneandhalfyear):][['399372', '399373', '399374', '399375','CBA00301']].values
                                                 , olsdf.loc[int(last_oneandhalfyear):][jjdm].values)
        result=list((np.array(result1)+np.array(result2)+np.array(result3))/3)
        result.append(jjdm)

        output.append(result)

    outdf=pd.DataFrame(data=output,columns=['大盘成长','大盘价值','中小成长','中小盘价值','中债','jjdm'])
    outdf=pd.merge(outdf,pri_basis,how='left',on='jjdm')
    outdf.to_csv('prv_core_ols.csv')



    # style_index_ret = get_styleindex_ret(['399372', '399373', '399374', '399375', '399376', '399377', 'CBA00301'],
    #                                      start_date='20100105')
    # style_index_ret['399374'] = (style_index_ret['399374'] + style_index_ret['399376']) / 2
    # style_index_ret['399375'] = (style_index_ret['399375'] + style_index_ret['399377']) / 2
    # style_index_ret=style_index_ret[['399372', '399373', '399374', '399375','CBA00301']]
    #
    # sql="select * from core_pool_history where asofdate='{}'".format('202203')
    # mutual_pool=pd.read_sql(sql,con=localdb).rename(columns={'基金代码':'jjdm',
    #                                                   '基金名称':'jjjc',
    #                                                   '基金经理':'manager'})
    # jjdm_list=mutual_pool['jjdm'].unique().tolist()
    #
    # output=[]
    #
    # for jjdm in jjdm_list:
    #     # get jj nav ret
    #     jj_ret = get_jj_daily_ret([jjdm])
    #     laster_half_year=util._shift_date( (datetime.datetime.strptime(str(jj_ret.index[-1]),
    #                                                  '%Y%m%d')-datetime.timedelta(days=183)).strftime('%Y%m%d'))
    #     last_year=util._shift_date( (datetime.datetime.strptime(str(jj_ret.index[-1]),
    #                                                  '%Y%m%d')-datetime.timedelta(days=365)).strftime('%Y%m%d'))
    #     last_oneandhalfyear=util._shift_date((datetime.datetime.strptime(str(jj_ret.index[-1]),
    #                                                  '%Y%m%d')-datetime.timedelta(days=365+182)).strftime('%Y%m%d'))
    #
    #     olsdf=pd.merge(jj_ret,style_index_ret,how='left',left_index=True,right_index=True).fillna(0)
    #
    #
    #     result1=util.my_general_linear_model_func(olsdf.loc[int(laster_half_year):][['399372', '399373', '399374', '399375','CBA00301']].values
    #                                              , olsdf.loc[int(laster_half_year):][jjdm].values)
    #     result2=util.my_general_linear_model_func(olsdf.loc[int(last_year):][['399372', '399373', '399374', '399375','CBA00301']].values
    #                                              , olsdf.loc[int(last_year):][jjdm].values)
    #     result3=util.my_general_linear_model_func(olsdf.loc[int(last_oneandhalfyear):][['399372', '399373', '399374', '399375','CBA00301']].values
    #                                              , olsdf.loc[int(last_oneandhalfyear):][jjdm].values)
    #     result=list((np.array(result1)+np.array(result2)*0.5+np.array(result3)*0.25)/1.75)
    #     result.append(jjdm)
    #
    #     output.append(result)
    #
    # outdf=pd.DataFrame(data=output,columns=['大盘成长','大盘价值','中小成长','中小盘价值','中债','jjdm'])
    # outdf=pd.merge(outdf,mutual_pool,how='left',on='jjdm')
    # outdf.to_csv('mutual_core_ols.csv')

def style_exp_simpleols_foroutsideuser_prv():

    #prv part
    for zqdm in ['399372', '399373', '399374', '399375', '399376', '399377', 'CBA00301']:

        sql="select spjg,jyrq from st_market.t_st_zs_hq where jyrq>='20100105' and zqdm='{}'"\
            .format(zqdm)
        temdf=hbdb.db2df(sql,db='alluser').rename(columns={'spjg':zqdm})
        if(zqdm=='399372'):
            style_index_ret=temdf.copy()
        else:
            style_index_ret=pd.merge(style_index_ret,temdf,how='left',on='jyrq')

    style_index_ret.set_index('jyrq',inplace=True)


    priv_pool=pd.read_excel(r"C:\Users\xuhuai.zhe\Downloads\私募跟踪池.xlsx")
    jjjc_con=util.list_sql_condition(priv_pool['基金简称'].values.tolist())
    pri_basis=hbdb.db2df("select jjdm,jjjc from st_hedge.t_st_jjxx where jjjc in ({})"
                         .format(jjjc_con),db='highuser')
    pri_basis.drop_duplicates('jjjc',keep='first',inplace=True)

    jjdm_list=hbdb.db2df("select jjdm from st_hedge.t_st_jjxx where cpfl='4' and jjzt='0' and jjfl='1' and clrq<='20200506' ",db='highuser') ['jjdm'].values.tolist()
    jjdm_list=list(set(jjdm_list+pri_basis['jjdm'].unique().tolist()))
    jjdm_list_core=pri_basis['jjdm'].unique().tolist()

    result1=[]
    result2 = []
    result3 = []

    result4=[]
    result5 = []
    result6 = []

    for jjdm in jjdm_list:

        # try:
        jj_ret=hbdb.db2df("select hbdr,jzrq,fqdwjz from st_hedge.t_st_rhb where jjdm='{}' and hbdr!=0".format(jjdm)
                          ,db='highuser').rename(columns={'hbdr':jjdm})
        if((len(jj_ret)==0 or jj_ret['jzrq'].min()>='20200507' or jj_ret['jzrq'].max()<='20220101')
                and (jjdm not in jjdm_list_core) ):
            continue
        jj_ret['jzrq']=jj_ret['jzrq'].astype(int)
        jj_ret.set_index('jzrq',inplace=True)

        olsdf=pd.merge(jj_ret,style_index_ret,how='left',left_index=True,right_index=True).fillna(0)
        if(len(olsdf)<=12):
            continue
        olsdf[['399372', '399373', '399374', '399375','399376', '399377', 'CBA00301']]=\
            olsdf[['399372', '399373', '399374', '399375','399376', '399377', 'CBA00301']].pct_change()*100

        olsdf['399374'] = (olsdf['399374'] + olsdf['399376']) / 2
        olsdf['399375'] = (olsdf['399375'] + olsdf['399377']) / 2
        olsdf.drop(['399376','399377'],axis=1,inplace=True)
        olsdf = olsdf[olsdf['399372'] < 9999]

        laster_half_year=olsdf.index[olsdf.index>=int((datetime.datetime.strptime(str(jj_ret.index[-1]),
                                                     '%Y%m%d')-datetime.timedelta(days=183)).strftime('%Y%m%d'))][0]
        last_year=olsdf.index[olsdf.index>=int((datetime.datetime.strptime(str(jj_ret.index[-1]),
                                                     '%Y%m%d')-datetime.timedelta(days=365)).strftime('%Y%m%d'))][0]
        last_oneandhalfyear=olsdf.index[olsdf.index>=int((datetime.datetime.strptime(str(jj_ret.index[-1]),
                                                     '%Y%m%d')-datetime.timedelta(days=365+182)).strftime('%Y%m%d'))][0]
        para = sm.OLS(olsdf.loc[int(laster_half_year):][jjdm].values,
                      olsdf.loc[int(laster_half_year):][
                          ['399372', '399373', '399374', '399375', 'CBA00301']].values).fit().params.tolist()
        result1.append(para+[jjdm])
        result4.append([para[0] + para[1], para[2] + para[3], para[0] + para[2],
                        para[1] + para[3], para[0] + para[1] - para[2] + para[3], para[0] + para[2] - para[1] + para[3],
                        jjdm])

        para = sm.OLS(olsdf.loc[int(last_year):][jjdm].values,
                      olsdf.loc[int(last_year):][
                          ['399372', '399373', '399374', '399375', 'CBA00301']].values).fit().params.tolist()
        result2.append(para+[jjdm])
        result5.append([para[0] + para[1], para[2] + para[3], para[0] + para[2],
                        para[1] + para[3], para[0] + para[1] - para[2] + para[3], para[0] + para[2] - para[1] + para[3],
                        jjdm])

        para = sm.OLS(olsdf.loc[int(last_oneandhalfyear):][jjdm].values,
                      olsdf.loc[int(last_oneandhalfyear):][
                          ['399372', '399373', '399374', '399375', 'CBA00301']].values).fit().params.tolist()
        result3.append(para+[jjdm])
        result6.append([para[0] + para[1], para[2] + para[3], para[0] + para[2],
                        para[1] + para[3], para[0] + para[1] - para[2] + para[3], para[0] + para[2] - para[1] + para[3],
                        jjdm])

        # except Exception as e:
        #     print(jjdm)
        #     print(e)



    result4=pd.DataFrame(data=result4,columns=['大盘','中小盘','成长','价值','大-中小','成长-价值','jjdm'])
    result5 = pd.DataFrame(data=result5, columns=['大盘','中小盘','成长','价值','大-中小','成长-价值','jjdm'])
    result6 = pd.DataFrame(data=result6, columns=['大盘','中小盘','成长','价值','大-中小','成长-价值','jjdm'])

    result1=pd.DataFrame(data=result1,columns=['大盘成长','大盘价值','中小盘成长','中小盘价值','中债','jjdm'])
    result2 = pd.DataFrame(data=result2, columns=['大盘成长','大盘价值','中小盘成长','中小盘价值','中债','jjdm'])
    result3 = pd.DataFrame(data=result3, columns=['大盘成长','大盘价值','中小盘成长','中小盘价值','中债','jjdm'])


    col_list = ['大盘成长', '大盘价值', '中小盘成长', '中小盘价值', '中债']
    result1[col_list]=result1[col_list].rank(method='min') / len(result1)
    result2[col_list]= result2[col_list].rank(method='min') / len(result2)
    result3[col_list] = result3[col_list].rank(method='min') / len(result3)



    output=result1.copy()
    output[col_list]=(result1[col_list]+result2[col_list]
                      +result3[col_list])/3
    outdf=pd.merge(pri_basis,output,how='left',on='jjdm')
    outdf.to_excel('prv_core_ols_1.xlsx')


    col_list2 = ['大盘', '中小盘', '成长', '价值', '大-中小', '成长-价值']
    result4[col_list2]=result4[col_list2].rank(method='min') / len(result4)
    result5[col_list2]= result5[col_list2].rank(method='min') / len(result5)
    result6[col_list2] = result6[col_list2].rank(method='min') / len(result6)
    output=result4.copy()
    output[col_list2]=(result4[col_list2]+result5[col_list2]
                      +result6[col_list2])/3
    outdf=pd.merge(pri_basis,output,how='left',on='jjdm')
    outdf.to_excel('prv_core_ols_2.xlsx')

def style_exp_simpleols_foroutsideuser_mu():



    style_index_ret = get_styleindex_ret(['399372', '399373', '399374', '399375', '399376', '399377', 'CBA00301'],
                                         start_date='20100105')
    style_index_ret['399374'] = (style_index_ret['399374'] + style_index_ret['399376']) / 2
    style_index_ret['399375'] = (style_index_ret['399375'] + style_index_ret['399377']) / 2
    style_index_ret=style_index_ret[['399372', '399373', '399374', '399375','CBA00301']]

    sql="select * from core_pool_history where asofdate='{}'".format('202203')
    mutual_pool=pd.read_sql(sql,con=localdb).rename(columns={'基金代码':'jjdm',
                                                      '基金名称':'jjjc',
                                                      '基金经理':'manager'})
    jjdm_list=util.get_mutual_stock_funds('20210331')


    result1=[]
    result2 = []
    result3 = []

    result4=[]
    result5 = []
    result6 = []

    for jjdm in jjdm_list:
        # # get jj nav ret
        # try:
        jj_ret = get_jj_daily_ret([jjdm])

        olsdf=pd.merge(jj_ret,style_index_ret,how='left',left_index=True,right_index=True).fillna(0)

        laster_half_year = olsdf.index[olsdf.index >= int((datetime.datetime.strptime(str(jj_ret.index[-1]),
                                                                                      '%Y%m%d') - datetime.timedelta(
            days=183)).strftime('%Y%m%d'))][0]
        last_year = olsdf.index[olsdf.index >= int((datetime.datetime.strptime(str(jj_ret.index[-1]),
                                                                               '%Y%m%d') - datetime.timedelta(
            days=365)).strftime('%Y%m%d'))][0]
        last_oneandhalfyear = olsdf.index[olsdf.index >= int((datetime.datetime.strptime(str(jj_ret.index[-1]),
                                                                                         '%Y%m%d')-datetime.timedelta(days=365+182)).strftime('%Y%m%d'))][0]
        para = sm.OLS(olsdf.loc[int(laster_half_year):][jjdm].values,
                      olsdf.loc[int(laster_half_year):][
                          ['399372', '399373', '399374', '399375', 'CBA00301']].values).fit().params.tolist()
        result1.append(para + [jjdm])
        result4.append([para[0] + para[1], para[2] + para[3], para[0] + para[2],
                        para[1] + para[3], para[0] + para[1] - para[2] + para[3],
                        para[0] + para[2] - para[1] + para[3],
                        jjdm])

        para = sm.OLS(olsdf.loc[int(last_year):][jjdm].values,
                      olsdf.loc[int(last_year):][
                          ['399372', '399373', '399374', '399375', 'CBA00301']].values).fit().params.tolist()
        result2.append(para + [jjdm])
        result5.append([para[0] + para[1], para[2] + para[3], para[0] + para[2],
                        para[1] + para[3], para[0] + para[1] - para[2] + para[3],
                        para[0] + para[2] - para[1] + para[3],
                        jjdm])

        para = sm.OLS(olsdf.loc[int(last_oneandhalfyear):][jjdm].values,
                      olsdf.loc[int(last_oneandhalfyear):][
                          ['399372', '399373', '399374', '399375', 'CBA00301']].values).fit().params.tolist()
        result3.append(para + [jjdm])
        result6.append([para[0] + para[1], para[2] + para[3], para[0] + para[2],
                        para[1] + para[3], para[0] + para[1] - para[2] + para[3],
                        para[0] + para[2] - para[1] + para[3],
                        jjdm])

        #
        # except Exception as e:
        #     print(jjdm)
        #     print(e)


    result4=pd.DataFrame(data=result4,columns=['大盘','中小盘','成长','价值','大-中小','成长-价值','jjdm'])
    result5 = pd.DataFrame(data=result5, columns=['大盘','中小盘','成长','价值','大-中小','成长-价值','jjdm'])
    result6 = pd.DataFrame(data=result6, columns=['大盘','中小盘','成长','价值','大-中小','成长-价值','jjdm'])

    result1=pd.DataFrame(data=result1,columns=['大盘成长','大盘价值','中小盘成长','中小盘价值','中债','jjdm'])
    result2 = pd.DataFrame(data=result2, columns=['大盘成长','大盘价值','中小盘成长','中小盘价值','中债','jjdm'])
    result3 = pd.DataFrame(data=result3, columns=['大盘成长','大盘价值','中小盘成长','中小盘价值','中债','jjdm'])


    col_list = ['大盘成长', '大盘价值', '中小盘成长', '中小盘价值', '中债']
    result1[col_list]=result1[col_list].rank(method='min') / len(result1)
    result2[col_list]= result2[col_list].rank(method='min') / len(result2)
    result3[col_list] = result3[col_list].rank(method='min') / len(result3)



    output=result1.copy()
    output[col_list]=(result1[col_list]+result2[col_list]
                      +result3[col_list])/3
    outdf=pd.merge(mutual_pool,output,how='left',on='jjdm')
    outdf.to_excel('mu_core_ols_1.xlsx')


    col_list2 = ['大盘', '中小盘', '成长', '价值', '大-中小', '成长-价值']
    result4[col_list2]=result4[col_list2].rank(method='min') / len(result4)
    result5[col_list2]= result5[col_list2].rank(method='min') / len(result5)
    result6[col_list2] = result6[col_list2].rank(method='min') / len(result6)
    output=result4.copy()
    output[col_list2]=(result4[col_list2]+result5[col_list2]
                      +result6[col_list2])/3

    output.to_excel('mu_core_ols_2all.xlsx')
    outdf=pd.merge(mutual_pool,output,how='left',on='jjdm')
    outdf.to_excel('mu_core_ols_2.xlsx')

class Scenario_return:
    @staticmethod
    def get_histroy_scenario_ret():
        benchmark_ret=get_monthly_index_ret('000002')
        benchmark_ret['med']=99999
        benchmark_ret['scenario'] = ''
        for i in range(1,len(benchmark_ret)):
            benchmark_ret.loc[i,'med']=benchmark_ret.loc[0:i-1]['hb1y'].median()
            if(benchmark_ret.loc[i,'med']>=benchmark_ret.loc[i,'hb1y']):
                benchmark_ret.loc[i, 'scenario']='opt'
            else:
                benchmark_ret.loc[i, 'scenario'] = 'pes'

        return  benchmark_ret[['scenario','hb1y','tjyf','rqzh']]

    @staticmethod
    def pessimistic_ret(jjdm,benchmark_ret):

        navdf,max_yearmonth,min_yearmonth=get_monthly_jjnav([jjdm])

        navdf=pd.merge(navdf,benchmark_ret,how='left',on='tjyf')

        navdf['ext_ret']=navdf['hb1y_x']-navdf['hb1y_y']
        navdf.rename(columns={'rqzh_y':'rqzh'},inplace=True)

        #last 12 month average month return by calculating last 12 month cul ret and turn it into month return

        temp=navdf[navdf['scenario']=='pes']['ext_ret'].rolling(12).apply(bhar)
        temp=temp.to_frame('pes_ext_ret')
        navdf=pd.merge(navdf,temp,how='left',left_index=True, right_index=True)

        temp=navdf[navdf['scenario']=='opt']['ext_ret'].rolling(12).apply(bhar)
        temp=temp.to_frame('opt_ext_ret')
        navdf=pd.merge(navdf,temp,how='left',left_index=True, right_index=True)

        navdf['ext_ret'] = navdf['ext_ret'].rolling(12).apply(bhar)


        last_pes_ret=np.nan
        last_opt_ret=np.nan

        for i in range(0,len(navdf)):
            if(navdf.loc[i]['pes_ext_ret']==navdf.loc[i]['pes_ext_ret']):
                last_pes_ret=navdf.loc[i]['pes_ext_ret']

            else:
                navdf.loc[i,'pes_ext_ret']=last_pes_ret

            if(navdf.loc[i]['opt_ext_ret']==navdf.loc[i]['opt_ext_ret']):
                last_opt_ret=navdf.loc[i]['opt_ext_ret']

            else:
                navdf.loc[i,'opt_ext_ret']=last_opt_ret

        navdf=navdf[navdf['ext_ret'].notnull()]

        # for col in['ext_ret','pes_ext_ret','opt_ext_ret']:
        #     navdf[col] = (navdf[col]/100).astype(float).map("{:.2%}".format)

        return navdf[['jjdm','tjyf','rqzh','ext_ret','pes_ext_ret','opt_ext_ret']]

    @staticmethod
    def factorlize_ret(factor_name,fre='M'):

        sql="select * from scenario_ret"
        raw_df=pd.read_sql(sql,con=localdb)

        raw_df.rename(columns={'rqzh':'date'},inplace=True)
        raw_df=raw_df[raw_df[factor_name].notnull()]


        if(fre=='Q'):
            raw_df = raw_df[(raw_df['tjyf'].astype(str).str[4:6] == '03') | (raw_df['tjyf'].astype(str).str[4:6] == '06') | (
                        raw_df['tjyf'].astype(str).str[4:6] == '09') | (raw_df['tjyf'].astype(str).str[4:6] == '12')]
        elif(fre=='HA'):
            raw_df = raw_df[(raw_df['tjyf'].astype(str).str[4:6] == '06') | (raw_df['tjyf'].astype(str).str[4:6] == '12')]


        return raw_df

class Style_exp:


    def __init__(self,asofdate,fre='Q',start_date=None,end_date=None):


        self.jjdm_list=util.get_mutual_stock_funds(asofdate)

        #self.write_style_exp2DB(self.jjdm_list, fre, start_date, end_date)

        #self.write_theme_exp2DB(self.jjdm_list, fre, start_date, end_date)

    @staticmethod
    def write_style_exp2DB(jjdm_list,fre,start_date=None,end_date=None):

        value_col = ['399370', '399371']
        size_col=['399314','399315','399316']
        bond_col=['CBA00301']

        #get value index ret :
        style_index_ret=get_styleindex_ret(value_col+size_col+bond_col)

        if(fre=='M'):
            def timezone_transform(olsdf):
                olsdf['yearmonth'] = [str(x)[0:6] for x in olsdf.index]
                return olsdf
        elif(fre=='Q'):
            def timezone_transform(olsdf):
                olsdf['yearmonth'] = ''
                olsdf.loc[olsdf.index.astype(str).str[4:6]<='03','yearmonth']='Q1'
                olsdf.loc[(olsdf.index.astype(str).str[4:6] <= '06')&(olsdf.index.astype(str).str[4:6] > '03'), 'yearmonth'] = 'Q2'
                olsdf.loc[(olsdf.index.astype(str).str[4:6] <= '09')&(olsdf.index.astype(str).str[4:6] > '06'), 'yearmonth'] = 'Q3'
                olsdf.loc[(olsdf.index.astype(str).str[4:6] <= '12')&(olsdf.index.astype(str).str[4:6] > '09'), 'yearmonth'] = 'Q4'
                olsdf['yearmonth']=olsdf.index.astype(str).str[0:4]+olsdf['yearmonth']

                return olsdf

        value_exp_df = pd.DataFrame()
        size_exp_df = pd.DataFrame()

        for jjdm in jjdm_list:

            #get jj nav ret
            jj_ret=get_jj_daily_ret([jjdm])

            olsdf = pd.merge(jj_ret, style_index_ret, how='inner', left_index=True, right_index=True)

            olsdf=timezone_transform(olsdf)


            tempdf=olsdf[olsdf[[jjdm]+value_col+bond_col].notnull().sum(axis=1)==(len(value_col)+2)]
            tempdf=tempdf.groupby('yearmonth')[[jjdm]+value_col+bond_col].apply(ols_for_group).to_frame('exp')
            i=0
            for col in value_col+bond_col:
                tempdf[col]=[x[i] for x in tempdf['exp']]
                i+=1
            tempdf.drop('exp',inplace=True,axis=1)
            tempdf['jjdm']=jjdm
            value_exp_df=pd.concat([value_exp_df,tempdf],axis=0)


            tempdf=olsdf[olsdf[[jjdm]+size_col+bond_col].notnull().sum(axis=1)==(len(size_col)+2)]
            tempdf=tempdf.groupby('yearmonth')[[jjdm]+size_col+bond_col].apply(ols_for_group).to_frame('exp')
            i=0
            for col in size_col+bond_col:
                tempdf[col]=[x[i] for x in tempdf['exp']]
                i+=1
            tempdf.drop('exp',inplace=True,axis=1)
            tempdf['jjdm'] = jjdm
            size_exp_df=pd.concat([size_exp_df,tempdf],axis=0)

            print('jj {} Done'.format(jjdm))

        value_exp_df=value_exp_df.reset_index().rename(columns={'yearmonth':'date'})
        size_exp_df=size_exp_df.reset_index().rename(columns={'yearmonth':'date'})

        value_exp_df['fre']=fre
        size_exp_df['fre']=fre

        value_exp_df.to_sql('nav_value_exposure',index=False,if_exists='append',con=localdb)
        size_exp_df.to_sql('nav_size_exposure', index=False, if_exists='append',con=localdb)

    @staticmethod
    def write_theme_exp2DB(jjdm_list,fre,start_date=None,end_date=None):

        industry_con=['Bank', 'RealEstate', 'Health', 'Transportation', 'Mining', 'NonFerMetal',
        'HouseApp', 'LeiService', 'MachiEquip', 'BuildDeco', 'CommeTrade',
        'CONMAT', 'Auto', 'Textile', 'FoodBever', 'Electronics',
        'Computer', 'LightIndus', 'Utilities', 'Telecom', 'AgriForest',
        'CHEM', 'Media', 'IronSteel', 'NonBankFinan', 'ELECEQP', 'AERODEF',
        'Conglomerates']

        bond_col=['CBA00301']

        #get value index ret :
        #style_index_ret=get_styleindex_ret(bond_col)
        style_index_ret=get_barra_ret(industry_con)
        style_index_ret.index=style_index_ret.index.astype(int)
        style_index_ret=pd.merge(style_index_ret,get_styleindex_ret(bond_col),
                                 how='inner',left_index=True,right_index=True)

        if(fre=='M'):
            def timezone_transform(olsdf):
                olsdf['yearmonth'] = [str(x)[0:6] for x in olsdf.index]
                return olsdf
        elif(fre=='Q'):
            def timezone_transform(olsdf):
                olsdf['yearmonth'] = ''
                olsdf.loc[olsdf.index.astype(str).str[4:6]<='03','yearmonth']='Q1'
                olsdf.loc[(olsdf.index.astype(str).str[4:6] <= '06')&(olsdf.index.astype(str).str[4:6] > '03'), 'yearmonth'] = 'Q2'
                olsdf.loc[(olsdf.index.astype(str).str[4:6] <= '09')&(olsdf.index.astype(str).str[4:6] > '06'), 'yearmonth'] = 'Q3'
                olsdf.loc[(olsdf.index.astype(str).str[4:6] <= '12')&(olsdf.index.astype(str).str[4:6] > '09'), 'yearmonth'] = 'Q4'
                olsdf['yearmonth']=olsdf.index.astype(str).str[0:4]+olsdf['yearmonth']

                return olsdf

        industry_exp_df = pd.DataFrame()

        for jjdm in jjdm_list:

            #get jj nav ret
            jj_ret=get_jj_daily_ret([jjdm])

            olsdf = pd.merge(jj_ret, style_index_ret, how='inner', left_index=True, right_index=True)

            olsdf=timezone_transform(olsdf)

            theme_col=['大金融','周期','制造', '消费', 'TMT']

            tempdf=olsdf[olsdf[[jjdm]+theme_col+bond_col].notnull().sum(axis=1)==(len(theme_col)+2)]
            tempdf=tempdf.groupby('yearmonth')[[jjdm]+theme_col+bond_col].apply(ols_withcons_for_group).to_frame('exp')
            i=0
            for col in theme_col+bond_col:
                tempdf[col]=[x[i] for x in tempdf['exp']]
                i+=1
            tempdf.drop('exp',inplace=True,axis=1)
            tempdf['jjdm']=jjdm
            industry_exp_df=pd.concat([industry_exp_df,tempdf],axis=0)

            print('jj {} Done'.format(jjdm))

        industry_exp_df=industry_exp_df.reset_index().rename(columns={'yearmonth':'date'})

        industry_exp_df['fre']=fre

        industry_exp_df.to_sql('nav_theme_exposure',index=False,if_exists='append',con=localdb)

class Style_analysis:

    def __init__(self,jjdm_list,fre,asofdate=datetime.datetime.today().strftime('%Y%m%d'),time_length=3):

        self.value_col = ['399370', '399371']
        self.size_col=['399314','399315','399316']
        self.bond_col=['CBA00301']
        self.theme_col=['大金融','周期','制造', '消费', 'TMT']
        self.jjdm_list=jjdm_list

        self.index_map=dict(zip(self.value_col+self.size_col,['成长','价值','大盘','中盘','小盘']))

        self.theme_map=dict(zip(self.theme_col,self.theme_col))

        start_year=str(int(asofdate[0:4])-time_length)

        if(fre=='M'):
            start_date=start_year+asofdate[4:6]
        else:
            if(asofdate[4:6]<='03'):
                Q=1
            elif(asofdate[4:6]>'03' and asofdate[4:6]<='06'):
                Q=2
            elif(asofdate[4:6]>'06' and asofdate[4:6]<='09'):
                Q=3
            elif(asofdate[4:6]>'09' and asofdate[4:6]<='12'):
                Q=4
            start_date=start_year+"Q"+str(Q)

        self.val_date=self.get_jj_valuation_date(jjdm_list,asofdate)
        self.fre=fre
        self.asofdate=asofdate
        self.start_date=start_date

    @staticmethod
    def get_jj_valuation_date(jjdm_list,asofdate):

        jjdm_con=util.list_sql_condition(jjdm_list)
        #read jjjl info
        sql="select jjdm,ryxm,rydm,rzrq from st_fund.t_st_gm_jjjl where ryzt='-1' and jjdm in ({0}) "\
            .format(jjdm_con)
        jj_val_date=hbdb.db2df(sql,db='funduser')

        #for jj with multi managers,take the one with longer staying in this jj
        jj_val_date=jj_val_date.sort_values('rzrq')
        jj_val_date.drop_duplicates('jjdm', keep='first', inplace=True)

        #remove jj with manager managing no longer than 1.5years
        # last_oneandhalfyear = (datetime.datetime.strptime(asofdate, '%Y%m%d')
        #                        -datetime.timedelta(days=560)).strftime('%Y%m%d')
        # jj_val_date['rzrq']=jj_val_date['rzrq'].astype(str)
        # jj_val_date=jj_val_date[jj_val_date['rzrq']<=last_oneandhalfyear]


        return  jj_val_date[['jjdm','rzrq','rydm']]

    @staticmethod
    def read_jj_style_exp(jjdm_list,type,fre,start_date):

        jjdm_con=util.list_sql_condition(jjdm_list)
        sql="select * from nav_{0}_exposure where jjdm in ({1}) and fre='{2}' and date>='{3}'"\
            .format(type,jjdm_con,fre,start_date)
        expdf=pd.read_sql(sql,con=localdb)

        return  expdf

    @staticmethod
    def cal_style_shift_ratio(df,style_col):

        # calculate the total change in styles

        df['shift_ratio'] = df[style_col].diff().abs().sum(axis=1)

        # df['change'] = df[style_col].diff().abs().sum(axis=1)
        # # calculate the average style exp between two dates
        # df['avg_exp'] = df[style_col].sum(axis=1).rolling(2).mean()
        # # calculate shift ratio
        # df['shift_ratio'] = df['change'] / df['avg_exp']

        return df['shift_ratio'].values

    @staticmethod
    def standardliza_by_rank(style_df,style_col,bond_col):

        style_df[[x+'_abs' for x in style_col]]=style_df[style_col]
        style_df[style_col] = style_df.groupby('date').rank(method='min')[style_col]

        style_df = pd.merge(style_df,
                            style_df.groupby('date').count()['jjdm'].to_frame('count'),
                            left_on='date', right_index=True)
        for col in style_col + bond_col:
            style_df[col] = style_df[col] / style_df['count']

        return  style_df

    @staticmethod
    def standardlize_by_robust(style_df,style_col):
        from sklearn.preprocessing import RobustScaler
        rs = RobustScaler()
        style_df[style_col] = rs.fit_transform(style_df[style_col].values)

        return  style_df

    def get_style_property(self,style_df,style_col,type,method=''):

        # style_df = style_df.drop_duplicates()
        style_map = self.index_map

        if(type=='size'):

            def centralization(df):
                centralization = np.mean((df.max(axis=1) * 2 + tempdf.median(axis=1)) / 3)
                return centralization
        else:
            def centralization(df):
                centralization = np.mean(df.max(axis=1))
                return centralization


        #standradlize the exp by either robustscaler or by ranking for each date
        if(method=='robust'):
            style_df = self.standardlize_by_robust(style_df, style_col)
        elif(method=='rank'):
            style_df=self.standardliza_by_rank(style_df,style_col,self.bond_col)


        asofdate=style_df['date'].max()

        style_property_df=pd.DataFrame()

        temp=style_df.groupby('jjdm').min()['date']
        new_jjdm_list=temp[temp<=self.start_date].index.tolist()

        new_jjdm_list.sort()

        style_property_df['jjdm']=new_jjdm_list

        for jjdm in new_jjdm_list:

            #check if manager changed during the time zone
            tempdf=style_df[style_df['jjdm']==jjdm]
            if(len(self.val_date[self.val_date['jjdm']==jjdm]['rzrq'])>0):
                manager_change=str(str(self.val_date[self.val_date['jjdm']==jjdm]['rzrq'].values[0])[0:6]<=self.start_date)
            else:
                manager_change='False'

            tempdf2 = tempdf.copy()
            total_weight = tempdf2[style_col].sum(axis=1)
            for col in style_col:
                tempdf2[col] = tempdf2[col].values / total_weight


            tempdf['shift_ratio'] = self.cal_style_shift_ratio(tempdf2, style_col)
            # tempdf['shift_ratio']=self.cal_style_shift_ratio(tempdf,style_col)/tempdf[self.bond_col].std()[0]


            # centralization=(tempdf[style_col].std(axis=1)/tempdf[style_col].mean(axis=1)).mean()
            #centralization = (tempdf[style_col].std(axis=1)).mean()
            centralization_lv=centralization(tempdf2[style_col])


            style_property_df.loc[style_property_df['jjdm'] == jjdm,
                                  'shift_ratio'] = tempdf['shift_ratio'].mean()
            style_property_df.loc[style_property_df['jjdm'] == jjdm,
                                  'centralization'] = centralization_lv

            for col in style_col:
                style_property_df.loc[style_property_df['jjdm'] == jjdm,
                                      style_map[col] + '_mean'] = tempdf[col].mean()
                # get the absolute exp
                style_property_df.loc[style_property_df['jjdm'] == jjdm,
                                      style_map[col] + '_abs_mean'] = tempdf[col+'_abs'].mean()


            style_property_df.loc[style_property_df['jjdm'] == jjdm,
                                  'manager_change'] = manager_change
        #get the style rank%
        # rank_col=style_property_df.columns.tolist()
        # rank_col.remove('jjdm')
        rank_col=['shift_ratio','centralization']
        style_property_df[[x+'_rank' for x in rank_col]]=style_property_df[rank_col].rank(method='min')/len(style_property_df)

        style_property_df['asofdate']=asofdate

        return style_property_df

    def save_style_property2localdb(self):

        # sql="select distinct asofdate from nav_style_property_value where fre='{0}' and by_manager='{1}' "\
        #     .format(self.fre,'True')
        # asofdate_list=pd.read_sql(sql,con=localdb)['asofdate'].values.tolist()
        #
        # if(self.asofdate in asofdate_list):
        #     sql="delete from nav_style_property_value where asofdate='{0}' and fre-'{1}' and by_manager='{2}'"\
        #         .format(self.asofdate,self.fre,'True'+str(self.consistant_date))
        #     localdb.excute(sql)


        # value_df=self.get_style_property(self.read_jj_style_exp(self.jjdm_list,
        #                                 'value',self.fre,self.start_date)
        #                                  ,self.value_col,'value',method='')
        # value_df['fre']=self.fre
        # value_df.to_sql('new_nav_style_property_value',index=False,con=localdb,if_exists='append')
        #
        # size_df=self.get_style_property(self.read_jj_style_exp(self.jjdm_list,
        #                                 'size',self.fre,self.start_date)
        #                                  ,self.size_col,'size',method='')
        # size_df['fre'] = self.fre
        # size_df.to_sql('new_nav_style_property_size',index=False,con=localdb,if_exists='append')


        value_df=self.get_style_property(self.read_jj_style_exp(self.jjdm_list,
                                        'value',self.fre,self.start_date)
                                         ,self.value_col,'value',method='rank')
        value_df['fre']=self.fre

        #check if data alreay exist :
        sql="delete from nav_style_property_value where asofdate='{0}' and fre='{1}'"\
            .format(value_df['asofdate'][0],self.fre)
        localdb.execute(sql)

        value_df.to_sql('nav_style_property_value',index=False,con=localdb,if_exists='append')

        size_df=self.get_style_property(self.read_jj_style_exp(self.jjdm_list,
                                        'size',self.fre,self.start_date)
                                         ,self.size_col,'size',method='rank')
        size_df['fre'] = self.fre

        #check if data alreay exist :
        sql="delete from nav_style_property_size where asofdate='{0}' and fre='{1}'"\
            .format(size_df['asofdate'][0],self.fre)
        localdb.execute(sql)

        size_df.to_sql('nav_style_property_size',index=False,con=localdb,if_exists='append')


        # industry_df=self.get_style_property(self.read_jj_style_exp(self.jjdm_list,
        #                                 'theme',self.fre,self.start_date)
        #                                  ,self.theme_col,'theme')
        # industry_df['fre']=self.fre
        # industry_df.to_sql('nav_style_property_theme',index=False,con=localdb,if_exists='append')


    #below if function for futher style shift analysis


    def style_change_detect_engine(self,q_df,diff1,diff2,q_list,col_list,t1,t2):

        style_change=[]

        for col in col_list:

            potential_date=diff2[diff2[col]<=-1*t1].index.to_list()
            last_added_date=q_list[-1]
            for date in potential_date:
                if(diff1.loc[q_df.index[q_df.index<=date][-3]][col]<=-1*t2):
                    added_date=q_df.index[q_df.index<=date][-3]
                elif(diff1.loc[q_df.index[q_df.index<=date][-2]][col]<=-1*t2):
                    added_date=q_df.index[q_df.index<=date][-2]
                elif(diff1.loc[q_df.index[q_df.index<=date][-1]][col]<=-1*t2):
                    added_date = q_df.index[q_df.index <= date][-1]
                else:
                    added_date = q_df.index[q_df.index <= date][-3]

                if((q_list.index(added_date)-q_list.index(last_added_date)<=2
                        and q_list.index(added_date)-q_list.index(last_added_date)>0) or added_date==q_list[-1]):
                    continue
                else:
                    style_change.append(added_date + "@" + col)
                    last_added_date = added_date

            potential_date = diff2[diff2[col] >= t1].index.to_list()
            last_added_date = q_list[-1]
            for date in potential_date:
                if (diff1.loc[q_df.index[q_df.index <= date][-3]][col] >= t2):
                    added_date = q_df.index[q_df.index <= date][-3]
                elif (diff1.loc[q_df.index[q_df.index <= date][-2]][col] >= t2):
                    added_date = q_df.index[q_df.index <= date][-2]
                elif (diff1.loc[q_df.index[q_df.index <= date][-1]][col] >= t2):
                    added_date = q_df.index[q_df.index <= date][-1]
                else:
                    added_date = q_df.index[q_df.index <= date][-3]

                if (q_list.index(added_date) - q_list.index(last_added_date) <= 2
                        and q_list.index(added_date) - q_list.index(last_added_date) > 0):
                    continue
                else:
                    style_change.append(added_date + "@" + col)
                    last_added_date = added_date

        return style_change

    def style_change_detect_engine2(self, q_df, diff1, col_list, t1, t2):

        style_change=[]
        t3=t2/2

        for col in col_list:

            tempdf=pd.merge(q_df[col],diff1[col],how='left',on='date')
            tempdf['style']=''
            style_num=0
            tempdf['style'].iloc[0:2] = style_num

            for i in range(2,len(tempdf)-1):
                if(tempdf[col+'_y'].iloc[i]>t1 and tempdf[col+'_y'].iloc[i+1]>-1*t3 ):
                    style_num+=1
                    added_date = tempdf.index[i]
                    style_change.append(added_date + "@" + col)
                elif(tempdf[col+'_x'].iloc[i]-tempdf[tempdf['style']==style_num][col+'_x'][0]>t1 and
                     tempdf[col+'_y'].iloc[i]>t2 and tempdf[col+'_y'].iloc[i+1]>-1*t3):
                    style_num += 1
                    added_date=tempdf.index[i]
                    style_change.append(added_date + "@" + col)
                elif(tempdf[col+'_y'].iloc[i]<-1*t1 and tempdf[col+'_y'].iloc[i+1]<t3 ):
                    style_num += 1
                    added_date = tempdf.index[i]
                    style_change.append(added_date + "@" + col)
                elif (tempdf[col + '_x'].iloc[i] - tempdf[tempdf['style'] == style_num][col + '_x'][0] < -1*t1 and
                      tempdf[col + '_y'].iloc[i] < -1*t2 and tempdf[col + '_y'].iloc[i + 1] <  t3):
                    style_num += 1
                    added_date = tempdf.index[i]
                    style_change.append(added_date + "@" + col)

                tempdf['style'].iloc[i] = style_num

        return style_change

    def style_change_detect(self,df,q_list,col_list,t1,t2):

        q_list.sort()
        q_df = df.loc[q_list]
        diff1=q_df.diff(1)
        # diff2=q_df.rolling(3).mean().diff(2)
        # diff4 = q_df.rolling(3).mean().diff(4)

        # style_change_short=self.style_change_detect_engine(q_df,diff1,diff2,q_list,col_list,t1,t2)
        # style_change_long=self.style_change_detect_engine(q_df,diff1,diff4,q_list,col_list,t1,t2)
        # style_change=style_change_short+style_change_long

        style_change = self.style_change_detect_engine2(q_df, diff1, col_list, t1, t2)

        return list(set(style_change)),np.array(q_list)

    def shifting_expression(self,change_ret,name,jjdm,style='Total'):

        change_winning_pro_hld = sum(change_ret[3]) / len(change_ret)
        change_winning_pro_nextq=sum(change_ret[2]) / len(change_ret)
        left_ratio = sum(change_ret[0]) / len(change_ret)
        left_ratio_deep = sum(change_ret[1]) / len(change_ret)
        # right_ratio = 1-left_ratio
        # right_ratio_deep = 1 - left_ratio_deep
        one_q_ret = change_ret[4].mean()
        hid_q_ret = change_ret[5].mean()

        return  np.array([style.split('_')[0],len(change_ret),change_winning_pro_hld,change_winning_pro_nextq
                             ,one_q_ret,hid_q_ret,left_ratio,left_ratio_deep])

    def style_change_ret(self,df,q_list,col_list,t1,t2,factor_ret):

        style_change,q_list = self.style_change_detect(df,q_list,col_list,t1,t2)
        change_count = len(style_change)
        style_changedf=pd.DataFrame()
        style_changedf['date']=[x.split('@')[0] for x in style_change]
        style_changedf['style']=[x.split('@')[1] for x in style_change]
        style_changedf.sort_values('date',inplace=True,ascending=False)
        style_chang_extret=dict(zip(style_change,style_change))


        # def get_factor_return(q_list, first_change_date, style):
        #
        #     # get value index ret :
        #     sql="select zqdm,jyrq,spjg from st_market.t_st_zs_hqql where zqdm='{0}' and jyrq>='{1}' and jyrq<='{2}'"\
        #         .format(style, q_list[q_list < first_change_date][-2]+'01', q_list[-1]+'31')
        #
        #     fac_ret_df=hbdb.db2df(sql,db='alluser')
        #     fac_ret_df['jyrq']=fac_ret_df['jyrq'].astype(str)
        #
        #     fac_ret_df['ym']=fac_ret_df['jyrq'].str[0:6]
        #     tempdf=fac_ret_df.drop_duplicates('ym', keep='last')[['jyrq','ym']]
        #     fac_ret_df=pd.merge(fac_ret_df,tempdf,how='left',on='jyrq').fillna('').drop('ym_x',axis=1)
        #
        #     # fac_ret_df['jyrq'] = fac_ret_df['ym']
        #     fac_ret_df.set_index('ym_y', drop=True, inplace=True)
        #
        #     fac_ret_df['price'] = fac_ret_df['spjg']
        #
        #     return fac_ret_df

        def q_ret(fac_ret_df,q0,q1,time_length=1):
            res=np.power(fac_ret_df.loc[q1]['price']/fac_ret_df.loc[q0]['price'],1/time_length)-1
            return  res


        if(change_count>0):
            for style in style_changedf['style']:

                changedf=style_changedf[style_changedf['style']==style]
                changedf=changedf.sort_values('date')
                first_change_date=changedf['date'].values[0]
                fac_ret_df=factor_ret[(factor_ret['zqdm'] == style) & (
                            factor_ret['jyrq'] >= q_list[q_list < first_change_date][-2] + '01') & (
                                       factor_ret['jyrq'] <= q_list[-1] + '31')]
                # fac_ret_df=get_factor_return(q_list,first_change_date,style)


                for i in range(len(changedf)):
                    date=changedf.iloc[i]['date']

                    observer_term=np.append(q_list[q_list<date][-2:],q_list[(q_list>=date)][0:2])

                    new_exp=df[style].loc[observer_term[2]]
                    old_exp=df[style].loc[observer_term[1]]

                    q0=observer_term[0]
                    q1=observer_term[1]
                    old_ret=q_ret(fac_ret_df,q0,q1)
                    #if_left_deep = fac_ret_df['price'].loc[q0:q1].mean() > fac_ret_df['price'].loc[q1]
                    if_left_deep =( (fac_ret_df['price'].loc[(fac_ret_df['jyrq']>=q0+'31')
                                                             &(fac_ret_df['jyrq']<=q1+'31')].mean()
                                     > fac_ret_df['price'].loc[q0:q1]).sum()\
                                   /len(fac_ret_df['price'].loc[q0:q1])>=0.5 )

                    q0=observer_term[1]
                    q1=observer_term[2]
                    current_ret=q_ret(fac_ret_df,q0,q1)
                    if_left=( (fac_ret_df['price'].loc[(fac_ret_df['jyrq']>=q0+'31')
                                                             &(fac_ret_df['jyrq']<=q1+'31')].mean()
                                     > fac_ret_df['price'].loc[q0:q1]).sum()\
                                   /len(fac_ret_df['price'].loc[q0:q1])>=0.5 )

                    q0=observer_term[2]
                    q1=observer_term[3]
                    next_ret=q_ret(fac_ret_df,q0,q1)


                    if (i != len(changedf) - 1):
                        q1 = changedf.iloc[i + 1]['date']
                        # q2 = q1
                    else:
                        q1 = q_list[-1]
                        # q2=fac_ret_df.index[-1]

                    change_date=date
                    time_length = q_list.tolist().index(q1) - q_list.tolist().index(change_date)
                    holding_ret=q_ret(fac_ret_df,q0,q1,time_length=time_length)

                    if_win_next=(new_exp>old_exp)&(next_ret>current_ret)
                    if_win_hld=(new_exp>old_exp)&(holding_ret>current_ret)

                    shift_retur_next= (new_exp-old_exp)*(next_ret-current_ret)
                    shift_retur_hld = (new_exp - old_exp) * (holding_ret - current_ret)

                    style_chang_extret[date+"@"+style]=[if_left,if_left_deep,if_win_next,if_win_hld,shift_retur_next,shift_retur_hld]

        return style_chang_extret

    def style_shifting_analysis(self,df,q_list,col_list,t1,t2,name,jjdm,factor_ret):

        # col_list=[x+"_exp_adj" for x in col]
        change_ret=self.style_change_ret(df,q_list,col_list,t1=t1,t2=t2,factor_ret=factor_ret)
        change_ret = pd.DataFrame.from_dict(change_ret).T
        change_ret['style'] = list([x.split('@')[1] for x in change_ret.index])
        change_ret['date'] = list([x.split('@')[0] for x in change_ret.index])

        data=[]

        if(len(change_ret)>0):
            data.append(self.shifting_expression(change_ret,name,jjdm))
            for style in change_ret['style'].unique():
                tempdf=change_ret[change_ret['style']==style]
                data.append(self.shifting_expression(tempdf,name,jjdm,style))

        shift_df = pd.DataFrame(data=data,columns=['风格类型','切换次数','胜率（直到下次切换）','胜率（下季度）',
                                                   '下季平均收益','持有平均收益','左侧比率','深度左侧比例'])
        # for col in ['胜率（直到下次切换）','胜率（下季度）','下季平均收益','持有平均收益','左侧比率','深度左侧比例']:
        #     shift_df[col] = shift_df[col].astype(float).map("{:.2%}".format)

        return  shift_df

    @staticmethod
    def read_style_exp(style,fre,start_date,end_date=None):

        if(end_date is not None):
            end_date="and date<='{}'".format(end_date)
        else:
            end_date=""

        sql=" SELECT * from nav_{0}_exposure where fre='{1}' and date>='{2}' {3} "\
            .format(style,fre,start_date,end_date)
        style_exp=pd.read_sql(sql,con=localdb)

        if(fre=='Q'):
            quarter2month=dict(zip(['Q1','Q2','Q3','Q4'],['03','06','09','12']))
            style_exp['date']=[x[0:4]+quarter2month[x[4:]] for x in style_exp['date']]



        return  style_exp

    def style_shift_analysis(self):

        #read style exp
        value_exp=self.read_style_exp('value',self.fre,self.start_date)
        size_exp = self.read_style_exp('size', self.fre,self.start_date)

        #standarlize style exp
        value_exp=self.standardliza_by_rank(value_exp,self.value_col,self.bond_col)
        size_exp = self.standardliza_by_rank(size_exp, self.size_col, self.bond_col)

        #shift the exp from rank(entire jj pool) to rank between exp col
        total_w=value_exp[self.value_col].sum(axis=1)
        for col in self.value_col:
            value_exp[col]=value_exp[col]/total_w

        total_w=size_exp[self.size_col].sum(axis=1)
        for col in self.size_col:
            size_exp[col]=size_exp[col]/total_w


        value_exp.set_index('date',inplace=True,drop=True)
        size_exp.set_index('date', inplace=True, drop=True)

        collect_df_size=pd.DataFrame()
        collect_df_value = pd.DataFrame()

        def get_factor_return(style_list,start_date,end_date):

            style=util.list_sql_condition(style_list)

            # get value index ret :
            sql="select zqdm,jyrq,spjg from st_market.t_st_zs_hqql where zqdm in({0}) and jyrq>='{1}' and jyrq<='{2}'"\
                .format(style, start_date+'01',end_date+'31')

            fac_ret_df=hbdb.db2df(sql,db='alluser')
            fac_ret_df['jyrq']=fac_ret_df['jyrq'].astype(str)

            fac_ret_df['ym']=fac_ret_df['jyrq'].str[0:6]
            tempdf=fac_ret_df.drop_duplicates('ym', keep='last')[['jyrq','ym']]
            fac_ret_df=pd.merge(fac_ret_df,tempdf,how='left',on='jyrq').fillna('').drop('ym_x',axis=1)

            # fac_ret_df['jyrq'] = fac_ret_df['ym']
            fac_ret_df.set_index('ym_y', drop=True, inplace=True)

            fac_ret_df['price'] = fac_ret_df['spjg']

            return fac_ret_df

        value_factor_ret=get_factor_return(self.value_col+self.size_col,start_date=value_exp.index[0],end_date=value_exp.index[-1])

        for jjdm in self.jjdm_list:

            print("{} start ".format(jjdm))

            try:

                tempdf =  value_exp[value_exp['jjdm'] == jjdm]

                q_list = tempdf.index.unique().tolist()
                q_list.sort()

                style_shift_df=pd.merge(pd.Series(['Total'] + self.value_col).to_frame('风格类型'),
                self.style_shifting_analysis(
                    tempdf[self.value_col],
                    q_list, self.value_col,
                    t1=0.35 , t2=0.35*0.75 , name='value', jjdm=jjdm,factor_ret=value_factor_ret),how='left',on=['风格类型'])

                style_shift_df = style_shift_df.T
                style_shift_df.columns = style_shift_df.loc['风格类型']
                style_shift_df.drop('风格类型', axis=0, inplace=True)
                style_shift_df['jjdm'] = jjdm
                style_shift_df.reset_index(drop=False, inplace=True)

                collect_df_value = pd.concat([collect_df_value, style_shift_df], axis=0)

                tempdf = size_exp[size_exp['jjdm'] == jjdm]

                q_list = tempdf.index.unique().tolist()
                q_list.sort()

                style_shift_df=pd.merge(pd.Series(['Total'] + self.size_col).to_frame('风格类型'),
                self.style_shifting_analysis(
                    tempdf[self.size_col],
                    q_list, self.size_col,
                    t1=0.2 , t2=0.2*0.75 , name='value', jjdm=jjdm,factor_ret=value_factor_ret),how='left',on=['风格类型'])

                style_shift_df = style_shift_df.T
                style_shift_df.columns = style_shift_df.loc['风格类型']
                style_shift_df.drop('风格类型', axis=0, inplace=True)
                style_shift_df['jjdm'] = jjdm
                style_shift_df.reset_index(drop=False, inplace=True)

                collect_df_size = pd.concat([collect_df_size, style_shift_df], axis=0)


            except Exception as e:
                print(jjdm)
                print(e)


        collect_df_value[['Total']+self.value_col] = collect_df_value[['Total']+self.value_col].astype(
            float)
        collect_df_size[['Total']+self.size_col] = collect_df_size[['Total']+self.size_col].astype(
            float)


        for collect_df in [collect_df_value,collect_df_size]:

            collect_df.rename(columns=self.index_map, inplace=True)

            col_name_list=collect_df.columns.to_list()
            col_name_list.remove('index')
            col_name_list.remove('jjdm')

            collect_df[[x+'_rank' for
                        x in col_name_list
                        ]]=collect_df.groupby('index').rank(method='min')[col_name_list]\
                           /collect_df.groupby('index').count()[col_name_list].loc['切换次数']

            collect_df.rename(columns={'index': '项目名'}, inplace=True)


            collect_df['asofdate']=value_exp.index.max()

            collect_df['fre']=self.fre


            if(len(collect_df.columns)==10):
                # check if already exist
                sql="delete from nav_shift_property_value where asofdate='{0}' and fre='{1}'"\
                    .format(value_exp.index.max(),self.fre)
                localdb.execute(sql)
                collect_df.to_sql('nav_shift_property_value',index=False,if_exists='append',con=localdb)
            else:
                # check if already exist
                sql="delete from nav_shift_property_size where asofdate='{0}' and fre='{1}'"\
                    .format(value_exp.index.max(),self.fre)
                localdb.execute(sql)
                collect_df.to_sql('nav_shift_property_size', index=False, if_exists='append', con=localdb)

        print('Done')

class Fund_ret_analysis:

    def __init__(self,asofdate):
        self.jjdm_list=util.get_mutual_stock_funds(asofdate)

    @staticmethod
    def calculate_bias(indexdf,tickerdf,ret_col):

        joint_df=pd.merge(tickerdf,indexdf,left_index=True,right_index=True)
        joint_df['diff']=joint_df[ret_col+'_x']-joint_df[ret_col+'_y']

        result=joint_df.groupby('jjdm').mean()['diff'].to_frame('mean')

        joint_df=pd.merge(joint_df,result,how='left',left_on='jjdm',right_index=True)
        #in order to relax the influence of mean on std, change diff to diff-mean
        joint_df['diff_adj']=joint_df['diff']-joint_df['mean']

        result['std']=joint_df.groupby('jjdm').std()['diff_adj']
        result.reset_index(inplace=True,drop=False)

        return result

    def save_index_difference2db(self,asofdate,time_length=3):

        start_date=str(int(asofdate[0:4])-time_length)+asofdate[4:]

        jj_ret_weekly=get_weekly_jjnav(self.jjdm_list,start_date=start_date,end_date=asofdate)
        index_ret_weekly=get_weekly_index_ret('930950',start_date=start_date,end_date=asofdate)
        jj_ret_weekly.set_index('tjrq',inplace=True,drop=True)
        index_ret_weekly.set_index('tjrq',inplace=True,drop=True)

        jj_ret_monthly,max_yearmonth,min_yearmonth=get_monthly_jjnav(self.jjdm_list,start_date=start_date,end_date=asofdate)
        index_ret_monthly=get_monthly_index_ret('930950',start_date=start_date,end_date=asofdate)
        jj_ret_monthly.set_index('tjyf',inplace=True,drop=True)
        index_ret_monthly.set_index('tjyf',inplace=True,drop=True)

        bias_weekly=self.calculate_bias(index_ret_weekly,jj_ret_weekly,'hb1z')
        bias_monthly=self.calculate_bias(index_ret_monthly, jj_ret_monthly, 'hb1y')

        for col in ['mean','std']:
            bias_weekly[col+'_rank']=bias_weekly[col].abs().rank(method='min')/len(bias_weekly)
            bias_monthly[col + '_rank'] = bias_monthly[col].abs().rank(method='min') / len(bias_monthly)

        bias_weekly.set_index('jjdm',inplace=True,drop=True)
        bias_monthly.set_index('jjdm',inplace=True,drop=True)

        bias_weekly.columns=[x+"_weekly" for x in bias_weekly.columns]
        bias_monthly.columns = [x + "_monthly" for x in bias_monthly.columns]

        output_df=pd.merge(bias_monthly,bias_weekly,how='inner',left_index=True,right_index=True)
        output_df['asofdate']=str(jj_ret_weekly.index.max())
        output_df.reset_index(inplace=True,drop=False)

        #check if data already exist
        sql="delete from nav_ret_bias where asofdate='{0}'".format(str(jj_ret_weekly.index.max()))
        localdb.execute(sql)

        output_df.to_sql('nav_ret_bias',con=localdb,index=False,if_exists='append')

        print('Done')

class Manager_volume_hsl_analysis:

    def __init__(self,jjdm_list,asofdate=datetime.datetime.today().strftime('%Y%m%d')):

        self.jjjl_df, \
        self.jjvol_df, \
        self.jjhsl_df=self.get_basic_info(jjdm_list,asofdate)


        #trying to make analysis on fund volumne,hls and ret, trying calculate the correlation between the volume and ret
        #the method is no persuvise and is therefore given up
        # date_list = list(set(self.jjvol_df['jsrq'].astype(str).unique().tolist()+self.jjhsl_df['date'].unique().tolist()))
        # date_list.sort()
        # self.ret_rank=self.get_ret_rank(date_list,jjdm_list)
        #result1=self.volume_with_ret_analysis(self.jjjl_df, self.jjvol_df, self.ret_rank)
        #self.hsl_analysis(self.jjjl_df,self.jjhsl_df)

        self.save_hsl_and_volume2db(self.jjvol_df, self.jjhsl_df)


    @staticmethod
    def get_basic_info(jjdm_list,asofdate):

        start_date=str(int(asofdate[0:4])-10)+asofdate[4:]

        jjdm_con=util.list_sql_condition(jjdm_list)

        sql="select jjdm,ryxm,ryzt,rzrq,lrrq from st_fund.t_st_gm_jjjl where jjdm in ({0}) and ryzw='基金经理' and rzrq>='{1}' "\
            .format(jjdm_con,start_date)
        jjjl_df=hbdb.db2df(sql,db='funduser')

        sql = "select jjdm,jsrq,jjjzc from st_fund.t_st_gm_zcpz where jjdm in ({0}) and jsrq>='{1}'"\
            .format(jjdm_con,start_date)
        jjvol_df = hbdb.db2df(sql, db='funduser')

        sql="select * from factor_hsl where jjdm in ({0}) and date>='{1}'"\
            .format(jjdm_con,start_date)
        jjhsl_df=pd.read_sql(sql,con=localdb)

        return  jjjl_df,jjvol_df,jjhsl_df

    @staticmethod
    def get_ret_rank(date_list,jjdm_list):

        jjdm_con = util.list_sql_condition(jjdm_list)
        date_con = util.list_sql_condition(date_list)

        sql="""select jjdm,JZRQ,pmnpyj,slnpyj,pmnpej,slnpej 
        from st_fund.t_st_gm_rqjhbpm 
        where jjdm in ({0}) and zblb=2101 and JZRQ in ({1}) and pmnpej!=99999"""\
            .format(jjdm_con,date_con)

        ret_rank_month=hbdb.db2df(sql,db='funduser')

        sql="""select jjdm,JZRQ,pmnpyj,slnpyj,pmnpej,slnpej 
        from st_fund.t_st_gm_rqjhbpm 
        where jjdm in ({0}) and zblb=2103 and JZRQ in ({1}) and pmnpej!=99999"""\
            .format(jjdm_con,date_con)

        ret_rank_quarter=hbdb.db2df(sql,db='funduser')

        ret_rank=pd.merge(ret_rank_month,ret_rank_quarter,how='inner',on=['jjdm','JZRQ'])

        ret_rank['yj_m']=ret_rank['pmnpyj_x']/ret_rank['slnpyj_x']
        ret_rank['yj_q'] = ret_rank['pmnpyj_y'] / ret_rank['slnpyj_y']
        ret_rank['ej_m'] = ret_rank['pmnpej_x'] / ret_rank['slnpej_x']
        ret_rank['ej_q'] = ret_rank['pmnpej_y'] / ret_rank['slnpej_y']

        # ret_rank.rename(columns={'pmnpyj_x':'pmnpyj_m','slnpyj_x':'slnpyj_m'
        #     ,'pmnpyj_y':'pmnpyj_q','slnpyj_y':'slnpyj_q','pmnpej_x':'pmnpej_m','slnpej_x':'slnpej_m',
        #                          'pmnpej_y':'pmnpej_q','slnpej_y':'slnpej_q'},inplace=True)

        return ret_rank[['jjdm','JZRQ','yj_m','yj_q','ej_m','ej_q']]

    @staticmethod
    def volume_with_ret_analysis(jjjl_df,jjvol_df,ret_rank):

        data_df=pd.merge(jjvol_df,ret_rank,how='inner',left_on=['jjdm','jsrq'],right_on=['jjdm','JZRQ'])

        fin_df=pd.DataFrame()
        manager_list=[]
        jjdm_list=[]
        ej_m_cor=[]
        ej_q_cor=[]

        for manager in jjjl_df['ryxm'].unique():
            tempdf=jjjl_df[jjjl_df['ryxm']==manager]

            for jjdm in tempdf['jjdm'].unique():
                tempdf3=tempdf[tempdf['jjdm']==jjdm]
                tempdf2=pd.DataFrame()
                for i in range(len(tempdf3)):

                    tempdf2=pd.concat([tempdf2,data_df[(data_df['jjdm'] == tempdf3.iloc[i]['jjdm'])
                                       &(data_df['JZRQ']>=tempdf3.iloc[i]['rzrq'])
                                       &(data_df['JZRQ']<=tempdf3.iloc[i]['lrrq'])]])


                cor=tempdf2[['jjjzc', 'yj_m', 'yj_q', 'ej_m', 'ej_q']].corr()['jjjzc'].loc[['ej_m','ej_q']]
                jjdm_list.append(jjdm)
                manager_list.append(manager)
                ej_q_cor.append(cor['ej_q'])
                ej_m_cor.append(cor['ej_m'])

        fin_df['manager']=manager_list
        fin_df['jjdm'] = jjdm_list
        fin_df['ej_m_cor'] = ej_m_cor
        fin_df['ej_q_cor'] = ej_q_cor

        return  fin_df

    @staticmethod
    def hsl_analysis(jjhsl_df, jjvol_df):

        print('')

    @staticmethod
    def save_hsl_and_volume2db(jjvol_df,jjhsl_df):

        jjvol_df['jsrq']=jjvol_df['jsrq'].astype(str)
        jjhsl_df.drop('count',axis=1,inplace=True)
        joint_df=pd.merge(jjvol_df,jjhsl_df,how='inner',left_on=['jjdm','jsrq'],right_on=['jjdm','date'])

        joint_df['jjjzc_vs_hsl']=joint_df['jjjzc']/joint_df['hsl']/1000000
        joint_df=pd.concat([joint_df,joint_df.groupby('date').rank(method='min')['jjjzc_vs_hsl'].to_frame('rank')],axis=1)
        joint_df=pd.merge(joint_df,
                          joint_df.groupby('date', as_index=False).count()[['date', 'jjdm']].rename(columns={'jjdm':'count'}),
                          how='left',on='date')
        joint_df['rank']=joint_df['rank']/joint_df['count']
        joint_df['asofdate']=joint_df['date'].max()

        #check if data already exist
        # sql="delete from nav_hsl_vs_volume where asofdate='{0}'".format(joint_df['date'].max())
        # localdb.execute(sql)

        joint_df[['jjdm','date','rank','jjjzc','hsl','asofdate']].to_sql('nav_hsl_vs_volume',index=False,if_exists='append',con=localdb)

        # tempdf_s=joint_df[joint_df['rank']<=0.25]
        # tempdf_s['type']='volume_small&hsl_big'
        # tempdf_b=joint_df[joint_df['rank']>=0.75]
        # tempdf_b['type'] = 'volume_big&hsl_small'
        #
        # result=pd.concat([tempdf_s,tempdf_b],axis=0)
        #
        # return  result

class Theme_analysis():
    def __init__(self, jjdm_list, fre, asofdate=datetime.datetime.today().strftime('%Y%m%d'), time_length=3):
        # 时间区间
        start_year = str(int(asofdate[0:4]) - time_length)
        if fre == 'M':
            start_date = start_year + asofdate[4:6]
        else:
            if asofdate[4:6] <= '03':
                Q = 1
            elif asofdate[4:6] > '03' and asofdate[4:6] <= '06':
                Q = 2
            elif asofdate[4:6] > '06' and asofdate[4:6] <= '09':
                Q = 3
            elif asofdate[4:6] > '09' and asofdate[4:6] <= '12':
                Q = 4
            start_date = start_year + "Q" + str(Q)
        self.start_date = start_date
        self.fre = fre
        self.asofdate = asofdate
        self.val_date = self.get_jj_valuation_date(jjdm_list, asofdate)
        self.jjdm_list = jjdm_list

        # 指数代码及数据
        # todo：采用2014版申万一级行业分类，采掘行业数据停更问题
        # industry_info = HBDB().read_industry_info()
        # industry_info = industry_info[(industry_info['hyhfbz'] == '2') & (industry_info['fljb'] == '1') & (industry_info['sfyx'] == '1')]
        self.industry_col = ['801010','801030','801040','801050','801080','801110',
                              '801120','801130','801140','801150','801160','801170',
                              '801180','801200','801210','801230','801710','801720',
                              '801730','801740','801750','801760','801770','801780',
                              '801790','801880','801890','801950','801960','801970','801980']
        self.bond_col = ['CBA00301']
        self.index_data = HBDB().read_index_daily_k_given_date_and_indexs(start_year + '0101', self.industry_col + self.bond_col)
        # self.index_data.to_hdf('E:/GitFolder/hbshare/fe/xwq/data/index_data.hdf', key='table', mode='w')
        # self.index_data = pd.read_hdf('E:/GitFolder/hbshare/fe/xwq/data/index_data.hdf', key='table')
        self.index_data = self.index_data.rename(columns={'zqdm': 'INDEX_SYMBOL', 'zqmc': 'INDEX_NAME', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX', 'ltsz': 'NEG_MARKET_VALUE'})
        self.index_data = self.index_data[['INDEX_SYMBOL', 'INDEX_NAME', 'TRADE_DATE', 'CLOSE_INDEX', 'NEG_MARKET_VALUE']]
        self.index_map = self.index_data[['INDEX_SYMBOL', 'INDEX_NAME']].set_index('INDEX_SYMBOL')['INDEX_NAME'].to_dict()

        # 主题行业对应关系
        self.theme_col = ['大金融', '消费', 'TMT', '周期', '制造']
        self.theme_industry = dict(zip(self.theme_col,
                             [['银行','非银金融','房地产'],
                              ['食品饮料','家用电器','医药生物','社会服务','农林牧渔','商贸零售','美容护理'],
                              ['通信','计算机','电子','传媒','国防军工'],
                              ['钢铁','有色金属','建筑装饰','建筑材料','基础化工','石油石化','煤炭','环保','公用事业'],
                              ['交通运输','机械设备','汽车','纺织服饰','轻工制造','电力设备']
                              ]
                             ))

        # self.theme_industry = {
        #     '大金融': ['银行', '非银金融', '房地产'],
        #     '消费': ['家用电器', '食品饮料', '医药生物', '休闲服务', '农林牧渔', '商业贸易', '纺织服装'],
        #     'TMT': ['电子', '计算机', '传媒', '通信'],
        #     '周期': ['钢铁', '采掘', '有色金属', '化工', '建筑装饰', '建筑材料'],
        #     '制造': ['公用事业', '交通运输', '机械设备', '汽车', '电气设备', '轻工制造'],
        # }
        # self.theme_col = list(self.theme_industry.keys())

        # 基金净值
        # self.fund_nav = HBDB().read_fund_nav_given_date_and_codes(start_year + '0101', self.jjdm_list)
        # self.fund_nav.to_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/fund_nav.hdf', key='table', mode='w')
        # self.fund_nav = pd.read_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/fund_nav.hdf', key='table')
        # self.fund_nav = self.fund_nav.rename(columns={'jjdm': 'FUND_CODE', 'jzrq': 'TRADE_DATE', 'jjjz': 'NAV', 'ljjz': 'CUM_NAV'})
        # self.fund_nav = self.fund_nav[['FUND_CODE', 'TRADE_DATE', 'NAV', 'CUM_NAV']]
        # self.fund_nav_adj = HBDB().read_fund_nav_adj_given_date_and_codes(start_year + '0101', self.jjdm_list)
        # self.fund_nav_adj.to_hdf('E:/GitFolder/hbshare/fe/xwq/data/fund_nav_adj.hdf', key='table', mode='w')
        self.fund_nav_adj = pd.read_hdf('E:/GitFolder/hbshare/fe/xwq/data/fund_nav_adj.hdf', key='table')
        self.fund_nav_adj = self.fund_nav_adj.rename(columns={'jjdm': 'FUND_CODE', 'jzrq': 'TRADE_DATE', 'fqdwjz': 'ADJ_NAV', 'hbdr': 'RET', 'hbfh': 'CUM_DIV_RET', 'hbcl': 'SOFAR_RET'})
        self.fund_nav_adj = self.fund_nav_adj[['FUND_CODE', 'TRADE_DATE', 'ADJ_NAV', 'RET', 'CUM_DIV_RET', 'SOFAR_RET']]

    def ols_for_group(self, arr):
        y_col = arr.columns[0]
        x_col = arr.columns.tolist()
        x_col.remove(y_col)
        X = arr[x_col].values
        Y = arr[y_col].values

        X = (X - X.mean()) / X.std(ddof=1)

        model = LR(fit_intercept=True)
        model.fit(X, Y)
        return model.coef_.tolist()

    def ols_for_group_with_cons(self, arr):
        y_col = arr.columns[0]
        x_col = arr.columns.tolist()
        x_col.remove(y_col)
        X = arr[x_col].values
        Y = arr[y_col].values

        X = (X - X.mean()) / X.std(ddof=1)

        def func(A):
            ls = 0.5 * (Y - np.dot(X, A)) ** 2
            result = np.sum(ls)
            return result

        def g1(A):
            return np.sum(A)

        def g2(A):
            return 1 - np.sum(A)

        constraints = [{'type': 'ineq', 'fun': g1},
                       {'type': 'eq', 'fun': g2}]
        bounds = [(0, 1)] * np.shape(X)[1]
        w = np.zeros(np.shape(X)[1])
        res = minimize(func, w,
                       bounds=bounds,
                       constraints=constraints,
                       method='SLSQP')
        # constraints = ({'type': 'ineq', 'fun': g1},
        #                {'type': 'eq', 'fun': g2})
        # bounds = [(0, 1)] * np.shape(X)[1]
        # res = shgo(func,
        #            bounds=bounds,
        #            constraints=constraints)
        return res.x.tolist()

    @staticmethod
    def read_jj_style_exp(jjdm_list, type, fre, start_date):
        jjdm_con = util.list_sql_condition(jjdm_list)
        sql = "select * from nav_{0}_exposure where jjdm in ({1}) and fre='{2}' and date>='{3}'".format(type, jjdm_con, fre, start_date)
        expdf = pd.read_sql(sql, con=localdb)
        return expdf

    @staticmethod
    def cal_style_shift_ratio(df, style_col):
        df = df.copy()
        # calculate the total change in styles
        df['change'] = df[style_col].diff().abs().sum(axis=1)
        # calculate the average style exp between two dates
        df['avg_exp'] = df[style_col].sum(axis=1).rolling(2).mean()
        # calculate shift ratio
        df['shift_ratio'] = df['change'] / df['avg_exp']
        return df['shift_ratio'].values

    @staticmethod
    def cal_style_centralization_level(df, style_col, num1=1, num2=2):
        df = df.set_index('date')[style_col]
        outputdf = pd.DataFrame(index=df.index,columns=['c_level'])
        for i in range(len(df)):
            outputdf.iloc[i]['c_level']=(df.iloc[i].sort_values()[-1*num1:].sum()+df.iloc[i].sort_values()[-1*num2:].sum())/2/df.iloc[i].sum()
        return outputdf.mean()[0]

    @staticmethod
    def get_jj_valuation_date(jjdm_list, asofdate):
        jjdm_con = util.list_sql_condition(jjdm_list)
        # read jjjl info
        sql = "select jjdm,ryxm,rydm,rzrq from st_fund.t_st_gm_jjjl where ryzt='-1' and jjdm in ({0})".format(jjdm_con)
        jj_val_date = hbdb.db2df(sql, db='funduser')
        # for jj with multi managers,take the one with longer staying in this jj
        # jj_val_date = jj_val_date.sort_values('rzrq')
        # jj_val_date.drop_duplicates('jjdm', keep='first', inplace=True)
        jj_val_date = jj_val_date.sort_values(['jjdm', 'rzrq']).drop_duplicates('jjdm', keep='first')
        # remove jj with manager managing no longer than 1.5years
        # last_oneandhalfyear = (datetime.datetime.strptime(asofdate, '%Y%m%d')
        #                        -datetime.timedelta(days=560)).strftime('%Y%m%d')
        # jj_val_date['rzrq']=jj_val_date['rzrq'].astype(str)
        # jj_val_date=jj_val_date[jj_val_date['rzrq']<=last_oneandhalfyear]
        return jj_val_date[['jjdm', 'rzrq', 'rydm']]

    def fit_theme_index(self, theme_industry, index_data):
        theme_ret_dic = {}
        for theme in theme_industry.keys():
            print('dealing {}...'.format(theme))
            theme_index_data = index_data[index_data['INDEX_NAME'].isin(theme_industry[theme])]
            theme_index_price = theme_index_data.pivot(index='TRADE_DATE', columns='INDEX_NAME', values='CLOSE_INDEX').sort_index().fillna(method='ffill')
            theme_index_ret = theme_index_price.pct_change()
            theme_index_nmv = theme_index_data.pivot(index='TRADE_DATE', columns='INDEX_NAME', values='NEG_MARKET_VALUE').sort_index().fillna(method='ffill')
            theme_index_weight = theme_index_nmv.apply(lambda x: x / x.sum(), axis=1)
            theme_ret = (theme_index_ret * theme_index_weight).sum(axis=1)
            theme_ret_dic[theme] = theme_ret
            print('finish dealing {}!'.format(theme))
        theme_ret = pd.DataFrame.from_dict(theme_ret_dic)

        return theme_ret

    def get_theme_exposure(self, index_data, nav):
        theme_ret = self.fit_theme_index(self.theme_industry, index_data)
        bond_price = index_data[index_data['INDEX_SYMBOL'].isin(self.bond_col)]
        bond_price = bond_price.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').sort_index().fillna(method='ffill')
        bond_ret = bond_price.pct_change()
        theme_ret = pd.concat([theme_ret, bond_ret], axis=1).fillna(0.0)

        if self.fre == 'M':
            def timezone_transform(olsdf):
                olsdf['yearmonth'] = [str(x)[0:6] for x in olsdf.index]
                return olsdf
        else:
            def timezone_transform(olsdf):
                olsdf['yearmonth'] = ''
                olsdf.loc[olsdf.index.astype(str).str[4:6] <= '03', 'yearmonth'] = 'Q1'
                olsdf.loc[(olsdf.index.astype(str).str[4:6] <= '06') & (olsdf.index.astype(str).str[4:6] > '03'), 'yearmonth'] = 'Q2'
                olsdf.loc[(olsdf.index.astype(str).str[4:6] <= '09') & (olsdf.index.astype(str).str[4:6] > '06'), 'yearmonth'] = 'Q3'
                olsdf.loc[(olsdf.index.astype(str).str[4:6] <= '12') & (olsdf.index.astype(str).str[4:6] > '09'), 'yearmonth'] = 'Q4'
                olsdf['yearmonth'] = olsdf.index.astype(str).str[0:4] + olsdf['yearmonth']
                return olsdf

        theme_exp_df = pd.DataFrame()
        for idx, jjdm in enumerate(self.jjdm_list):
            jj_ret = nav[nav['FUND_CODE'] == jjdm][['TRADE_DATE', 'RET']].set_index('TRADE_DATE').rename(columns={'RET': jjdm})
            olsdf = pd.merge(jj_ret, theme_ret, how='inner', left_index=True, right_index=True)
            olsdf = timezone_transform(olsdf)
            tempdf = olsdf[olsdf[[jjdm] + self.theme_col + self.bond_col].notnull().sum(axis=1) == (len(self.theme_col) + 2)]
            tempdf = tempdf.groupby('yearmonth')[[jjdm] + self.theme_col + self.bond_col].apply(self.ols_for_group_with_cons).to_frame('exp')
            for i, col in enumerate(self.theme_col + self.bond_col):
                tempdf[col] = [exp[i] for exp in tempdf['exp']]
            tempdf.drop('exp', inplace=True, axis=1)
            tempdf['jjdm'] = jjdm
            theme_exp_df = pd.concat([theme_exp_df, tempdf], axis=0)
            print('[{}/{}:{}] Done!'.format(idx, len(self.jjdm_list), jjdm))
        theme_exp_df = theme_exp_df.reset_index().rename(columns={'yearmonth': 'date'})
        theme_exp_df['fre'] = self.fre
        theme_exp_df.to_sql('nav_theme_exposure', index=False, if_exists='append', con=localdb)
        return

    def get_theme_property(self, style_df, style_col, method='rank'):
        if self.fre == 'M':
            def timezone_transform(olsdf):
                olsdf['yearmonth'] = [str(x)[0:6] for x in olsdf.index]
                return olsdf
        else:
            def timezone_transform(olsdf):
                olsdf['yearmonth'] = ''
                olsdf.loc[olsdf.index.astype(str).str[4:6] <= '03', 'yearmonth'] = 'Q1'
                olsdf.loc[(olsdf.index.astype(str).str[4:6] <= '06') & (olsdf.index.astype(str).str[4:6] > '03'), 'yearmonth'] = 'Q2'
                olsdf.loc[(olsdf.index.astype(str).str[4:6] <= '09') & (olsdf.index.astype(str).str[4:6] > '06'), 'yearmonth'] = 'Q3'
                olsdf.loc[(olsdf.index.astype(str).str[4:6] <= '12') & (olsdf.index.astype(str).str[4:6] > '09'), 'yearmonth'] = 'Q4'
                olsdf['yearmonth'] = olsdf.index.astype(str).str[0:4] + olsdf['yearmonth']
                return olsdf
        self.val_date = timezone_transform(self.val_date.set_index('rzrq'))

        if (method == 'robust'):
            from sklearn.preprocessing import RobustScaler
            rs = RobustScaler()
            style_df[style_col] = rs.fit_transform(style_df[style_col].values)
        else:
            style_df[style_col] = style_df.groupby('date').rank(method='min')[style_col]
            style_df = pd.merge(style_df, style_df.groupby('date').count()['jjdm'].to_frame('count'), left_on='date', right_index=True)
            for col in style_col:
                style_df[col] = style_df[col] / style_df['count']
        asofdate = style_df['date'].max()
        style_property_df = pd.DataFrame()
        temp = style_df.groupby('jjdm').min()['date']
        new_jjdm_list = temp[temp <= self.start_date].index.tolist()
        new_jjdm_list.sort()
        style_property_df['jjdm'] = new_jjdm_list
        for idx, jjdm in enumerate(new_jjdm_list):
            # check if manager changed during the time zone
            tempdf = style_df[style_df['jjdm'] == jjdm]
            manager_change = str(str(self.val_date[self.val_date['jjdm'] == jjdm]['yearmonth'].values[0])[0:6] > self.start_date) if len(self.val_date[self.val_date['jjdm'] == jjdm]) > 0 else ''
            tempdf['shift_ratio'] = self.cal_style_shift_ratio(tempdf, style_col)
            centralization = self.cal_style_centralization_level(tempdf, style_col, 1, 2)
            # centralization = (tempdf[style_col].std(axis=1) / tempdf[style_col].mean(axis=1)).mean()
            style_property_df.loc[style_property_df['jjdm'] == jjdm, 'shift_ratio'] = tempdf['shift_ratio'].mean()
            style_property_df.loc[style_property_df['jjdm'] == jjdm, 'centralization'] = centralization
            for col in style_col:
                style_property_df.loc[style_property_df['jjdm'] == jjdm, col + '_mean'] = tempdf[col].mean()
            style_property_df.loc[style_property_df['jjdm'] == jjdm, 'manager_change'] = manager_change
            print('[{}/{}:{}] Done!'.format(idx, len(new_jjdm_list), jjdm))
        rank_col = ['shift_ratio', 'centralization'] + [col + '_mean' for col in style_col]
        style_property_df[[x + '_rank' for x in rank_col]] = style_property_df[rank_col].rank(method='min') / len(style_property_df)
        style_property_df['asofdate'] = asofdate
        return style_property_df


    def save_theme_property2localdb(self):
        self.get_theme_exposure(self.index_data, self.fund_nav_adj)

        # sql = "select distinct asofdate from nav_style_property_value where fre='{0}' and by_manager='{1}' " \
        #     .format(self.fre, 'True')
        # asofdate_list = pd.read_sql(sql, con=localdb)['asofdate'].values.tolist()
        #
        # if (self.asofdate in asofdate_list):
        #     sql = "delete from nav_style_property_value where asofdate='{0}' and fre-'{1}' and by_manager='{2}'" \
        #         .format(self.asofdate, self.fre, 'True' + str(self.consistant_date))
        #     localdb.excute(sql)

        value_df = self.get_theme_property(self.read_jj_style_exp(self.jjdm_list, 'theme', self.fre, self.start_date), self.theme_col, method='rank')
        value_df['fre'] = self.fre
        value_df.to_sql('nav_style_property_theme', index=False, con=localdb, if_exists='append')
        return



if __name__ == '__main__':

    style_exp_simpleols_foroutsideuser_mu()
    #style_exp_simpleols_foroutsideuser()
    #style_exp_foroutsideuser()
    # df1=pd.read_excel(r"C:\Users\xuhuai.zhe\Downloads\股多-估值表-20220428.xlsx")
    # jjdm_con=util.list_sql_condition(df1['基金代码'].values.tolist())
    # df2=hbdb.db2df("select jjdm,weight,trade_date from st_hedge.r_st_sm_subjective_fund_holding where jjdm in ({0})"
    #                .format(jjdm_con),db='highuser')
    # df2['flag'] = 0
    # df2.loc[df2['weight'] == 99999, 'flag'] = 1
    # df2=df2.groupby(['jjdm','trade_date']).sum().reset_index()
    # df2['trade_date']=df2['trade_date'].astype(str)+','
    # df2=pd.merge(df2.groupby('jjdm')['flag'].mean().reset_index(),
    #              df2.groupby('jjdm')['trade_date'].sum().reset_index(),how='inner',on='jjdm')
    # df2.loc[df2['flag']==1,'flag']='解析失败'
    # df2.loc[df2['flag']==0,'flag']='解析成功'
    #
    # df=pd.merge(df1,df2,how='left',left_on='基金代码',right_on='jjdm').drop('jjdm',axis=1)
    # df.to_excel('对比结果新.xlsx')
    # print('')

    #calculate the return for different scenarios

    # stock_jjdm_list=util.get_mutual_stock_funds('20211231')
    # stock_jjdm_list.sort()
    # benchmark_ret = get_histroy_scenario_ret()
    # saved_df=pd.DataFrame()
    # for jjdm in stock_jjdm_list:
    #     scenario_ret=pessimistic_ret(jjdm,benchmark_ret)
    #     saved_df=pd.concat([saved_df,scenario_ret],axis=0)
    # saved_df.to_sql('scenario_ret',index=False,con=localdb,if_exists='append')

    #barra return daily return
    #factor_ret_df=get_barra_daily_ret()

    #write style exp into local db
    # se = Style_exp('20211231','M')
    # se = Style_exp('20211231', 'Q')

    #style exp analysis
    #

    # sql="select * from value_exposure where jjdm='002849' "
    # test=pd.read_sql(sql,con=localdb)[['399370','399371','CBA00301','date']]
    # test.set_index('date',inplace=True)
    # plot=functionality.Plot(2000,1000)
    # plot.plotly_line_style(test,'asdf')
    #

    # #style property calculation
    # jjdm_list=util.get_mutual_stock_funds('20211231')
    # sa=Style_analysis(jjdm_list,fre='M',time_length=3)
    # sa.style_shift_analysis()
    #sa=Style_analysis(jjdm_list,fre='Q',time_length=3)
    # sa.style_shift_analysis()


    # sa.save_style_property2localdb()
    # #
    # sa=Style_analysis(jjdm_list,asofdate='20220310',fre='M',time_length=3)
    # sa.save_style_property2localdb()
    # sa=Style_analysis(jjdm_list,asofdate='20220310',fre='Q',time_length=3)
    # sa.save_style_property2localdb()


    #manager hsl and volume estimate

    # jjdm_list=util.get_mutual_stock_funds('20211231')
    # ma = Manager_volume_hsl_analysis(jjdm_list)

    #fund return analysis
    # fa=Fund_ret_analysis(asofdate='20211231')
    # fa.save_index_difference2db(asofdate=datetime.datetime.today().strftime('%Y%m%d'),time_length=3)


    # for fre in ['Q']:
    #     jjdm_list = util.get_mutual_stock_funds('20211231')
    #     ta = Theme_analysis(jjdm_list, fre=fre, time_length=3)
    #     ta.save_theme_property2localdb()

    # jjdm_list = ['000577', '000729', '001410', '001667', '001856', '002340', '005233', '005267', '005827', '005968', '006624', '163415', '450004', '450009', '519126', '519133', '700003']
    # sql = "select * from nav_style_property_theme"
    # df = pd.read_sql(sql, con=localdb)
    # df = df[df['jjdm'].isin(jjdm_list)].sort_values(['jjdm', 'fre'])
    # df.to_excel('C:/Users/wenqian.xu/Desktop/test/test.xlsx')

