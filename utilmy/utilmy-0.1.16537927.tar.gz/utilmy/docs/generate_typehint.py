# -*- coding: utf-8 -*-
MNAME = "utilmy.docs.generate_typehint"
HELP  = """ Utils for type generation


  test files via monkeytype run MY_SCRIPT.py command
  That create SQLite3 DB locally and stores dtypes of variables
    then to apply it for a files I was using: monkeytype apply MY_SCRIPT
  documentation here: https://pypi.org/project/MonkeyType/


"""
import os, sys, time, datetime,inspect, json, yaml, gc, glob, pandas as pd, numpy as np
from box import Box

import subprocess, shutil, re, sysconfig
from ast import literal_eval
from email.policy import default


## required if we want to annotate files in site-packages
os.environ["MONKEYTYPE_TRACE_MODULES"] = 'utilmy,site-packages'

###################################################################################
from utilmy import log, log2, os_makedirs
import utilmy
def help():
    """function help.
    Doc::
            
            Args:
            Returns:
                
    """
    from utilmy import help_create
    print( help_create(__file__) )


####################################################################################
def test_all():
  """function test_all.
  Doc::
          
        Args:
        Returns:
            
  """
  test1()


def test1():
  """function test1.
  Doc::
          
        Args:
        Returns:
            
  """
  log(utilmy.__file__)

  exclude = ""; nfile= 10
  dir0   = os.getcwd()
  dirin  = dir0 + "/utilmy/tabular/" 
  dirout = dir0 + "/docs/types/"
  diroot = dir0        
  dirin = dirin.replace("\\", "/") + '/'

  run_monkeytype(dirin, dirout, mode='full,stub', diroot=diroot, nfile=3, exclude="sparse" )
  os.system( f"ls {dirout}/")


def run_utilmy(nfile=10000):
  """function run_utilmy.
  Doc::
          
        Args:
            nfile:   
        Returns:
            
  """
  log(utilmy.__file__)
  exclude = "";
  dir0   = os.getcwd()
  dirin  = dir0 + "/utilmy/" 
  dirout = dir0 + "/docs/types/"
  diroot = dir0        
  dirin = dirin.replace("\\", "/") + '/'

  run_monkeytype(dirin, dirout, mode='full,stub', diroot=diroot, nfile=nfile, exclude="z" )
  os.system( f"ls {dirout}/")



def run_utilmy_overwrite(nfile=100000):
  """function run_utilmy2.
  Doc::
          
        Args:
            nfile:   
        Returns:
            
  """
  log('OVERWRITE FILES')
  exclude = ""; 
  dir0   = os.getcwd()
  dirin  = dir0 + "/utilmy/" 
  dirout = dir0 + "/utilmy/"
  diroot = dir0        
  dirin = dirin.replace("\\", "/") + '/'

  log("dirin0: ", dirin)

  run_monkeytype(dirin, dirout, mode='full,overwrite', diroot=diroot, nfile=nfile, exclude="/z" )
  os.system( f"ls {dirout}/")



def test2():
  """function test2.
  Doc::
          
        Args:
        Returns:
            
  """
  log(utilmy.__file__)

  dir0 = utilmy.__file__.replace("\\","/") 
  dir0 = "/".join( dir0.split("/")[:-2])  +"/"
  log(dir0)
  os.chdir(dir0)

  dirin  = "utilmy/tabular/" 
  dirout = "docs/stub/"

  run_monkeytype(dirin, dirout, mode='stub', diroot=None, nfile=10, exclude="sparse" )
  os.system( f"ls {dirout}/")



def os_path_norm(diroot):
    """function os_path_norm.
    Doc::
            
            Args:
                diroot:   
            Returns:
                
    """
    diroot = diroot.replace("\\", "/")
    return diroot + "/" if diroot[-1] != "/" else  diroot



def glob_glob_python(dirin, suffix ="*.py", nfile=7, exclude=""):
    """function glob_glob_python.
    Doc::
            
            Args:
                dirin:   
                suffix :   
                nfile:   
                exclude:   
            Returns:
                
    """
    flist = glob.glob(dirin + suffix) 
    flist = flist + glob.glob(dirin + "/**/" + suffix ) 
    if exclude != "":
      flist = [ fi for fi in flist if exclude not in fi ]
    flist = flist[:nfile]
    log(flist)
    return flist


