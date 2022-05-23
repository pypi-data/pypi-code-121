import pdb
from pyecharts.charts import Line
from pyecharts.charts import Bar
from pyecharts import options as opts

from pyecharts.charts import Line
from pyecharts.charts import Bar
from pyecharts import options as opts

class FlowMoney(object):
    @classmethod
    def flow_money(cls, flow_money, name, width='1600px', height = '600px'):
        trade_date_list = [d.date() for d in flow_money.index.tolist()]
        bar_plot = cls.flowmoney_bar(flow_money[['net_flowmoney']], trade_date_list, name)
        line_plot = cls.flowmoney_line(flow_money[['ma5']], trade_date_list)
        bar_plot.overlap(line_plot)
        return bar_plot
    
    @classmethod
    def flowmoney_bar(cls, flowmoney_data, trade_date_list, name):
        bar_plot = Bar()
        flowmoney_drop = [[x, flowmoney_data.net_flowmoney[x], -1 if flowmoney_data.net_flowmoney[x] <= 0 \
                        else 1]  for x in range(0, len(flowmoney_data.index))]
    
        bar_plot.add_xaxis(trade_date_list)
        bar_plot.add_yaxis('净资金流入', flowmoney_drop, 
                           label_opts=opts.LabelOpts(is_show=False))
        bar_plot.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        bar_plot.set_global_opts(
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
                tooltip_opts=opts.TooltipOpts(
                    trigger="axis",
                    axis_pointer_type="cross",
                    background_color="rgba(245, 245, 245, 0.8)",
                    border_width=1,
                    border_color="#ccc",
                    textstyle_opts=opts.TextStyleOpts(color="#000"),
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
            datazoom_opts=opts.DataZoomOpts(is_show=True,
                        type_="slider",
                        pos_top="90%",
                        range_start=0,
                        range_end=100,),
            title_opts=opts.TitleOpts(title= name + '-净资金流入图')
        )
        
        return bar_plot
    
    @classmethod
    def flowmoney_line(cls, flowmoney_data, trade_date_list):
        line_plot = Line()
        line_plot.add_xaxis(trade_date_list)
        result_format = [result  for result in flowmoney_data['ma5'].values.tolist()]
        line_plot.add_yaxis('5日净资金流入均值', result_format,linestyle_opts=opts.LineStyleOpts(width=3, opacity=0.5),
                           is_smooth=True,
                           is_connect_nones=True,
                           is_symbol_show=True,
                           itemstyle_opts=opts.ItemStyleOpts(color="#0004a1"),
                           label_opts=opts.LabelOpts(is_show=False))
        return line_plot