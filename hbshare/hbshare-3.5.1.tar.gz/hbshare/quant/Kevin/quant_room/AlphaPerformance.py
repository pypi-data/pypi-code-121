"""
Alpha标的表现统计
"""
import pandas as pd
import hbshare as hbs
import datetime
import plotly
from plotly.offline import plot as plot_ly
import plotly.graph_objs as go

plotly.offline.init_notebook_mode(connected=True)


alpha_dict = {
    "hs300": {
        "明汯稳健增长2期1号": "SK5676",
        "幻方300指数增强欣享一号": "SNL044",
        "星阔春山一号": "SQF231"
    },
    "zz500": {
        "明汯价值成长1期3号": "SEE194",
        "启林中证500指数增强8号": "SNL641",
        "幻方量化500指数专享60号1期": "SNA691",
        "天演启航量化500指增": "SQP881",
        "诚奇睿盈500指数增强尊享1号": "SQK764",
        "星阔广厦1号中证500指数增强": "SNU706",
        "量锐62号": "SGR954",
        "因诺聚配中证500指数增强": "SGX346",
        "赫富500指数增强一号": "SEP463",
        "量派500增强8号": "SNJ513",
        "凡二英火5号": "SJM016",
        "希格斯旅行者1号": "SJA569",
        "伯兄建康": "SQT564",
        "概率500指增1号": "SQT076",
        "白鹭精选量化鲲鹏十号": "SQB109"
              },
    "zz1000": {
        "启林广进中证1000指数增强1号": "SSU078",
        "明汯量化中小盘增强1号": "SGG585",
        # "量派中证1000增强12号": "SQJ816",
        "凡二量化中证1000增强1号": "SSC067",
        # "希格斯旅行者中证1000指数增强1号": "SSD078",
        "衍复鲲鹏三号": "SJM688",
        "概率1000指增1号": "SQQ803"},
    "all_market": {
        "明汯股票精选13号": "SSL078",
        "天演赛能": "P22984",
        "诚奇睿盈优选尊享1号": "SSU249",
        "星阔山海6号股票优选": "SSE288"
                   },
    "market_neutral": {
        "明汯中性7号1期": "SEL756",
        "天演广全": "SLC213",
        "诚奇睿盈对冲尊享1号": "SNR622",
        "赫富对冲四号": "SEW735",
        "星阔云起1号": "SNU704",
        "茂源巴舍里耶2期": "SCV226",
        "伯兄卢比孔": "SL3246",
        "概率一号": "SNM976"
    },
    "cb": {"悬铃C号": "SEK201",
           "百奕传家一号": "SJS027",
           "艾方可转债1号": "SCK025",
           "安值福慧量化1号": "SCP765"}
}


