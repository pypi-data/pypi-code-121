# Use should provide a conformant object `hive`
# and call the function `test_all` in their Hive setup
# to test the UDF functionalities.

import random
import string
from typing import List, Sequence, Tuple

import numpy as np
import pandas as pd
from hive_udf import (
    make_udf,
    hive_udf_example,
    hive_udaf_example,
    hive_udf_args_example)


class _Hive:
    def execute(self, sql: str):
        raise NotImplementedError

    def fetchall(self) -> List[tuple]:
        raise NotImplementedError

    def create_table(self, db_name, tb_name, cols: Sequence[Tuple[str, str]]):
        raise NotImplementedError


def _test_udf(hive, db_name, tb_name):
    print('records in table:')
    hive.execute(f'SELECT * FROM {db_name}.{tb_name} LIMIT 10')
    print(hive.fetchall())

    code = make_udf(hive_udf_example)
    sql = f'''
        SELECT
            TRANSFORM (
                id,
                info_json
            )
            USING '{code}'
            AS (make STRING, price FLOAT)
        FROM {db_name}.{tb_name}
        '''
    hive.execute(sql)
    rows = hive.fetchall()
    z = pd.DataFrame.from_records(
        list(rows), columns=['make', 'price'])
    z = z.sort_values(['make', 'price'])
    print('z')
    print(z)
    print('')

    # Expected result:
    #
    #     make   price
    # 1   ford  2000.0
    # 5   ford  4000.0
    # 2   ford     NaN
    # 0  honda  1000.0
    # 4  honda  2000.0
    # 3  tesla  3000.0

    assert len(z) == 6
    assert z['make'].tolist() == [
        'ford', 'ford', 'ford', 'honda', 'honda', 'tesla']
    assert np.isnan(z['price'].iloc[2])
    assert z['price'].iloc[3] == 1000


def _test_udaf(hive, db_name, tb_name):
    code = make_udf(hive_udaf_example)
    sql = f'''
        SELECT
            TRANSFORM (
                info_json
            )
            USING '{code}'
            AS (make STRING, avg_price FLOAT, null_prices INT)
        FROM (
            SELECT
                id,
                info_json
            FROM {db_name}.{tb_name}
            CLUSTER BY GET_JSON_OBJECT(info_json, '$.make')
            ) AS t
    '''
    hive.execute(sql)
    rows = hive.fetchall()
    z = pd.DataFrame.from_records(
        list(rows), columns=['make', 'avg_price', 'null_prices'])
    print('z')
    print(z)
    print('')

    # Expected result:
    #
    #     make  avg_price  null_prices
    # 1   ford     3000.0            1
    # 0  honda     1500.0            0
    # 2  tesla     3000.0            0

    assert len(z) == 3
    z = z.sort_values(['make'])
    assert z['make'].tolist() == ['ford', 'honda', 'tesla']
    assert z['avg_price'].tolist() == [3000, 1500, 3000]
    assert z['null_prices'].tolist() == [1, 0, 0]


def _run_sql(hive, sql, cols):
    hive.execute(sql)
    rows = hive.fetchall()
    z = pd.DataFrame.from_records(list(rows), columns=cols)
    z = z.sort_values(cols)
    print('z')
    print(z)
    print('')
    return z


