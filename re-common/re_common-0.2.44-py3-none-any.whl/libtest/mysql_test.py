from re_common.baselibrary.utils.basefile import BaseFile

from re_common.facade.mysqlfacade import MysqlUtiles

from re_common.baselibrary.utils.basedir import BaseDir
from re_common.facade.loggerfacade import get_streamlogger

curPath = BaseDir.get_file_dir_absolute(__file__)


def test_mysql_create():
    """
    创建表 pytest mysql_test.py::test_mysql_create -s
    :return:
    """
    mysqls = MysqlUtiles(BaseFile.get_new_path(curPath, "mysql.ini"), "db", get_streamlogger())
    sql = """
CREATE TABLE `test1` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `username` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户名',
  `passwd` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '密码',
  `only` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '唯一性约束',
  PRIMARY KEY (`id`),
  UNIQUE KEY `only` (`only`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    bool, msg = mysqls.ExeSqlToDB(sql)


def test_mysql_insert():
    """
    插入表 更新删除都可以使用ExeSqlToDB这个函数
    pytest mysql_test.py::test_mysql_insert -s
    :return:
    """
    mysqls = MysqlUtiles(BaseFile.get_new_path(curPath, "mysql.ini"), "db", get_streamlogger())
    sql = "INSERT INTO mysqlltest.test1 (username, passwd, `only`) VALUES('test1', 'test1', 'test1');"
    bool, msg = mysqls.ExeSqlToDB(sql, errExit=False)
    print(bool)
    print(msg)


def test_mysql_insert_list():
    """
    插入表 pytest mysql_test.py::test_mysql_insert_list -s
    :return:
    """
    listsql = []
    mysqls = MysqlUtiles(BaseFile.get_new_path(curPath, "mysql.ini"), "db", get_streamlogger())
    sql = "INSERT INTO mysqlltest.test1 (username, passwd, `only`) VALUES('%s', '%s', '%s');"
    for i in range(100):
        temp = sql % (i, i, i)
        listsql.append(temp)
    bool, successcount, errcount = mysqls.ExeSqlListToDB(listsql, errExit=False)
    print(bool)
    print(successcount)
    print(errcount)
    bool, successcount, errcount = mysqls.ExeSqlListToDB(listsql, errExit=True)
    print(bool)
    print(successcount)
    print(errcount)


def test_mysql_select():
    """
    查询数据 pytest mysql_test.py::test_mysql_select -s
    :return:
    """
    listsql = []
    mysqls = MysqlUtiles(BaseFile.get_new_path(curPath, "mysql.ini"), "db", get_streamlogger())
    sql = "SELECT * FROM test1"
    bool, rows = mysqls.SelectFromDB(sql)
    print(bool)
    print(rows)


def test_mysql_select_dicts():
    """
    查询数据 返回dicts 形式的数据
    pytest mysql_test.py::test_mysql_select_dicts -s
    :return:
    """
    listsql = []
    mysqls = MysqlUtiles(BaseFile.get_new_path(curPath, "mysql.ini"), "db", get_streamlogger(), cursorsnum=1)
    sql = "SELECT * FROM test1"
    bool, rows = mysqls.SelectFromDB(sql)
    print(bool)
    print(rows)


def test_mysql_select_one():
    """
    查询数据只返回一条数据
    pytest mysql_test.py::test_mysql_select_one -s
    :return:
    """
    listsql = []
    mysqls = MysqlUtiles(BaseFile.get_new_path(curPath, "mysql.ini"), "db", get_streamlogger())
    sql = "SELECT * FROM test1"
    bool, rows = mysqls.SelectFromDBFetchOne_noyield(sql)
    print(bool)
    print(rows)


def test_mysql_select_one_yeild():
    """
    查询数据 以yeild循环返回
    pytest mysql_test.py::test_mysql_select_one_yeild -s
    :return:
    """
    listsql = []
    mysqls = MysqlUtiles(BaseFile.get_new_path(curPath, "mysql.ini"), "db", get_streamlogger())
    sql = "SELECT * FROM test1"
    for one in mysqls.SelectFromDBFetchOne(sql):
        print(one)


def test_mysql_exesqlmany():
    """
    同时插入多条数据
    pytest mysql_test.py::test_mysql_exesqlmany -s
    :return:
    """
    listpara = []
    mysqls = MysqlUtiles(BaseFile.get_new_path(curPath, "mysql.ini"), "db", get_streamlogger())
    sql = "INSERT INTO mysqlltest.test1 (username, passwd, `only`) VALUES(%s, %s, %s);"
    for i in range(101, 201):
        listpara.append((i, i, i))
    bool, rows = mysqls.ExeSqlMany(sql, listpara)
    print(bool)
    print(rows)


test_mysql_exesqlmany()


def test_dict_mysql():
    strings = """
            host = 192.168.31.209
            user = root
            passwd = vipdatacenter
            db = data_gather_record
            port = 3306
            chartset = utf8
            """

    dicts_change = {"key为原来的": "values为现在的"}

    from re_common.baselibrary.tools.stringtodicts import StringToDicts
    dicts = StringToDicts().string_to_dicts_by_equal(strings)
    mysqlutils = MysqlUtiles("", "", builder="MysqlBuilderForDicts", dicts=dicts)
