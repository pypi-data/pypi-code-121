import os, logging

def get_alpha_logs_root():
    current_folder  = os.path.dirname(os.path.realpath(__file__))
    dirs            = current_folder.split(os.sep)
    log_dir         = os.sep.join(dirs[:-1]) + os.sep + 'logs'
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)
    return log_dir

def check_root(root):
    if root == '':
        return root
    if root is None:
        root = get_alpha_logs_root()

    if not os.path.isdir(root):
        os.makedirs(root)
    return root

def get_level(level):
    lvl = logging.INFO 
    if level.upper() == 'ERROR':
        lvl = logging.ERROR 
    elif level.upper() == 'DEBUG':
        lvl = logging.DEBUG 
    elif level.upper() == 'WARNING':
        lvl = logging.WARNING 
    return lvl