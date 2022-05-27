import numpy as np
import pandas as pd
from hbshare.fe.XZ import db_engine as dbeng
from hbshare.fe.XZ import functionality
from hbshare.fe.mutual_analysis import holdind_based
from hbshare.fe.mutual_analysis import nav_based as nbs
import datetime
from sklearn import preprocessing
from hbshare.fe.factor_analysis import simple_factor_generator as sfg

util=functionality.Untils()
hbdb=dbeng.HBDB()
fre_map={'M':'2101','Q':'2103','HA':'2106'}

def get_jjnav(jjdm_list,date_list,fre):

    fre_con=fre_map[fre]

    jjdm_con=util.list_sql_condition(jjdm_list)
    date_con=util.list_sql_condition(date_list)

    #get the nav ret  for given jjdm and time zone(already times 100)
    sql="select jjdm,jzrq,zbnp from st_fund.t_st_gm_rqjhb where jjdm in ({0}) and jzrq in ({1}) and zbnp!=99999 and zblb='{2}' "\
        .format(jjdm_con,date_con,fre_con)
    navdf=hbdb.db2df(sql, db='funduser')

    return navdf

def get_daily_jjnav(jjdm_list,start_date,end_date):

    jjdm_con=util.list_sql_condition(jjdm_list)

    #get the daily nav ret for given jjdm and time zone
    sql="select jjdm,jzrq,hbdr from st_fund.t_st_gm_rhb where jjdm in ({0}) and jzrq>='{1}' and jzrq<='{2}' and hbdr!=99999  "\
        .format(jjdm_con,start_date,end_date)
    navdf=hbdb.db2df(sql, db='funduser')

    return navdf

def bhar(arr):
    return np.cumprod((arr/100+1)).values[-1]

def pic_grouping(df,pic_title,fre,width=1000,height=1000):

    df['date']=df['date'].astype(str)
    # fre_code=fre_map[fre]
    draw_df=pd.DataFrame()
    df=df.sort_values('date')
    draw_df['date']=df['date'].unique()
    ret_list=[[],[],[],[],[]]
    for i in range(len(draw_df)):
        date=draw_df.iloc[i]['date']
        tempdf=df[df['date']==date].groupby('group').mean()
        for j in range(5):
            ret_list[j].append(tempdf.loc[j]['zbnp'])

    # data_con=until.list_sql_condition(draw_df['date'].tolist())
    # sql = "select zbnp,jyrq from st_market.t_st_zs_rqjhb where zqdm='930950' and zbnp!=99999 and zblb='{1}' and jyrq in ({0}) "\
    #     .format(data_con,fre_code)
    # benchmark_ret=hbdb.db2df(sql,db='alluser')
    # benchmark_ret['jyrq']=benchmark_ret['jyrq'].astype(str)
    # draw_df=pd.merge(draw_df,benchmark_ret,how='left',right_on='jyrq',left_on='date').drop('jyrq',axis=1)
    # draw_df.rename(columns={'zbnp':'benchmark_ret'},inplace=True)
    draw_df = pd.merge(draw_df, df.groupby('date').mean()[['zbnp']], how='left', right_index=True, left_on='date')
    draw_df.rename(columns={'zbnp': 'benchmark_ret'}, inplace=True)
    for i in range(5):
        draw_df['group_'+str(i)]=ret_list[i]
        draw_df['group_'+str(i)]=draw_df['group_'+str(i)].rolling(len(draw_df), 1).apply(bhar)

    draw_df['benchmark_ret']=draw_df['benchmark_ret'].rolling(len(draw_df), 1).apply(bhar)

    draw_df['date']=draw_df['date'].astype(str)
    draw_df.set_index('date',inplace=True)

    plot=functionality.Plot(width,height)
    plot.plotly_line_style(draw_df,pic_title)
    ext_ret = 1+np.max([draw_df.iloc[-1]['group_4'] - draw_df.iloc[-1]['benchmark_ret']
                     , draw_df.iloc[-1]['group_0'] - draw_df.iloc[-1]['benchmark_ret']])
    if(fre=='M'):
        mi=len(draw_df)/12
    elif(fre=='Q'):
        mi = len(draw_df) / 4
    elif(fre=='HA'):
        mi = len(draw_df) / 2
    else:
        print('input frequence is not supported, only M,Q,HY is supported')
        raise Exception

    ext_ret =np.power(ext_ret, 1/mi) - 1
    print('annually ext ret for best group is {}%'.format(ext_ret*100))

def get_stock_ret(ticker_list,date,fre):

    ticker_con = util.list_sql_condition(ticker_list)
    sql = "select jjdm,jzrq,zbnp from st_fund.t_st_gm_rqjhb where zblb='{2}' and jjdm in ({0}) and jzrq ='{1}' and zbnp!=99999 " \
        .format(ticker_con, date, fre)
    retdf = hbdb.db2df(sql, db='funduser')

    return retdf

