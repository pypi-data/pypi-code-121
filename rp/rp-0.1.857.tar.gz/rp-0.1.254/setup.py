from setuptools import setup,find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path
# from rp import *
here=path.abspath(path.dirname(__file__))
print("HERE IS "+here)
# quit()
def string_to_text_file(file_path,string,) :
    file=open(file_path,"w")
    try:
        file.write(string)
    except:
        file=open(file_path,"w",encoding='utf-8')
        file.write(string,)

    file.close()
def text_file_to_string(file_path) :
    return open(file_path).read()
import os

def version():
    version_path=os.path.join(here,'rp/version.py')
    i=int(text_file_to_string(version_path))
    return str(i)


# Get the long description from the relevant file
with open(path.join(here,'README'),encoding='utf-8') as f:
    long_description=f.read()

setup   (
    #region
        #TODO: FIX PYFLANN  at libs/pyflann It doens't include the directories we need (ones that dont have python files in them) In fact, it really doesn't include ANY non-.py files. Which is an issue because pyflann needs the binaries included.
        setup_requires=['setuptools_scm'],#on the publisher's end: pip install setuptools_scm
        include_package_data=True,
    #endregion
        name='rp',
        # Versions should comply with PEP440.  For a discussion on single-sourcing
        # the version across setup.py and the project code, see
        # http://packaging.python.org/en/latest/tutorial.html#version
        version='0.1.'+version(),
        description='Ryan\'s Python',
        url='https://github.com/RyannDaGreat/Quick-Python',
        author='Ryan Burgert',
        author_email='ryancentralorg@gmail.com',
        # license='Maybe MIT? trololol no licence 4 u! (until i understand what *exactly* it means to have one)',
        keywords='not_searchable_yet_go_away_until_later_when_this_is_polished',
        packages=["rp",
                  'rp.rp_ptpython',
                  'rp.prompt_toolkit',
                  "rp.prompt_toolkit.clipboard",
                  "rp.prompt_toolkit.contrib",
                  "rp.prompt_toolkit.contrib.completers",
                  "rp.prompt_toolkit.contrib.regular_languages",
                  "rp.prompt_toolkit.contrib.telnet",
                  "rp.prompt_toolkit.contrib.validators",
                  "rp.prompt_toolkit.eventloop",
                  "rp.prompt_toolkit.filters",
                  "rp.prompt_toolkit.key_binding",
                  "rp.prompt_toolkit.key_binding.bindings",
                  "rp.prompt_toolkit.layout",
                  "rp.prompt_toolkit.styles",
                  "rp.prompt_toolkit.terminal",
                  "rp.libs.pyflann",
                  "rp.libs.super_mario",
                  "rp.libs.pyflann.io",
                  "rp.libs.pyflann.util",
                  "rp.libs.pyflann.bindings",
                  ]
        ,
        install_requires=[
        'wcwidth',#?
        # 'xonsh>=0.9.11',#For SHELL. Xonsh is finicky about it's version of prompt toolkit and pygments, apparently.
        # 'prompt-toolkit>=2.0.10'#Also for Xonsh...this isn't worth crashing over...
        'pygments',#Needed for xonsh 
        'six',#Not sure what needs this but its required
        'stackprinter',#For MMORE
        'inflect',#For some fancy completions plural ist comprehensoins
        'jedi',#Needed otherwise pseudoterminal doesnt do completions
        "doge",#For lolz
        ],
        entry_points=
        {
            'console_scripts':['rp = rp.__main__:main']
        },
    )

#TODO: This is good for some computers:
# alias rp="python3 -c 'import rp                         
# rp.pseudo_terminal()'"


