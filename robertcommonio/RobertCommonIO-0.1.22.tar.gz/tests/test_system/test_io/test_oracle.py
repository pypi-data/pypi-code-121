import time
from typing import Optional, Any, Union, List, Dict

from sqlalchemy import create_engine, text
from sqlalchemy.pool.impl import QueuePool
from sqlalchemy.schema import CreateTable
from sqlalchemy.ext.declarative import declarative_base

import cx_Oracle
from datetime import datetime

import os
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

class SQLAlCheAccessor:

    def __init__(self, config: Any=None):
        self.engine: dict = {}

    def add_engine(self, engine_name: str, engine_conn: str, engine_pool_class: Any=QueuePool, engine_pool_recycle: int=60):
        '''
                添加一个数据库连接池
                @Example:
                    PostgreSQL
                        # default
                        engine = create_engine('postgresql://scott:tiger@localhost/mydatabase')
                        # psycopg2
                        engine = create_engine('postgresql+psycopg2://scott:tiger@localhost/mydatabase')
                        # pg8000
                        engine = create_engine('postgresql+pg8000://scott:tiger@localhost/mydatabase')

                    MySQL
                        # default
                        engine = create_engine('mysql://scott:tiger@localhost/foo')
                        # mysqlclient (a maintained fork of MySQL-Python)
                        engine = create_engine('mysql+mysqldb://scott:tiger@localhost/foo')
                        # PyMySQL
                        engine = create_engine('mysql+pymysql://scott:tiger@localhost/foo')

                    Oracle
                        engine = create_engine('oracle://scott:tiger@127.0.0.1:1521/sidname')
                        engine = create_engine('oracle+cx_oracle://scott:tiger@tnsname')

                    SQL Server
                        # pyodbc
                        engine = create_engine('mssql+pyodbc://scott:tiger@mydsn')
                        # pymssql
                        engine = create_engine('mssql+pymssql://scott:tiger@hostname:port/dbname')

                    SQLite
                        engine = create_engine('sqlite:///foo.db')
                        engine = create_engine('sqlite:///C:\\path\\to\\foo.db')

            '''
        if engine_name not in self.engine.keys():
            engine = create_engine(engine_conn, poolclass=engine_pool_class, pool_recycle=engine_pool_recycle)
            if engine:
                self.engine[engine_name] = engine
        return self.engine.get(engine_name)

    def get_engine(self, engine_name: str):
        return self.engine.get(engine_name)

    def to_dict(self, records: Union[List[Optional[Dict]], Dict]):
        if isinstance(records, Dict):
            values = {}
            for k, v in records.items():
                values[k] = v
            return values
        elif isinstance(records, List):
            values = []
            for record in records:
                value = {}
                for k, v in record.items():
                    value[k] = v
                values.append(value)
            return values
        return records

    def read_sql(self, engine_name: str, sql_cmd: str, to_dict: bool=True):
        with self.get_engine(engine_name).connect() as conn:
            records = conn.execute(sql_cmd).mappings().all()
            if to_dict is True:
                return self.to_dict(records)
            return records


    def execute_sql(self, engine_name: str, sql_cmd: str, params: list=None):
        with self.get_engine(engine_name).connect() as conn:
            return conn.execute(text(sql_cmd), params).rowcount

    def execute_multi_sql(self, engine_name: str, cmd_tuple: list):
        with self.get_engine(engine_name).begin() as conn:
            rowcount = 0
            for cmd in cmd_tuple:
                rowcount = conn.execute(text(cmd[0]), cmd[1]).rowcount + rowcount
            return rowcount

    def get_table_struct(self, engine_name: str, table_name: str):
        engine = self.get_engine(engine_name)
        if engine is not None:
            base = declarative_base()
            base.metadata.reflect(engine)
            # 获取原表对象
            oldTable = base.metadata.tables[table_name]
            # 获取原表建表语句
            crate_sql = str(CreateTable(oldTable))
            base.metadata.clear()
            return crate_sql

    def generate_sql_format(self, table_name: str, action: str = 'replace', colums: list = None, filter: list = None):
        if action in ['replace', 'append']:
            return f"insert into {table_name} ({', '.join('{}'.format(k) for k in colums)}) VALUES ({', '.join(':{}'.format(k) for k in colums)})"
        elif action == 'update':
            return f"update {table_name} set {', '.join('{} = :{}'.format(k, k) for k in colums)} where {', '.join('{} = :{}'.format(k, k) for k in filter)}"
        elif action == 'delete':
            return f"delete from {table_name} where {', '.join('{} = :{}'.format(k, k) for k in filter)}"

    def generate_sql_cmds(self, table_name: str, records: list, action: str = 'replace', colums: list = None, filter: list = None):
        cmds = []
        if len(records) > 0:
            if action == 'replace':
                if filter is None:
                    cmds.append((f"delete from {table_name}", None))
                else:
                    cmds.append((self.generate_sql_format(table_name, 'delete', None, filter), records))

            cmds.append((self.generate_sql_format(table_name, action, records[0].keys() if colums is None else colums, filter), records))
        return cmds