def _test_udf_args(hive, db_name, tb_name):
    def make_sql(country, default_price):
        code = make_udf(hive_udf_args_example, country, default_price)
        sql = f'''
            SELECT
                TRANSFORM (
                    id,
                    info_json
                )
                USING '{code}'
                AS (make STRING, price FLOAT)
            FROM {db_name}.{tb_name}
            '''
        return sql

    # ## jap ###

    sql = make_sql('jap', 250)
    z = _run_sql(hive, sql, ['make', 'price'])

    # Expected result:
    #
    #     make   price
    # 0  honda  1000.0
    # 1  honda  2000.0

    assert z['make'].tolist() == ['honda', 'honda']
    assert z['price'].tolist() == [1000, 2000]

    # ## america ###

    sql = make_sql('america', 550)
    z = _run_sql(hive, sql, ['make', 'price'])

    # Expected result:
    #
    #     make   price
    # 1   ford   550.0
    # 0   ford  2000.0
    # 3   ford  4000.0
    # 2  tesla  3000.0

    assert z['make'].tolist() == ['ford', 'ford', 'ford', 'tesla']
    assert z['price'].tolist() == [550, 2000, 4000, 3000]

    sql = make_sql('all', 340)
    z = _run_sql(hive, sql, ['make', 'price'])

    # Expected result:
    #
    #    make   price
    # 2  ford   340.0
    # 1  ford  2000.0
    # 5  ford  4000.0
    # 0 honda  1000.0
    # 4 honda  2000.0
    # 3 tesla  3000.0

    assert z['make'].tolist() == ['ford', 'ford', 'ford',
                                  'honda', 'honda', 'tesla']
    assert z['price'].tolist() == [340, 2000, 4000, 1000, 2000, 3000]


def _test_udf_followed_by_agg(hive, db_name, tb_name):
    code = make_udf(hive_udf_example)
    sql = f'''
        SELECT
            make,
            SUM(price) AS price_total
        FROM (
            SELECT
                TRANSFORM (
                    id,
                    info_json
                )
                USING '{code}'
                AS (make STRING, price FLOAT)
            FROM {db_name}.{tb_name}
            ) A
        GROUP BY make
        '''
    z = _run_sql(hive, sql, ['make', 'price_total'])

    # Expected result:
    #
    #     make price_total
    # 0   ford      6000.0
    # 1  honda      3000.0
    # 2  tesla      3000.0

    assert len(z) == 3
    assert z['make'].tolist() == ['ford', 'honda', 'tesla']
    assert z['price_total'].tolist() == [6000.0, 3000.0, 3000.0]


def _make_tmp_name():
    return 'tmp_' + ''.join(random.choices(string.ascii_lowercase, k=20))


def _get_databases(hive: _Hive):
    hive.execute('SHOW DATABASES')
    z = hive.fetchall()
    return [v[0] for v in z]


def _get_tables(hive: _Hive, db_name: str):
    hive.execute(f'SHOW TABLES IN {db_name}')
    z = hive.fetchall()
    return [v[0] for v in z]


def test_all(hive: _Hive, db_name: str):
    assert db_name in _get_databases(hive)

    tb_name = _make_tmp_name()

    print('creating table "{}.{}"'.format(db_name, tb_name))
    hive.execute(f'DROP TABLE IF EXISTS {db_name}.{tb_name}')

    # hive.execute(f'''
    #              CREATE TABLE {db_name}.{tb_name}
    #              (
    #                  id INT,
    #                  info_json STRING
    #              )
    #              STORED AS ORC
    #              TBLPROPERTIES (
    #                  'orc.compress'='ZLIB'
    #              )
    #              ''')
    hive.create_table(
        db_name,
        tb_name,
        [('id', 'INT'), ('info_json', 'STRING')],
    )

    try:
        assert tb_name in _get_tables(hive, db_name)
        print(f'table {db_name}.{tb_name} created successfully')

        hive.execute(f'''
                     INSERT OVERWRITE TABLE {db_name}.{tb_name}
                     VALUES
                        (1, '{{"make": "honda", "price": 1000}}'),
                        (2, '{{"make": "ford", "price": 2000}}'),
                        (3, '{{"make": "ford"}}'),
                        (4, '{{"make": "tesla", "price": 3000}}'),
                        (5, '{{"make": "honda", "price": 2000}}'),
                        (6, '{{"make": "ford", "price": 4000}}')
                     ''')

        _test_udf(hive, db_name, tb_name)
        _test_udaf(hive, db_name, tb_name)
        _test_udf_args(hive, db_name, tb_name)
        _test_udf_followed_by_agg(hive, db_name, tb_name)
    finally:
        print(f'dropping table {db_name}.{tb_name}')
        hive.execute(f'DROP TABLE IF EXISTS {db_name}.{tb_name}')
        assert tb_name not in _get_tables(hive, db_name)
