import datetime
import pandas as pd
import numpy as np
from hbshare.fe.XZ import db_engine
from hbshare.fe.XZ import functionality
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns  #Python library for Vidualization
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import linkage, dendrogram
from hbshare.fe.mutual_analysis import  holdind_based as hb


util=functionality.Untils()
hbdb=db_engine.HBDB()
localdb=db_engine.PrvFunDB().engine
theme_map=hb.Industry_analysis().ind2thememap

new_col_name = ['农林牧渔', '基础化工', '钢铁', '有色金属', '电子', '家用电器', '食品饮料',
                     '纺织服饰', '轻工制造', '医药生物', '公用事业', '交通运输', '房地产', '商贸零售',
                     '社会服务', '综合', '建筑材料', '建筑装饰', '电力设备', '国防军工', '计算机', '传媒',
                     '通信', '银行', '非银金融', '汽车', '机械设备', '煤炭', '石油石化', '环保', '美容护理']
index_code_list = ['801010', '801030', '801040', '801050', '801080', '801110',
                        '801120', '801130', '801140', '801150', '801160', '801170',
                        '801180', '801200', '801210', '801230', '801710', '801720',
                        '801730', '801740', '801750', '801760', '801770', '801780',
                        '801790', '801880', '801890', '801950', '801960', '801970', '801980']
index_code_map = dict(zip(index_code_list, new_col_name))

def read_industry_info():

    #read financial info from local db
    sql="SELECT * from hbs_industry_financial_stats where class_level=1"
    industry_fin_df=pd.read_sql(sql,con=localdb)

    start_date=str(int(industry_fin_df['ENDDATE'].max()[0:4])-1)+industry_fin_df['ENDDATE'].max()[4:]+"01"
    end_date=industry_fin_df['ENDDATE'].max()+"31"
    industry_fin_df=industry_fin_df[(industry_fin_df['ENDDATE']>=start_date)&(industry_fin_df['ENDDATE']<=end_date)]

    style = util.list_sql_condition(index_code_list)
    sql = "select zqdm,jyrq,spjg from st_market.t_st_zs_hqql where zqdm in ({0}) and jyrq>='{1}' and  jyrq<='{2}'  " \
        .format(style, start_date, end_date)
    fac_ret_df = hbdb.db2df(sql, db='alluser')
    fac_ret_df['jyrq'] = fac_ret_df['jyrq'].astype(str)
    fac_ret_df.set_index('jyrq', drop=True, inplace=True)

    fac_ret_df['price'] = fac_ret_df['spjg']

    fac_ret_df['zqdm'] = [index_code_map[x] for x in fac_ret_df['zqdm']]

    fac_ret_df['ym']=fac_ret_df.index.astype(str).str[0:6]

    fac_ret_df2=fac_ret_df.groupby(['ym','zqdm']).mean().reset_index().drop('spjg',axis=1)
    fac_ret_df2['diff']=fac_ret_df2.groupby('zqdm')['price'].diff()
    fac_ret_df2['growth']=fac_ret_df2['diff']/fac_ret_df2['price']

    fac_ret_df['diff']=fac_ret_df.groupby('zqdm')['price'].diff()
    fac_ret_df['growth']=fac_ret_df['diff']/fac_ret_df['price']
    fac_ret_df.drop(['price','spjg','ym','diff'],axis=1,inplace=True)

    industry_fin_df=pd.merge(industry_fin_df,fac_ret_df2[['ym', 'zqdm','growth']],
                             how='left',left_on=['industry_name','ENDDATE'],right_on=['zqdm','ym']).drop(['zqdm','ym'],axis=1)

    return industry_fin_df,fac_ret_df

def standardlize(df):

    scaler = StandardScaler()
    scaler.fit(df)
    scaled_ds = pd.DataFrame(scaler.transform(df), columns=df.columns)

    return  scaled_ds

