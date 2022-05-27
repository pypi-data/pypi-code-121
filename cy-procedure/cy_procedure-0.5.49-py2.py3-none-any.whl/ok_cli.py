import sys
import click as c
from multiprocessing import Pool
from cy_widgets.exchange.provider import *
from cy_components.helpers.formatter import *
from cy_data_access.models.config import *
from .subject.exchange.okex import *


@c.group()
@c.option('--db-user', envvar='DB_CLI_USER', required=True)
@c.option('--db-pwd', envvar='DB_CLI_PWD', required=True)
@c.option('--db-host', default='127.0.0.1:27017', required=True)
@c.pass_context
def cyok(ctx, db_user, db_pwd, db_host):
    ctx.ensure_object(dict)
    ctx.obj['db_u'] = db_user
    ctx.obj['db_p'] = db_pwd
    ctx.obj['db_h'] = db_host


def get_rates(instr_id, ok_handler):
    try:
        info = ok_handler.fetch_swap_instrument_fund_rate(instr_id)
        return "{}: \t上次: {}% \t下次: {}%".format(
            instr_id,
            round(float(info['funding_rate']) * 100, 2),
            round(float(info['estimated_rate']) * 100, 2),
        )
    except Exception as e:
        return "{} Failed".format(instr_id)


@cyok.command()
@c.pass_context
def instruments_fund_rates(cxt):
    """资金费率"""
    # ccxt
    provider = CCXTProvider("", "", ExchangeType.Okex)
    ok_handler = OKExHandler(provider)
    all_instruments = ok_handler.fetch_all_swap_instruments()
    filtered = filter(lambda x: "USD" in x['instrument_id'] and "USDT" not in x['instrument_id'], all_instruments)
    mapped = map(lambda x: x['instrument_id'], filtered)

    pool = Pool(20)
    result = []
    for instr_id in mapped:
        result.append(pool.apply_async(get_rates, args=(instr_id, ok_handler,)))
    pool.close()
    pool.join()
    strings = list(sorted([x.get() for x in result]))
    for s in strings:
        print(s)


@cyok.command()
@c.option('-f', required=False)
@c.pass_context
def delivery_instruments(cxt, f):
    provider = CCXTProvider("", "", ExchangeType.Okex)
    ok_handler = OKExHandler(provider)
    all_instruments = ok_handler.fetch_all_delivery_instruments()
    for info in all_instruments:
        if f is None or f.upper() in info['instrument_id']:
            print("{}\t{}\t\t{}".format(info['instrument_id'], info.get('alias', 'forever'), info['contract_val']))
