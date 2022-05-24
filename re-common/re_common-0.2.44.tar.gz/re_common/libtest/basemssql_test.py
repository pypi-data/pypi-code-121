###########################################
# 同项目调用基础包
import datetime
import gzip
import json
import os
import sys
import time

filepath = os.path.abspath(__file__)
pathlist = filepath.split(os.sep)
pathlist = pathlist[:-3]
TopPath = os.sep.join(pathlist)
sys.path.insert(0, TopPath)
print(TopPath)
############################################

from re_common.baselibrary.utils.basemssql import BaseMsSql
from re_common.baselibrary.utils.basefile import BaseFile
from re_common.baselibrary.utils.basetime import BaseTime
bt = BaseTime()

host = "127.0.0.1"
user = "sa"
pwd = "xujiang1994323"
db = "patData"
charset = "utf8"

basemssql = BaseMsSql(host, user, pwd, db, charset, as_dict=True)
basemssql.conn()
basemssql.exec_select_query("select * from [dbo].[New_pattzb]")
outPathFile = r"F:\db3\patnetjson_big\jss_patent.big_json.gz"
i = 0
size = 10000
count = 2000000
outPathFile = BaseFile.get_new_filename(outPathFile, sign=".")
start = time.time()
end = False
while True:
    with gzip.open(outPathFile, 'wb') as f:
        while True:
            a = basemssql.cur.fetchmany(size=size)
            if not a:
                print(i)
                print(int(time.time() - start))
                print("break")
                end = True
                break
            for row in a:
                dicts = {}
                for k,v in row.items():
                    # print(k)
                    try:
                        v = v.encode('latin-1').decode('gbk')
                    except:
                        pass
                    if isinstance(v, datetime.datetime):
                        v = bt.datetime_to_string(v, "%Y-%m-%d %H:%M:%S")
                    dicts[k] = v
                    # print(type(v))
                # print(dicts)
                line = json.dumps(dicts,ensure_ascii=False)+"\n"
                # print(line)
                lines = line.encode(encoding="utf8")
                f.write(lines)
            i = i + size
            print(i)
            print(int(time.time() - start))
            if i >= count:
                outPathFile = BaseFile.get_new_filename(outPathFile, sign=".")
                i=0
                break
    if end:
        break



