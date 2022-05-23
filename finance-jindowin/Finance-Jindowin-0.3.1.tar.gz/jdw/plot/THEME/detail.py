from pyecharts.charts import Page
from pyecharts.charts import TreeMap
from pyecharts.charts import WordCloud
from pyecharts import options as opts
from pyecharts.globals import SymbolType
from prettytable import PrettyTable
from pyecharts.components import Table
from pyecharts.charts import Grid
from pyecharts.types import Optional, Sequence
from .brief import Brief as plot_theme_brief
from .indicators import Indicators as plot_theme_indicators
from .returns import Returns as plot_theme_returns
from .sentiment import Sentiment as plot_theme_sentiment
from .hkshshz import HkShSz as plot_theme_hkshshz
from .flow_money import FlowMoney as plot_theme_flow_money
import html,pdb

class NewsTable(Table):
    def add(self, headers: Sequence, rows:Sequence, attributes: Optional[dict]=None):
        attributes = {"style":"font-size: 13px;"}
        table = PrettyTable(headers, attributes=attributes)
        for r in rows:
            table.add_row(r)
        table.align["链接"] = 'l'
        table.align["标题"] = 'l'
        self.html_content = html.unescape(table.get_html_string(format=True))
        return self
    
class StockTable(Table):
    def add(self, headers: Sequence, rows:Sequence, attributes: Optional[dict]=None):
        attributes = {"style":"font-size: 13px;"}
        table = PrettyTable(headers, attributes=attributes)
        for r in rows:
            table.add_row(r)
        table.align["昨收盘"] = 'l'
        self.html_content = html.unescape(table.get_html_string(format=True))
        return self
    
class Detail(object):
    @classmethod
    def draw(cls, name, event, indicators, returns, sentiment, flowmoney, hkshsz,
             selstock, sentistock, news, members):
        page = Page(layout=Page.DraggablePageLayout)
        page.add(
            cls.news_table(news, name, event),
            plot_theme_indicators.indicators(indicators, name, '1200px', '900px'),
            plot_theme_sentiment.sentiment(sentiment, name, '1200px', '900px'),
            plot_theme_returns.returns(returns, name, '1200px', '900px'),
            plot_theme_flow_money.flow_moeny(flowmoney, name, '1200px', '900px'),
            plot_theme_hkshshz.hkshsz(hkshsz, indicators, name, '1200px', '900px'),
            cls.selstock(selstock,name,'weight', 5),
            cls.selstock(sentistock,name,'sentiments', 10),
            cls.members_table(members,name),
        )
        return page
    
    @classmethod
    def members_table(cls, data, name):
        table = StockTable()
        columns = ['code','name','close']
        if not data.empty:
            data = data[columns]
            data['name'] = "<a href='../stock/" + data['code'] + ".html'>" + data['name'] + "</a>"
            data['code'] = "<a href='../stock/" + data['code'] + ".html'>" + data['code'] + "</a>"
            data = data.rename(
                columns={'code':'股票代码','name':'股票名称','close':'收盘价'})
        headers = data.columns.tolist()
        rows = data.values.tolist()
        table.add(headers, rows)
        table.set_global_opts(
            title_opts=opts.ComponentTitleOpts(title= name + " 成分股",subtitle='点击股票代码查看详情')
            
        )
        return table
        
        
    @classmethod
    def news_table(cls, data, name, event):
        table = NewsTable()
        columns = ['title','publish_time','url']
        if not data.empty:
            data = data[columns]
            data['publish_time'] = data['publish_time'].dt.strftime('%Y-%m-%d')
            data['url'] = "<a href=\"" + data['url'] + "\"" + ">" +  '详情' + "</a>"
            data = data.sort_values(by='publish_time', ascending=False).rename(
                columns={'title':'标题','publish_time':'发布时间','url':''}).head(20)
        headers = data.columns.tolist()
        rows = data.values.tolist()
        table.add(headers, rows)
        table.set_global_opts(
            title_opts=opts.ComponentTitleOpts(title= name + " 相关新闻",subtitle=event)
            
        )
        return table
        
        
    @classmethod
    def stock_show(cls, selstock, sentistock, name):
        sel = cls.selstock(selstock,name,'weight', 5)
        senti = cls.selstock(sentistock,name,'sentiments', 10)
        grid = Grid()
        grid.add(sel, grid_opts=opts.GridOpts(pos_left="55%"))
        grid.add(senti, grid_opts=opts.GridOpts(pos_right="55%"))
        return grid
        
    @classmethod
    def selstock(cls, stock_data, name, col='weight', count=10):
        stock = stock_data.sort_values(by=col, ascending=False)[0:count]
        stock[col] = stock[col].round(4)
        stock['title'] = stock['name'] + '(' + stock['code'] + ')'
        stock_data = stock[['title',col]].rename(columns={
            'title':'name',col:'value'}).to_dict(orient='record')
        col_name = '精选股票' if col == 'weight' else '热门股票'
        return cls.treemap_stock(stock_data, col_name)
        '''
        stock_data = stock[['name',col]].to_dict(orient='split')['data']
        col_name = '精选股票前' if col == 'weight' else '热门股票前'
        legend_opts = legend_opts=opts.LegendOpts(pos_left="20%") if col == 'weight' \
            else opts.LegendOpts(pos_right="20%")
        return cls.wc_stock(stock_data, name, col_name + str(count), legend_opts)
        '''
    @classmethod
    def treemap_stock(cls, data, col_name, width='800px', height='800px'):
        tree_map = TreeMap(init_opts=opts.InitOpts(width=width,height=height))
        tree_map.add("", data, visual_min=300,leaf_depth=1,
            label_opts=opts.LabelOpts(position="inside"))
        tree_map.set_global_opts(title_opts=opts.TitleOpts(title= col_name))
        return tree_map
        
    @classmethod
    def wc_stock(cls, stock_data, name, col_name, legend_opts):
        wc_plot = WordCloud(init_opts=opts.InitOpts(width='800px',height='400px'))
        wc_plot.add("",stock_data, word_size_range=[20,35],
            shape=SymbolType.DIAMOND,
            textstyle_opts=opts.TextStyleOpts(font_family="cursive"))
        wc_plot.set_global_opts(
            legend_opts=legend_opts,
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
            title_opts=opts.TitleOpts(title= name + '-' + col_name)
        )
        return wc_plot