def run_monkeytype(dirin:str, dirout:str, diroot:str=None, mode="stub", nfile=10, exclude="" ):
    """Generate type hints for files.
    Doc::
            
                  Args:
                      dirin (str): _description_
                      dirout (str): _description_
                      diroot (str, optional): _description_. Defaults to None.
                      mode (str, optional): _description_. Defaults to "stub".
                      nfile (int, optional): _description_. Defaults to 10.
                      exclude (str, optional): _description_. Defaults to "".
                    exclude = ""; nfile= 10
                    dir0 = os.getcwd()
                    dirin  = dir0 + "/utilmy/tabular/" 
                    dirout = dir0 + "/docs/stub/"
                    diroot = dir0        
                    dirin = dirin.replace("\\", "/") + '/'
    """   

    import os, sys
    os.makedirs(dirout, exist_ok=True)
    #if "utilmy." in dirin :
    #    dir0 =  os.path.dirname( utilmy.__file__) + "/"        
    #    dirin = dir0 +  dirin.replace("utilmy", "").replace(".", "/").replace("//","/")

    diroot = os.getcwd()  if diroot is None else diroot
    diroot = os_path_norm(diroot)

    log("dirin:", dirin)

    
    flist = glob_glob_python(dirin, suffix ="*.py", nfile=nfile, exclude=exclude)

    for fi0 in flist :
      try :
        log(f"\n\n\n\n\n\n\n####### Processing file {fi0} ###########")
        fi      = fi0.replace("\\", "/")
        fi_dir  = os.path.dirname(fi).replace("\\", "/")  + "/"

        ### Relative to module root path
        fi_pref  = fi.replace(diroot, "")
        mod_name = fi_pref.replace(".py","").replace("/",".")
        mod_name = mod_name[1:] if mod_name[0] == "." else mod_name
        log(f'fi_dir : {fi_dir},  {fi_pref}')


        log(f"#### Runing Monkeytype to get traces database")
        fi_monkey = os.getcwd() + '/ztmp_monkey.py'
        ### Monkeytype require using temporary runner script to import packages (Not necessary if the file is a pytest) 
        with open( fi_monkey, mode='w' ) as fp :
          fp.write( f"import {mod_name}  as mm ; mm.test_all()" )

        # run monkeytype on temporary script
        os.system(f"monkeytype run ztmp_monkey.py"  )


        log(f"###### Generate output in mode {mode}")
        ### copy sqlite traces database where our file is located
        try:  
          shutil.move("monkeytype.sqlite3", fi_dir + "monkeytype.sqlite3" ) 
        except: pass

        dircur = os.getcwd()
        os.chdir(fi_dir)

        if "full" in mode :  #### Overwrite
            
            dirouti     = dirout +"/full/"+ fi_pref if 'overwrite' not in mode  else dirout +"/"+ fi_pref.replace("/utilmy/", "/") 
            dirouti_tmp = dirouti.replace(".py",  "_tmp.py")
            
            os_makedirs(dirouti)
            cmd = f'monkeytype apply {mod_name} > {dirouti_tmp} 2>&1' 
            subprocess.call(cmd, shell=True)

            isok = os_file_compile_check(dirouti_tmp)
            if isok :
              if os.path.exists(dirouti): os.remove(dirouti)
              os.remove(dirouti)
              os.rename(dirouti_tmp, dirouti)
            else :
              os.remove(dirouti_tmp)


        if "stub" in mode:
            dirouti = dirout +"/stub/"+ fi_pref.replace(".py", ".pyi")
            os_makedirs(dirouti)       
            cmd = f'monkeytype stub {mod_name} > {dirouti} 2>&1' 
            subprocess.call(cmd, shell=True)

        log(f"####### clean up")
        try :
          os.remove(f'{fi_dir}/monkeytype.sqlite3' )
          os.remove(fi_monkey)
        except : pass  
        os.chdir( dircur )

      except Exception as e :
         log(e)





if 'utilties':
    def os_path_norm(diroot:str):
        """os_path_norm 
        Args:
            diroot:
        Returns:
            _description_
        """
        diroot = diroot.replace("\\", "/")
        return diroot + "/" if diroot[-1] != "/" else  diroot


    def glob_glob_python(dirin, suffix ="*.py", nfile=7, exclude=""):
        """glob_glob_python 
        Args:
            dirin: _description_
            suffix: _description_. Defaults to "*.py".
            nfile: _description_. Defaults to 7.
            exclude: _description_. Defaults to "".

        Returns:
            _description_
        """
        import glob
        dirin = str(dirin)
        flist = glob.glob(dirin + suffix) 
        flist = flist + glob.glob(dirin + "/**/" + suffix ) 
        elist = []
        
        if exclude != "":    
           for ei in exclude.split(";"):
               elist = glob.glob(ei + "/" + suffix ) 
        flist = [ fi for fi in flist if fi not in elist ]

        #### Unix format 
        flist = [  fi.replace("\\", "/") for fi in flist]

        flist = flist[:nfile]
        log(dirin, flist)
        return flist

    def os_makedirs(filename):
        if isinstance(filename, str):
            filename = [os.path.dirname(filename)]

        if isinstance(filename, list):
            folder_list = filename
            for f in folder_list:
                try:
                    if not os.path.exists(f):
                        os.makedirs(f)
                except Exception as e:
                    print(e)
            return folder_list



    #############################################################################################
    def os_file_compile_check_batch(dirin:str, nfile=10) -> dict:
        """ check if .py can be compiled
        """
        flist   = glob_glob_python( dirin, "*.py",nfile= nfile)
        results = []
        for fi in flist :
            res = os_file_compile_check(fi)
            results.append(res)

        #results = [os.system(f"python -m py_compile {i}") for i in flist]
        results = { flist[i]:  results[i] for i in range(len(flist)) }
        return results


    def os_file_compile_check(filename:str, verbose=1):
        """ check if .py can be compiled

        """
        import ast, traceback
        try : 
            with open(filename, mode='r') as f:
                source = f.read()
            ast.parse(source)
            return True
        except Exception as e:
            if verbose >0 : 
                print(e)
                traceback.print_exc() # Remove to silence any errros
        return False


    def os_file_compile_check_ovewrite(filei:str, filei_tmp:str):
        """

        """
        isok = os_file_compile_check(file_tmp, verbose=0)   
        log('compile', isok)
        if isok :
            if os.path.exists(filei): os.remove(filei)
            os.rename(filei, filei_tmp)
        else :
            os.remove(filei_tmp)






################################################################################
################################################################################
if __name__ == '__main__':
  import fire 
  fire.Fire()
 