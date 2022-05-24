from os.path import realpath, dirname
from pypers import import_all

"""
return a dictionary containing img idx
that needs to be merged in data idx
"""
# img_files  [ {'st13': _, 'crc': _, 'idx': _},
#              {'st13': _, 'crc': _, 'idx': _} ]
# data_files [ {'st13': _, 'latest': _, 'idx': _},
#              {'st13': _, 'latest': _, 'idx': _} ]
#
# return { st13: { idx_img: _, idx_data: _, latest: _ },
#          st13: { idx_img: _, idx_data: _, latest: _ }
def merge_data_img_files(data_files, img_files):
    # group data by app_num
    st13_files = {}
    for img_record in img_files:
        st13 = img_record['st13']
        if not st13_files.get(st13):
            st13_files[st13] = {
                'idx_data': None,
                'latest': None,
                'idx_img': []
            }

        st13_files.setdefault(st13, {})
        st13_files[st13]['idx_img'].append(img_record['idx'])

    for data_record in data_files:
        st13 = data_record['st13']
        if not st13_files.get(st13):
            st13_files[st13] = {
                'idx_data': None,
                'latest': None,
                'idx_img': []
            }
        st13_files[st13]['idx_data'] = data_record['idx']
        st13_files[st13]['latest'] = data_record['latest']

    return st13_files

# Import all Steps in this directory.
import_all(namespace=globals(), dir=dirname(realpath(__file__)))

