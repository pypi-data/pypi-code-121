from os.path import realpath, dirname
from pypers import import_all


def walker(r, d, files, sub_folders, unused):
    # skip application images -- not necessary
    data_files = [f for f in files if f.startswith('DATA-')]
    if len(data_files):
        sub_folders.append(r)


def get_sub_folders(obj):
    data = obj.get_xmls_files_with_path(walker)
    sub_folders = data[0]
    sub_folders.sort()
    obj.logger.info('extracted << %s >> folders' % len(sub_folders))
    return sub_folders


# Import all Steps in this directory.
import_all(namespace=globals(), dir=dirname(realpath(__file__)))
