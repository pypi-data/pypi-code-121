from robertcommonio.system.io.sqlalche import SQLAlCheAccessor
import sqlite3
import cx_Oracle
import os
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

def test_sqlite():
    accessor = SQLAlCheAccessor()
    accessor.add_engine('sqlite0', 'sqlite+pysqlite:///:memory:')
    accessor.execute_sql('sqlite0', 'CREATE TABLE some_table (x int, y int)')
    accessor.execute_sql('sqlite0', 'INSERT INTO some_table (x,y) VALUES (:x, :y)', [{"x": 1, "y": 1}, {"x": 2, "y": 4}])
    print(accessor.read_sql('sqlite0', 'SELECT * FROM some_table'))

def test_sqlite1():
    accessor = SQLAlCheAccessor()
    accessor.add_engine('sqlite0', 'sqlite:///config.db')
    accessor.execute_sql('sqlite0', 'CREATE TABLE some_table (x int, y int)')
    accessor.execute_sql('sqlite0', 'INSERT INTO some_table (x,y) VALUES (:x, :y)', [{"x": 1, "y": 1}, {"x": 2, "y": 4}])
    print(accessor.read_sql('sqlite0', 'SELECT * FROM some_table'))

def test_mysql():
    accessor = SQLAlCheAccessor()
    accessor.add_engine('mysql0', 'mysql+pymysql://root:RNB.beop-2013@localhost/beopdata')

    print(accessor.read_sql('mysql0', 'SELECT * FROM some_table'))

    records = [{"A": 1, "B": 1, "C": 5.2, "D": "2021-07-23 00:00:00"}, {"A": 2, "B": 3, "C": 4.2, "D": "2021-07-25 00:00:00"}]
    cmds = accessor.generate_sql_cmds('some_table', records, 'replace', list(records[0].keys()))

    print(accessor.execute_multi_sql('mysql0', cmds))

    print(accessor.read_sql('mysql0', 'SELECT * FROM some_table'))

    record_update = [{"A": 1, "B": 1, "C": 5.2, "D": "2021-07-23 01:00:00"}, {"A": 2, "B": 3, "C": 4.2, "D": "2021-07-25 01:00:00"}]
    cmd_update = accessor.generate_sql_cmds('some_table', record_update, 'update', ["B", "C", "D"], ["A"])

    print(accessor.execute_multi_sql('mysql0', cmd_update))

    print(accessor.read_sql('mysql0', 'SELECT * FROM some_table'))

    print()

def test_oracle():
    accessor = SQLAlCheAccessor()
    accessor.add_engine('oracle0', 'oracle://cy2003:goen_cy2003@10.192.1.216:1521/gc')

    r = accessor.read_sql('oracle0', 'SELECT * FROM action_syn1 where date_out is null')

    records = [{"ID": '1512005962', "CNTR_NO": "123"}, {"ID": '1512005970', "CNTR_NO": "234"}]
    cmds = accessor.generate_sql_cmds('action_syn1', records, 'replace', list(records[0].keys()), ['ID'])

    print(accessor.execute_multi_sql('oracle0', cmds))

    print(accessor.read_sql('mysql0', 'SELECT * FROM some_table'))


    print()

def test_syn_oracle():
    accessor = SQLAlCheAccessor()
    accessor.add_engine('oracle0', 'oracle://XX:XX@10.192.1.250:1521/gc')
    accessor.add_engine('oracle1', 'oracle://XX:XX@10.192.1.216:1521/gc')

    r = accessor.read_sql('oracle0', 'SELECT * FROM action_syn1 where date_out is null')

    records = [{"ID": '1512005962', "CNTR_NO": "123"}, {"ID": '1512005970', "CNTR_NO": "234"}]
    cmds = accessor.generate_sql_cmds('action_syn1', records, 'replace', list(records[0].keys()), ['ID'])

    print(accessor.execute_multi_sql('oracle0', cmds))

    print(accessor.read_sql('mysql0', 'SELECT * FROM some_table'))

test_oracle()