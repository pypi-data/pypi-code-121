import json
from .utils import json_col_to_df

import requests
import pandas as pd
# code from https://towardsdatascience.com/decoding-ethereum-smart-contract-data-eed513a65f76

import sys
import traceback
from functools import lru_cache

from web3 import Web3
from web3.auto import w3
from web3._utils.events import get_event_data

from eth_utils import event_abi_to_log_topic, to_hex
from hexbytes import HexBytes
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

# import swifter

# code from https://towardsdatascience.com/decoding-ethereum-smart-contract-data-eed513a65f76


# decode transactions
def decode_tuple(t, target_field):
    output = dict()
    for i in range(len(t)):
        if isinstance(t[i], (bytes, bytearray)):
            output[target_field[i]['name']] = to_hex(t[i])
        elif isinstance(t[i], (tuple)):
            output[target_field[i]['name']] = decode_tuple(t[i], target_field[i]['components'])
        else:
            output[target_field[i]['name']] = t[i]
    return output


def decode_list_tuple(l, target_field):
    output = l
    for i in range(len(l)):
        output[i] = decode_tuple(l[i], target_field)
    return output


def decode_list(l):
    output = l
    for i in range(len(l)):
        if isinstance(l[i], (bytes, bytearray)):
            output[i] = to_hex(l[i])
        else:
            output[i] = l[i]
    return output


def convert_to_hex(arg, target_schema):
    """
    utility function to convert byte codes into human readable and json serializable data structures
    """
    output = dict()
    for k in arg:
        if isinstance(arg[k], (bytes, bytearray)):
            output[k] = to_hex(arg[k])
        elif isinstance(arg[k], (list)) and len(arg[k]) > 0:
            target = [a for a in target_schema if 'name' in a and a['name'] == k][0]
            if target['type'] == 'tuple[]':
                target_field = target['components']
                output[k] = decode_list_tuple(arg[k], target_field)
            else:
                output[k] = decode_list(arg[k])
        elif isinstance(arg[k], (tuple)):
            target_field = [a['components'] for a in target_schema if 'name' in a and a['name'] == k][0]
            output[k] = decode_tuple(arg[k], target_field)
        else:
            output[k] = arg[k]
    return output


@lru_cache(maxsize=None)
def _get_contract(address, abi):
    """
    This helps speed up execution of decoding across a large dataset by caching the contract object
    It assumes that we are decoding a small set, on the order of thousands, of target smart contracts
    """
    if isinstance(abi, (str)):
        abi = json.loads(abi)

    contract = w3.eth.contract(address=Web3.toChecksumAddress(address), abi=abi)
    return (contract, abi)


def decode_tx(address, input_data, abi):
    if abi is not None:
        try:
            (contract, abi) = _get_contract(address, abi)
            func_obj, func_params = contract.decode_function_input(input_data)
            target_schema = [a['inputs'] for a in abi if 'name' in a and a['name'] == func_obj.fn_name][0]
            decoded_func_params = convert_to_hex(func_params, target_schema)
            return {"fn_name": func_obj.fn_name, **decoded_func_params}
        except Exception as e:
            e = sys.exc_info()[0]
            print(f'decode error: {repr(e)}')
            return {"fn_name": "decode error"}
    else:
        return {"fn_namename": 'no matching abi'}


# decode event log
@lru_cache(maxsize=None)
def _get_topic2abi(abi):
    if isinstance(abi, (str)):
        abi = json.loads(abi)

    event_abi = [a for a in abi if a['type'] == 'event']
    topic2abi = {event_abi_to_log_topic(_): _ for _ in event_abi}
    return topic2abi


@lru_cache(maxsize=None)
def _get_hex_topic(t):
    hex_t = HexBytes(t)
    return hex_t

# code from https://towardsdatascience.com/decoding-ethereum-smart-contract-data-eed513a65f76


