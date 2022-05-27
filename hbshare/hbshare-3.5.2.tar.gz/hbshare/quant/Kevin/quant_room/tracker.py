"""
Kevin的标的池跟踪模块：tracker
"""
import os
import pandas as pd
import hbshare as hbs
import datetime
from sqlalchemy import create_engine
from hbshare.quant.Kevin.quant_room.MyUtil.data_loader import get_fund_nav_from_sql, get_trading_day_list
from hbshare.quant.Kevin.quant_room.MyUtil.util_func import cal_annual_return, cal_annual_volatility
from hbshare.quant.Kevin.asset_allocation.macro_index.util import create_table, delete_duplicate_records, WriteToDB
import plotly.express as px
import plotly
import plotly.graph_objs as go
from plotly.offline import plot as plot_ly
import plotly.figure_factory as ff


def get_track_config_from_db():
    params_tmp = {
        "ip": "192.168.223.152",
        "user": "readonly",
        "pass": "c24mg2e6",
        "port": "3306",
        "database": "riskmodel"
    }
    engine_tmp = "mysql+pymysql://{}:{}@{}:{}/{}".format(params_tmp['user'], params_tmp['pass'],
                                                         params_tmp['ip'],
                                                         params_tmp['port'], params_tmp['database'])

    sql_script = "SELECT * FROM tracker"
    engine = create_engine(engine_tmp)
    data = pd.read_sql(sql_script, engine)

    return data


def write_config_to_DB(table_name, is_increment=1):
    data = pd.read_excel(os.path.join("D:\\量化产品跟踪\\tracker", "config.xlsx"), sheet_name=0)
    if is_increment == 1:
        sql_script = "delete from {}".format(table_name)
        # delete first
        delete_duplicate_records(sql_script)
        # add new records
        WriteToDB().write_to_db(data, table_name)
    else:
        sql_script = """
            create table {}(
            id int auto_increment primary key,
            fund_id varchar(10),
            fund_name varchar(100),
            pool varchar(20),
            strategy_type varchar(20),
            level2type varchar(20),
            level3type varchar(20),
            abr varchar(20))
        """.format(table_name)
        create_table(table_name, sql_script)
        WriteToDB().write_to_db(data, table_name)


def plot_render(plot_dic, width=1200, height=800, **kwargs):
    kwargs['output_type'] = 'div'
    plot_str = plotly.offline.plot(plot_dic, **kwargs)
    print('%%angular <div style="height: %ipx; width: %spx"> %s </div>' % (height, width, plot_str))


