import json
import traceback
from pymssql import InternalError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from docparser.core.behavior_base import BehaviorBase


class AddressRepairBehavior(BehaviorBase):
    __sql_filter_arr = ["delete", "insert", "truncate", "drop", "update", "remove", "create", "table", "database"]
    __sql_find_str_filter = ["\"", "\\", "/", "*", "'", "=", "-", "#", ";", "", "+", "%", "$", "(", ")", "@", "!"]
    """
    地址修补处理行为
    =============
    配置说明：主节点下
    "address_repair":{
                    "db":{
                        "pub": {"user":"","pwd":"","server":"","database":""}
                    },
                    "repairs": [
                        {"key":"","table": "","db_key":"","sql":"","column":[],"value":"","mapping":"", "old_val_handle": "empty|retain","try_match":True}
                    ]
                }
    """

    class_index = 2

    def data_processing(self, ref_data, data: list, error: list, config: dict, logger, additional) -> dict:

        sub_conf = config.get("address_repair")
        if data and len(data) > 0 and sub_conf is not None:
            repair_config = sub_conf.get("repairs")
            db_configs = sub_conf.get("db")
            if repair_config is None or db_configs is None:
                return additional

            cache_db_engine = {}
            for conf in repair_config:

                key = conf.get("key")
                db_key = conf.get("db_key")
                table_name = conf.get("table")
                db_conf = db_configs.get(db_key)
                mapping = conf.get("mapping")
                try_match = conf.get("try_match", True)
                old_val_handle = conf.get("old_val_handle", "empty")

                db_engine = self.get_engine(db_key, db_conf, cache_db_engine)

                data_vals = self._find_values(key, table_name, data)
                new_vals = self.get_db_data(db_engine,
                                            data_vals,
                                            conf.get("sql"),
                                            conf.get("column"),
                                            conf.get("value"),
                                            mapping,
                                            try_match
                                            )
                if mapping is not None:
                    if table_name is not None and table_name.strip() != "":
                        data[table_name]["column"].append(mapping)
                        table_index = self._find_col_index(key, table_name, data)
                        for i, v in enumerate(new_vals):
                            if isinstance(v, tuple):
                                data[table_name]["rows"][i].append(v[1])
                                if old_val_handle == "empty":
                                    data[table_name]["rows"][i][table_index] = ""
                    else:
                        if isinstance(new_vals[0], tuple):
                            data[mapping] = new_vals[0][1]
                            if old_val_handle == "empty":
                                data[key] = ""
                else:
                    self._restore_values(key, table_name, data, new_vals)
            cache_db_engine = None
        return additional

    @classmethod
    def sql_filter(cls, sql):
        for s in AddressRepairBehavior.__sql_filter_arr:
            if sql.lower().find("delete") > -1 and sql.lower().find("isdeleted") > -1:
                continue
            if sql.lower().find(s) > -1:
                raise ValueError("检测到危险语句，停止执行")

    @classmethod
    def sql_filter_str(cls, sql):
        for s in AddressRepairBehavior.__sql_find_str_filter:
            sql = sql.replace(s, "")
        return sql

    @classmethod
    def get_engine(cls, key, db_config, cache_db_engine):
        """
        获得sql引擎
        """
        if (engine := cache_db_engine.get(key)) is None:
            pwd = db_config.get("pwd").replace("@", "%40")
            engine = create_engine('mssql+pymssql://%s:%s@%s/%s' % (db_config.get("user"),
                                                                    pwd,
                                                                    db_config.get("server"),
                                                                    db_config.get("database")),
                                   echo=False)
            engine = sessionmaker(bind=engine)
            cache_db_engine[key] = engine

        return engine

    @classmethod
    def get_db_data(cls, db_engine, data_vals, sql, column, value_column, mapping, try_match):

        cls.sql_filter(sql)
        handle_values = []



        for value in data_vals:
            value = cls.sql_filter_str(value)
            if try_match:
                many_match_result = []
                first_arr_val = value.split(',')[0]
                sql = sql.replace("${value}", first_arr_val)
            else:
                sql = sql.replace("${value}", value)


            with db_engine() as session:
                cursor = session.execute(sql)
                result = cursor.fetchall()

            is_all_match = False

            if len(result) > 1:
                for row in result:
                    # 全文匹配
                    for index in column:
                        if row[index] == value:
                            is_all_match = True
                            if mapping:
                                handle_values.append((value, str(row[value_column])))
                            else:
                                handle_values.append(str(row[value_column]))
                            break
                        if not is_all_match and try_match:
                            if row[index] == first_arr_val:
                                if mapping:
                                    many_match_result.append((value, str(row[value_column])))
                                else:
                                    many_match_result.append(str(row[value_column]))

                if try_match and len(many_match_result) == 1:
                    is_all_match = True
                    handle_values.append(many_match_result[0])
                    many_match_result.clear()

                if is_all_match:
                    break

            elif len(result) == 1:
                is_all_match = True
                if mapping is not None:
                    handle_values.append((value, str(result[0][value_column])))
                else:
                    handle_values.append(str(result[0][value_column]))
            if not is_all_match:
                handle_values.append(value)
        return handle_values


if __name__ == "__main__":
    test_data = {"test1": "NINGBO, CHINA", "test2": "DISHMAN-PHARMACEUTICAL-",
                  "address":
                      {"column": ["col1", "col2", "col3", "col4"],
                       "rows": [
                           ["aaedfkkk", "sc", "ITAAPS", "LIA NYU NGANG1, USA"],
                           ["12f", "HI", "mckdg", "IA"]
                       ]
                       }}
    AddressRepairBehavior().data_processing(
        None, test_data,
        [],
        {
            "address_repair": {
                "db": {
                    "pub": {"user": "co", "pwd": "Co&23@2332$22", "server": "db.dev.com:1433",
                            "database": "CO_PUB"}
                },
                "repairs": [
                    {"key": "test1", "table": "", "db_key": "pub",
                     "sql": "SELECT  [FullName],[LocalName],[name],[code],[Id] from Places WHERE IsDeleted = 0 and IsOcean = 1 and IsValid = 1 and ([FullName] like '%${value}%' or charindex([FullName],'${value}')> 0) ;",
                     "column": [0, 2, 3], "value": 4, "mapping": "youid",
                     "old_val_handle": "empty", "try_match": True}
                ]

            }
        }, None, {}
    )

    print(test_data)