class EtherScan:

    def __init__(self, api_key, mainnet_url):
        if not api_key:
            raise ValueError('API key for App Annie not supplied')
        self.API_KEY = api_key
        self.url = f"{mainnet_url}/api"
        # default parameters
        self.default_parameters = {
            "apikey": self.API_KEY
        }

    def get_params(self, **kwargs):
        return {**self.default_parameters, **kwargs}

    @retry(retry=retry_if_exception_type(ValueError), wait=wait_fixed(2), stop=stop_after_attempt(7))
    def request_to_df(self, params={}):

        def _print_error(resp, e):
            print(f"ValueError: {e}")
            print(f"Resp: {resp}")
            print(f"Resp content: {resp.content}")
            print(f"Resp json: {resp.json()}")
            print("---" * 10)

        resp = requests.get(self.url, params=self.get_params(**params))
        try:
            df = pd.DataFrame(resp.json())  
        except Exception as e:
            _print_error(resp, e)
            raise
        return df

    def get_contract(self, addr):
        params = {
            "module": "contract",
            "action": "getsourcecode",
            "address": addr,
        }
        resp = requests.get(self.url, params=self.get_params(**params))
        return resp.json()['result'][0]

    def _get_trans(self, addr, startblock=0, endblock=None, internal=False):
        params = {
            "module": "account",
            "action": "txlistinternal" if internal else "txlist",
            "address": addr,
            "startblock": startblock,
            "sort": "asc",
        }
        if endblock:
            params['endblock'] = endblock
        df = self.request_to_df(params=params)
        if len(df) > 0:
            df = json_col_to_df(df, "result", prefix=False)
            df['timeStamp'] = pd.to_datetime(df['timeStamp'], unit='s')
            df.blockNumber = df.blockNumber.astype(int)
        return df

    def get_all_trans(self, addr, startblock=0, endblock=None, internal=False):
        df_list = []
        print(f"Get trans for {addr}")
        while True:
            df = self._get_trans(addr, startblock=startblock, internal=internal, endblock=endblock)
            if len(df) == 0:
                break
            print(f"Get {len(df)} data points from datetime {df.timeStamp.min()} to {df.timeStamp.max()}")
            df_list.append(df)

            if len(df) < 10000 or df.blockNumber.max() == endblock:
                break
            else:
                startblock = df.blockNumber.max()

        return pd.concat(df_list, axis=0).drop_duplicates("hash").reset_index(drop=True) if len(df_list) > 0 else pd.DataFrame()

    def decode_tx(self, address, input_data, abi):
        if input_data == "0x":
            return {"fn_name": "0x"}
        if abi is not None:
            try:
                (contract, abi) = _get_contract(address, abi)
                func_obj, func_params = contract.decode_function_input(input_data)
                target_schema = [a['inputs'] for a in abi if 'name' in a and a['name'] == func_obj.fn_name][0]
                decoded_func_params = convert_to_hex(func_params, target_schema)
                return {"fn_name": func_obj.fn_name, **decoded_func_params}
            except Exception as e:
                e = sys.exc_info()[0]
                print(f'decode error: {repr(e)}')
                return {"fn_name": "decode error"}
        else:
            return {"fn_name": 'no matching abi'}

    def _get_events(self, addr, startblock=0, endblock=None):
        params = {
            "module": "logs",
            "action": "getLogs",
            "address": addr,
            "fromBlock": startblock,
            "toBlock": "latest",
        }
        if endblock:
            params['endblock'] = endblock
        df = self.request_to_df(params=params)
        if len(df) > 0:
            df = json_col_to_df(df, "result", prefix=False)
            for c in ['blockNumber', 'timeStamp', 'gasPrice', 'gasUsed', 'logIndex']:
                df[c] = df[c].apply(lambda x: 0 if x == '0x' else int(x, 16))
            df['timeStamp'] = pd.to_datetime(df['timeStamp'], unit='s')
        return df

    def get_all_events(self, addr, startblock=0, endblock=None):
        df_list = []
        print(f"Get event logs for {addr}")
        while True:
            df = self._get_events(addr, startblock=startblock)
            if len(df) == 0:
                break

            print(f"Get {len(df)} data points from datetime {df.timeStamp.min()} to {df.timeStamp.max()}")
            df_list.append(df)

            if len(df) < 1000  or df.blockNumber.max() == endblock:
                break
            else:
                startblock = df.blockNumber.max()

        return pd.concat(df_list, axis=0).drop_duplicates(['transactionHash', 'logIndex']).reset_index(drop=True) if len(df_list) > 0 else pd.DataFrame()

    def decode_log(self, data, topics, abi):
        if abi is not None:
            try:
                topic2abi = _get_topic2abi(abi)

                log = {
                    'address': None,  # Web3.toChecksumAddress(address),
                    'blockHash': None,  # HexBytes(blockHash),
                    'blockNumber': None,
                    'data': data,
                    'logIndex': None,
                    'topics': [_get_hex_topic(_) for _ in topics],
                    'transactionHash': None,  # HexBytes(transactionHash),
                    'transactionIndex': None
                }
                event_abi = topic2abi[log['topics'][0]]
                evt_name = event_abi['name']

                data = get_event_data(w3.codec, event_abi, log)['args']
                target_schema = event_abi['inputs']
                decoded_data = convert_to_hex(data, target_schema)

                return (evt_name, json.dumps(decoded_data), json.dumps(target_schema))
            except Exception:
                print(f'decode error: {traceback.format_exc()}')
                return ('decode error', traceback.format_exc(), None)

        else:
            return ('no matching abi', None, None)

    def _get_erc20_trans(self, addr=None, contractaddr=None, startblock=0, endblock=None):
        assert addr is not None or contractaddr is not None
        params = {
            "module": "account",
            "action": "tokentx",
            "startblock": startblock,
            "sort": "asc"
        }
        if addr:
            params['address'] = addr
        if contractaddr:
            params['contractaddress'] = contractaddr
        if endblock:
            params['endblock'] = endblock
        df = self.request_to_df(params=params)
        if len(df) > 0:
            df = json_col_to_df(df, "result", prefix=False)
            df['timeStamp'] = pd.to_datetime(df['timeStamp'], unit='s')
            df.blockNumber = df.blockNumber.astype(int)
        return df

    def get_all_erc20_trans(self, addr=None, contractaddr=None, startblock=0, endblock=None):
        assert addr is not None or contractaddr is not None
        df_list = []
        is_end = False
        print(f"Get erc20 trans for {addr or contractaddr}")
        while True:
            df = self._get_erc20_trans(addr, contractaddr, startblock=startblock)

            if len(df) == 0:
                break
            elif len(df) < 10000 or df.blockNumber.max() == endblock:
                is_end = True
            else:
                is_end = False

            print(f"Get {len(df)} data points from datetime {df.timeStamp.min()} to {df.timeStamp.max()}")

            if len(df_list) > 0:  # remove duplicate hash data
                df = df[~df['hash'].isin(df_list[-1]['hash'])]
            df_list.append(df)

            if is_end:
                break
            else:
                startblock = df.blockNumber.max()

        return pd.concat(df_list, axis=0).reset_index(drop=True) if len(df_list) > 0 else pd.DataFrame()
