from enum import Enum
import pymssql


class DataBaseArgumentsEnum(Enum):
    HOST = "host"
    SERVER = "server"
    DATABASE = "database"
    ACCOUNT = "account"
    SECRET = "secret"
    PORT = "port"
    AS_DICT = "as_dict"


class Connection:
    def __init__(self, connector):
        self.connector = connector
        self.cursor = connector.cursor()


class MssqlUtils:
    DEFAULT_ARGS = {
        DataBaseArgumentsEnum.HOST.value: "127.0.0.1",
        DataBaseArgumentsEnum.SERVER.value: "127.0.0.1",
        DataBaseArgumentsEnum.DATABASE.value: "",
        DataBaseArgumentsEnum.ACCOUNT.value: "sa",
        DataBaseArgumentsEnum.SECRET.value: "",
        DataBaseArgumentsEnum.PORT.value: 1433,
        DataBaseArgumentsEnum.AS_DICT.value: True,
    }

    @staticmethod
    def get_connection(**kwargs):
        args = dict(MssqlUtils.DEFAULT_ARGS, **kwargs)
        return Connection(pymssql.connect(
            host=args.get(DataBaseArgumentsEnum.HOST.value),
            server=args.get(DataBaseArgumentsEnum.SERVER.value),
            database=args.get(DataBaseArgumentsEnum.DATABASE.value),
            user=args.get(DataBaseArgumentsEnum.ACCOUNT.value),
            password=args.get(DataBaseArgumentsEnum.SECRET.value),
            port=args.get(DataBaseArgumentsEnum.PORT.value),
            as_dict=args.get(DataBaseArgumentsEnum.AS_DICT.value)
        ))

    @staticmethod
    def close(connector):
        try:
            connector.cursor.close()
        except Exception as e:
            pass

        try:
            connector.connector.close()
        except Exception as e:
            pass
