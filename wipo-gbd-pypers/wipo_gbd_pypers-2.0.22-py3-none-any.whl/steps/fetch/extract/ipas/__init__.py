from os.path import realpath, dirname
from pypers import import_all
import os
from pypers.utils import utils


def get_sub_folders(obj):
    obj.get_xmls_files_with_path()
    if len(obj.input_archive) == 0:
        return []
    # extraction results into a list of sub archives
    # extract those too
    sub_archives = [os.path.join(obj.dest_dir[0], sub_archive)
                    for sub_archive in os.listdir(obj.dest_dir[0])
                    if sub_archive.lower().endswith('.zip')]
    obj.logger.info('extracted << %s >> sub archives' % len(sub_archives))
    return sub_archives


def extract_sub_archive(obj, sub_archive):
    sub_archive_name = os.path.basename(sub_archive)
    sub_dest_dir = os.path.join(
        obj.dest_dir[0], os.path.splitext(sub_archive_name)[0])
    obj.logger.info('extracting %s into %s' % (sub_archive_name, sub_dest_dir))
    # extract sub archive then delete it
    utils.zipextract(sub_archive, sub_dest_dir)
    os.remove(sub_archive)
    return sub_archive_name, sub_dest_dir


# Import all Steps in this directory.
import_all(namespace=globals(), dir=dirname(realpath(__file__)))


