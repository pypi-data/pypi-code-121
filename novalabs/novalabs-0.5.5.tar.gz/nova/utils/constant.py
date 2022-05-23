EXCEPTION_LIST_BINANCE = [
    'BTCSTUSDT', 'BTCDOMUSDT', '1000XECUSDT', 'ETHUSDT_220325',
    '1000BTTCUSDT', '1000SHIBUSDT', 'DEFIUSDT', 'BTCUSDT_220325',
    'API3USDT', 'ANCUSDT', 'IMXUSDT', 'FLOWUSDT'
]

VAR_NEEDED_FOR_POSITION = [
    'all_entry_time', 'all_entry_point', 'all_entry_price',
    'all_exit_time', 'all_exit_point', 'all_tp', 'all_sl'
]

DEFINITION_STATISTIC = {
    'per_position_per_pair' : {
        'nb_minutes_in_position': '',
        'tx_fees_paid': '',
        'PL_amt_realized': '',
        'PL_prc_realized': '',
        'next_entry_time': '',
        'minutes_bf_next_position': ''
    },
    'per_pair_agg': {
        'total_position': '',
        'avg_minutes_in_position':'',
        'total_profit_amt': '',
        'total_profit_prc': '',
        'total_tx_fees': '',
        'avg_minutes_before_next_position': '',
        'max_minutes_without_position': '',
        'min_minutes_without_position': '',
        'perc_winning_trade': '',
        'avg_profit': '',
        'nb_{pos}_position': '',
        'nb_tp_{pos}': '',
        'nb_sl_{pos}': '',
        'nb_exit_{pos}': '',
        'nb_ew_{pos}': '',
        '{pos}_profit_amt': '',
        '{pos}_profit_prc': '',
        'avg_minutes_in_{pos}': '',
        'nb_{ext}': '',
        'avg_minutes_before_{ext}': '',
    },
    'per_pair_time': {
        'all_positions': '',
        'total_profit_bot': '',
        'long_profit_bot': '',
        'short_profit_bot': '',
        'in_position_{pair}': '',
        'total_profit_{pair}': '',
        'long_profit_{pair}': '',
        'short_profit_{pair}': '',
    },
    'global_bot_statistics': {
        'average_profit': '',
        'max_nb_pos': '',
        'perc_winning_trade': ''
    }
}

POSITION_PROD_COLUMNS = [
    'id', 'pair', 'status', 'quantity', 'type', 'side', 'tp_id', 'tp_side',
    'tp_type', 'tp_stopPrice', 'sl_id', 'sl_side', 'sl_type', 'sl_stopPrice',
    'nova_id', 'time_entry'
]


BINANCE_KLINES_COLUMNS = [
    'open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
    'quote_asset_volume', 'nb_of_trades', 'taker_base_volume',
    'taker_quote_volume', 'ignore'
]
