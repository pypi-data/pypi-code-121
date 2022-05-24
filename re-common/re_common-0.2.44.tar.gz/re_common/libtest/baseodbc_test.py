from re_common.baselibrary.utils.baseodbc import BaseODBC

baseodbc = BaseODBC(r"C:\Users\xuzhu\Desktop\DB_20200701_GB.mdb")
# baseodbc = BaseODBC(r"D:\download\cnki_qk\download\get_journal\mdb\cnki期刊信息_20200315.mdb")
baseodbc.get_cur()
sql = "select * from `CN`"
for row in baseodbc.select(sql):
    print(row)