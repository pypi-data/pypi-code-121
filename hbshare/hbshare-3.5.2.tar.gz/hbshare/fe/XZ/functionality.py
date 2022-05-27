import pandas as pd
import datetime
import plotly.graph_objs as go
import  plotly.figure_factory as ff
import statsmodels.api as sm
import numpy as np
from hbshare.fe.XZ import db_engine
import plotly
import plotly.io as pio
import cvxopt.solvers as sol
from cvxopt import matrix as mat
sol.options['show_progress'] = False

hbdb=db_engine.HBDB()

class Untils:

    def __init__(self,val_hld=None,indus_info=None,fin_info=None,benchmark_info=None):
        from hbshare.fe.XZ.config import config_pfa
        configuration = config_pfa.Config()
        self.asset_type_code= configuration.Asset_type
        self.val_hld=val_hld
        self.indus_info=indus_info
        self.fin_info=fin_info
        self.bench_info=benchmark_info
        if((val_hld is not None)&(indus_info is not None)&(fin_info is not None)&(benchmark_info is not None)):
            self.purified_stk_hld= self.cleaning_stock_hld()

    def shift_df_date(self,bench_df,df,bench_date_col,date_col):

        for date in list(set(bench_df[bench_date_col].unique()).difference(set(df[date_col].unique()))):
            date_delta=df[date_col]-date
            df .loc[date_delta.abs() == date_delta.abs().min(), date_col] = date
        return df

    def cleaning_stock_hld(self):

        rawdata=self.val_hld[~self.val_hld['Stock_code'].isnull()]

        temp_df=pd.merge(
            rawdata,self.indus_info[['SECUCODE','FIRSTINDUSTRYNAME']],how='left',left_on='Stock_code',right_on='SECUCODE'
        ).drop(['SECUCODE'],axis=1)

        #original used to shift the date that is missed in from any information table(any table except the fund valuation table)
        #this part is then abandoned by using '' for missing date
        # self.fin_info=self.shift_df_date(temp_df,self.fin_info,'Stamp_date','TRADINGDAY')
        # self.bench_info = self.shift_df_date(temp_df, self.bench_info, 'Stamp_date', 'ENDDATE')[['SECUCODE','WEIGHT','ENDDATE','Index_type']]

        self.bench_info=self.bench_info.rename(columns={'WEIGHT':'Index_Weight'})
        self.bench_info=pd.merge(temp_df[['Stamp_date', 'Stock_code','Weight']],self.bench_info,how='left',left_on=['Stock_code','Stamp_date'],right_on=['SECUCODE','ENDDATE'])
        self.bench_info['Index_type'].fillna('1800以外', inplace=True)
        self.bench_info['Index_Weight'].fillna(0, inplace=True)
        temp_df=pd.merge(temp_df,self.fin_info,how='left',left_on=['Stock_code','Stamp_date'],right_on=['SECUCODE','TRADINGDAY']).drop('ROW_ID',axis=1)

        return temp_df

    def aggregate_by(self,df,groupby,method,method_on):

        if(method=='sum'):
            output_df = df.groupby(groupby).sum(method_on).unstack().fillna(0)[
                (method_on)].fillna(0)
        elif(method=='average'):
            output_df = df.groupby(groupby).mean(method_on).unstack().fillna(0)[
                (method_on)].fillna(0)
        else:
            raise Exception
            print('Please check the aggregation method')

        output_df['日期'] = output_df.index

        return output_df

    def asset_allocation_stats(self):

        data=self.val_hld
        output_df = pd.DataFrame(columns=['日期'])
        output_df['日期']=data['Stamp_date'].unique()

        for keys in self.asset_type_code.keys():

            output_df =pd.merge(output_df,data[data['Code']==self.asset_type_code[keys]][['Weight','Stamp_date']],
                                how='left',left_on='日期',right_on='Stamp_date')
            output_df.rename(columns={'Weight':keys},inplace=True)
            output_df=output_df.drop(['Stamp_date'],axis=1)

        output_df['A股']=0
        for col in [x for x in list(self.asset_type_code.keys()) if ('上交所' in x or '深交所' in x) ]:
            output_df['A股']= output_df['A股']+output_df[col].fillna(0)
        output_df['港股']=output_df['港股通'].fillna(0)+output_df['深港通'].fillna(0)

        return output_df.fillna(0)

    def rank_filter(self,input_df,thresholds):

        index_list=['前'+str(x)+'大' for x in thresholds ]
        output_df=pd.DataFrame(columns=input_df['日期'])
        input_df=input_df.drop(['日期'],axis=1).T
        for col in input_df.columns:
            values=[]
            for rank in thresholds:
                values.append( [ input_df[col].sort_values(ascending=False).values[0:rank],
                                 input_df[col].sort_values(ascending=False).index[0:rank]] )
            output_df[col]=values
        output_df.index=index_list
        output_df=output_df.T
        output_df['日期']=output_df.index

        return  output_df

    def fund_risk_exposure(self,left_table,row_factors_df,left_col):

        left_table['Stamp_date']=[ ''.join(x.split('-')) for x in left_table[left_col[0]].astype(str)]
        factors_col=row_factors_df.columns.drop(['ticker','trade_date']).tolist()
        fund_factors=pd.merge(left_table,row_factors_df
                              ,how='left',right_on=['ticker','trade_date'],left_on=[left_col[1],'Stamp_date'])\
            .drop(left_col[1],axis=1)

        for col in factors_col:
            fund_factors[col]=fund_factors[col].astype(float)*fund_factors[left_col[2]]/100
        fund_factors=fund_factors.groupby(['trade_date']).sum(factors_col)[factors_col]

        # fund_factors['Stamp_date'] = fund_factors.index
        fund_factors['JYYF']=[ x[0:6] for x in fund_factors.index]

        return fund_factors

    def generate_ret_df(self):


        ret_df=self.val_hld[self.val_hld['Code'].str.contains('今日单位净值') | self.val_hld['Code'].str.contains('基金单位净值:')]['Code'].unique()[0]
        ret_df=self.val_hld[self.val_hld['Code']==ret_df][['Code','Name','Stamp_date']]
        ret_df.rename(columns={'Name':'Net_value'},inplace=True)
        ret_df['Return']=ret_df['Net_value'].astype(float).pct_change()
        ret_df.drop('Code',axis=1,inplace=True)
        ret_df.reset_index(drop=True, inplace=True)

        return ret_df

    def iter_list(self,inputlist,iter_num,bench_factor):
        import itertools
        iter_list=list(itertools.combinations(inputlist,iter_num-1))
        output_list=[]
        for col in bench_factor:
            output_list+=[x+(col,) for x in iter_list]
        return output_list

    def calculate_alpha(self,ols_df,factors_list,num_factors,ret_col,date_col,bench_factor):

        iter_list = self.iter_list(factors_list, num_factors,bench_factor)
        alpha = []
        rsquar = []
        factors = []
        parameters = []
        for factors_combine in iter_list:
            model = sm.OLS(ols_df[ret_col].values, ols_df[['const'] + list(factors_combine)].values)
            results = model.fit()
            alpha.append(results.params[0])
            rsquar.append(results.rsquared)
            factors.append(list(factors_combine))
            parameters.append(results.params)

        summary_df = pd.DataFrame()
        summary_df['alpha'] = alpha
        summary_df['rsquar'] = rsquar
        summary_df['factors'] = factors
        summary_df['parameters'] = parameters

        max_rsquare = summary_df['rsquar'].max()
        max_rsquare_para_value = summary_df[summary_df['rsquar'] == max_rsquare]['parameters'].values[0]
        max_rsquare_para_name = ['const'] + summary_df[summary_df['rsquar'] == max_rsquare]['factors'].values[0]

        # max_rsquare_alpha=
        # max_rsquare_alpha_t_value=
        # max_rsquare=1/max_rsquare
        # alpha_score=0.25*max_rsquare_alpha

        simulated_df = ols_df[max_rsquare_para_name]
        simulated_df['simulated_ret'] = np.dot(simulated_df, max_rsquare_para_value.T)
        simulated_df['real_ret'] = ols_df[ret_col].values
        simulated_df['日期'] = ols_df[date_col].values

        return summary_df,simulated_df,','.join(max_rsquare_para_name)

    @staticmethod
    def list_sql_condition(list):
        return "'"+"','".join(list)+"'"

    @staticmethod
    def get_mutual_stock_funds(asofQ):

        hbdb=db_engine.HBDB()

        last_2years=(datetime.datetime.strptime(asofQ, '%Y%m%d')-datetime.timedelta(days=730))\
            .strftime('%Y%m%d')

        sql="select jjdm,jjmc,clrq  from st_fund.t_st_gm_jjxx where cpfl='2' and (ejfl='13' or ejfl='35' or ejfl='37') and jjzt='0' and clrq<='{0}'  ".format(last_2years)
        stock_jjdm=hbdb.db2df(sql,db='funduser').sort_values(['clrq','jjdm'])
        stock_jjdm.drop_duplicates(['jjmc'],keep='first',inplace=True)

        jjdm_list=stock_jjdm['jjdm'].tolist()
        ticker_con="'"+"','".join(jjdm_list)+"'"

        sql="select jjdm,avg(gptzzjb) from st_fund.t_st_gm_zcpz where jjdm in ({0}) group by jjdm"\
            .format(ticker_con)
        tempdf = hbdb.db2df(sql, db='funduser')
        jjdm_list=tempdf[tempdf['avg(gptzzjb)']>=60]['jjdm'].tolist()
        ticker_con = "'" + "','".join(jjdm_list) + "'"

        sql="select jjdm,min(gptzzjb) from st_fund.t_st_gm_zcpz where jsrq<='{0}' and jsrq>={1} and jjdm in ({2}) group by jjdm"\
            .format(asofQ,last_2years,ticker_con)

        tempdf=hbdb.db2df(sql,db='funduser')
        jjdm_list = tempdf[tempdf['min(gptzzjb)'] >= 50]['jjdm'].tolist()

        return  jjdm_list

    @staticmethod
    def _shift_date(date):
        trade_dt = datetime.datetime.strptime(date, '%Y%m%d')
        pre_date = (trade_dt -datetime.timedelta(days=30)).strftime('%Y%m%d')

        sql_script = "SELECT JYRQ, SFJJ, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {}".format(
            pre_date,date)
        df=hbdb.db2df(sql_script,db='readonly')
        df=df.rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                      "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        df['isOpen'] = df['isOpen'].astype(int).replace({0: 1, 1: 0})
        df['isMonthEnd'] = df['isMonthEnd'].fillna(0).astype(int)

        trading_day_list = df[df['isOpen'] == 1]['calendarDate'].tolist()

        return trading_day_list[-1]

    @staticmethod
    # 写一个通用的多元一次回归的算法模型，自变量个数不确定
    def my_general_linear_model_func(A1, b1):

        P = 2 * np.dot(np.transpose(A1), A1)
        Q = - 4 * np.dot(np.transpose(A1), b1)
        P = mat(P)
        Q = mat(Q)

        lb=[0]*A1.shape[1]
        ub=[1]*A1.shape[1]

        G = mat(np.vstack((np.diag([-1]*A1.shape[1]), np.diag([1]*A1.shape[1]))), tc='d')
        h = mat(np.array(lb+ub), tc='d') # 为各参数的上下限！！！！
        A = mat(np.array([[1]*A1.shape[1]]), tc='d')
        b = mat(np.array([1]), tc='d')

        result = sol.qp(P, Q,G, h, A, b)

        return [ x for x in result['x']]

