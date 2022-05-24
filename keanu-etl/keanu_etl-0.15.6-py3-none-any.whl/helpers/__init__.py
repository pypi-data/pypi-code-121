import os


def schema_path(helper_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, helper_name + ".sql")

