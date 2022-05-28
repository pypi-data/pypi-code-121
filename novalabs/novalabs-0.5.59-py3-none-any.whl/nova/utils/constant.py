EXCEPTION_LIST_BINANCE = [
    'BTCSTUSDT', 'BTCDOMUSDT', '1000XECUSDT', 'ETHUSDT_220325',
    '1000BTTCUSDT', '1000SHIBUSDT', 'DEFIUSDT', 'BTCUSDT_220325',
    'API3USDT', 'ANCUSDT', 'IMXUSDT', 'FLOWUSDT'
]

VAR_NEEDED_FOR_POSITION = [
    'all_entry_time', 'all_entry_point', 'all_entry_price',
    'all_exit_time', 'all_exit_point', 'all_tp', 'all_sl'
]

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

DATA_FORMATING = {
    "binance": {
        "columns": [
            'open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
            'quote_asset_volume', 'nb_of_trades', 'taker_base_volume',
            'taker_quote_volume', 'ignore'
        ],
        "num_var": [
            "open", "high", "low", "close", "volume", "quote_asset_volume",
            "nb_of_trades", "taker_base_volume", "taker_quote_volume"
        ],
        "date_var": [
            "open_time", "close_time"
        ]
    }
}
