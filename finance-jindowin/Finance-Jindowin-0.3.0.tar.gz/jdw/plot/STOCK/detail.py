import pdb
import pandas as pd
from pyecharts.charts import Page
from prettytable import PrettyTable
from pyecharts.charts import TreeMap
from pyecharts.components import Table
from pyecharts.charts import Tab
from pyecharts.options import ComponentTitleOpts
from pyecharts import options as opts
from pyecharts.types import Optional, Sequence

from .sentiment import Sentiment as plot_stock_sentiment
from .flow_money import FlowMoney as plot_stock_flow_money
from .hkshshz import HkShSz as plot_stock_hkshsz

import html

class ThemeTable(Table):
    def add(self, headers: Sequence, rows:Sequence, attributes: Optional[dict]=None):
        attributes = {"style":"font-size: 13px;"}
        table = PrettyTable(headers, attributes=attributes)
        for r in rows:
            table.add_row(r)
        table.align["驱动事件"] = 'l'
        table.align["主题概念"] = 'l'
        self.html_content = html.unescape(table.get_html_string(format=True))
        return self
    

class Detail(object):
    @classmethod
    def draw(cls, name, sentiment_data, flowmoeny_data, hkshsz_data, theme_data):
        page = Page(layout=Page.DraggablePageLayout)
        page.add(
            cls.theme_table(theme_data, name),
            plot_stock_sentiment.sentiment(sentiment_data, name,'1200px', '900px'),
            plot_stock_flow_money.flow_money(flowmoeny_data, name,'1200px', '900px'),
            plot_stock_hkshsz.hkshsz(hkshsz_data, name,'1200px', '900px'),
        )
        return page
    
    @classmethod
    def theme_table(cls, data, name):
        table = ThemeTable()
        columns = ['tid','name','event','update_time']
        if not data.empty:
            data = data[columns]
            data['update_time'] = data['update_time'].dt.strftime('%Y-%m-%d')
            data['event'] = data['event'].apply(lambda x: x[:28] + '......' if len(x) > 28 else x)
            data['name'] = "<a href='./detail/" + data['tid'] + ".html'>" + data['name'] + "</a>"
            data = data.sort_values(by='update_time', ascending=False).drop(['tid'],axis=1).rename(
                columns={'name':'主题概念','update_time':'更新时间','event':'驱动事件'}).head(20)
        headers = data.columns.tolist()
        rows = data.values.tolist()
        table.add(headers, rows)
        table.set_global_opts(
            title_opts=opts.ComponentTitleOpts(title= name + " 关联主题概念")
            
        )
        return table