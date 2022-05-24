import time

import pymongo

from re_common.baselibrary.utils.basepymongo import BasePyMongo

basemongo = BasePyMongo("mongodb://cjrw:vipdatacenter@192.168.31.166:27017/")
basemongo.use_db("collection")
basemongo.create_col("jss_w_f_panternt_page")
starttime = time.time()
print(basemongo.delete_col())

print(time.time() - starttime)
# dicts = {
#   "cid": "string",
#   "pagenum": "string",
#   "down_date": "string",
#   "html": "string",
#   "types": "string"
# }
# basemongo.insert_one(dicts)
