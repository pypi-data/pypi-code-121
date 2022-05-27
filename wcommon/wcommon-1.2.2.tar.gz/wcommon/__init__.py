# coding=utf-8
from __future__ import division
import time as timetool
import datetime as datetime_tool
import requests
import json
import subprocess
import socket
import traceback
import os
import sys
import pymysql
import re
import configparser
from loguru import logger
import hashlib

# from Crypto.Cipher import AES
# from binascii import b2a_hex

# reload(sys)
# sys.setdefaultencoding('utf8')
# print("WARN:please configuration the configuraion_file variable")

configuraion_file = "/data/apps/public/conf.ini"


def getConfig():
    print(configuraion_file)
    import configparser
    config = configparser.ConfigParser()
    config.read(configuraion_file)
    return config


# for python2
# def execute_command2(cmd):
#     status,output = commands.getstatusoutput(cmd)
#     if status == 0:
#         status = True
#     else:
#         status = False
#
#     tempLines = output.split("\n")
#
#     lines = []
#
#     for e in tempLines:
#         t = e.strip()
#         if len(t) >0 :
#             lines.append(t)
#
#     return (status, output, lines)


# for python3
def execute_command3(cmd):
    status, output = subprocess.getstatusoutput(cmd)
    if status == 0:
        status = True
    else:
        status = False

    temp_lines = output.split("\n")

    lines = []

    for e in temp_lines:
        t = e.strip()
        if len(t) > 0:
            lines.append(t)

    return status, output, lines


# 如果subprocess.getstatusoutput出现乱码而失败，就使用这个方法执行命令
def execute_command_use_os(cmd):
    r = os.system(cmd)
    return r


