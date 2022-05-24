import logging
import dropbox
import pandas as pd
import operator
from functools import partial, reduce
from itertools import product
import numpy as np
import sqlite3
from os.path import expanduser
import getpass
import platform
import datetime

class ParameterGrid:
    def __init__(self, param_grid):
        param_grid = [param_grid]
        self.param_grid = param_grid

    def __iter__(self):
        for p in self.param_grid:
            items = sorted(p.items())
            if not items:
                yield {}
            else:
                keys, values = zip(*items)
                for v in product(*values):
                    params = dict(zip(keys, v))
                    yield params

    def __len__(self):
        """Number of points on the grid."""
        # Product function that can handle iterables (np.product can't).
        product = partial(reduce, operator.mul)
        return sum(product(len(v) for v in p.values()) if p else 1
                   for p in self.param_grid)

    def __getitem__(self, ind):
        for sub_grid in self.param_grid:
            keys, values_lists = zip(*sorted(sub_grid.items())[::-1])
            sizes = [len(v_list) for v_list in values_lists]
            total = np.product(sizes)

            if ind >= total:
                # Try the next grid
                ind -= total
            else:
                out = {}
                for key, v_list, n in zip(keys, values_lists, sizes):
                    ind, offset = divmod(ind, n)
                    out[key] = v_list[offset]
                return out


def setup_custom_logger(name, log_level=logging.INFO):
    logger = logging.getLogger(name)
    log_format = (
        '%(asctime)s - %(levelname)s - '
        # '[%(filename)s:%(lineno)s - %(funcName)15s() ] - '
        '%(message)s'
    )
    # log_format = '%(asctime)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt=log_format)
    # logging.basicConfig(filename='dummy.log', level=logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger.setLevel(log_level) # set log level
    logger.addHandler(handler)

    return logger

def read_upbit_1h_db(table_name):
    system = platform.system()
    if system.startswith("Darwin"):
        path =  f'/Users/{getpass.getuser()}/Dropbox/database/'
    if system.startswith("Linux"):
        path =  f'/home/{getpass.getuser()}/Dropbox/database/'

    db_name = 'upbit_1h.db'

    con = sqlite3.connect(path + db_name)
    cur = con.cursor()

    sql = f'SELECT * FROM {table_name}'
    cur.execute(sql)

    rows = cur.fetchall()
    cols = [column[0] for column in cur.description]
    df = pd.DataFrame.from_records(data=rows, columns=cols, index=['date'])
    df.index = pd.to_datetime(df.index)
    df.dropna(inplace=True)
    return df

def minus_date(days):
    today = datetime.date.today()
    yester = today - datetime.timedelta(days=days)
    # print(yester)
    yester = yester.strftime('%Y-%m-%d')
    return yester

def trading_sell_round(price):
    string_price = ''
    for s in str(price):
        if s == '.':
            break
        string_price = string_price + s

    price = int(string_price)

    if len(str(string_price)) == 3:
        # if 123
        price = price + 1

    if len(str(string_price)) == 4:
        # if 1234
        x = price
        increment = 5
        price = x - (x % increment)

    if len(str(string_price)) == 5:
        # if 12345
        x = price
        increment = 10
        price = x - (x % increment)

    if len(str(string_price)) == 6:
        # if 1234567
        x = price
        increment = 50
        price = x - (x % increment)

    if len(str(string_price)) >= 7:
        # if 1234567
        price = round(price, -3)

    return price

if __name__ == "__main__":
    # logger = setup_custom_logger('root')
    # df = read_upbit_1h_db('BTC')
    print(minus_date(2))
