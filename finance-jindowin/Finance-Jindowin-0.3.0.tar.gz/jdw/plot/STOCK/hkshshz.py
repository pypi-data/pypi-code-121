from pyecharts.charts import Line
from pyecharts.charts import Bar
from pyecharts import options as opts
from pyecharts.charts import Grid
from pyecharts.charts import Line
from pyecharts.charts import Bar
from pyecharts import options as opts
import pandas as pd
import pdb

class HkShSz(object):
    @classmethod
    def hkshsz(cls, hkshsz_data, name, width='1600px', height = '600px'):
        trade_date_list = [d.date() for d in hkshsz_data.index.tolist()]
        bar_plot = cls.hkshsz_bar(hkshsz_data[['shhkneg']], trade_date_list, name)
        line_plot = cls.hkshsz_line(hkshsz_data[['shhk_money_flowin']], trade_date_list, name)
        grid = Grid()
        grid.add(bar_plot,
                grid_opts=opts.GridOpts(
                     pos_left="5%", pos_right="4%", height="45%"
                 ))
    
        grid.add(
            line_plot,
            grid_opts=opts.GridOpts(
                pos_left="5%", pos_right="4%", pos_top="55%", height="40%"
            ))
        
        return grid
    
    @classmethod
    def hkshsz_line(cls, shhk_money_data, trade_date_list, name):
        line_plot = Line()
        line_plot.add_xaxis(trade_date_list)
        result_format = [result  for result in shhk_money_data['shhk_money_flowin'].values.tolist()]
        line_plot.add_yaxis('净资金流入',
                            result_format,
                            linestyle_opts=opts.LineStyleOpts(
                                width=3, opacity=0.5),
                           is_smooth=True,
                           is_connect_nones=True,
                           is_symbol_show=False,
                           itemstyle_opts=opts.ItemStyleOpts(color="#0004a1"),
                           label_opts=opts.LabelOpts(is_show=False))
        line_plot.set_global_opts(
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
                ),legend_opts=opts.LegendOpts(pos_right="30%", pos_top="0%")
            )
            
        return line_plot
    

    @classmethod
    def hkshsz_bar(cls, vol_data, trade_date_list, name):
        bar_plot = Bar()
        vol_data['shhkneg'] = (vol_data['shhkneg'] * 100).round(2)
        vol_drop = [[x, vol_data.shhkneg[x], -1 if vol_data.shhkneg[x] <= 0 \
                        else 1]  for x in range(0, len(vol_data.index))]
        bar_plot.add_xaxis(trade_date_list)
        bar_plot.add_yaxis('流通市值占比(%)', vol_drop, 
                           label_opts=opts.LabelOpts(is_show=False))
        bar_plot.set_global_opts(
            yaxis_opts=opts.AxisOpts(
                    is_scale=True,
                    splitarea_opts=opts.SplitAreaOpts(
                        is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                    ),
                ))
        bar_plot.set_global_opts(
            xaxis_opts=opts.AxisOpts(is_scale=True,
                                axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                                axistick_opts=opts.AxisTickOpts(is_show=False),
                                splitline_opts=opts.SplitLineOpts(is_show=False),
                                axislabel_opts=opts.LabelOpts(is_show=False)),
            yaxis_opts=opts.AxisOpts(
                    is_scale=True,
                    axislabel_opts=opts.LabelOpts(formatter="{value}%"),
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
                    series_index=[0],
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
            title_opts=opts.TitleOpts(title= name + '-北上资金'))
        return bar_plot