from setuptools import setup,find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path
# from rp import *
here=path.abspath(path.dirname(__file__))
print("HERE IS " + here)
# quit()

def get_all_files_in_folder_recursively(folder):
    import os, glob
    #https://stackoverflow.com/questions/2212643/python-recursive-folder-read
    for filename in glob.iglob(os.path.join(folder,'**','*'),recursive=True):
        yield filename

def non_python_files(relative_folder_path):
    folder_path=path.join(here,relative_folder_path)
    return [path for path in get_all_files_in_folder_recursively(folder_path) if not path.endswith('.py')]

def string_to_text_file(file_path,string,):
    file=open(file_path,"w")
    try:
        file.write(string)
    except:
        file=open(file_path,"w",encoding='utf-8')
        file.write(string,)

    file.close()
def text_file_to_string(file_path):
    return open(file_path).read()
import os

def version():
    version_path=os.path.join(here,'rp/version.py')
    i=int(text_file_to_string(version_path))
    return str(i)

def get_all_packages():
    return open(os.path.join(here,'rp/list_of_modules.py')).read().split('\n')

print('-' * 60)
print('ALL PACKAGES:')
print('\n'.join(get_all_packages()))
print('-' * 60)

# Get the long description from the relevant file
with open(path.join(here,'README'),encoding='utf-8') as f:
    long_description=f.read()

setup(
    # region
    # TODO: FIX PYFLANN  at libs/pyflann It doens't include the directories we need (ones that dont have python files in them) In fact, it really doesn't include ANY non-.py files. Which is an issue because pyflann needs the binaries included.
    setup_requires=['setuptools_scm'],  # on the publisher's end: pip install setuptools_scm
    package_data={'': [
        *non_python_files('rp/libs/jedi'), #Its annoying but I have to include my own old version of JEDI in rp, otherwise rp will break due to jedi deprecations
        *non_python_files('rp/libs/parso'), #Because the new parso >0.7 is bad for rp, we include this too. Its used in JEDI and ptpython

    ]},
    # include_package_data=True, ##<-------- KEEP THIS LINE TURNED OFF OR ELSE NON-PYTHON FILES WONT BE COPIED!! https://stackoverflow.com/questions/29036937/how-can-i-include-package-data-without-a-manifest-in-file
    # endregion
    name='rp',
    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # http://packaging.python.org/en/latest/tutorial.html#version
    version='0.1.' + version(),
    description='Ryan\'s Python',
    url='https://github.com/RyannDaGreat/Quick-Python',
    author='Ryan Burgert',
    author_email='ryancentralorg@gmail.com',
    # license='Maybe MIT? trololol no licence 4 u! (until i understand what *exactly* it means to have one)',
    keywords='not_searchable_yet_go_away_until_later_when_this_is_polished',
    packages=get_all_packages(),
    # ["rp",
    #  'rp.rp_ptpython',
    #  'rp.prompt_toolkit',
    #  "rp.prompt_toolkit.clipboard",
    #  "rp.prompt_toolkit.contrib",
    #  "rp.prompt_toolkit.contrib.completers",
    #  "rp.prompt_toolkit.contrib.regular_languages",
    #  "rp.prompt_toolkit.contrib.telnet",
    #  "rp.prompt_toolkit.contrib.validators",
    #  "rp.prompt_toolkit.eventloop",
    #  "rp.prompt_toolkit.filters",
    #  "rp.prompt_toolkit.key_binding",
    #  "rp.prompt_toolkit.key_binding.bindings",
    #  "rp.prompt_toolkit.layout",
    #  "rp.prompt_toolkit.styles",
    #  "rp.prompt_toolkit.terminal",
    #  "rp.libs.pyflann",
    #  "rp.libs.super_mario",
    #  "rp.libs.pyflann.io",
    #  "rp.libs.pyflann.util",
    #  "rp.rp_ptpdb",
    #  "rp.libs.pyflann.bindings",
    #  ]
    # ,
    install_requires=[
        'wcwidth',  # ?
        # 'xonsh>=0.9.11',#For SHELL. Xonsh is finicky about it's version of prompt toolkit and pygments, apparently.
        # 'prompt-toolkit>=2.0.10'#Also for Xonsh...this isn't worth crashing over...
        'pygments',  # Needed for xonsh
        'six',  # Not sure what needs this but its required
        'stackprinter',  # For MMORE
        'inflect',  # For some fancy completions plural ist comprehensoins
        # 'jedi',  # Needed otherwise pseudoterminal doesnt do completions
        "doge",  # For lolz cause why not
        # 'parso', #For rp.libs.jedi -- now this is bundled into rp
        'dill', #For the pseudo_terminal to run properly
    ],
    entry_points=
    {
        'console_scripts':['rp = rp.__main__:main']
    },
)
# TODO: This is good for some computers:
# alias rp="python3 -c 'import rp                         
# rp.pseudo_terminal()'"
