import pandas as pd
import numpy as np
from hbshare.quant.CChen.load_data import load_calendar
from hbshare.quant.CChen.fund_perf import performance_analysis
from pyecharts.charts import Line, Grid
import pyecharts.options as opts
from pyecharts.components import Table
from pyecharts.options import ComponentTitleOpts


def load_factors(factor_dict, start_date, end_date, table, path, freq='w'):
    cal = load_calendar(start_date=start_date, end_date=end_date, freq=freq, db_path=path)

    data_all = pd.read_sql_query(
        'select TDATE, CLOSE, FACTOR from ' + table
        + ' where TDATE<=' + end_date.strftime('%Y%m%d')
        + ' and TDATE>=' + start_date.strftime('%Y%m%d')
        + ' and FACTOR in ' + str(tuple(factor_dict.keys()))
        + ' order by TDATE',
        path
    )
    data_all['FACTOR'] = data_all['FACTOR'].apply(lambda x: factor_dict[x])
    data_all = data_all.pivot(index='TDATE', columns='FACTOR', values='CLOSE')
    # data_all = data_all / data_all.loc[data_all.index[0], :]

    data = cal.merge(data_all.reset_index().rename(columns={'TDATE': 't_date'}), on='t_date', how='left')
    data = data.set_index(data['t_date'])[list(factor_dict.values())]
    data = data / data.loc[data.index[0], :]
    return data


def plot_lines(data, width=700, height=500, title='', legend_type='plain'):

    web = Line(
        init_opts=opts.InitOpts(
            # page_title='CTA大类因子',
            # width=str(width) + 'px',
            # height=str(height) + 'px',
        )
    ).add_xaxis(
        xaxis_data=data.index.tolist()
    )
    for i in data.columns:
        web.add_yaxis(
            series_name=i,
            y_axis=(data[i] / data[i][0]).round(4).tolist(),
            symbol="emptyCircle",
            is_symbol_show=True,
            label_opts=opts.LabelOpts(is_show=False),
            is_selected=True
        )

    web.set_global_opts(
        title_opts=opts.TitleOpts(
            title=title
        ),
        # tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
        # toolbox_opts=opts.ToolboxOpts(is_show=True),
        xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
        yaxis_opts=opts.AxisOpts(
            axislabel_opts=opts.LabelOpts(formatter="{value}"),
            min_='dataMin',
            max_='dataMax',
        ),
        datazoom_opts=[
            opts.DataZoomOpts(range_start=0, range_end=100),
            # opts.DataZoomOpts(pos_left="5%", xaxis_index=0),
            # opts.DataZoomOpts(pos_right="5%", xaxis_index=1),
            opts.DataZoomOpts(type_="inside")
        ],
        legend_opts=opts.LegendOpts(
            type_=legend_type,
            pos_top="5%",
            pos_left='5%',
            pos_right='5%'
        )
    )

    # return web
    grid = (
        Grid(init_opts=opts.InitOpts(
            width=str(width) + "px", height=str(height) + "px")
        ).add(
            web, grid_opts=opts.GridOpts(
                # pos_right=str(chart_pos_right) + "%",
                # pos_left=str(chart_pos_left) + "%",
                pos_top='20%',
            ),
            is_control_axis_index=True
        )
    )
    return grid


def factor_holding_period(factor_dict, start_date, end_date, path, table='cta_factor'):
    # holding_long_list = []
    # holding_short_list = []
    holding_list = []
    factor_selected = []
    for i in factor_dict:
        # print(i)
        factor_selected.append(i)
        factor_data = pd.read_sql_query(
            'select * from ' + table
            + ' where TDATE<=' + end_date.strftime('%Y%m%d')
            + ' and TDATE>=' + start_date.strftime('%Y%m%d')
            + ' and FACTOR=\'' + i + '\'',
            path
        )
        factor_data['UCODE'] = factor_data['EXCHANGE'].astype(str) + factor_data['PCODE'].astype(str)

        factor_pos = factor_data.pivot(index='TDATE', columns='UCODE', values='POS')

        pos_long = factor_pos[factor_pos > 0].fillna(0)
        pos_short = factor_pos[factor_pos < 0].fillna(0) * -1

        pos_long_cumdays = pos_long.cumsum() * pos_long * (pos_long - pos_long.shift(-1))
        pos_short_cumdays = pos_short.cumsum() * pos_short * (pos_short - pos_short.shift(-1))

        pos_long_days = (
                pos_long_cumdays[pos_long_cumdays > 0].ffill().fillna(0)
                - pos_long_cumdays[pos_long_cumdays > 0].ffill().fillna(0).shift(1)
        )
        pos_short_days = (
                pos_short_cumdays[pos_short_cumdays > 0].ffill().fillna(0)
                - pos_short_cumdays[pos_short_cumdays > 0].ffill().fillna(0).shift(1)
        )
        # holding_period_long = np.nanmean(pos_long_days[pos_long_days > 0])
        # holding_period_short = np.nanmean(pos_short_days[pos_short_days > 0])
        holding_period_all = np.nanmean(pos_long_days[pos_long_days > 0].append(pos_short_days[pos_short_days > 0]))

        # holding_long_list.append(holding_period_long)
        # holding_short_list.append(holding_period_short)
        holding_list.append(holding_period_all)

    rrr = pd.DataFrame(
        {
            'index': factor_selected,
            # '多头持仓天数': holding_long_list,
            # '空头持仓天数': holding_short_list,
            '平均持仓天数': holding_list
        }
    )

    return rrr.set_index('index').round(2)


def factor_perf(factor_dict, start_date, end_date, path, table='cta_index'):
    index_data = pd.read_sql_query(
        'select * from ' + table
        + ' where TDATE<=' + end_date.strftime('%Y%m%d')
        + ' and TDATE>=' + start_date.strftime('%Y%m%d')
        + ' and FACTOR in ' + str(tuple(factor_dict.keys())),
        path
    ).pivot(index='TDATE', columns='FACTOR', values='CLOSE').reset_index().rename(columns={'TDATE': 't_date'})

    rrr = performance_analysis(
        data_df=index_data,
        start_date=start_date,
        end_date=end_date,
        ret_num_per_year=250,
        print_info=False
    )
    rr0 = rrr[0].iloc[[0, 1, 4]].set_index('index').T.rename(columns={
        start_date.strftime('%Y%m%d') + '以来累计': '累计收益率(%)',
        start_date.strftime('%Y%m%d') + '以来年化': '年化收益率(%)',
        '最大回撤': '最大回撤(%)',
    })
    rr0 = (rr0 * 100).round(2)
    return rr0


def factor_stats(factor_dict, start_date, end_date, path):
    fhp = factor_holding_period(factor_dict=factor_dict, start_date=start_date, end_date=end_date, path=path)
    fp = factor_perf(factor_dict=factor_dict, start_date=start_date, end_date=end_date, path=path)
    fff = fhp.reset_index().merge(fp.reset_index(), on='index')
    fff['因子代码'] = fff['index']
    fff['index'] = fff['index'].apply(lambda x: factor_dict[x])
    return fff


def plot_table(data, title='', subtitle=''):
    table = Table()
    headers = data.columns.tolist()
    rows = data.values.tolist()
    table.add(headers, rows)
    table.set_global_opts(
        title_opts=ComponentTitleOpts(title=title, subtitle=subtitle)
    )
    return table
