from rp import *
def get_all_packages():
    #EXAMPLE: print('\n'.join(get_all_packages())) --->
    # rp.junk
    # rp.rp_ptpython
    # rp.prompt_toolkit
    # rp.rp_ptpdb
    # rp.libs.tetris
    # rp.libs.super_mario
    # rp.libs.pyflann
    # rp.libs.tetris.graphics
    # rp.libs.tetris.graphics.examples
    # rp.libs.tetris.graphics.graphics
    # rp.libs.pyflann.util
    # rp.libs.pyflann.io
    # rp.libs.pyflann.bindings
    # rp.prompt_toolkit.filters
    # rp.prompt_toolkit.layout
    # rp.prompt_toolkit.terminal
    # rp.prompt_toolkit.contrib
    # rp.prompt_toolkit.key_binding
    # rp.prompt_toolkit.styles
    # rp.prompt_toolkit.eventloop
    # rp.prompt_toolkit.clipboard
    # rp.prompt_toolkit.contrib.completers
    # rp.prompt_toolkit.contrib.regular_languages
    # rp.prompt_toolkit.contrib.validators
    # rp.prompt_toolkit.contrib.telnet
    # rp.prompt_toolkit.key_binding.bindings
    # rp
    from rp import get_file_paths,is_a_folder
    def is_a_module(path):
        path=path_join('..',path)
        path=get_absolute_path(path,)
        #print('path-',path)
        out= is_a_folder(path) and '__init__.py' in get_all_files(path,relative=True,physical=False)
        return out
    ans=get_all_paths(include_folders=True,include_files=False,recursive=True,relative='..',physical=False)
    #print(ans)
    ans=list(filter(is_a_module,ans))
    ans=[x.replace('/','.') for x in ans]
    ans+=['rp']
    return ans
set_current_directory('/Users/Ryan/PycharmProjects/QuickPython/rp')

string_to_text_file('/Users/Ryan/PycharmProjects/QuickPython/rp/list_of_modules.py',line_join(get_all_packages()))
