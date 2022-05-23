import pdb
from pyecharts.charts import Kline
from pyecharts.charts import Line
from pyecharts.charts import Bar
from pyecharts.charts import Grid
from pyecharts import options as opts

class Indicators(object):
    @classmethod
    def ma_line(cls, ma_data, trade_date_list):
        line_plot = Line()
        line_plot.add_xaxis(trade_date_list)
        for ma_name in ['ma5', 'ma10', 'ma20', 'ma40', 'ma60']:
            result_format = [result  for result in ma_data[ma_name].values.tolist()]
            line_plot.add_yaxis(ma_name.upper(), result_format,
                           is_smooth=True,
                           is_connect_nones=True,
                           is_symbol_show=False,
                           label_opts=opts.LabelOpts(is_show=False))
        line_plot.set_global_opts(title_opts=opts.TitleOpts(title=""),
                         xaxis_opts=opts.AxisOpts(
                    axistick_opts=opts.AxisTickOpts(is_align_with_label=True),
                    is_scale=False,
                    boundary_gap=False,
                ),yaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(formatter="{value}")
                ))
        
        return line_plot
    
    @classmethod
    def vol_bar(cls, vol_data, trade_date_list):
        volume_drop = [[x, vol_data.turnover_vol[x], -1 if vol_data.close_price[x] <= \
                    vol_data.open_price[x] else 1]  for x in range(0, len(vol_data.index))]
        bar_plot = Bar()
        bar_plot.add_xaxis(trade_date_list)
        bar_plot.add_yaxis('volume', volume_drop, label_opts=opts.LabelOpts(is_show=False),
                      xaxis_index=1, yaxis_index=1)
        bar_plot.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        bar_plot.set_global_opts(
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    is_scale=True,
                    grid_index=1,
                    boundary_gap=False,
                    axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                    split_number=20,
                    min_="dataMin",
                    max_="dataMax",),
                yaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(formatter="{value}")
                ),legend_opts=opts.LegendOpts(pos_right="30%", pos_top="70%")
            )
        return bar_plot
    
    @classmethod
    def madvol_line(cls, madvol_data, trade_date_list):
        line_plot = Line()
        line_plot.add_xaxis(trade_date_list)
        result_format = [result  for result in madvol_data['ma5_vol'].values.tolist()]
        line_plot.add_yaxis('ma5', result_format,linestyle_opts=opts.LineStyleOpts(width=3, opacity=0.5),
                           is_smooth=True,
                           is_connect_nones=True,
                           is_symbol_show=True,
                           itemstyle_opts=opts.ItemStyleOpts(color="#0004a1"),
                           label_opts=opts.LabelOpts(is_show=False))
        return line_plot

    
    @classmethod
    def kline(cls, kdata, trade_date_list, name, width='1600px', height = '900px'):
        kline_plot = Kline(init_opts=opts.InitOpts(width=width,height=height))
        kline_plot.add_xaxis(trade_date_list)
        kline_plot.add_yaxis(
                "K线",
                kdata.tolist(),
                itemstyle_opts=opts.ItemStyleOpts(color="#ec0000", color0="#00da3c"),
                markline_opts=opts.MarkLineOpts(
                    data=[opts.MarkLineItem(type_="max", value_dim="close")],
                ),
            )
        kline_plot.set_global_opts(
            xaxis_opts=opts.AxisOpts(is_scale=True,
                                axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                                axistick_opts=opts.AxisTickOpts(is_show=False),
                                splitline_opts=opts.SplitLineOpts(is_show=False),
                                axislabel_opts=opts.LabelOpts(is_show=False)),
            yaxis_opts=opts.AxisOpts(
                    is_scale=True,
                    splitarea_opts=opts.SplitAreaOpts(
                        is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                    ),
                ),
                brush_opts=opts.BrushOpts(
                    x_axis_index="all",
                    brush_link="all",
                    out_of_brush={"colorAlpha": 0.1},
                    brush_type="lineX",
                ),
                tooltip_opts=opts.TooltipOpts(
                    trigger="axis",
                    axis_pointer_type="cross",
                    background_color="rgba(245, 245, 245, 0.8)",
                    border_width=1,
                    border_color="#ccc",
                    textstyle_opts=opts.TextStyleOpts(color="#000"),
                ),
                axispointer_opts=opts.AxisPointerOpts(
                    is_show=True,
                    link=[{"xAxisIndex": "all"}],
                    label=opts.LabelOpts(background_color="#777"),
                ),
                visualmap_opts=opts.VisualMapOpts(
                    is_show=False,
                    dimension=2,
                    series_index=[6],
                    is_piecewise=True,
                    pieces=[
                        {"value": 1, "color": "#ec0000"},
                        {"value": -1, "color": "#00da3c"},
                    ],
                ),
                datazoom_opts=[
                    opts.DataZoomOpts(
                        is_show=False,
                        type_="inside",
                        xaxis_index=[0, 1],
                        range_start=0,
                        range_end=100,
                    ),
                    opts.DataZoomOpts(
                        is_show=True,
                        xaxis_index=[0, 1],
                        type_="slider",
                        pos_top="90%",
                        range_start=0,
                        range_end=100,
                    ),
                ],
                title_opts=opts.TitleOpts(title=name + '-行情图'),
            )
        
        return kline_plot
    
    @classmethod
    def indicators(cls, indicators, name, width='1200px', height = '900px'):
        trade_date_list = [d.date() for d in indicators.index.tolist()]
        kline_plot = cls.kline(indicators[['open_price','close_price','lowest_price','highest_price']].values,
                          trade_date_list, name)
        
        maline_plot = cls.ma_line(indicators[['ma5','ma10','ma20','ma40','ma60']],
                             trade_date_list)
        kline_plot.overlap(maline_plot)
        
        vol_plot = cls.vol_bar(indicators[['turnover_vol','open_price','close_price']], 
            trade_date_list)
        
        mavol_plot = cls.madvol_line(indicators[['ma5_vol']], trade_date_list)
        vol_plot.overlap(mavol_plot)
        
        grid = Grid()
        grid.add(kline_plot,
                grid_opts=opts.GridOpts(
                     pos_left="5%", pos_right="4%", height="55%"
                 ))
    
        grid.add(
            vol_plot,
            grid_opts=opts.GridOpts(
                pos_left="5%", pos_right="4%", pos_top="70%", height="15%"
            ))
        
        return grid