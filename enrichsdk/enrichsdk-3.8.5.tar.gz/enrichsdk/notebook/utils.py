import os
from shutil import copyfile, copy


def create_dir(dest_dir):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)


def accepted_types():
    return ["csv", "tsv"]
