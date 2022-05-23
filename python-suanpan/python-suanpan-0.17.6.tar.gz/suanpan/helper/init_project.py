import os
import shutil


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def init_project(project_name, code_format=''):
    if not code_format:
        print('choose a code format!')
        return

    root = os.path.abspath(os.path.dirname(__file__))
    src = os.path.join(root, 'example', code_format)
    dest = os.path.abspath(os.curdir)
    if project_name:
        dest = os.path.join(dest, project_name)

        if os.path.exists(dest):
            print(f'folder {project_name} is not empty!')
            return
    else:
        # init in current path
        if any(os.scandir(dest)):
            print('current folder is not empty!')
            return

    copytree(src, dest)
