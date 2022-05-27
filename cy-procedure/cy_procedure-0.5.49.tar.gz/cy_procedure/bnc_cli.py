"""Console script for cy_procedure."""
import sys
import click as c
from cy_widgets.exchange.provider import *
from cy_components.helpers.formatter import *
from cy_data_access.models.config import *
from .subject.exchange.binance import *


@c.group()
@c.option('--db-user', envvar='DB_CLI_USER', required=True)
@c.option('--db-pwd', envvar='DB_CLI_PWD', required=True)
@c.option('--db-host', default='127.0.0.1:27017', required=True)
@c.pass_context
def cybnc(ctx, db_user, db_pwd, db_host):
    ctx.ensure_object(dict)
    ctx.obj['db_u'] = db_user
    ctx.obj['db_p'] = db_pwd
    ctx.obj['db_h'] = db_host


@cybnc.command()
@c.option('--begin', type=str, prompt="Begin date (e.g. 20201122)", default='20210917', required=True)
@c.option('--end', type=str, prompt="End date (e.g. 20201122)", default='20301022', required=False)
@c.option('--asset', type=str, prompt=True, required=True, default='USDT')
@c.pass_context
def interests(cxt, begin, end, asset):
    connect_db_env(db_name=DB_CONFIG)
    # ccxt
    ccxt_config = CCXTConfiguration.configuration_with_id(13)
    if ccxt_config is None:
        print("ccxt configuration not founded.")
        return
    provider = CCXTProvider(ccxt_config.app_key, ccxt_config.app_secret, ExchangeType.Binance)
    binance_handler = BinanceHandler(provider)
    end_timestamp = DateFormatter.convert_string_to_timestamp(
        end, '%Y%m%d') if end is not None else datetime.now().timestamp()
    interests = binance_handler.lending_interest_history(
        DateFormatter.convert_string_to_timestamp(begin, '%Y%m%d'), end_timestamp, asset)
    total = 0
    print("利息记录")
    for interest in interests[::-1]:
        daily_interest = float(interest['interest'])
        total += daily_interest
        print(DateFormatter.convert_timestamp_to_string(int(interest['time']), "%Y%m%d"), daily_interest)
    print("Total:", total)


@cybnc.command()
@c.pass_context
def instruments_fund_rates(cxt):
    # ccxt
    connect_db_env(db_name=DB_CONFIG)
    ccxt_config = CCXTConfiguration.configuration_with(CCXTExchangeType.Binance)
    if ccxt_config is None:
        print("ccxt configuration not founded.")
        return
    provider = CCXTProvider(ccxt_config.app_key, ccxt_config.app_secret, ExchangeType.Binance)
    binance_handler = BinanceHandler(provider)
    all_premiums = binance_handler.all_premium()
    filtered = list(filter(lambda x: len(x['lastFundingRate']) > 0 and float(x['lastFundingRate']) > 0, all_premiums))
    sorted_list = sorted(filtered, key=lambda x: x['symbol'])
    for info in sorted_list:
        print("{}: 最新费率: {}% 下次: {}".format(
            info['symbol'],
            round(float(info['lastFundingRate']) * 100, 2),
            DateFormatter.convert_timestamp_to_string(info['nextFundingTime'], "%H:%M:%S"),
            DateFormatter.convert_timestamp_to_string(info['time'], "%H:%M:%S")
        ))


@cybnc.command()
@c.pass_context
def u_future_position(cxt):
    # ccxt
    connect_db_env(db_name=DB_CONFIG)
    ccxt_config = CCXTConfiguration.configuration_with_id(16)
    if ccxt_config is None:
        print("ccxt configuration not founded.")
        return
    provider = CCXTProvider(ccxt_config.app_key, ccxt_config.app_secret, ExchangeType.Binance)

    account = provider.ccxt_object_for_query.fapiPrivateV2_get_account()
    balance_df = pd.DataFrame()
    balance_df.loc[0, 'totalWalletBalance'] = float(account['totalWalletBalance'])
    balance_df.loc[0, 'totalUnrealizedProfit'] = float(account['totalUnrealizedProfit'])
    balance_df.loc[0, 'totalMarginBalance'] = float(account['totalMarginBalance'])
    balance_df['unrealizedPnlPercent'] = balance_df['totalUnrealizedProfit'] / balance_df['totalWalletBalance']
    pos_df = pd.DataFrame(account['positions'])
    # 只保留实际持仓的数据
    pos_df = pos_df[pos_df['entryPrice'].astype(float) > 0]
    pos_df = pos_df[['symbol', 'unrealizedProfit', 'entryPrice', 'positionAmt', 'notional']]
    for col in ['unrealizedProfit', 'entryPrice', 'positionAmt', 'notional']:
        pos_df[col] = pos_df[col].astype(float)

    print('余额信息：\n', balance_df.T)
    print('仓位信息：\n', pos_df)
