import plotly.express as px
import pandas as pd
import numpy as np

def process_orderbook_metrics(orderbook_df = None, id=False, amounts_to_pass = [100,500,1000,5000,10000,50000,100000], pair='free'):
    if id >= 0:
        df = orderbook_df[(orderbook_df['id'] == id)].copy()
    else:
        raise Exception('No id provided')

    bid_df = df[df.type == 'bid'].copy()
    ask_df = df[df.type == 'ask'].copy()

    bid_df.sort_values('price', ascending=False, inplace=True)
    bid_df['cumulative_quantity'] = bid_df['amount'].cumsum()

    ask_df.sort_values('price', ascending=True, inplace=True)
    ask_df['cumulative_quantity'] = ask_df['amount'].cumsum()

    best_bid_price = bid_df['price'].max()
    best_ask_price = ask_df['price'].min()
    mid_market_price = (ask_df['price'].min() + bid_df['price'].max())/2

    max_sell_quantity = bid_df['cumulative_quantity'].max()
    max_buy_quantity = ask_df['cumulative_quantity'].max()

    bid_df['previous_price']=bid_df['price'].shift()
    bid_df['previous_cumulative_quantity']=bid_df['cumulative_quantity'].shift()

    def compute_change_rate(row):
        price = row['price']
        previous_price = row['previous_price']
        cumulative_quantity = row['cumulative_quantity']
        previous_cumulative_quantity = row['previous_cumulative_quantity']
        if np.isnan(row['cumulative_quantity']):
            return np.nan
        rate_of_change =abs((price -previous_price)/(cumulative_quantity - previous_cumulative_quantity))
        return rate_of_change


    bid_df['rate_of_change'] = bid_df.apply(compute_change_rate, axis = 1)

    ask_df['previous_price']=ask_df['price'].shift()
    ask_df['previous_cumulative_quantity']=ask_df['cumulative_quantity'].shift()
    ask_df['rate_of_change'] = ask_df.apply(compute_change_rate, axis = 1)

    bid_df[['price', 'cumulative_quantity', 'rate_of_change']]
    ask_df[['price', 'cumulative_quantity', 'rate_of_change']]

    results = []
    for amount_to_pass in amounts_to_pass:
        bought_amount = 0.
        bought_costs = 0.
        bought_max_rate_of_change = 0.
        for _, row in ask_df.iterrows():
            current_available_amount = row['amount']
            local_price = row['price']
            local_rate_of_change = row['rate_of_change']
            if not np.isnan(local_rate_of_change) and abs(local_rate_of_change)>bought_max_rate_of_change:
                bought_max_rate_of_change = abs(local_rate_of_change)
            end_reached = False
            if  current_available_amount > (amount_to_pass-bought_amount):
                local_amount = amount_to_pass-bought_amount
                end_reached = True
            else :
                local_amount = current_available_amount
            bought_amount = bought_amount + local_amount
            bought_costs = bought_costs + local_amount*local_price
            if end_reached:
                break
        bought_price = bought_costs / bought_amount
        assert ((bought_amount == amount_to_pass) or (bought_amount == max_buy_quantity))


        sold_amount = 0.
        sold_costs = 0.
        sold_max_rate_of_change = 0.
        for _, row in bid_df.iterrows():
            current_available_amount = row['amount']
            local_price = row['price']
            local_rate_of_change = row['rate_of_change']
            if not np.isnan(local_rate_of_change) and abs(local_rate_of_change)>sold_max_rate_of_change:
                sold_max_rate_of_change = abs(local_rate_of_change)
            end_reached = False
            if  current_available_amount > (amount_to_pass-sold_amount):
                local_amount = amount_to_pass-sold_amount
                end_reached = True
            else :
                local_amount = current_available_amount
            sold_amount = sold_amount + local_amount
            sold_costs = sold_costs + local_amount*local_price
            if end_reached:
                break
        sold_price = sold_costs / sold_amount
        assert ((sold_amount == amount_to_pass) or ( sold_amount == max_sell_quantity))

        buying_slippage = abs((sold_price - best_bid_price)/best_bid_price)
        selling_slippage = abs((bought_price - best_ask_price)/best_ask_price)
        results.append({
                'id':id,
                'pair':pair,
                'amount':amount_to_pass,
                f'sold_max_rate_of_change':-sold_max_rate_of_change,#### we want to get the lowest slope magnitude
                f'bid_max_rate_of_change':-bought_max_rate_of_change,#### we want to get the lowest slope magnitude
                f'buying_slippage' :buying_slippage ,
                f'selling_slippage' : selling_slippage,
                f'bid_ask_spread': (best_ask_price-best_bid_price)/best_bid_price,
        })

    return results

def process_plot_orderbook(orderbook_df = None, id=False, amount_to_pass =5000, pair='free',title = ''):
    if id >= 0:
        df = orderbook_df[(orderbook_df['id'] == id)].copy()
    else:
        raise Exception('No id provided')

    bid_df = df[df.type == 'bid'].copy()
    ask_df = df[df.type == 'ask'].copy()

    bid_df.sort_values('price', ascending=False, inplace=True)
    bid_df['cumulative_quantity'] = bid_df['amount'].cumsum()
    bid_df['to_keep'] = bid_df['cumulative_quantity']-amount_to_pass
    bid_df['to_keep'] = bid_df['to_keep']<=0
    bid_df['to_keep'] = bid_df['to_keep'].shift(1, axis=0)
    bid_df['to_keep'] = bid_df['to_keep'].fillna(True)
    bid_pass_df = bid_df[bid_df['to_keep']].copy()

    ask_df.sort_values('price', ascending=True, inplace=True)
    ask_df['cumulative_quantity'] = ask_df['amount'].cumsum()
    ask_df['to_keep'] = ask_df['cumulative_quantity']-amount_to_pass
    ask_df['to_keep'] = ask_df['to_keep']<=0
    ask_df['to_keep'] = ask_df['to_keep'].shift(1, axis=0)
    ask_df['to_keep'] = ask_df['to_keep'].fillna(True)
    ask_pass_df = ask_df[ask_df['to_keep']].copy()
    ask_pass_df['type']='ask'
    bid_pass_df['type']='bid'

    all_data_df = pd.concat([bid_pass_df[['price','cumulative_quantity','type']].copy(),ask_pass_df[['price','cumulative_quantity','type']].copy()])

    all_data_df.sort_values(by=['price'], ascending = True, inplace = True)

    fig = plot_order_book(data_df=all_data_df, title=title)
    return fig


def plot_order_book(data_df=None, title = ''):
    fig = px.line(data_df, x="price", y="cumulative_quantity", color="type",markers=True,title=title)
    return fig