class Plot:
    def __init__(self,fig_width,fig_height):

        self.fig_width=fig_width
        self.fig_height=fig_height
        self.ams_color_lista=['#C94649','#EEB2B4','#E1777A','#D57C56','#E39A79','#DB8A66','#E5B88C']
        self.ams_color_listb = ['#8588B7', '#B4B6D1', '#55598D', '#628497', '#A9C6CB','#866EA9','#B79BC7']
        self.ams_color_listc = ['#7D7D7E', '#CACACA', '#A7A7A8', '#606063', '#C4C4C4','#99999B','#B7B7B7']
    #
    def plot_render(self,data,layout, **kwargs):
        kwargs['output_type'] = 'div'
        plot_str = plotly.offline.plot({"data": data, "layout": layout}, **kwargs)
        print('%%angular <div style="height: %ipx; width: %spx"> %s </div>' % (self.fig_height, self.fig_width, plot_str))

    # def plot_render(self,data,layout):
    #     fig = go.Figure(data=data, layout=layout)
    #     fig.show()

    @staticmethod
    def save_pic2local(data,layout,name):
        fig = go.Figure(data=data, layout=layout)
        fig.write_image(name+'.png')
        # pio.write_image(fig,name+'.png')


    def plotly_style_bar(self,df, title_text,legend_x=0.30):
        fig_width, fig_height = self.fig_width,self.fig_height
        cols = df.columns.tolist()

        data = []
        for i in range(len(cols)):
            col = cols[i]
            trace = go.Bar(
                x=df.index.tolist(),
                y=df[col],
                name=col,

            )
            data.append(trace)

        layout = go.Layout(
            title=dict(text=title_text),
            autosize=False, width=fig_width, height=fig_height,
            yaxis=dict(tickfont=dict(size=12), showgrid=True),
            xaxis=dict(showgrid=True),
            legend=dict(orientation="h", x=legend_x),
            template='plotly_white'
        )

        self.plot_render(data, layout)

    def plotly_jjpic_bar(self,df, title_text,legend_x=0.30):
        fig_width, fig_height = self.fig_width,self.fig_height
        cols = df.columns.tolist()

        a=int(np.floor(len(cols)/3))
        b=len(cols)%3

        color_list=self.ams_color_lista[0:a+int(b==1)]+\
                   self.ams_color_listb[0:a+int(b==2)]+\
                   self.ams_color_listc[0:a]

        data = []
        for i in range(len(cols)):
            col = cols[i]
            trace = go.Bar(
                x=df.index.tolist(),
                y=df[col],
                name=col,
                marker=dict(color=color_list[i])
            )
            data.append(trace)

        layout = go.Layout(
            title=dict(text=title_text),
            autosize=False, width=fig_width, height=fig_height,
            yaxis=dict(tickfont=dict(size=12), showgrid=True),
            xaxis=dict(showgrid=True),
            legend=dict(orientation="h", x=legend_x),
            template='plotly_white'
        )

        self.plot_render(data, layout)
        #self.save_pic2local(data, layout,title_text)

    def plotly_pie(self,df, title_text):
        fig_width, fig_height = self.fig_width,self.fig_height
        labels = df.index.tolist()
        values = df.values.round(3).reshape(1,len(df)).tolist()[0]

        a=int(np.floor(len(labels)/3))
        b=len(labels)%3

        color_list=self.ams_color_lista[0:a+int(b==1)]+\
                   self.ams_color_listb[0:a+int(b==2)]+\
                   self.ams_color_listc[0:a]

        # color_list = ['#C94649', '#8588B7', '#7D7D7E']
        data = [go.Pie(labels=labels, values=values, hoverinfo="label+percent",marker=dict(colors=color_list),
                       texttemplate="%{label}: %{percent}")]
        layout = go.Layout(
            title=dict(text=title_text),
            autosize=False, width=fig_width, height=fig_height
        )

        self.plot_render(data, layout)
        #self.save_pic2local(data, layout, title_text)

    def plotly_area(self,df,title_text):
        fig_width, fig_height = self.fig_width,self.fig_height
        names = df.columns.to_list()
        names.remove('日期')
        cols =df['日期'].to_list()

        data = []
        for name in names:
            tmp = go.Scatter(
                x=cols,
                y=df[name].values,
                name=name,
                mode='lines',
                line=dict(width=0.5),
                fill='tonexty',
                stackgroup='one')
            data.append(tmp)

        layout = go.Layout(
            title=title_text,
            autosize=False,
            width=fig_width,
            height=fig_height,
            showlegend=True,
            xaxis=dict(type='category'),
            yaxis=dict(
                type='linear',
                range=[1, 100],
                dtick=20,
                ticksuffix='%'))

        self.plot_render(data, layout)

    def plotly_line(self,df, title_text):

        fig_width, fig_height = self.fig_width,self.fig_height
        names = df.columns.to_list()
        names.remove('日期')
        cols =df['日期'].to_list()

        data = []
        for name in names:
            trace = go.Scatter(
                x=cols,
                y=df[name].values,
                name=name,
                mode="lines+markers"
            )
            data.append(trace)

        date_list = df.index.tolist()

        layout = go.Layout(
            title=dict(text=title_text),
            autosize=False, width=fig_width, height=fig_height,
            yaxis=dict(tickfont=dict(size=12), showgrid=True),
            xaxis=dict(showgrid=True),
            yaxis2={'anchor': 'x', "overlaying": 'y', "side": 'right'},
            template='plotly_white'
        )

        self.plot_render(data, layout)

    def plotly_line_style(self, df, title_text,fix_range=False):

        fig_width, fig_height = self.fig_width,self.fig_height
        cols = df.columns.tolist()
        # color_list = ['rgb(49, 130, 189)', 'rgb(204, 204, 204)', 'rgb(216, 0, 18)']
        data = []

        data = []
        for col in cols:
            trace = go.Scatter(
                x=df.index.tolist(),
                y=df[col],
                name=col,
                mode="lines+markers"
            )
            data.append(trace)

        date_list = df.index.tolist()

        layout = go.Layout(
            title=dict(text=title_text),
            autosize=False, width=fig_width, height=fig_height,
            # yaxis=dict(tickfont=dict(size=12), showgrid=True),
            xaxis=dict(showgrid=True),
            # yaxis2={'anchor': 'x', "overlaying": 'y', "side": 'right'},
            template='plotly_white'
        )

        self.plot_render(data, layout)

    def plotly_line_multi_yaxis(self,df,title_text,y2_col):

        fig_width, fig_height = self.fig_width,self.fig_height
        names = df.columns.to_list()
        for name in y2_col+['日期']:
            names.remove(name)
        cols =df['日期'].to_list()

        data = []
        for name in names:
            trace = go.Scatter(
                x=cols,
                y=df[name].values,
                name=name+'(左轴)',
                mode="lines+markers"
            )
            data.append(trace)

        for name in y2_col:
            trace = go.Scatter(
                x=cols,
                y=df[name].values,
                name=name+'(右轴)',
                mode="lines+markers",
                yaxis='y2'
            )
            data.append(trace)

        date_list = df.index.tolist()

        layout = go.Layout(
            title=dict(text=title_text),
            autosize=False, width=fig_width, height=fig_height,
            yaxis=dict(tickfont=dict(size=12), showgrid=True),
            xaxis=dict(showgrid=True),
            yaxis2={'anchor': 'x', "overlaying": 'y', "side": 'right'},
            template='plotly_white'
        )

        self.plot_render(data, layout)

    def plotly_table(self, df, table_width, title_text):

        fig=ff.create_table(df)
        fig.layout.width=table_width
        fig.layout.title=title_text
        self.plot_render(fig.data,fig.layout )

    def ploty_polar(self,df,title):

        fig_width, fig_height = self.fig_width, self.fig_height

        th=df.columns.tolist()
        r_data=df.values[0].tolist()

        trace0 = go.Scatterpolar(
            r=r_data,
            theta=th,
            fill='toself',
        )

        data = [trace0]
        layout = go.Layout(
            title=dict(text=title),
            autosize=False, width=fig_width, height=fig_height,
            polar=dict(
                radialaxis=dict(visible=True,range = [0, 9])
                ),
            showlegend=False
        )

        self.plot_render(data, layout)

    def ploty_heatmap(self,z,z_text,title):

        #fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_width=[0.3, 0.2, 0.7])

        fig_width, fig_height = self.fig_width, self.fig_height

        fig=ff.create_annotated_heatmap(z,annotation_text=z_text)
        fig['layout']['yaxis']['autorange'] = "reversed"

        fig.layout.width=fig_width
        fig.layout.title=title

        self.plot_render(fig.data,fig.layout)

    def plotly_line_with_annotation(self, df,data_col,anno_col, title_text,fix_range=False):

        fig_width, fig_height = self.fig_width,self.fig_height
        cols =data_col

        data = []
        for col in cols:
            trace = go.Scatter(
                x=df.index.tolist(),
                y=df[col].values.tolist(),
                name=col,
                mode="lines"
            )
            data.append(trace)
        df=df[df[anno_col[0]].notnull()]
        for col2 in anno_col:
            trace=go.Annotation(
                textfont=go.Font(
                    size=1
                ),
                text=df[col2].values.tolist(),
                x=df.index.tolist(),
                y=df[col].values.tolist(),
                mode="markers",
                marker=dict( size=10),
                name='trade_point',

            )
            data.append(trace)

        # date_list = df.index.tolist()


        layout = go.Layout(
            title=dict(text=title_text),
            autosize=False, width=fig_width, height=fig_height,
            # yaxis=dict(tickfont=dict(size=12), showgrid=True),
            xaxis=dict(showgrid=True),
            # yaxis2={'anchor': 'x', "overlaying": 'y', "side": 'right'},
            template='plotly_white',


        )

        self.plot_render(data, layout)


if __name__ == '__main__':

    uti=Untils()
    uti.get_mutual_stock_funds('20211231')