def PCA_function(scaled_ds,pca_num):

    if(pca_num is not None):
        pca = PCA(n_components=pca_num)
        pca.fit(scaled_ds)
        PCA_ds = pd.DataFrame(pca.transform(scaled_ds))
    else:
        PCA_ds=scaled_ds

    return  PCA_ds

def pro_of_sameclass(df):

    output=pd.DataFrame()
    for col in df.columns.tolist():
        pro_list=[]
        for col2 in df.columns.tolist():
            pro_list.append((df[col2]==df[col]).sum()/len(df))
        output[col]=pro_list
    output.index=df.columns.tolist()
    return output

def K_means(df,loop_num=100,pca_num=None):

    if(len(df.columns)==1):
        scaled_ds=df
    else:
        scaled_ds = standardlize(df)

    PCA_ds=PCA_function(scaled_ds, pca_num)

    X=PCA_ds.values

    # wcss = []
    # for i in range(1, 11):
    #     kmeans = KMeans(n_clusters=i, init='k-means++', random_state=0)
    #     kmeans.fit(X)
    #     wcss.append(kmeans.inertia_)

    # plt.plot(range(1, 11), wcss)
    # plt.title('The Elbow Method')
    # plt.xlabel('no of clusters')
    # plt.ylabel('wcss')
    # plt.show()

    theme_df=pd.DataFrame()
    score_list=[]
    for i in range(loop_num):
        kmeansmodel = KMeans(n_clusters=5, init='k-means++', random_state=i)
        y_kmeans = kmeansmodel.fit_predict(X)
        score_list.append(kmeansmodel.inertia_)

        theme_df['theme_{}'.format(i)]=y_kmeans

    return  theme_df,np.mean(score_list)

def HC(df,figname,pca_num=None):

    if(len(df.columns)==1):
        scaled_ds=df
    else:
        scaled_ds = standardlize(df)

    PCA_ds=PCA_function(scaled_ds, pca_num)
    PCA_ds.index=df.index
    merg = linkage(PCA_ds, method="ward")
    plt.rcParams['font.sans-serif']='SimHei'# scipy is an algorithm of hiyerarchal clusturing
    dendrogram(merg, leaf_rotation=90,labels=df.index)
    plt.xlabel("data points")
    plt.ylabel("euclidean distance")
    # plt.show()
    plt.savefig('{}.png'.format(figname))
    plt.close()

    # X=PCA_ds.values
    #
    # theme_df=pd.DataFrame()
    #
    # hiyerartical_cluster = AgglomerativeClustering(n_clusters=5, affinity="euclidean", linkage="ward")
    # cluster = hiyerartical_cluster.fit_predict(X)
    # theme_df['theme']=cluster

    #return  theme_df