def grouping(groupdf,retdf,factor_name,col_list,factor_date,ret_date=None):

    if(ret_date is None):
        ret_date=''

    gap = int(np.floor(len(retdf) * 0.2))
    retdf = retdf[col_list+[ factor_name]]
    for group in range(2):
        tempgroup = retdf.sort_values(factor_name)[col_list].iloc[(group) * gap:(1 + group) * gap]
        tempgroup['group'] = group
        tempgroup['date'] = factor_date
        tempgroup['ret_date'] = ret_date
        groupdf = pd.concat([groupdf, tempgroup], axis=0)

        if (group == 0):
            tempgroup = retdf.sort_values(factor_name)[col_list].iloc[-1 * (1 + group) * gap:]
        else:
            tempgroup = retdf.sort_values(factor_name)[col_list].iloc[
                        -1 * (1 + group) * gap:-1 * (group) * gap]
        tempgroup['group'] = 4 - group
        tempgroup['date'] = factor_date
        tempgroup['ret_date'] = ret_date
        groupdf = pd.concat([groupdf, tempgroup], axis=0)

    tempgroup = retdf.sort_values(factor_name)[col_list].iloc[
                2 * gap:-2 * gap]
    tempgroup['group'] = 2
    tempgroup['date'] = factor_date
    tempgroup['ret_date'] = ret_date
    groupdf = pd.concat([groupdf, tempgroup], axis=0)

    return groupdf

def single_factor_ic(factor_df,factor_name,fre,fund_flag=True):

    date_list = factor_df['date'].unique().tolist()
    date_list.sort()
    ic_df=pd.DataFrame()
    # ic_df['date']=date_list[0:-1]
    ic_list=[]
    ic_date=[]
    fre=fre_map[fre]
    groupdf=pd.DataFrame()

    if(fund_flag):
        # ticker_ret=pd.DataFrame()
        for i in range(len(date_list)-1):
            factor_date=date_list[i]
            #ret_date = (datetime.datetime.strptime(factor_date, '%Y%m%d')+ datetime.timedelta(days=91)).strftime('%Y%m%d')

            ret_date=date_list[i+1]

            #get the stock return
            ticker_list = factor_df[factor_df['date']==factor_date]['jjdm'].unique().tolist()
            retdf=get_stock_ret(ticker_list,ret_date,fre)

            #to make sure that the ic calculation is robust, add a requiement of the number of funds in ic calculations
            if(len(retdf)<400):
                continue

            ic_date.append(factor_date)

            retdf['jzrq']=retdf['jzrq'].astype(str)
            retdf=pd.merge(retdf,factor_df[factor_df['date']==factor_date],how='inner',on='jjdm')
            #calculate the spearman correlation between fund return and factors
            ic_list.append(retdf[['zbnp',factor_name]].corr(method='spearman')['zbnp'][1])

            #divide the groups
            groupdf=grouping(groupdf,retdf,factor_name,['jjdm', 'zbnp'],factor_date,ret_date)

        #
        i+=1
        factor_date = date_list[i]
        retdf=factor_df[factor_df['date'] == factor_date]
        groupdf2 = grouping(groupdf[['jjdm','group','date','ret_date']], retdf, factor_name,['jjdm'], factor_date)

    ic_df['ic']=ic_list
    ic_df['date']=ic_date

    print('\n the average ic of {3} is {0}, the pro that ic >0 is {1},the ic std is {4},the IR of the factor is{2} '
          .format(ic_df['ic'].describe()['mean'],
                  sum(ic_df['ic']>0)/len(ic_df),
                  ic_df['ic'].describe()['mean']/ic_df['ic'].describe()['std'],factor_name,
                  ic_df['ic'].describe()['std']))

    return groupdf,groupdf2.drop('ret_date',axis=1)

