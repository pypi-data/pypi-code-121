import argparse, os, sys

# redifine path
sys.path.append('../')
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.getcwd())

from alphaz.libs import test_lib
from alphaz.utils.selectionMenu import SelectionMenu

from core import core
api = core.api

MENU_PARAMETERS = {
    "selections": [
        {'header':"TESTS"},
        {   
            'name':'all_tests',
            'description':"All tests mode",
            "selections": ['execute','save'],
            "after": {
                "function":{
                    'method':test_lib.operate_all_tests_auto,
                    'kwargs':{
                        'directory':core.config.get(['tests','auto_directory']),
                        "import_path": core.config.get(['tests','auto_import']),
                        'output':True,
                        'verbose':True,
                        'action':"{{selected}}",
                    }
                }
            }
        },
    ]                 
}

if __name__ == "__main__":
    parser          = argparse.ArgumentParser(description='Alpha')
    parser.add_argument('--configuration', '-c', help='Set configuration')

    args            = parser.parse_args()

    m                       = SelectionMenu("Alpha",MENU_PARAMETERS,save_directory= core.config.get(["menus","save_directory"]))
    m.run()