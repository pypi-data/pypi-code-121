from re_common.baselibrary.database.msqlite3 import Sqlite3
from re_common.baselibrary.utils.basedir import BaseDir

onepath = r"F:\db32\test\base_obj_meta_a_qkwx.cnki_qk.20200527_000.db3"
for file in BaseDir.get_dir_all_files(r"F:\db32\cnki"):
    Sqlite3.sqlite3_merge(onepath, file, tablename="base_obj_meta_a")