# 执行shell命令,并返回结果
def execute_command(cmd):
    major = sys.version_info[0]
    if major == 2:
        proc = subprocess.Popen([cmd, ], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        return out
    else:
        return execute_command3(cmd)


# 将datetime转为timestamp
def timestamp(dt):
    return int(timetool.mktime(dt.timetuple()))


def parseCommandArguments(args):
    arg_dict = {}
    for argument in args:
        print("argument:" + argument)
        if argument.startswith("-D"):
            arg = argument[2:]

            idx = arg.find("=")

            k = arg[0:idx]
            v = arg[idx + 1:]
            arg_dict[k] = v
    return arg_dict


def wait_until(future_timestamp):
    print("futureTimestamp %s " % future_timestamp)

    now = datetime_tool.datetime.now()
    now_timestamp = timestamp(now)

    print("nowTimestamp %s " % now_timestamp)

    if now_timestamp < future_timestamp:
        d = future_timestamp - now_timestamp
        timetool.sleep(d)


# 获取redisCluster的对象
# def getRedisCluster(redisClusterStr):
#     from rediscluster import StrictRedisCluster
#     print(redisClusterStr)
#     redisCluster = []
#     for nodePort in redisClusterStr.split(","):
#         kv = nodePort.split(":")
#         node = {"host": kv[0], "port": kv[1]}
#         redisCluster.append(node)
#
#     print(redisCluster)
#     rc = StrictRedisCluster(startup_nodes=redisCluster, decode_responses=True)
#     return rc

# mysql some operations
def getDatabase(section="mysql"):
    try:
        import configparser
        import pymysql
        config = configparser.ConfigParser()
        config.read(configuraion_file)
        host = config.get(section, "host")
        port = int(config.get(section, "port"))
        user = config.get(section, "user")
        password = config.get(section, "passwd")
        database = config.get(section, "database")
        charset = config.get(section, "charset")

        db = pymysql.connect(host=host, port=port, user=user, passwd=password, db=database, charset=charset,
                             autocommit=True,
                             cursorclass=pymysql.cursors.DictCursor)
        return db
    except ImportError:
        print("Error: configparser or pymysql module not exists")
    except Exception as e:
        logger.error(e)
        traceback.print_exc()

    return None


def query(database, sql, argumentTuple=(), timestamp2str=True, debug=True):
    import pymysql
    cursor = database.cursor()
    if debug:
        print("query sql:\t%s, arguments: %s" % (sql, argumentTuple))
    if len(argumentTuple) == 0:
        cursor.execute(sql)
    else:
        cursor.execute(sql, argumentTuple)
    rows = []

    if timestamp2str:
        timestamp_field_array = []
        for tp in cursor.description:
            if tp[1] == pymysql.constants.FIELD_TYPE.TIMESTAMP:
                timestamp_field_array.append(tp[0])

        for row in cursor:
            for field in timestamp_field_array:
                tmp_value = row[field].strftime("%Y-%m-%d %H:%M:%S")
                row[field] = tmp_value
            rows.append(row)
    else:
        for row in cursor:
            rows.append(row)
    return rows


def insert(database, tableName, dic, commit=True, debug=True):
    cursor = database.cursor()
    cols = []
    vals = []
    placeholders = []
    doc_id = ""
    for key in dic.keys():
        val = dic[key]
        if val is not None:
            cols.append(key)
            placeholders.append("%s")
            vals.append(val)
    insert_sql = "INSERT INTO " + tableName + " ( %s ) VALUES ( %s )" % (",".join(cols), ",".join(placeholders))
    if debug:
        print(insert_sql)

    if commit:
        print(tuple(vals))
        cursor.execute(insert_sql, tuple(vals))
        doc_id = cursor.lastrowid
    if commit:
        database.commit()

    return doc_id


def updateById(database, tableName, id, dic, idFieldName="id", commit=True):
    cursor = database.cursor()
    vals = []
    placeholders = []
    for key in dic.keys():
        val = dic[key]
        if val is not None:
            placeholders.append("{} = %s ".format(key))
            vals.append(val)
    setting = " , ".join(placeholders)
    vals.append(id)
    update_sql = "update {0} set {1} where {2} = %s ".format(tableName, setting, idFieldName)
    print(update_sql)

    if commit:
        print(tuple(vals))
        cursor.execute(update_sql, tuple(vals))
    if commit:
        database.commit()


def execute(database, sql, argumentTuple=(), debug=True):
    cursor = database.cursor()
    if debug:
        print("query sql:\t%s, arguments: %s" % (sql, argumentTuple))
    if len(argumentTuple) == 0:
        cursor.execute(sql)
    else:
        cursor.execute(sql, argumentTuple)


def delete(database, sql, commit=True):
    cursor = database.cursor()
    print("delete sql:\t" + sql)
    if commit:
        cursor.execute(sql)
        database.commit()


def mysql_execute(database, sql, argumentTuple, commit=True):
    cursor = database.cursor()
    if argumentTuple:
        cursor.execute(sql, argumentTuple)
    else:
        cursor.execute(sql)
    if commit:
        database.commit()


# 获取文件的创建时间
def getFileCreateTime(filePath):
    # filePath = unicode(filePath,'utf8')
    t = os.path.getctime(filePath)
    return datetime_tool.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")


# 获取文件的访问时间
def getFileAccessTime(filePath):
    # filePath = unicode(filePath,'utf8')
    t = os.path.getatime(filePath)
    return datetime_tool.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")


# 获取文件的修改时间
def getFileModifyTime(filePath):
    # filePath = unicode(filePath,'utf8')
    t = os.path.getmtime(filePath)
    return datetime_tool.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")


def getHost(url):
    begin_index = url.find("//")
    end_index = url.find("/", begin_index + 2)
    host = url[begin_index + 2:end_index]
    return host


def getHostname(url):
    begin_index = url.find("//")
    end_index = url.find(":", begin_index + 2)
    if end_index < 0:
        end_index = url.find("/", begin_index + 2)
    hostname = url[begin_index + 2:end_index]
    return hostname


def getFileSize(filePath):
    fsize = os.path.getsize(filePath)
    return fsize


def getFilePrefix(path):
    return os.path.splitext(path)[0]


def getFilePostfix(path):
    return os.path.splitext(path)[1][1:]


def getLocalHostname():
    hostname = ""
    try:
        hostname = socket.gethostname()
    except Exception as e:
        logger.debug(e)
        traceback.print_exc()
    return hostname


def getLocalIp():
    ip = ""
    try:
        # ip=socket.gethostbyname(socket.gethostname())
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
    except Exception as e:
        logger.debug(e)
        traceback.print_exc()
    return ip


def get_external_ip():
    # 这里的-s参数目的是在进行网络请求的时候禁止在控制台输出进度
    proc = subprocess.Popen(["curl -s https://api.hohode.com/ip"], stdout=subprocess.PIPE, shell=True)
    (outer_ip, err) = proc.communicate()
    if isinstance(outer_ip, bytes):
        outer_ip = outer_ip.decode("utf8")
    return outer_ip


def ding_send_text(message, token=None, mobiles=[], is_at_all=False):
    logger.warning("Sorry, this method is deprecated !")


def eweixin_send_text(message, token=None, mobiles=[], is_at_all=False):
    weixin_send_text(message, token, mobiles, is_at_all)


def weixin_send_text(message, token=None, mobiles=[], is_at_all=False):
    if not token:
        config = getConfig()
        token = config.get("eweixin", "token")
    content = "{}[{}]\n{}".format(getLocalHostname(), getLocalIp(), message)
    data = json.dumps({"msgtype": "text", "text": {"content": content, "mentioned_mobile_list": mobiles}})
    requests.post("https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=" + token, data,
                  auth=('Content-Type', 'application/json'))


def get_md5_code(content):
    """
    :param content: 原始字符串
    :return : 对原始字符串进行MD5加密的字符串
    """
    m = hashlib.md5()
    b = content.encode(encoding='utf-8')
    m.update(b)
    return m.hexdigest()


# def aes(text,apiSecret):
#     """
#     AES加密
#     :param text:text
#     :param apiSecret:apiSecret
#     :return: AES加密后的字符串
#     """
#     key = apiSecret[:16].encode('gbk')# 密匙，apiSecret的前十六位
#     iv = apiSecret[16:].encode('gbk')# 偏移量，apiSecret的后十六位
#     mycipher = AES.new(key, AES.MODE_CBC, iv)
#     # 加密的明文长度必须为16的倍数，如果长度不为16的倍数，则需要补足为16的倍数
#     # 将iv（密钥向量）加到加密的密文开头，一起传输
#     ciphertext = iv + mycipher.encrypt(text.encode())
#     e = b2a_hex(ciphertext)[32:].decode() # 加密后
#     return e  # 加密

def dejson(content):
    """
    :param content: 非标准Json字符串，像JavaScript的类Json字符串那样
    :return: 标准的Json字符串
    """
    tmp_content = re.sub("\\s+", "", content)
    tmp_content = re.sub(":'", r':"', tmp_content)
    tmp_content = re.sub("':", r'":', tmp_content)
    tmp_content = re.sub("',", r'",', tmp_content)
    tmp_content = re.sub(",'", r',"', tmp_content)
    tmp_content = re.sub("[{]'([a-zA-Z]{2,})", r'{"\1', tmp_content)

    tmp_content = re.sub("\\['", r'["', tmp_content)
    tmp_content = re.sub("'}", r'"}', tmp_content)
    tmp_content = re.sub("']", r'"]', tmp_content)

    # tmp_content = re.sub("[{]([a-zA-Z])", r'{"\1', tmp_content)
    tmp_content = re.sub("""[{]([a-zA-Z])""", r'{"\1', tmp_content)
    tmp_content = re.sub("\\b([a-zA-Z])(\\w+):", r'\1\2":', tmp_content)
    tmp_content = re.sub(",([a-zA-Z])", r',"\1', tmp_content)
    return tmp_content


class Mysql():

    def __init__(self, configuraion_file="/data/apps/public/conf.ini", section="mysql"):
        self.database = None
        try:
            config = configparser.ConfigParser()
            config.read(configuraion_file)
            host = config.get(section, "host")
            port = int(config.get(section, "port"))
            user = config.get(section, "user")
            password = config.get(section, "passwd")
            database_str = config.get(section, "database")
            charset = config.get(section, "charset")

            self.database = pymysql.connect(host=host, port=port, user=user, passwd=password, db=database_str,
                                            charset=charset, autocommit=True,
                                            cursorclass=pymysql.cursors.DictCursor)

            # def ping_mysql_loop():
            #     while True:
            #         if self.database:
            #             self.database.ping()
            #             t.sleep(10)
            #
            # logger.debug("启动定时ping的线程")
            # Thread(target=ping_mysql_loop).start()

        except ImportError:
            print("Error: configparser or pymysql module not exists")
        except Exception as e:
            logger.error(e)
            traceback.print_exc()

    def query(self, sql, argumentTuple=(), timestamp2str=True):
        # self.database.ping()
        cursor = self.database.cursor()
        logger.debug("query sql:\t%s, arguments: %s" % (sql, argumentTuple))
        if len(argumentTuple) == 0:
            cursor.execute(sql)
        else:
            cursor.execute(sql, argumentTuple)
        rows = []

        if timestamp2str:
            timestamp_field_array = []
            for tp in cursor.description:
                if tp[1] == pymysql.constants.FIELD_TYPE.TIMESTAMP:
                    timestamp_field_array.append(tp[0])

            for row in cursor:
                for field in timestamp_field_array:
                    tmp_value = row[field].strftime("%Y-%m-%d %H:%M:%S")
                    row[field] = tmp_value
                rows.append(row)
        else:
            for row in cursor:
                rows.append(row)
        return rows

    def insert(self, tableName, dic, commit=True):
        # self.database.ping()
        cursor = self.database.cursor()
        cols = []
        vals = []
        placeholders = []
        id = ""
        for key in dic.keys():
            val = dic[key]
            if val is not None:
                cols.append(key)
                placeholders.append("%s")
                vals.append(val)
        insert_sql = "INSERT INTO " + tableName + " ( %s ) VALUES ( %s )" % (",".join(cols), ",".join(placeholders))
        logger.debug(insert_sql)

        if commit:
            logger.debug(tuple(vals))
            cursor.execute(insert_sql, tuple(vals))
            id = cursor.lastrowid
        if commit:
            self.database.commit()

        return id

    def update_by_id(self, tableName, id, dic, idFieldName="id", commit=True):
        # self.database.ping()
        cursor = self.database.cursor()
        vals = []
        placeholders = []
        for key in dic.keys():
            val = dic[key]
            if val is not None:
                placeholders.append("{} = %s ".format(key))
                vals.append(val)
        setting = " , ".join(placeholders)
        vals.append(id)
        update_sql = "update {0} set {1} where {2} = %s ".format(tableName, setting, idFieldName)
        logger.debug(update_sql)

        if commit:
            logger.debug(tuple(vals))
            cursor.execute(update_sql, tuple(vals))
        if commit:
            self.database.commit()

    def execute(self, sql, argumentTuple=(), commit=True):
        # self.database.ping()
        cursor = self.database.cursor()
        logger.debug("query sql:\t%s, arguments: %s" % (sql, argumentTuple))
        if len(argumentTuple) == 0:
            cursor.execute(sql)
        else:
            cursor.execute(sql, argumentTuple)
        if commit:
            self.database.commit()

    def delete(self, sql, commit=True):
        # self.database.ping()
        cursor = self.database.cursor()
        logger.debug("delete sql:\t" + sql)
        if commit:
            cursor.execute(sql)
            self.database.commit()

    # Bulk Insert
    def bulk_insert(self, table_name, field_array, values_array, batch_size=100):
        field_line = ",".join(field_array)
        placeholder = ",".join(list(map(lambda x: "%s", field_array)))
        logger.info("insert bulk data ")
        ql = "INSERT INTO {} ({}) values ({})".format(table_name, field_line, placeholder)
        logger.debug(ql)
        cursor = self.database.cursor()
        for start in range(0, len(values_array), batch_size):
            logger.debug(values_array[start:start + batch_size])
            cursor.executemany(ql, values_array[start:start + batch_size])
            self.database.commit()

    # Bulk Insert
    def bulk_insert2(self, table_name, data, batch_size=100):
        """
        :param table_name: table name
        :param data:  object array
        :param batch_size: size of batch to commit
        :return:
        """
        field_array = data[0].keys()
        field_line = ",".join(field_array)
        placeholder = ",".join(list(map(lambda x: "%s", field_array)))
        logger.info("insert bulk data ")
        ql = "INSERT INTO {} ({}) values ({})".format(table_name, field_line, placeholder)
        logger.debug(ql)

        values_array = []
        for row in data:
            tmp_ar = []
            for i in field_array:
                val = row.get(i)
                tmp_ar.append(val)
            values_array.append(tmp_ar)
        print(values_array)
        cursor = self.database.cursor()
        for start in range(0, len(values_array), batch_size):
            logger.debug(values_array[start:start + batch_size])
            cursor.executemany(ql, values_array[start:start + batch_size])
            self.database.commit()