def cluster_engine(industry_fin_df,potient_featute_list):

    method1df = pd.DataFrame()
    method2df = pd.DataFrame()
    method3df = pd.DataFrame()
    method4df = pd.DataFrame()

    for i in range(len(potient_featute_list)):
        print("test number {} \n".format(i + 1))
        if(i>0):
            feature_list = [potient_featute_list[0]]+[potient_featute_list[i]]
        else:
            feature_list= [potient_featute_list[0]]

        feature_df = industry_fin_df.groupby(['industry_name']).mean()[feature_list]
        feature_df=feature_df[feature_df.isnull().sum(axis=1) == 0]

        new_industry_fin_df = pd.DataFrame()
        new_industry_fin_df['industry_name'] = industry_fin_df['industry_name'].unique().tolist()
        for date in industry_fin_df['ENDDATE'].unique()[1:]:
            new_industry_fin_df = pd.merge(new_industry_fin_df,
                                           industry_fin_df[industry_fin_df['ENDDATE'] == date][
                                               ['industry_name', 'ENDDATE'] + feature_list], how='left',
                                           on='industry_name').drop('ENDDATE', axis=1)
        new_industry_fin_df = new_industry_fin_df[new_industry_fin_df.isnull().sum(axis=1) == 0]

        result3, kmeans_score3 = K_means(new_industry_fin_df.drop('industry_name', axis=1))

        result, kmeans_score = K_means(feature_df)

        # result2 = HC(feature_df)

        HC(new_industry_fin_df.set_index('industry_name'),feature_list[-1])


        theme_map = pd.DataFrame()
        theme_map['industry_name'] = feature_df.index
        theme_map = pd.concat([theme_map, result], axis=1)

        # theme_map2 = pd.DataFrame()
        # theme_map2['industry_name'] = industry_fin_df.groupby(['industry_name']).mean().index
        # theme_map2 = pd.concat([theme_map2, result2], axis=1)
        # theme_map2['industry_name'] = theme_map2['industry_name'] + ","

        theme_map3 = pd.DataFrame()
        theme_map3['industry_name'] = new_industry_fin_df['industry_name']
        theme_map3 = pd.concat([theme_map3, result3], axis=1)

        # theme_map4 = pd.DataFrame()
        # theme_map4['industry_name'] = industry_fin_df.groupby(['industry_name']).mean().index
        # theme_map4 = pd.concat([theme_map4, result4], axis=1)
        # theme_map4['industry_name'] = theme_map4['industry_name'] + ","

        test = theme_map.T
        test.columns = test.iloc[0]
        test.drop('industry_name', axis=0, inplace=True)
        pro1 = pro_of_sameclass(test)
        pro1['feature_list']=util.list_sql_condition(feature_list)
        test = test.astype(float).corr()
        test['feature_list']=util.list_sql_condition(feature_list)

        test2 = theme_map3.T
        test2.columns = test2.iloc[0]
        test2.drop('industry_name', axis=0, inplace=True)
        pro2 = pro_of_sameclass(test2)
        pro2['feature_list']=util.list_sql_condition(feature_list)
        test2 = test2.astype(float).corr()
        test2['feature_list']=util.list_sql_condition(feature_list)


        # dy_columns = (test > 0.8).sum().sort_values(ascending=False).index.tolist()
        # theme_cluster = []
        # for col in ['社会服务', '环保', '国防军工', '电力设备', '美容护理', '公用事业']:
        #     if (col in dy_columns):
        #         industry_list = test[test[col] > 0.8].index.tolist()
        #         theme_cluster.append(util.list_sql_condition(industry_list))
        #
        # for item in theme_cluster:
        #     print(item)
        # print('Kmeans_score is {} \n'.format(kmeans_score))
        # theme_cluster.append(kmeans_score)
        method1df=pd.concat([method1df,pro1],axis=0)
        method2df = pd.concat([method2df, test], axis=0)

        # dy_columns = (test2 > 0.8).sum().sort_values(ascending=False).index.tolist()
        # theme_cluster = []
        # for col in ['社会服务', '环保', '国防军工', '电力设备', '美容护理', '公用事业']:
        #     if (col in dy_columns):
        #         industry_list = test2[test2[col] > 0.8].index.tolist()
        #         theme_cluster.append(util.list_sql_condition(industry_list))
        # for item in theme_cluster:
        #     print(item)
        # print('Kmeans_score is {} \n'.format(kmeans_score3))
        # theme_cluster.append(kmeans_score3)
        method3df = pd.concat([method3df, pro2], axis=0)
        method4df = pd.concat([method4df, test2], axis=0)

        # print(theme_map2.groupby('theme').sum())
        # method3df = pd.concat([method3df, theme_map2.groupby('theme').sum()], axis=0)


    method1df.to_excel('method1df.xlsx')
    method2df.to_excel('method2df.xlsx')
    method3df.to_excel('method3df.xlsx')
    method4df.to_excel('method4df.xlsx')
    print('done')

