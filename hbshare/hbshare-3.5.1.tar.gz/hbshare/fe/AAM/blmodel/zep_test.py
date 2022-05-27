from hbshare.fe.XZ import project
from hbshare.fe.XZ import functionality
import pandas as pd


projectC = project.Projects()
plot = functionality.Plot(fig_width=400, fig_height=600)

index_list = ['HSI001', '881001', 'W00083', 'ND100']
bond_list =['003328', '003847', '700006', '004706', '160618', '003474']
assets_lists = index_list + bond_list
risk_aversion_edited=0.6201726167388938
selected_date='20220430'
selected_v='20220430_v1'
selected_date2=selected_date
selected_v2=selected_v
confidence=0.05
confidence2=confidence

ub=[0.15, 0.8, 0.15, 0.5]
ub2=[0.2, 0.2, 0.2, 0.2, 0.2, 0.2]
lb=[-0.05, -0.4, -0.05, -0.05]
lb2=[-0.1, -0.1, -0.1, -0.1, -0.1, -0.1]


columns = ['股票权重', '债券权重', '风险厌恶'] + assets_lists

draw_df = pd.DataFrame()

n = 1
while n < 21:
    Xs = 0.05 * n
    Xb = 1 - Xs
    risk_aversion_new = risk_aversion_edited / Xs + (2 - risk_aversion_edited)

    w_s = projectC.bl_model(end_date=selected_date,
                            asset_list=index_list,
                            version=selected_v, tau=confidence, ub=ub, lb=lb, asset_type='index',
                            risk_aversion=risk_aversion_new)
    w_s['Weight'] = w_s['Weight'] * Xs
    w_s['Weight'] = ['{:.2%}'.format(x) for x in w_s['Weight']]

    w_b = projectC.bl_model(end_date=selected_date2,
                            asset_list=bond_list,
                            version=selected_v2, tau=confidence2, ub=ub2, lb=lb2, asset_type='public_fund',
                            risk_aversion=risk_aversion_new)

    w_b['Weight'] = w_b['Weight'] * Xb
    w_b['Weight'] = ['{:.2%}'.format(x) for x in w_b['Weight']]

    Xs = '{:.2%}'.format(Xs)
    Xb = '{:.2%}'.format(Xb)
    risk_aversion_new = '{:.4f}'.format(risk_aversion_new)
    tempdf = pd.DataFrame()
    tempdf['Asset'] = ['stock_weight', 'bond_weight', 'risk_aversion']
    tempdf['Weight'] = [Xs, Xb, risk_aversion_new]

    inputdf = pd.concat([tempdf, w_s, w_b], axis=0)
    inputdf = inputdf['Weight'].to_frame().T
    draw_df = pd.concat([draw_df, inputdf], axis=0)

    n += 1

draw_df.columns=columns
draw_df.to_csv('blresult_{}.csv'.format(selected_date),encoding='gbk')