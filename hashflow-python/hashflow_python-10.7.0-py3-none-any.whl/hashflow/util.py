import eth_keys
import eth_account
from web3 import Web3
from enum import IntEnum


class Trade(IntEnum):
    
    tokens = 1
    eth_to_token = 2
    token_to_eth = 3


class Flag(IntEnum):
 
    off = 0
    on = 1
    na = 2

class Quote(object):

    def __init__(
        self,
        pool,
        eoa,
        trader,
        effectiveTrader,
        base_token_address,
        quote_token_address,
        base_token_amount,
        quote_token_amount,
        fees,
        expiry,
        flag,
        txid,
        trade_eoa,
        k_value=None,
        nonce=None,
    ):

        self.pool = pool
        self.eoa = eoa
        self.trader = trader
        self.effectiveTrader = effectiveTrader
        self.base_token_address = base_token_address
        self.quote_token_address = quote_token_address
        self.base_token_amount = base_token_amount
        self.quote_token_amount = quote_token_amount
        self.fees = fees
        self.expiry = expiry
        self.flag = flag
        self.txid = txid
        self.trade_eoa = trade_eoa
        self.k_value = k_value
        self.nonce = nonce


def strip_hex_prefix(input):
    if input[0:2] == '0x':
        return input[2:]
    else:
        return input


def normalize_private_key(private_key):
    if type(private_key) == str:
        return bytearray.fromhex(strip_hex_prefix(private_key))
    elif type(private_key) == bytearray:
        return private_key
    else:
        raise TypeError('private_key incorrect type')


def private_key_to_address(key):
    eth_keys_key = eth_keys.keys.PrivateKey(key)
    return eth_keys_key.public_key.to_checksum_address()


def sign_digest(digest, private_key):
    result = eth_account.account.Account.signHash(digest, private_key)
    return result['signature'].hex()