class FundTracker:
    def __init__(self, end_date):
        self.end_date = end_date
        self._load_data()

    @staticmethod
    def _load_benchmark(start_date, end_date, benchmark_id):
        sql_script = "SELECT JYRQ as TRADEDATE, ZQDM, SPJG as TCLOSE from funddb.ZSJY WHERE" \
                     " ZQDM = '{}' " \
                     "and JYRQ >= {} and JYRQ <= {}".format(benchmark_id, start_date, end_date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        data = pd.DataFrame(res['data'])
        benchmark_df = data.set_index('TRADEDATE')['TCLOSE']

        return benchmark_df

    def _load_data(self):
        config_df = get_track_config_from_db()
        end_dt = datetime.datetime.strptime(self.end_date, '%Y%m%d')
        pre_date = (end_dt - datetime.timedelta(days=180)).strftime('%Y%m%d')
        trading_day_list = get_trading_day_list(pre_date, self.end_date, frequency="week")[-9:]

        return_dict = {}

        # 500指增
        fund_dict = config_df[config_df['level2type'] == "500指增"].set_index('fund_name')['fund_id'].to_dict()
        fund_nav = get_fund_nav_from_sql(pre_date, self.end_date, fund_dict).reindex(
            trading_day_list).dropna(axis=1)
        benchmark_series = self._load_benchmark(pre_date, self.end_date, '000905').reindex(
            trading_day_list).pct_change().dropna()
        return_df = fund_nav.pct_change().dropna().sub(benchmark_series, axis=0).sort_index()
        return_dict['500_alpha'] = return_df
        # 1000指增
        fund_dict = config_df[config_df['level2type'] == "1000指增"].set_index('fund_name')['fund_id'].to_dict()
        fund_nav = get_fund_nav_from_sql(pre_date, self.end_date, fund_dict).reindex(
            trading_day_list).dropna(axis=1)
        benchmark_series = self._load_benchmark(pre_date, self.end_date, '000852').reindex(
            trading_day_list).pct_change().dropna()
        return_df = fund_nav.pct_change().dropna().sub(benchmark_series, axis=0).sort_index()
        return_dict['1000_alpha'] = return_df
        # 量化多头
        fund_dict = config_df[config_df['strategy_type'] == "量化多头"].set_index('fund_name')['fund_id'].to_dict()
        fund_nav = get_fund_nav_from_sql(pre_date, self.end_date, fund_dict).reindex(
            trading_day_list).dropna(axis=1)
        benchmark_series = self._load_benchmark(pre_date, self.end_date, '000985').reindex(
            trading_day_list)
        fund_nav['benchmark'] = benchmark_series
        return_df = fund_nav.pct_change().dropna().sort_index()
        return_dict['all_market'] = return_df
        # 市场中性
        fund_dict = config_df[config_df['strategy_type'] == "市场中性"].set_index('fund_name')['fund_id'].to_dict()
        fund_nav = get_fund_nav_from_sql(pre_date, self.end_date, fund_dict).reindex(
            trading_day_list).dropna(axis=1)
        return_df = fund_nav.pct_change().dropna().sort_index()
        return_dict['market_neutral'] = return_df
        # 套利
        fund_dict = config_df[config_df['strategy_type'] == "套利"].set_index('fund_name')['fund_id'].to_dict()
        fund_nav = get_fund_nav_from_sql(pre_date, self.end_date, fund_dict).reindex(
            trading_day_list).dropna(axis=1)
        return_df = fund_nav.pct_change().dropna().sort_index()
        return_dict['arbitrage'] = return_df

        self.return_dict = return_dict
        self.config_df = config_df

    def alpha_period_index_scatter(self, return_df):
        annual_return = return_df.apply(cal_annual_return, axis=0)
        annual_vol = return_df.apply(cal_annual_volatility, axis=0)
        df = pd.merge(annual_return.to_frame('超额年化收益'), annual_vol.to_frame('超额年化波动'),
                      left_index=True, right_index=True).round(4)
        df = pd.merge(df, self.config_df.set_index('fund_name')['abr'], left_index=True, right_index=True)
        df.rename(columns={"abr": "name"}, inplace=True)

        fig = px.scatter(df, x='超额年化波动', y='超额年化收益', text='name')
        fig.update_traces(
            textposition="top center",
            textfont={'color': '#bebebe', 'size': 12}
        )
        fig.update_layout(
            title_text="<b>500指增收益风险比（过去8周）<b>",
            template='plotly_white',
            width=1000,
            height=600,
            yaxis=dict(tickfont=dict(size=12), tickformat=',.1%', showgrid=True),
            xaxis=dict(showgrid=True, tickformat=',.1%'),
        )

        return fig.data, fig.layout

    def alpha_performance(self, return_df):
        df = return_df.sort_index(ascending=False).iloc[:2].T.round(4)
        df.columns = ["current_week", "pre_week"]
        df = pd.merge(df, self.config_df.set_index('fund_name')['abr'], left_index=True, right_index=True)
        df.rename(columns={"abr": "name"}, inplace=True)

        fig = px.scatter(df, x='pre_week', y='current_week', text='name')
        fig.update_traces(
            textposition="top center",
            textfont={'color': '#bebebe', 'size': 12}
        )
        fig.update_layout(
            title_text="<b>500指增过去两周超额表现<b>",
            template='plotly_white',
            width=1000,
            height=600,
            yaxis=dict(tickfont=dict(size=12), tickformat=',.1%', showgrid=True),
            xaxis=dict(showgrid=True, tickformat=',.1%'),
        )

        fig.add_shape(type="rect",
                      xref="x", yref="y",
                      x0=df['pre_week'].median(),
                      x1=df['pre_week'].max(),
                      y0=df['current_week'].median(),
                      y1=df['current_week'].max(),
                      fillcolor="lightgray",
                      line=dict(color='red', width=2, dash='dot'),
                      opacity=0.2
                      )
        fig.add_shape(type="rect",
                      xref="x", yref="y",
                      x0=df['pre_week'].min(),
                      x1=df['pre_week'].median(),
                      y0=df['current_week'].min(),
                      y1=df['current_week'].median(),
                      fillcolor="lightgray",
                      line=dict(color='green', width=2, dash='dot'),
                      opacity=0.2
                      )

        return fig.data, fig.layout

    @staticmethod
    def table_plot(return_df, fig_width, fig_height):
        cum_return = (1 + return_df).cumprod() - 1
        cum_return = cum_return.iloc[[0, 1, 3, 7]].T
        cum_return.columns = ['上周', '近两周', '近四周', '近八周']
        cum_return = cum_return.sort_values(by='上周', ascending=False)
        cum_return.index.name = "产品名称"
        for col in cum_return.columns:
            cum_return[col] = cum_return[col].apply(lambda x: format(x, '.2%'))
        fig = ff.create_table(cum_return.reset_index())
        fig.layout.autosize = False
        fig.layout.width = fig_width
        fig.layout.height = fig_height

        return fig.data, fig.layout

    @staticmethod
    def plotly_line(df, title_text, figsize=(1000, 600)):
        fig_width, fig_height = figsize
        data = []
        for col in df.columns:
            trace = go.Scatter(
                x=df.index.tolist(),
                y=df[col],
                name=col,
                mode="lines"
            )
            data.append(trace)

        layout = go.Layout(
            title=dict(text=title_text),
            autosize=False, width=fig_width, height=fig_height,
            yaxis=dict(tickfont=dict(size=12), showgrid=True),
            xaxis=dict(showgrid=True),
            legend=dict(orientation="h"),
            template='plotly_white'
        )

        return data, layout

    def run(self):
        return_dict = self.return_dict
        # 500指增
        return_df = return_dict['500_alpha']
        data, layout = self.alpha_period_index_scatter(return_df)
        plot_render({"data": data, "layout": layout}, width=1000, height=600)
        data, layout = self.alpha_performance(return_df)
        plot_render({"data": data, "layout": layout}, width=1000, height=600)
        # 1000指增
        return_df = return_dict['1000_alpha'].sort_index(ascending=False)
        nav_df = (1 + return_df.sort_index()).cumprod()
        nav_df = nav_df / nav_df.iloc[0]
        data, layout = self.plotly_line(nav_df, "<b>1000指增近期走势<b>")
        plot_render({"data": data, "layout": layout}, width=1000, height=600)
        data, layout = self.table_plot(return_df, 1000, 40 * return_df.shape[1])
        plot_render({"data": data, "layout": layout}, height=40 * return_df.shape[1])
        # 全市场选股
        return_df = return_dict['all_market'].sort_index(ascending=False).rename(columns={"benchmark": "中证全指"})
        nav_df = (1 + return_df.sort_index()).cumprod()
        nav_df = nav_df / nav_df.iloc[0]
        data, layout = self.plotly_line(nav_df, "<b>全市场选股近期走势<b>")
        plot_render({"data": data, "layout": layout}, width=1000, height=600)
        data, layout = self.table_plot(return_df, 1000, 40 * return_df.shape[1])
        plot_render({"data": data, "layout": layout}, height=40 * return_df.shape[1])
        # 市场中性
        return_df = return_dict['market_neutral'].sort_index(ascending=False)
        nav_df = (1 + return_df.sort_index()).cumprod()
        nav_df = nav_df / nav_df.iloc[0]
        data, layout = self.plotly_line(nav_df, "<b>市场中性近期走势<b>")
        plot_render({"data": data, "layout": layout}, width=1000, height=600)
        data, layout = self.table_plot(return_df, 1000, 40 * return_df.shape[1])
        plot_render({"data": data, "layout": layout}, height=40 * return_df.shape[1])


if __name__ == '__main__':
    # write_config_to_DB("tracker", is_increment=1)
    FundTracker('20220415').run()