class AlphaPerformance:
    def __init__(self, start_date, end_date, fund_info_dict):
        self.start_date = start_date
        self.end_date = end_date
        self.fund_info_dict = fund_info_dict
        self._load_data()

    def _load_calendar(self):
        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {}".format(
            self.start_date, self.end_date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        df = pd.DataFrame(res['data']).rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                     "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        df['isOpen'] = df['isOpen'].astype(int).replace({0: 1, 1: 0})
        df['isWeekEnd'] = df['isWeekEnd'].fillna(0).astype(int)
        df['isMonthEnd'] = df['isMonthEnd'].fillna(0).astype(int)

        self.calendar_df = df[['calendarDate', 'isOpen', 'isWeekEnd', 'isMonthEnd']]

        trading_day_list = df[df['isWeekEnd'] == 1]['calendarDate'].tolist()

        return trading_day_list

    def _load_data(self):
        nav_series_dict = dict()

        for strategy_type, id_dict in self.fund_info_dict.items():
            nav_list = []
            for fund_name, fund_id in id_dict.items():
                sql_script = "SELECT a.jjdm fund_id, b.jzrq TRADEDATE, b.fqdwjz as ADJ_NAV from " \
                             "st_hedge.t_st_jjxx a, st_hedge.t_st_rhb b where a.cpfl = '4' and a.jjdm = b.jjdm " \
                             "and a.jjzt not in ('3') " \
                             "and a.jjdm = '{}' and b.jzrq >= {} and b.jzrq <= {} " \
                             "order by b.jzrq".format(fund_id, self.start_date, self.end_date)
                res = hbs.db_data_query("highuser", sql_script, page_size=5000)
                data = pd.DataFrame(res['data']).set_index('TRADEDATE')['ADJ_NAV']
                data.name = fund_name
                nav_list.append(data)

            nav_df = pd.concat(nav_list, axis=1)
            nav_series_dict[strategy_type] = nav_df.sort_index()

        self.nav_series_dict = nav_series_dict

    @staticmethod
    def _load_benchmark(benchmark_id, start_date, end_date):
        sql_script = "SELECT JYRQ as TRADEDATE, ZQMC as INDEXNAME, SPJG as TCLOSE from funddb.ZSJY WHERE ZQDM = '{}' " \
                     "and JYRQ >= {} and JYRQ <= {}".format(benchmark_id, start_date, end_date)
        res = hbs.db_data_query('readonly', sql_script)
        data = pd.DataFrame(res['data']).rename(columns={"TCLOSE": "benchmark"}).set_index('TRADEDATE')[['benchmark']]

        return data

    @staticmethod
    def plotly_line(df, title_text, sava_path, figsize=(1200, 500)):
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

        # date_list = df.index.tolist()
        # tick_vals = [i for i in range(0, len(df), 4)]
        # tick_text = [date_list[i] for i in range(0, len(df), 4)]

        layout = go.Layout(
            title=dict(text=title_text),
            autosize=False, width=fig_width, height=fig_height,
            yaxis=dict(tickfont=dict(size=12), showgrid=True),
            # xaxis=dict(showgrid=True, tickvals=tick_vals, ticktext=tick_text),
            xaxis=dict(showgrid=True),
            template='plotly_white'
        )
        fig = go.Figure(data=data, layout=layout)

        plot_ly(fig, filename=sava_path, auto_open=False)

    def get_construct_result(self):
        trading_day_list = self._load_calendar()

        # 300指增
        # nav_df = self.nav_series_dict['hs300'].reindex(trading_day_list).dropna(how='all')
        # return_df = nav_df.fillna(method='ffill').pct_change().fillna(0.)
        # benchmark_series = self._load_benchmark('000300', self.start_date, self.end_date).reindex(
        #     trading_day_list).pct_change().fillna(0.)
        # return_df = return_df.sub(benchmark_series['benchmark'], axis=0)
        # 500指增
        nav_df = self.nav_series_dict['zz500'].reindex(trading_day_list).dropna(how='all')
        benchmark_series = self._load_benchmark('000905', self.start_date, self.end_date).reindex(
            trading_day_list).pct_change().fillna(0.)
        return_df = nav_df.fillna(method='ffill').pct_change().fillna(0.)
        return_df = return_df.sub(benchmark_series['benchmark'], axis=0)
        # (1 + return_df).cumprod().loc[['20211231', '20220128', '20220225', '20220325'],:].pct_change().dropna().T.to_clipboard()
        adj_nav_df = (1 + return_df).cumprod()
        self.plotly_line(
            adj_nav_df, "500指增产品走势图", "D:\\量化产品跟踪\\代销及FOF标的\\500指增走势.html", figsize=(1200, 600))
        # 1000指增
        nav_df = self.nav_series_dict['zz1000'].reindex(trading_day_list).dropna(how='all')
        benchmark_series = self._load_benchmark('000852', self.start_date, self.end_date).reindex(
            trading_day_list).pct_change().fillna(0.)
        return_df = nav_df.fillna(method='ffill').pct_change().fillna(0.)
        return_df = return_df.sub(benchmark_series['benchmark'], axis=0)
        adj_nav_df = (1 + return_df).cumprod()
        self.plotly_line(
            adj_nav_df, "1000指增产品走势图", "D:\\量化产品跟踪\\代销及FOF标的\\1000指增走势.html", figsize=(1200, 600))
        # 全市场选股
        nav_df = self.nav_series_dict['all_market'].reindex(trading_day_list).dropna(how='all')
        benchmark_series = self._load_benchmark('000985', self.start_date, self.end_date).reindex(
            trading_day_list).pct_change().fillna(0.)
        return_df = nav_df.fillna(method='ffill').pct_change().fillna(0.)
        return_df = return_df.sub(benchmark_series['benchmark'], axis=0)
        adj_nav_df = (1 + return_df).cumprod()
        self.plotly_line(
            adj_nav_df, "量化多头产品走势图", "D:\\量化产品跟踪\\代销及FOF标的\\全市场选股走势.html", figsize=(1200, 600))
        # 市场中性
        nav_df = self.nav_series_dict['market_neutral'].reindex(trading_day_list).dropna(how='all')
        return_df = nav_df.fillna(method='ffill').pct_change().fillna(0.)
        adj_nav_df = (1 + return_df).cumprod()
        self.plotly_line(
            adj_nav_df, "市场中性产品走势图", "D:\\量化产品跟踪\\代销及FOF标的\\市场中性走势.html", figsize=(1200, 600))
        # 可转债
        nav_df = self.nav_series_dict['cb'].reindex(trading_day_list).dropna(how='all')
        return_df = nav_df.fillna(method='ffill').pct_change().fillna(0.)
        adj_nav_df = (1 + return_df).cumprod()
        self.plotly_line(adj_nav_df, "可转债套利产品走势图", "D:\\量化产品跟踪\\代销及FOF标的\\可转债走势.html",
                         figsize=(1200, 600))


if __name__ == '__main__':
    AlphaPerformance('20211231', '20220513', alpha_dict).get_construct_result()