 from re_common.baselibrary.tools.stringtodicts import StringToDicts
from re_common.facade.mysqlfacade import MysqlUtiles

"""
本方法主要用于provider 变化,有时候我们可能需要更新209的provider
用该方法更新方便快捷
"""
strings = """
        host = 192.168.31.209
        user = root
        passwd = vipdatacenter
        db = data_gather_record
        port = 3306
        chartset = utf8
        """

dicts_change = {"key为原来的": "values为现在的"}

dicts = StringToDicts().string_to_dicts_by_equal(strings)
mysqlutils = MysqlUtiles("", "", builder="MysqlBuilderForDicts", dicts=dicts)
mysqlutils.ExeSqlToDB("SET FOREIGN_KEY_CHECKS=0;")
for key, values in dicts_change:
    sql1 = "update `data_gather_record`.`task` set `provider` = '{}' WHERE `provider` = '{}';".format(values, key)
    sql2 = "update `data_gather_record`.`updating` set `provider` = '{}' WHERE `provider` = '{}';".format(values, key)
    mysqlutils.ExeSqlToDB(sql1)
    mysqlutils.ExeSqlToDB(sql2)

mysqlutils.ExeSqlToDB("SET FOREIGN_KEY_CHECKS=1;")
