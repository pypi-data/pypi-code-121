# Import pybit and define the HTTP object.
from pybit import HTTP  # supports inverse perp & futures, usdt perp, spot.
from pybit import usdc_options  # <-- import HTTP & WSS for inverse perp
from pybit import spot  # <-- import HTTP & WSS for spot
from pybit import inverse_futures, usdt_perpetual, account_asset
from time import sleep


api_key = "oo41mOmCWs4FLbt5o8"
api_secret = "szj59aOiHAqMljDKyy14TEt4tdyfzGcG5fCL"

# WITHDRAW KEY
api_key = "kef3uac2epEaUQs384"
api_secret = "6CFJiNdDDIqe7nM1wvEnp2jKwACDKsH6kqiz"

## Authenticated
session = account_asset.HTTP(
    endpoint="https://api.bybit.com",
    api_key=api_key,
    api_secret=api_secret
)
from time import time

#print(session.query_supported_deposit_list())
#print(session.query_deposit_records())
#print(session.query_withdraw_records())
#print(session.query_coin_info())
#print(session.query_asset_info())
#print(session.query_deposit_address(coin="BTC"))

r = session.withdraw(coin="BTC", chain="BTC",
                     address="1W2gk6R5A6eAfdY2in2dMQDfSgpaX3gpH",
                     amount="0.001")
withdrawal_id = r["result"]["id"]
print(r)

sleep(1)
print(session.cancel_withdrawal(id=withdrawal_id))
exit()


# We can fetch our wallet balance using an auth'd session.
session_auth.get_wallet_balance(coin="BTC")


"""
Spot & other APIs.
from pybit import HTTP  <-- supports inverse perp & futures, usdt perp, spot.
from pybit.spot import HTTP   <-- exclusively supports spot.
"""

# Reassign session_auth to exclusively use spot.
session_auth = spot.HTTP(
    endpoint="https://api.bybit.com",
    api_key="...",
    api_secret="..."
)


# Prefer spot endpoint via the `spot` arg
session_unauth = HTTP(endpoint="https://api.bybit.com", spot=True)

# Require spot endpoint (`spot` arg unnecessary)
session_auth.get_wallet_balance(coin="BTC")
