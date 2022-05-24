from plotly.subplots import make_subplots
import plotly.graph_objs as go


def generate_overview(slippage_df = None, error_message = None):
    if slippage_df is None:
        fig = make_subplots(rows=1, cols=1)
        if error_message is not None:
            fig.update_layout(height=600, width=1600, title_text=error_message)
        else:
            fig.update_layout(height=600, width=1600, title_text="graph cannot be completed")
        return fig
    else:

        slippage_df['total_fees'] = slippage_df['funding_fees_usd_eth']+slippage_df['funding_fees_usd_btc']+slippage_df['trading_fees_usd_eth']+slippage_df['trading_fees_usd_btc']
        fig = make_subplots(rows=3, cols=1)

        fig.append_trace(
            go.Scatter(
                x=slippage_df.index,
                y=slippage_df.wallet_amount_usd,
                name='Valorisation',
                opacity=0.8),
            row=1, col=1)

        fig.append_trace(
            go.Scatter(
                x=slippage_df.index,
                y=slippage_df.pnl,
                name='pnl',
                opacity=0.8),
            row=2, col=1)

        fig.append_trace(
            go.Scatter(
                x=slippage_df.index,
                y=slippage_df.total_fees,
                name='total fees',
                opacity=0.8),
            row=3, col=1)

        fig.update_layout(height=600, width=1600, title_text="slippage overview",showlegend=True)
        #fig.update_xaxes(rangeslider_visible=True)
        return fig

def generate_slippage_repartition(slippage_df = None, error_message = None):
    if slippage_df is None:
        fig = make_subplots(rows=1, cols=1)
        if error_message is not None:
            fig.update_layout(height=600, width=1600, title_text=error_message)
        else:
            fig.update_layout(height=600, width=1600, title_text="graph cannot be completed")
        return fig
    else:
        trace1 = go.Bar(
            x=slippage_df.index,
            y=slippage_df.slippage_eth_cash_cc,
            name='slippage_eth_cash_cc'
        )
        trace2 = go.Bar(
            x=slippage_df.index,
            y=slippage_df.slippage_btc_cash_cc,
            name='slippage_btc_cash_cc'
        )

        fig = go.Figure(data=[trace1, trace2], layout=go.Layout(barmode='stack'))

        fig.update_layout(height=600, width=1600, title_text='slippage', showlegend=True)
        fig.update_xaxes(rangeslider_visible=True)
        return fig



def generate_fees_repartition(slippage_df = None, error_message = None):
    if slippage_df is None:
        fig = make_subplots(rows=1, cols=1)
        if error_message is not None:
            fig.update_layout(height=600, width=1600, title_text=error_message)
        else:
            fig.update_layout(height=600, width=1600, title_text="graph cannot be completed")
        return fig
    else:
        trace1 = go.Bar(
            x=slippage_df.index,
            y=slippage_df.funding_fees_usd_eth,
            name='funding_fees_usd_eth'
        )
        trace2 = go.Bar(
            x=slippage_df.index,
            y=slippage_df.funding_fees_usd_btc,
            name='funding_fees_usd_btc'
        )
        trace3 = go.Bar(
            x=slippage_df.index,
            y=slippage_df.trading_fees_usd_eth,
            name='trading_fees_usd_eth'
        )
        trace4 = go.Bar(
            x=slippage_df.index,
            y=slippage_df.trading_fees_usd_btc,
            name='trading_fees_usd_btc'
        )

        fig = go.Figure(data=[trace1, trace2, trace3, trace4], layout=go.Layout(barmode='stack'))

        fig.update_layout(height=600, width=1600, title_text='fees', showlegend=True)
        fig.update_xaxes(rangeslider_visible=True)

        return fig