def factor_narrow_level(groupdf,fre):

    fre_code=fre_map[fre]
    data_con=util.list_sql_condition(groupdf['date'].unique().tolist())
    sql = "select zbnp,jyrq from st_market.t_st_zs_rqjhb where zqdm='930950' and zbnp!=99999 and zblb='{1}' and jyrq in ({0}) " \
        .format(data_con, fre_code)
    benchmark_ret = hbdb.db2df(sql, db='alluser')
    benchmark_ret['jyrq']=benchmark_ret['jyrq'].astype(str)


    ret_df=pd.DataFrame()
    for date in groupdf['date'].unique().tolist():
        tempdf=get_stock_ret(groupdf[groupdf['date']==date]['jjdm'].tolist(),date, fre_map['HA'])
        ret_df=pd.concat([ret_df,tempdf],axis=0)

    ret_df['jzrq']=ret_df['jzrq'].astype(str)
    groupdf=pd.merge(groupdf,ret_df,how='left',left_on=['jjdm','date'],right_on=['jjdm','jzrq']).drop('jzrq',axis=1)
    groupdf=pd.merge(groupdf,benchmark_ret,how='left',left_on='date',right_on='jyrq').drop('jyrq',axis=1)
    groupdf['zbnp']=groupdf['zbnp_x']-groupdf['zbnp_y']
    groupdf.drop(['zbnp_y','zbnp_x'],axis=1,inplace=True)

    factor_narrow_df=pd.DataFrame()
    factor_narrow_df['date']=groupdf['date'].unique()

    for group in [0,4]:
        lsd = []
        std=[]
        corr=[]
        ext_ret=[]
        for date in groupdf['date'].unique():
            tempgroupdf = groupdf[(groupdf['group'] == group)&(groupdf['date'] == date)]
            lsd.append(tempgroupdf['zbnp'].std() / tempgroupdf['zbnp'].mean())

            #get the fund daily returns for the last 60 days
            pre60date=  (datetime.datetime.strptime(date, '%Y%m%d')-datetime.timedelta(days=60)).strftime('%Y%m%d')
            navdf=get_daily_jjnav(tempgroupdf['jjdm'].unique().tolist(),pre60date,date)

            # calculate the factor ret vol for last60 days
            std.append(navdf.groupby('jzrq').mean().std().values[0])

            # calculate the corr insiede the group
            tempdf=navdf.groupby('jzrq').mean().reset_index()
            tempdf['jjdm']='avg'
            navdf=pd.concat([navdf,tempdf],axis=0)
            corr.append(np.mean(navdf.groupby(['jzrq','jjdm']).sum().unstack().corr()[('hbdr',    'avg')].tolist()[0:-1]))

            ext_ret.append(tempgroupdf['zbnp'].mean())

        #z score
        lsd=preprocessing.scale(lsd)
        corr = preprocessing.scale(corr)
        std = preprocessing.scale(std)
        ext_ret=preprocessing.scale(ext_ret)

        factor_narrow_df['lsd_'+str(group)]=lsd
        factor_narrow_df['corr_' + str(group)] = corr
        factor_narrow_df['std_' + str(group)] = std
        factor_narrow_df['ext_ret_' + str(group)] = ext_ret

    factor_narrow_df.set_index('date', inplace=True)
    factor_narrow_df=factor_narrow_df.sum(axis=1).to_frame('factor_narrow_lv')
    return  factor_narrow_df

if __name__ == '__main__':

    localdb=dbeng.PrvFunDB().engine
    bra = holdind_based.Barra_analysis()
    brison=holdind_based.Brinson_ability()


    #factor: hsl
    factor_name='hsl'

    raw_df=sfg.read_factors('factor_hsl')
    groupdf,factrodf=single_factor_ic(raw_df,factor_name=factor_name,fre='HA',fund_flag=True)

    pic_grouping(groupdf, factor_name, 'HA')

    # factor_narrow_lv = factor_narrow_level(factrodf, 'HA')
    # plot = functionality.Plot(2000, 1000)
    # plot.plotly_line_style(factor_narrow_lv, '因子拥挤度')


    # # # new joinner  return factor ic test
    # factor_name='t1_ret'
    #
    # raw_df=bra.factorlize_new_joinner(factor_name)
    # groupdf,factrodf=single_factor_ic(raw_df,factor_name='new_join_'+factor_name,fre='Q',fund_flag=True)
    #
    # pic_grouping(groupdf, factor_name, 'Q')
    #
    # factor_narrow_lv = factor_narrow_level(factrodf, 'Q')
    # plot = functionality.Plot(2000, 1000)
    # plot.plotly_line_style(factor_narrow_lv, '因子拥挤度')

    #
    # # #pess return as factor
    # factor_name='ext_ret'
    # sr=nbs.Scenario_return()
    # raw_df = sr.factorlize_ret(factor_name)
    # groupdf,factrodf = single_factor_ic(raw_df, factor_name=factor_name, fre='M', fund_flag=True)
    # pic_grouping(groupdf, '超额月度',fre='M')
    # factrodf['date']=factrodf['date'].astype(str)
    # factor_narrow_lv = factor_narrow_level(factrodf, 'Q')
    # plot = functionality.Plot(2000, 1000)
    # plot.plotly_line_style(factor_narrow_lv, '因子拥挤度')
    #
    # factor_name='pes_ext_ret'
    #raw_df=nbs.factorlize_ret(factor_name,fre='Q')
    # groupdf=single_factor_ic(raw_df, factor_name=factor_name, fre='Q',fund_flag=True)
    # grouping(groupdf,'逆境季度')

    # for factor_name in ['short_term_equity','long_term_equity','short_term_sector',
    #                     'long_term_sector','short_term_trading','long_term_trading',
    #                     'short_term_asset','long_term_asset']:
    #
    #     raw_df=brison.factorlize_brinson(factor_name)
    #     groupdf,factrodf=single_factor_ic(raw_df, factor_name=factor_name, fre='HA',fund_flag=True)
    #
    #     factor_narrow_lv=factor_narrow_level(factrodf,'HA')
    #
    #
    #     pic_grouping(groupdf, factor_name, 'HA')
    #     plot = functionality.Plot(1000, 1000)
    #     plot.plotly_line_style(factor_narrow_lv, '因子拥挤度')