def method1_usinglocabdata():

    industry_fin_df,fac_ret_df=read_industry_info()
    industry_fin_df=industry_fin_df[['industry_name','ENDDATE','ROE', 'EPS', 'OPERCASHFLOWPS', 'NETPROFITGROWRATE',
       'OPERATINGREVENUEYOY', 'NETASSETPS', 'DIVIDENDRATIO', 'PE', 'PB', 'PEG',
       'AVERAGEMV','growth']]

    industry_fin_df=industry_fin_df[(industry_fin_df['industry_name']!='综合')]
    # industry_fin_df=industry_fin_df[(industry_fin_df['industry_name'] != '农林牧渔')]

    potient_featute_list=['growth','ROE','PE','DIVIDENDRATIO','NETPROFITGROWRATE','EPS','PB','PEG','OPERCASHFLOWPS']

    cluster_engine(industry_fin_df,potient_featute_list)

def read_industry_index_data(end_date=datetime.datetime.today().strftime('%Y%m%d'),time_length=2):


    zqdm_con=util.list_sql_condition(index_code_list)
    start_date=str(int(end_date[0:4])-time_length)+end_date[4:]
    sql="select zqdm,jyrq,zdfd,roe,pe,pb,gxl from st_market.t_st_zs_hqql where jyrq>='{0}' and jyrq<='{1}' and zqdm in({2})"\
        .format(start_date,end_date,zqdm_con)
    index_data=hbdb.db2df(sql,db='alluser')
    index_data['industry_name']=[index_code_map[x] for x in index_data['zqdm']]
    index_data.rename(columns={'jyrq':'ENDDATE'},inplace=True)

    return index_data.drop('zqdm',axis=1)

def method2_usingdailyretfromdb():

    industry_fin_df=read_industry_index_data()
    potient_featute_list = ['zdfd','roe','gxl','pe']
    industry_fin_df = industry_fin_df[(industry_fin_df['industry_name'] != '综合')]
    cluster_engine(industry_fin_df, potient_featute_list)


if __name__ == '__main__':

    # method1_usinglocabdata()
    # method2_usingdailyretfromdb()

    theme_map=theme_map[(theme_map['industry_name']!='社会服务')&
                        (theme_map['industry_name']!='农林牧渔')&
    (theme_map['industry_name']!='美容护理')&
    (theme_map['industry_name']!='电力设备')&
    (theme_map['industry_name']!='农林牧渔')&
    (theme_map['industry_name']!='国防军工')&
    (theme_map['industry_name']!='建筑材料')&
    (theme_map['industry_name']!='环保')&
    (theme_map['industry_name']!='公用事业')&
    (theme_map['industry_name']!='纺织服饰')&
    (theme_map['industry_name']!='房地产')&
    (theme_map['industry_name']!='医药生物')&
    (theme_map['industry_name']!='商贸零售')&
    (theme_map['industry_name']!='传媒')&
    (theme_map['industry_name']!='有色金属')&
    (theme_map['industry_name']!='建筑装饰')&
    (theme_map['industry_name']!='基础化工')&
    (theme_map['industry_name']!='石油石化')&
    (theme_map['industry_name']!='交通运输')&
    (theme_map['industry_name']!='汽车')]
    df1 = pd.read_excel(r"E:\GitFolder\hbshare\fe\mutual_analysis\行业聚类日频数据结果\method1df.xlsx"
                        ,sheet_name='Sheet2')
    df2 = pd.read_excel(r"E:\GitFolder\hbshare\fe\mutual_analysis\行业聚类日频数据结果\method3df.xlsx",
                        sheet_name='Sheet2')
    df1=pd.merge(df1,theme_map,how='left',
                 left_on='Unnamed: 0',right_on='industry_name').drop(['Unnamed: 0','industry_name'],axis=1)
    df2=pd.merge(df2,theme_map,how='left',
                 left_on='Unnamed: 0',right_on='industry_name').drop(['Unnamed: 0','industry_name'],axis=1)
    df1=df1.groupby('theme').mean()
    df2=df2.groupby('theme').mean()
    df1.to_excel(r"E:\GitFolder\hbshare\fe\mutual_analysis\行业聚类日频数据结果\method12_result.xlsx")
    df2.to_excel(r"E:\GitFolder\hbshare\fe\mutual_analysis\行业聚类日频数据结果\method34_result.xlsx")
    print('')