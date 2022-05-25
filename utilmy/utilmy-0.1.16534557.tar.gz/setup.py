# pylint: disable=C0321,C0103,C0301,E1305,E1121,C0302,C0330,C0111,W0613,W0611,R1705
# -*- coding: utf-8 -*-
"""


"""
import io, os, subprocess, sys
from setuptools import find_packages, setup

######################################################################################
root = os.path.abspath(os.path.dirname(__file__))



##### Version  #######################################################################
version ='0.1.16534557'
cmdclass= None
print("version", version)



##### Requirements ###################################################################
#with open('install/reqs_image.cmd') as fp:
#    install_requires = fp.read()
install_requires = ['pyyaml', 'stdlib_list', 'python-box', 'fire' ]



###### Description ###################################################################
#with open("README.md", "r") as fh:
#    long_description = fh.read()

def get_current_githash():
   import subprocess 
   # label = subprocess.check_output(["git", "describe", "--always"]).strip();   
   label = subprocess.check_output([ 'git', 'rev-parse', 'HEAD' ]).strip();      
   label = label.decode('utf-8')
   return label

githash = get_current_githash()


#####################################################################################
ss1 = f"""

1000's of One Liner functions for 
   Visualization
   Data processing
   Data pipelining
   Batching
   Distributed compute
   Spark
   Pytorch
   Keras
   Image
   NLP Transformers
   Tabular Transformers

   
Stats usage:
   > 1 million Donwload !
   https://pepy.tech/project/utilmy


   https://pypistats.org/packages/utilmy



Details:
   https://packagegalaxy.com/python/utilmy



To get access to the docs, 
please Follow me on Github:

   https://tinyurl.com/2p848smu


Then, you will receive invite for the doc here:
   https://groups.google.com/g/utilmy




Hash:
{githash}


"""
### git hash : https://github.com/arita37/myutil/tree/{githash}

long_description = f""" ``` """ + ss1 +  """```"""



### Packages  ########################################################
packages = ["utilmy"] + ["utilmy." + p for p in find_packages("utilmy")]
#packages = ["utilmy"] + ["utilmy.viz" + p for p in find_packages("utilmy.viz")]
packages = ["utilmy"] + [ p for p in  find_packages(include=['utilmy.*']) ]
print(packages)


scripts = [     ]



### CLI Scripts  ###################################################   
entry_points={ 'console_scripts': [

    'docs      = utilmy.docs.cli:run_cli',

    'templates = utilmy.templates.cli:run_cli',

    #### generic
    'utilmy = utilmy.cli:run_cli_utilmy',


    #### generic for All code
    'utilmy2 = utilmy.cli:run_all_utilmy2',

    ###  sspark
    'sspark = utilmy.sspark.src.util_spark:run_cli_sspark',


    ###  image
    'image = utilmy.images.util_image:run_cli',

 ] }




##################################################################   
setup(
    name="utilmy",
    description="utils",
    keywords='utils',
    
    author="Nono",    
    install_requires=install_requires,
    python_requires='>=3.6.5',
    
    packages=packages,

    include_package_data=True,
    #    package_data= {'': extra_files},

    package_data={
       '': ['*','*/*','*/*/*','*/*/*/*']
    },

   
    ### Versioning
    version=version,
    #cmdclass=cmdclass,


    #### CLI
    scripts = scripts,
  
    ### CLI pyton
    entry_points= entry_points,


    long_description=long_description,
    long_description_content_type="text/markdown",


    classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Topic :: Scientific/Engineering',
          'Topic :: Scientific/Engineering :: ' +
          'Artificial Intelligence',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: ' +
          'Python Modules',
          'Topic :: Scientific/Engineering :: Information Analysis',
          'Environment :: Console',
          'Environment :: Web Environment',
          'Operating System :: POSIX',
          'Operating System :: MacOS :: MacOS X',
      ]
)



def os_bash_append(cmd):
  """  Append to bashrc
  """
  try :
    fpath = os.path.expanduser("~/.bashrc")
    with open(fpath, "r") as bashrc:
        bashrc = "".join( bashrc.readlines())

    #if cmd in bashrc :
    #    return False   #### Already exist

    with open(fpath, "at") as bashrc:
        bashrc.write("\n"+ cmd +"\n")
    return True
  except Exception as e:
    print(e)  
    return False


#### Add environemment variables  utilmy path
try :
    repopath = os.path.dirname( os.path.abspath(__file__).replace("\\", "/") )  + "/utilmy/"
    if 'win' in sys.platform :
        os.system(f" set  utilmy='{repopath}/' ")  ### Any new session
        os.system(f" setx utilmy='{repopath}/' ")  ### Current session

    elif 'linux' in sys.platform :
        os_bash_append(f"""export utilmy={repopath}/    """)
        os.system(f" export utilmy={repopath}/ ")
        print(' source  ~/.bashrc  ')

    print(" $utilmy  can be used as shortcut of the package library path for Command Line Usage")    

except :
    pass



def os_cmd_to_bashrc(cmd):
    try :
        if 'win' in sys.platform :
            os.system(f""" set  {cmd} """)  ### Any new session
            os.system(f""" setx {cmd} """)  ### Current session

        elif 'linux' in sys.platform :
            os_bash_append(f"""{cmd}""")
            print(' source  ~/.bashrc  ')

    except :
        pass


#### Spark Alias for command line
# cmd= "alias sspark='python $utilmy/sspark/src/util_spark.py '"
# os_cmd_to_bashrc(cmd)








































"""
alias sspark='python /workspace/myutil/utilmy/sspark/src/util_spark.py'


from setuptools import setup, find_packages


setup(
    name='xpdtools',
    version='0.2.0',
    packages=find_packages(),
    description='data processing module',
    zip_safe=False,
    package_data={'xpdan': ['config/*']},
    include_package_data=True,
    entry_points={'console_scripts': 'iq = xpdtools.raw_to_iq:main_cli'}
)


def main_cli(): fire.Fire(main)
    
    
"""





"""
:: Sets environment variables for both the current `cmd` window 
::   and/or other applications going forward.
:: I call this file keyz.cmd to be able to just type `keyz` at the prompt 
::   after changes because the word `keys` is already taken in Windows.

@echo off

:: set for the current window
set APCA_API_KEY_ID=key_id
set APCA_API_SECRET_KEY=secret_key
set APCA_API_BASE_URL=https://paper-api.alpaca.markets

:: setx also for other windows and processes going forward
setx APCA_API_KEY_ID     %APCA_API_KEY_ID%
setx APCA_API_SECRET_KEY %APCA_API_SECRET_KEY%
setx APCA_API_BASE_URL   %APCA_API_BASE_URL%

"""





