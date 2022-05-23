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
import html
    
class BriefTable(Table):
    def add(self, headers: Sequence, rows:Sequence, attributes: Optional[dict]=None):
        attributes = {"style":"font-size: 13px;"}
        table = PrettyTable(headers, attributes=attributes)
        for r in rows:
            table.add_row(r)
        table.align["驱动事件"] = 'l'
        table.align["主题概念"] = 'l'
        table.align["成交量"] = 'r'
        table.align["净资金流入"] = 'r'
        table.align["净买入额"] = 'r'
        self.html_content = html.unescape(table.get_html_string(format=True))
        return self
    
class Brief(object):
    @classmethod
    def brief_tab(cls, data, width='1400px', height='800px', trade_date = None):
        tab = Tab()
        vol_rate_pot = cls.brief_table(data=data, subtitle='根据北上资金净买入额每天变化率排序,变化率越高排名越靠前', 
                                       sort_name='vol_rate',width=width,height=height)
        flowmoney_pot = cls.brief_table(data=data, subtitle='根据净资金流入排序,净资金流入越高排名越靠前',
                                        sort_name='flow_money',width=width,height=height)
        sentiment_pot = cls.brief_table(data, subtitle='根据净资金流入排序,净资金流入越高排名越靠前',
                                        sort_name='sentiment',width=width,height=height)
        returns_pot = cls.brief_table(data, subtitle='根据构建组合收益率进行排序,收益率越高排名越靠前',
                                      sort_name='returns',width=width,height=height)
        updatetime_pot = cls.brief_table(data, subtitle='根据驱动事件爆发的时间进行排序,时间越靠近排名越靠前',
                                      sort_name='update_time',width=width,height=height)
        
        tab.add(updatetime_pot, '按爆发时间排序')
        tab.add(sentiment_pot, '按情绪排序')
        tab.add(returns_pot, '按收益排序')
        tab.add(flowmoney_pot, '按净资产流入排序')
        tab.add(vol_rate_pot, '按净买入排序')
        return tab
        
    @classmethod
    def brief_table(cls, data, subtitle=None, sort_name='sentiment', is_full=False, 
                    width='1400px', height='800px', trade_date=None):
        table = BriefTable()
        data = pd.DataFrame(data)
        data['returns'] = (data['returns'] * 100).round(2).astype(str) + '%'
        data['shhk_value'] = data['close']* data['party_vol']
        data['flow_money'] = data['flow_money'].round(2)
        data['vol_rate'] = (data['vol_rate'] * 100).round(2)
        
        ##排序
        data = data.sort_values(by=sort_name, ascending=False)
        if not is_full:
            if trade_date is not None:
                data['trade_date'] = trade_date
            data['vol_rate'] = data['vol_rate'].astype(str) + '%'
            data['event'] = data['event'].apply(lambda x: x[:28] + '......' if len(x) > 28 else x)
            data['title'] = "<a href='./detail/" + data['tid'] + ".html'>" + data['title'] + "</a>"
            
        columns = ['title','returns','sentiment', 'close',
                   'vol','flow_money','vol_rate',
                   'update_time','event'] if not is_full else ['title','returns',
                   'sentiment', 'close','vol','flow_money','vol_rate',
                   'update_time','event','tid']
        if trade_date is not None:
            columns.append('trade_date')
        data = data[columns].rename(
            columns={'trade_date':'交易日','title':'主题概念','event':'驱动事件',
                    'returns':'收益','sentiment':'情绪','close':'收盘价','flow_money':'净资金流入',
                     'vol_rate':'净买入(北上)','vol':'成交量','update_time':'爆发时间',
                     'tid':'编号','trade_date':'更新日期'})
        subtitle = "点击名称查看详情" if subtitle is None else subtitle
        headers = data.columns.tolist()
        rows = data.values.tolist()
        table.add(headers, rows)
        table.set_global_opts(
            title_opts=opts.ComponentTitleOpts(title="主题概念摘要",subtitle=subtitle)
            
        )
        return table
    
    @classmethod
    def brief_treemap(cls, data, col='returns', width='1400px', height = '800px'):
        data = pd.DataFrame(data)[['title',col]].rename(
            columns={'title':'name',col:'value'}).to_dict(orient='record')
        tree_map = TreeMap(init_opts=opts.InitOpts(width=width,height=height))
        tree_map.add("", data, visual_min=300,leaf_depth=1,
            label_opts=opts.LabelOpts(position="inside"))
        col_name = '收益' if col == 'returns' else '情绪'
        tree_map.set_global_opts(title_opts=opts.TitleOpts(title= col_name + "热力图"))
        return tree_map
    
    @classmethod
    def tab_brief(cls, data_sets, width='1200px', height = '700px'):
        tab = Tab()
        for k, v in data_sets.items():
            tab.add(cls.brief(v,width,height),k)
        return tab
    