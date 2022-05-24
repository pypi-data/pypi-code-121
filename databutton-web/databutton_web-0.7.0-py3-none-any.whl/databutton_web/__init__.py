import os

__version__ = '0.7.0'

def get_static_file_path():
    dir_name = os.path.dirname(os.path.realpath(__file__))
    app_path = os.path.join(dir_name, 'local')
    return app_path
    