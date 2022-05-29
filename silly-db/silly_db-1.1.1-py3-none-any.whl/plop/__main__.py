import sys
import os
import platform
import shutil

from silly_db.helpers import set_executable


help = """
PLOP
Provide a Local Operationnal Pack

'python3 -m silly_db.plop [option]'

options are:


[db]
provides::
- a 'database' directory containing:
    - a 'migrations' directory containing 2 examples: inital.sql, populate.sql
- a 'main_example.py' that could be a starting point for your project.
"""

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
cwd = os.getcwd()
this_os = platform.system()


def get_db():
    """Copy a starter kit in the working directory in a more convenient
    way for work"""
    shutil.copy(BASE_DIR+'/db/main_example.py', cwd)
    shutil.copytree(
        BASE_DIR+'/db/database', os.path.join(cwd, "database"))
    print("files successfully acquired")
    # if not running windows, set executable:
    if not this_os.lower().startswith("w"):
        set_executable(os.path.join(cwd, 'main_example.py'))


options = {
    'db': get_db,
}


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print(help)

    if len(sys.argv) == 2:
        arg = sys.argv[1].lower()
        if arg not in options:
            print("invalid option given to silly_db.plop")
            print(help)
        else:
            options[arg]()
