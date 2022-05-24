from re_common.baselibrary.utils.basefile import BaseFile

from re_common.facade.mysqlfacade import MysqlUtiles


def get_rawid_from_mysql():
    strings = """
            host = 192.168.31.209
            user = root
            passwd = vipdatacenter
            db = cnki_qk
            port = 3306
            chartset = utf8
            """
    mysqlrawid = r"F:\fun2\mysqlrawid.txt"
    feilds = "filename"

    dicts_change = {"key为原来的": "values为现在的"}

    from re_common.baselibrary.tools.stringtodicts import StringToDicts

    dicts = StringToDicts().string_to_dicts_by_equal(strings)
    mysqlutils = MysqlUtiles("", "", builder="MysqlBuilderForDicts", dicts=dicts)
    offset = 0
    limit = 1000000
    while True:
        bools, raws = mysqlutils.SelectFromDB("select `{}` from article limit {},{}".format(feilds, offset, limit))
        if len(raws) == 0:
            break
        with open(mysqlrawid, 'w', encoding="utf-8") as f:
            for row in raws:
                f.write(row[0] + "\n")
        offset = offset + limit


# get_rawid_from_mysql()
# print(BaseFile.get_file_line_num(r'C:\Users\xuzhu\Downloads\part-r-00000'))

def read_files_compose():
    """
    读取两个文件对比
    :return:
    """
    sets1 = set()
    sets2 = set()
    for value in BaseFile.read_file_r_mode_yield(r'C:\Users\xuzhu\Downloads\part-r-00000'):
        sets2.add(value)

    for value in BaseFile.read_file_r_mode_yield(r'F:\fun2\mysqlrawid.txt'):
        sets1.add(value)
    set3 = sets1 - sets2
    cha = r"F:\fun2\cha.txt"
    with open(cha, 'w', encoding="utf-8") as f:
        for row in set3:
            f.write(row + "\n")


#read_files_compose()

def set_stat():
    strings = """
               host = 192.168.31.209
               user = root
               passwd = vipdatacenter
               db = cnki_qk
               port = 3306
               chartset = utf8
               """
    charawid = r"F:\fun2\cha.txt"

    dicts_change = {"key为原来的": "values为现在的"}

    from re_common.baselibrary.tools.stringtodicts import StringToDicts

    dicts = StringToDicts().string_to_dicts_by_equal(strings)
    mysqlutils = MysqlUtiles("", "", builder="MysqlBuilderForDicts", dicts=dicts)
    lists = []
    for values in BaseFile.read_file_r_mode_yield(charawid):
        lists.append(values)
        if len(lists) > 100000:
            sql = "update article set stat=0,ref_stat=0 where filename in {}".format(tuple(lists))
            mysqlutils.ExeSqlToDB(sql)
            lists.clear()

    if len(lists) > 0:
        if len(lists) == 1:
            lists.append("test")
        sql = "update article set stat=0,ref_stat=0 where filename in {}".format(tuple(lists))
        mysqlutils.ExeSqlToDB(sql)
        lists.clear()

set_stat()