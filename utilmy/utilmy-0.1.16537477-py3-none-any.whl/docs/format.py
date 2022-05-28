# -*- coding: utf-8 -*-
MNAME = "utilmy.docs.format"
""" A simple python module to parse the code and format it based on some rules.

Goal is to normalize all python files with similar structure.

Some rules are
    rule 1 - change a line starting with 3 #'s into x #'s where x is 90 by default
            if no text was found else preserve text and fill the rest with #'s
    rule 2 - normalize log statements in the file
    
    rule 4 - align assignment operators


### Usage
cd myutil
python utilmy/docs/format.py  test1



### TODO
   Add functions for formating functions and dictionaries






"""
import os,sys,time,gc, glob, numpy as np, pandas as pd,re, fire, tqdm, datetime
from typing import List, Optional, Tuple, Union
from box import Box


#############################################################################################
from utilmy import log, log2
def help():
    """function help """
    #from utilmy import help_create
    #print( help_create(MNAME) )



#############################################################################################
def test_all() -> None:
    """function test_all """
    log(MNAME)
    test1()
    test2()


def test1():
    """function test1   """
    import utilmy
    dirin = os.path.dirname(  utilmy.__file__ )  ### Repo Root folder
    flist = glob_glob_python(dirin,nfile=1)
    log(flist)
    os_file_compile_check_batch(flist[0])


def test2() -> None:
    """function test2   """
    import utilmy
    dirin = os.path.dirname(utilmy.__file__)  ### Repo Root folder
    dirout = os.makedirs('utilmy/docs/test/')[0] ### test dir
    reformatter(dirin,dirout)



#############################################################################################
def batch_format_file2():
     format_list= [      format_comments,
         format_logs,
         format_imports,
         format_assignments
     ]
     in_file ="utilmy/utilmy.py"
     dirout = "ztest/"
     batch_format_file(in_file, dirout, format_list)


def batch_format_file(in_file:str, dirout:str, format_list:list):
    """function batch_format_file
        
    """
    # if input is a file and make sure it exits
    if os.path.isfile(in_file):
        with open(in_file) as f:
            text = f.read()

        ######## Apply formatting ###########################################
        text_f = text
        for fun_format in  format_list :
           log(str(fun_format)) 
           text_f = fun_format(text_f)


        #####################################################################
        # get the base directory of source file for makedirs function
        file_path, file_name = os.path.split(in_file)
        if not os.path.exists(os.path.join(dirout, file_path)):
            os.makedirs(os.path.join(dirout, file_path))
        fpath2 = os.path.join(dirout, file_path, file_name)

        ### Temp file for checks  ######################################### 
        ftmp =   os.path.join(dirout, file_path, "ztmp.py")
        with open(ftmp, "w") as f:
            f.write(text_f)

        #### Compile check
        isok  = os_file_compile_check(ftmp)
        if isok :
            if os.path.isfile(fpath2):  os.remove(fpath2)
            os.rename(ftmp, fpath2)
            log(fpath2)
        else :    
            log('Cannot compile', fpath2)
            os.remove(ftmp)
    else:
        log(f"No such file exists {in_file}, make sure your path is correct")



def batch_format_dir(dirin:str, dirout:str, format_list:list,):
    """function batch_format_dir
        
    """
    src_files = os_glob(dirin)
    #flist = glob_glob_python(dirin, suffix ="*.py", nfile=nfile, exclude="*zz*")

    for f in tqdm.tqdm(src_files):
        if os_file_haschanged(f, weeks=100):
            try :
               batch_format_file(f, dirout, format_list)
            except Exception as e:
               log(e)   
        else:
            print(f"{f} is not modified within one week")



