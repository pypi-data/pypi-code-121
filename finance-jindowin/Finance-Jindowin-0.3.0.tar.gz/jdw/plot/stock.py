from pyecharts import options as opts
from pyecharts.charts import WordCloud
from pyecharts.globals import SymbolType

def selstock(stock, basic, width='1200px', height = '600px'):
    stock = stock.sort_values(by='weight', ascending=False)[0:10]
    stock['weight'] = stock['weight'].round(4)
    stock_data = stock[['name','weight']].to_dict(orient='split')['data']
    return wc_stock(stock_data, basic.loc[0]['name'], '精选股票前10')

def sentistock(stock, basic, width='1200px', height = '600px'):
    stock = stock.sort_values(by='sentiments', ascending=False)[0:10]
    stock['sentiments'] = stock['sentiments'].round(4)
    stock_data = stock[['name','sentiments']].to_dict(orient='split')['data']
    return wc_stock(stock_data, basic.loc[0]['name'], '热度股票前10')
    

def wc_stock(stock_data, block_name, col_name):
    wc_plot = WordCloud()
    wc_plot.add("",stock_data, word_size_range=[20,35],
        shape=SymbolType.DIAMOND,
        textstyle_opts=opts.TextStyleOpts(font_family="cursive")).render_notebook()
    wc_plot.set_global_opts(
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
            ),title_opts=opts.TitleOpts(title= block_name + '-' + col_name)
    )
    return wc_plot
    