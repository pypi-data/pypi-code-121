import base64
from urllib.parse import quote_plus

from pymongo import MongoClient

from licsber.github import get_secret


def get_mongo(pwd_b64=get_secret('L_MONGO_PWD_B64'),
              username=get_secret('L_MONGO_USERNAME'),
              host=get_secret('L_MONGO_HOST'),
              port=get_secret('L_MONGO_PORT'),
              db_name=get_secret('L_MONGO_DEFAULT_DB'),
              connect=True,
              ):
    """
    获取mongo数据库连接, 用于爬虫.
    :param pwd_b64: base64后的密码.
    :param username: 具有数据库权限的用户名.
    :param host: mongodb的url.
    :param port: host的端口.
    :param db_name: 数据库名称.
    :param connect: 是否默认连接.
    :return: mongo数据库连接.
    """
    if not pwd_b64:
        pwd_b64 = input('请输入mongo数据库连接密码(base64表示).')

    pwd = base64.b64decode(pwd_b64).decode('utf-8')
    username = quote_plus(username)
    pwd = quote_plus(pwd)

    conn_str = f"mongodb://{username}:{pwd}@{host}:{port}/{db_name}?retryWrites=true"
    client = MongoClient(
        conn_str,
        uuidRepresentation='standard',
        serverSelectionTimeoutMS=5000,
        connect=connect,
    )

    db = client[db_name]
    return db