class SynOracle():

    def __init__(self):
        self.accessor = None
        self.oracle_250 = 'oracle_250'
        self.oracle_216 = 'oracle_216'
        self.oracle_250_con = 'oracle://cy2003:goen_cy2003@10.192.1.250:1521/gc'
        self.oracle_216_con = 'oracle://cy2003:goen_cy2003@10.192.1.216:1521/gc'

        self.syn_interval = 600  # 同步间隔
        self.table_src = 'ACTION'  # 在场箱表
        self.table_dst = 'ACTION_SYN'
        self.cache_file = 'action_216_time.txt'
        self.limit = 500
        self.ole_last_syn = self.get_syn_time()  # 进出场扫描时间
        self.column = 'ID,CNTR_NO,CNTR_SIZE,CNTR_TYPE,MARK_OW,MARK_NS,OPERATOR_I,KIND_CNTR_I,PLAN_ID_I,KIND_I,STATUS_I,FE_I,EIR_NO_I,SEAL_NO_I,VESSEL_I,VOY_I,BLNO_I,CARGONAME_I,CLASS_I,UNDG_NO_I,GWET_I,PLACE_I,CUSER_I,DWDM_CD_I,TRUCK_NO_I,DRIVER_I,MARK_TC_I,REMARK_I,IC_KIND_I,IC_NO_I,DATE_IN,DATE_GATE_OUT,DATE_DROP,DRIVER_CY_I,SB_NO_I,CASH_I,LDR_I,DATE_LR_I,OPERATOR_O,KIND_CNTR_O,PLAN_ID_O,KIND_O,STATUS_O,FE_O,EIR_NO_O,SEAL_NO_O,VESSEL_O,VOY_O,BLNO_O,CARGONAME_O,CLASS_O,UNDG_NO_O,GWET_O,PLACE_O,CUSER_O,DWDM_CD_O,TRUCK_NO_O,DRIVER_O,MARK_TC_O,REMARK_O,IC_KIND_O,IC_NO_O,DATE_OUT,DATE_GATE_IN,DATE_LIFT,DRIVER_CY_O,SB_NO_O,CASH_O,LDR_O,DATE_LR_O,LOCK_OUT,SEAT_PLAN,SEAT,OPERATOR,KIND_CNTR,FE,STATUS,RELEASE_NO'.lower()
        self.columns = self.column.split(',')

        print(f"Start At {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def get_accessor(self):
        if self.accessor is None:
            self.accessor = SQLAlCheAccessor()
            self.accessor.add_engine(self.oracle_250, self.oracle_250_con)
            self.accessor.add_engine(self.oracle_216, self.oracle_216_con)
        return self.accessor

    def save_syn_time(self, now: datetime):
        self.ole_last_syn = now
        with open(self.cache_file, 'w') as f:
            f.write(f"{now.strftime('%Y-%m-%d %H:%M:%S')}")

    def get_syn_time(self):
        try:
            if os.path.exists(self.cache_file) is True:
                with open(self.cache_file, 'r') as f:
                    time = f.read()
                    if len(time) > 0:
                        return datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
        except Exception as e:
            strError = 'ERROR: %s' % e.__str__()
            print(strError)
        return datetime.now()

    def split_to_list(self, values, size: int):
        if isinstance(values, dict):
            results = [{}]
            for k, v in values.items():
                if len(results[-1]) >= size:
                    results.append({k: v})
                else:
                    results[-1][k] = v
            return results
        elif isinstance(values, list):
            return [values[i:i + size] for i in range(0, len(values), size)]
        return values

    def syn_record(self):
        try:
            now = datetime.now()
            if self.get_accessor() is not None:
                records_on = self.accessor.read_sql(self.oracle_250, f"Select {self.column} from {self.table_src} where DATE_OUT is NULL")
                records_out = self.accessor.read_sql(self.oracle_250, f"Select {self.column} from {self.table_src} where DATE_OUT > to_date('{self.ole_last_syn.strftime('%Y-%m-%d %H:%M:%S')}', 'yyyy-mm-dd hh24:mi:ss') and DATE_OUT <= to_date('{now.strftime('%Y-%m-%d %H:%M:%S')}', 'yyyy-mm-dd hh24:mi:ss') order by DATE_OUT desc")
                print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}]: get online({len(records_on)}) out({len(records_out)}[{self.ole_last_syn.strftime('%Y-%m-%d %H:%M:%S')}-{now.strftime('%Y-%m-%d %H:%M:%S')}])")
                records_on.extend(records_out)
                if len(records_on) > 0:
                    records = self.split_to_list(records_on, self.limit)
                    cmds = []
                    for record in records:
                        cmds.extend(self.accessor.generate_sql_cmds(self.table_dst, record, 'replace', self.columns, ['id']))
                    result = self.accessor.execute_multi_sql(self.oracle_216, cmds)
                    if len(records_out) > 0:
                        self.save_syn_time(records_out[0]['date_out'])
                    end = datetime.now()
                    print(f"[{end.strftime('%Y-%m-%d %H:%M:%S')}]: syn success cost: {'{:.2f}'.format((end - now).total_seconds())}s online: {len(records_on)} out: {len(records_out)} result: {result}")
            else:
                raise Exception(f"no accessor")
        except Exception as e:
            print(e.__str__())

    def syn_records(self):
        while True:
            self.syn_record()
            time.sleep(self.syn_interval)

SynOracle().syn_records()