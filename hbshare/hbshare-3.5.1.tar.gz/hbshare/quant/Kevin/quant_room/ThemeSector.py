"""
股票改概念板块处理
"""
from WindPy import w
import pandas as pd
import hbshare as hbs
import plotly.figure_factory as ff
import plotly
from plotly.offline import plot as plot_ly
import plotly.graph_objs as go

plotly.offline.init_notebook_mode(connected=True)

w.start()


# 以20220128为例
date = '20220128'
sql_script = "SELECT SYMBOL, TDATE, VATURNOVER, TCAP FROM finchina.CHDQUOTE WHERE TDATE = {}".format(date)
data = pd.DataFrame(hbs.db_data_query('readonly', sql_script, page_size=5000)['data'])
data = data[data['SYMBOL'].str[0].isin(['0', '3', '6'])]
data = data[data['VATURNOVER'] > 1e-6]
data['sec_code'] = data['SYMBOL'].apply(lambda x: x + '.SH' if x[0] == '6' else x + '.SZ')
ticker_list = data['sec_code'].tolist()
res = w.wss(','.join(ticker_list), 'concept', "tradeDate={}".format(date))
if res.ErrorCode != 0:
    df = pd.DataFrame()
    print("fetch concept data error: trade_date = {}".format(date))
else:
    df = pd.DataFrame(res.Data[0], index=res.Codes, columns=res.Fields)
    df.index.name = 'sec_code'
# 处理
concept_list = []
for sec in df.index.tolist():
    sub_list = df.loc[sec, 'CONCEPT'].split(';')
    concept_list = list(set(concept_list).union(set(sub_list)))

concept_df = pd.DataFrame(index=df.index, columns=concept_list)
for sec in concept_df.index.tolist():
    sub_list = df.loc[sec, 'CONCEPT'].split(';')
    concept_df.loc[sec, sub_list] = 1
# 每个概念的只数和市值统计
concept_df = pd.merge(concept_df, data[['sec_code', 'TCAP']], left_index=True, right_on='sec_code')
count_df = pd.DataFrame(index=concept_df.columns[:-2], columns=['number', 'mkv'])
for col in concept_df.columns[:-2]:
    count_df.loc[col, 'number'] = concept_df[col].value_counts().loc[1]
    count_df.loc[col, 'mkv'] = concept_df.groupby(col)['TCAP'].sum().loc[1] / 1e+8
# 筛选概念
select_df = count_df[(count_df['number'] < 500) & (count_df['number'] > 40) & (count_df['mkv'] > 10000)]
big_concept = ['茅', '先进制造', '顺周期', '资源股', '新能源汽车',
               '新能源', '半导体产业', '光伏', '芯片', '锂电池',
               '白马股', '大消费', '碳中和', '元宇宙', '新基建']
# 计算重合度
sub_df = concept_df[big_concept + ['sec_code', 'TCAP']].dropna(subset=big_concept, how='all')
overlap_df = pd.DataFrame(index=big_concept, columns=big_concept)
for i in range(len(big_concept)):
    for j in range(len(big_concept)):
        if i == j:
            overlap_df.iloc[i, j] = 1.
            continue
        tmp = sub_df[[big_concept[i], big_concept[j], 'sec_code', 'TCAP']]
        tmp['sum'] = tmp[[big_concept[i], big_concept[j]]].sum(axis=1)
        overlap_cap = tmp.groupby('sum')['TCAP'].sum().loc[2.] if 2. in tmp.groupby('sum')['TCAP'].sum().index else 0
        overlap_df.iloc[i, j] = np.round(overlap_cap / tmp[tmp[big_concept[i]] == 1]['TCAP'].sum(), 2)

name_list = ['顺周期', '资源股',
             '半导体产业', '光伏', '锂电池',
             '大消费', '元宇宙', '新基建']
corr_df = overlap_df.loc[name_list, name_list]

fig = ff.create_annotated_heatmap(
    z=corr_df.to_numpy(),
    x=list(corr_df.index.values),
    y=list(corr_df.columns.values),
    xgap=3, ygap=3,
    zmin=-1, zmax=1,
    colorscale='earth',
    colorbar_thickness=30,
    colorbar_ticklen=3,
)
fig.update_layout(title_text='<b>Overlap Matrix (cont. Concept)<b>',
                  title_x=0.5,
                  titlefont={'size': 24},
                  width=800, height=600,
                  xaxis_showgrid=False,
                  xaxis={'side': 'bottom'},
                  yaxis_showgrid=False,
                  yaxis_autorange='reversed',
                  paper_bgcolor=None,
                  )
plot_ly(fig, filename="D:\\123.html", auto_open=False)
# 以因诺为例
from hbshare.quant.Kevin.quant_room.PrivateHoldingAnalysis import HoldingAnalysor
# holding_cl = HoldingAnalysor('因诺聚配中证500指数增强', "20220131", "000905")
holding_cl = HoldingAnalysor('星阔广厦1号中证500指数增强', "20220128", "000905")
portfolio_weight_series = holding_cl.data_param['portfolio_weight_series']
benchmark_weight_series = holding_cl.data_param['benchmark_weight_series']
tmp = concept_df.copy()
tmp['ticker'] = tmp['sec_code'].apply(lambda x: x.split('.')[0])
tmp = tmp.set_index('ticker')[name_list].dropna(how='all', subset=name_list)
weight_df = pd.merge(portfolio_weight_series.to_frame('pf'), benchmark_weight_series.to_frame('bm'),
                     left_index=True, right_index=True, how='outer').fillna(0.)
pf_concept = tmp.merge(weight_df, left_index=True, right_index=True)

contr_df = []
for name in name_list:
    a = pf_concept.groupby(name)[['pf', 'bm']].sum().loc[1]
    a.name = name
    contr_df.append(a)

contr_df = pd.concat(contr_df, axis=1).T