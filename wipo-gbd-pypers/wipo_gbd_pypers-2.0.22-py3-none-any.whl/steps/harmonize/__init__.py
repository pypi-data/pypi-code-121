from os.path import realpath, dirname
from pypers import import_all

"""
This function will return the merged value of data_files and img_files into
one dict with a key of appnum and data and(or) img as value.
data with no st13 and img with no crc will be ignored
"""
# [{ "appnum": _,
#    "data": { "gbd": _, "ori": _, "qc" : [], "st13": _},
#    "img": [{ "crc": _, "high": _, "icon" : [], "ori": _, "thum": ...} ...]}
#  { ... }]
def merge_data_img_files(data_files, img_files):
    # group data by app_num
    appnum_files = {}
    for appnum, item in data_files.items():
        # skip not transformed
        if not item.get('st13', None):
            continue
        appnum_files.setdefault(appnum, {})
        appnum_files[appnum]['appnum'] = appnum
        appnum_files[appnum]['data'] = item

    for appnum, item in img_files.items():
        # a logo with no record => useless
        if not appnum_files.get(appnum):
            continue
        for i, img in enumerate(item):
            # skip not transformed
            if not img.get('crc', None):
                del item[i]
        appnum_files[appnum]['img'] = item

    return appnum_files

# Import all Steps in this directory.
import_all(namespace=globals(), dir=dirname(realpath(__file__)))