#############################################################################################
if 'check if .py compile':
    def os_file_compile_check_batch(dirin:str, nfile=10) -> dict:
        """
        """
        flist   = glob_glob_python( dirin, "*.py",nfile= nfile)
        res_dict = {}
        for fi in flist :
            res = os_file_compile_check(fi)
            res_dict[fi] =  res 
        
        return res_dict


    def os_file_compile_check(filename:str, verbose=1):
        """  check if syntax error in the .py file

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




#############################################################################################
########## Formatters #######################################################################
def codesource_extrac_block(txt)
    """ Split the code source into Code Blocks:
       header
       import
       variable
       logger
       test
       core

       footer

    """
    dd = Box({})
    lines = txt.split("/n")       
    lineblock = []

    flag_test= False

    for ii,line in enumerate(lines) :

      if 'import ' in line and ii < 20 :
         dd.header = lineblock
         lineblock = []

      if ('def ' in line or 'class ' in line  or 'from utilmy import log' in line ) and ii < 50 and not 'import' in dd:
         dd['import'] = lineblock
         lineblock = []


      if ('def test(' in line ) and ii < 50 and not 'logger' in dd :
          flag_test = True
          dd['logger'] = lineblock


      if 'def ' in line and 'def test' not in line and flag_test and ii >10 :
          ####  functions    
         dd['test'] = lineblock
         lineblock = []


      if 'if main ==  ' in line and  ii >10 :
         dd['core'] = lineblock
         lineblock = []

      lineblock.append(line)

      dd['footer'] = lineblock
        
      return dd  


        
        
def format_import_merge(text):
    """  Put all import at start of the .py file
         Remove the import at the top.
         Keep the import inside the functions or inside the code (== ad hoc import         
         return new lines
    """
    lines = text.split("\n")
    dd = Box({})
    
    import_list = [] ; from_list = []
    for line in lines :
      if "import " in line :
         if "from " in li : from_list.append(line)
         else :             import_list.append(line)

            
    #### reformat import   ################################################
    llall = []
    for imp in import_list :
        ll    = [ t.strip for t in  imp.split(",") if 'import' not in t ]
        llall = llall + ll

    lall = sorted( lall )
    ssall = ""
    for mi in lall:
       ss =  ss + mi + ","
       if len(ss) >  90 :
          ssall = ssall + ss  + "/n"
          ss = "import "

    ### all imports         
    ssall = ssall + ss  + "/n"


    ####
    lines2 = []
    for ii, line in enumerate(lines):
      if ii < 100 :
        if line.startswith("import ") : continue  ### Remove Old import
      lines2.append(line)  

    ### Add new import
    lines2 = sall + "\n" + lines2 

    #### 
    return '\n'.join(lines2)
    
    
def format_add_helper_logger(txt):
    lines = txt.split("/n")       
    new ="""#############################################################################################
    from utilmy import log, log2
    def help():
        ### helper shows list of all tests  
        from utilmy import help_create
        print( help_create(MNAME) )
    """
    new = new.replace( " " * 4, "")

    doinsert = False
    for line in lines :
        if "def help()" in line :
           doinsert = True

    if doinsert :
       format_insert_into_block(new, lines, block_id='2')          

    
def format_header(text):
    """  Normalized header
    """
    lines = text.split("\n")
    dd = Box({})

    for line in lines:
        if "MNAME=" in line :
            dd['mname'] = False

    if dd.mname :
        msg = 'MNAME=" utilmy.  "'
        lines = [msg] + lines 

    if dd['help'] :
        pass

    return '\n'.join(lines)


def format_comments(text="default", line_size=90):
    """
    Takes a string of text and formats it based on rule 1 (see docs).
    """
    # rules to detect fancy comments, if not text
    regex1 = r"^ *?####*$"
    # rules to detect fancy comments, if text
    regex2 = r"^ *?####*([^#\n\r]+)#*"
    # if detected pattern 1, replace with this
    subst1 = "#"*line_size

    # if detected pattern 2, replace with this
    def subst2(match_obj):
        fix_pad = 4 + 2  # 4 hashes on left plus two spaces
        cap_group = match_obj.group(1).strip()
        return '#### ' + cap_group + ' ' + '#'*(line_size-fix_pad-len(cap_group))

    text = re.sub(regex1, subst1, text, 0, re.MULTILINE)
    text = re.sub(regex2, subst2, text, 0, re.MULTILINE)
    # formatted text to return
    return text


def format_logs(text="default", line_size=90):
    """
    Takes a string of text and formats it based on rule 2 (see docs).
    """
    # rule to find log statemets
    regex3 = r"log\(\"#+(.*?)#*(\".*)"

    # substitution to replace the found log statements
    def subst3(match_obj):
        fix_pad = 4 + 2  # 4 hashes on left plus two spaces
        cap_group = match_obj.group(1).strip()
        return r'log("#### ' + cap_group + ' ' + '#'*(line_size-fix_pad-len(cap_group)) + match_obj.group(2)

    text = re.sub(regex3, subst3, text, 0, re.MULTILINE)
    # return formatted text
    return text


def format_imports(text):
    """rule 3 - put all consecutive imports on one line
    """
    # rule to find consective imports
    regex4 = r"^import[\s\w]+?(?=from|^\s*$)"

    # this subsitution will happen with a function
    def subst4(match_obj):
        pattern = r"import (\w+)"
        ind_imports = re.findall(pattern, match_obj.group(0))
        return r"import " + ", ".join(ind_imports) + "\n"

    text = re.sub(regex4, subst4, text, 0, re.MULTILINE)
    # return formatted text
    return text


def format_assignments(text):
    """
    Aligns assignment statements in the source file and return a text.
    """
    lines = text.split("\n")

    # process text line by and store each line at its starting index
    formated_text = []
    a_block_left = []
    a_block_right = []

    # these statements may contain = too are not assignment
    skip_tokens = ['if', 'for', 'while', '(', ')', 'else']

    def format_assignment_block():
        """
        Process an assignment block, returns formatted list of
        assignment lines in that block.
        """
        max_left = max([len(left) for left in a_block_left])
        f_assignments = []
        for left, right in zip(a_block_left, a_block_right):
            new_line = left + ' '*(max_left-len(left)) + ' = ' + right
            f_assignments.append(new_line)
        return f_assignments

    for line in lines:
        # assignment should contain = and shouldn't contain anything from skip_tokens
        # empty list is considered false
        if "=" in line and not ["bad" for t in skip_tokens if t in line.split("=")[0]]:
            left = line.split("=")[0]
            right = "= ".join(line.split("=")[1:] )

            # need to preserve spaces on left
            a_block_left.append(left.rstrip())
            a_block_right.append(right.strip())

        else:
            # if not assingment, process the block if not empty
            if len(a_block_left) != 0:
                f_assignments = format_assignment_block()
                formated_text.extend(f_assignments)
                a_block_left = []
                a_block_right = []
            # if not assingment, preserve the line
            formated_text.append(line)

    # check if the block is non empty at the end
    # because the else will not trigger if assignment lines are at the last
    if len(a_block_left) != 0:
        f_assignments = format_assignment_block()
        formated_text.extend(f_assignments)

    # join individual lines in list and returns as text string
    return '\n'.join(formated_text)


#############################################################################################
def format_add_logger(txt:str, ):
    """  adding log function import and replace all print( with log(
    """        
    import_line = "from utilmy import log, log2"
    if txt.find(import_line)==-1:

        #### It's stupid, did you check.....
        txt = import_line+"\n"+txt
    txt = txt.replace("print(",'log(')
    return txt


def format_add_header(txt:str):
    """



    """
    if find_str(txt,  'MNAME') < 0  : 
        ll2 = "NAME" + ""


    if find_str(txt,  'HELP') < 0 : 
            pass


    ### Write down and check
    to_file(ll2, finew)
    isok  = os_file_compile_check(finew)
    if isok :
        os.remove(fi)
        os.rename(finew, fi)
    else :    
        os.remove(finew)
        err_list.append(fi)
        
  
def find_str(word, word_list):
    for ii, wi in enumerate(word_list) :
        if word in wi : return ii
    return -1    





#############################################################################################
if 'utilties':
    def load_function_uri(uri_name="path_norm"):
        """ Load dynamically function from URI

        ###### Pandas CSV case : Custom MLMODELS One
        #"dataset"        : "mlmodels.preprocess.generic:pandasDataset"

        ###### External File processor :
        #"dataset"        : "MyFolder/preprocess/myfile.py:pandasDataset"

        """
        
        import importlib, sys
        from pathlib import Path
        pkg = uri_name.split(":")

        assert len(pkg) > 1, "  Missing :   in  uri_name module_name:function_or_class "
        package, name = pkg[0], pkg[1]
        
        try:
            #### Import from package mlmodels sub-folder
            return  getattr(importlib.import_module(package), name)

        except Exception as e1:
            try:
                ### Add Folder to Path and Load absoluate path module
                path_parent = str(Path(package).parent.parent.absolute())
                sys.path.append(path_parent)
                #log(path_parent)

                #### import Absolute Path model_tf.1_lstm
                model_name   = Path(package).stem  # remove .py
                package_name = str(Path(package).parts[-2]) + "." + str(model_name)
                #log(package_name, model_name)
                return  getattr(importlib.import_module(package_name), name)

            except Exception as e2:
                raise NameError(f"Module {pkg} notfound, {e1}, {e2}")



    def os_glob(dirin):
        """
        os_glob a given directory for all .py files and returns a list of source files.
        """
        files = glob.glob(dirin + "/**/*.py", recursive=True)
        # remove .ipynb_checkpoints
        files = [s for s in files if ".ipynb_checkpoints" not in s]
        # print("os_glob files done ... ")
        return files


    def os_file_haschanged(in_file, weeks=1):
        file_stats = os.stat(in_file)
        mod_date = datetime.datetime.fromtimestamp(file_stats.st_mtime)
        now = datetime.datetime.now()
        week_delta = datetime.timedelta(weeks=weeks)

        if now - mod_date < week_delta:
            return True     # file can be formatted
        else:
            return False



    def to_file(txt_big, fpath, mode='w', encoding='utf-8'):
        with open(fpath,mode=mode,encoding=encoding) as fp:
            fp.write(txt_big)

        if not os.path.is_file(fpath) :
            print('File not exist', fpath)   
        

    def find_in_lines(lines, word):
        for ii,li in enumerate(lines) :
            if word in li : return ii
        return -1    
    


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
        log(flist)
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


###################################################################################################
if __name__ == "__main__":
    import fire
    # fire.Fire()  ### python utilmy/ZZZZZ/util_xxxx.py  test1\

    test1()








if 'zold':

    def zzbatch_format_file(in_file, dirout):
        """function batch_format_file
            
        """
        # if input is a file and make sure it exits
        if os.path.isfile(in_file):
            with open(in_file) as f:
                text = f.read()
            ###################################################################

            text_f = format_comments(text)
            text_f = format_logs(text_f)
            text_f = format_imports(text_f)
            text_f = format_assignments(text_f)




            # get the base directory of source file for makedirs function
            file_path, file_name = os.path.split(in_file)
            if not os.path.exists(os.path.join(dirout, file_path)):
                os.makedirs(os.path.join(dirout, file_path))
            fpath2 = os.path.join(dirout, file_path, file_name)

            ### Temp file for checks  ######################################### 
            ftmp =   os.path.join(dirout, file_path, "ztmp.py")
            with open(ftmp, "w") as f:
                f.write(text_f)

            #### Compile check
            isok  = os_file_compile_check(ftmp)
            if isok :
                if os.path.isfile(fpath2):  os.remove(fpath2)
                os.rename(ftmp, fpath2)
                log(fpath2)
            else :    
                log('Cannot compile', in_file)
                os.remove(ftmp)
                err_list.append(fi)
        else:
            print(f"No such file exists {in_file}, make sure your path is correct")


    def zzbatch_format_dir(dirin, dirout):
        """function batch_format_dir
            
        """
        src_files = os_glob(dirin)
        #flist = glob_glob_python(dirin, suffix ="*.py", nfile=nfile, exclude="*zz*")

        for f in tqdm.tqdm(src_files):
            if os_file_haschanged(f, weeks=2):
                try :
                   batch_format_file(f, dirout)
                except Exception as e:
                   log(e)   
            else:
                print(f"{f} is not modified within one week")


"""
for fi in flist :
    fi       = os_path_norm(fi)
    fname    = fi.split(os.sep)[-1] 
    file_new = reformat_pyfile(fi) 
    to_file(file_new, dirout + "/" + fname)
"""

