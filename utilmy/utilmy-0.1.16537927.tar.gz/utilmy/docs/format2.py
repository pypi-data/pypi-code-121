# -*- coding: utf-8 -*-
MNAME = "utilmy.docs.format2"
""" utils for re-formatting files using TEMPLATES



"""
import re, os, sys, glob
from pprint import pprint

#################################################################################################################
# from utilmy import log, log2, help_create

def log(*s) : 
    """function log.
    Doc::
            
            Args:
                *s:   
            Returns:
                
    """
    print(*s, flush=True)


#################################################################################################################
def test1():
    """ python utilmy/docs/format2.py  test1 .
    Doc::
            
            
    """
    #### cd myutil
    dirtest = "utilmy/docs/"


    format_file2(dirtest + '/test_script/test_script_no_header.py', dirtest + '/test_script/output/test_script_no_header.py')
    format_file2(dirtest + '/test_script/test_script_no_logger.py', dirtest + '/test_script/output/test_script_no_logger.py')
    format_file2(dirtest + '/test_script/test_script_no_core.py', dirtest + '/test_script/output/test_script_no_core.py')
    format_file2(dirtest + '/test_script/test_script_normalize_import.py', dirtest + '/test_script/output/test_script_normalize_import.py')


    format_file3(dirtest + '/test_script/test_script_normalize_import.py', dirtest + '/test_script/output')
    format_file3(dirtest + '/test_script/test_script_no_header.py', dirtest + '/test_script/output')
    format_file3(dirtest + '/test_script/test_script_no_logger.py', dirtest + '/test_script/output')
    format_file3(dirtest + '/test_script/test_script_no_core.py', dirtest + '/test_script/output')




##### Run Scripts ###############################################################################################
def format_utilmy(nfile=10):
    """function format_utilmy.
    Doc::
            
            Args:
                nfile:   
            Returns:
                
    """
    dirin = os.getcwd() + "/utilmy/"
    direxclude ="*utilmy/z*"

    dirout =  os.getcwd() +'/utilmy/'
    format_list = [ format_file ]


    src_files = glob_glob_python(dirin, nfile=nfile, exclude=direxclude)
    for ii, fi in src_files:
        try :
            log(ii,fi)
            batch_format_file(fi, dirout, format_list)
        except Exception as e:
            log(e)   


def format_file2(file_path, output_file):
    """function format_file2.
    Doc::
            
            Args:
                file_path:   
                output_file:   
            Returns:
                
    """
    new_all_lines = format_file(file_path)
    # new_all_lines = ss.split("\n")
    print(str(new_all_lines)[:100] )
    os.makedirs( os.path.dirname(output_file) , exist_ok=True)
    with open(output_file, 'w+', encoding='utf-8') as f:
        f.writelines(new_all_lines)


def format_file3(file_path, output_file):
    """function format_file3.
    Doc::
            
            Args:
                file_path:   
                output_file:   
            Returns:
                
    """
    ## Safe Modification
    batch_format_file(in_file= file_path, dirout= output_file, 
                    format_list= [ format_file ])



###### Core formatter ###########################################################################################
def format_file(file_path):
    """function format_file.
    Doc::
            
            Args:
                file_path:   
            Returns:
                
    """
    all_lines = get_file(file_path)
    info = extrac_block(all_lines)

    new_headers = normalize_header(file_path, info['header'])
    new_imports = normalize_import(info['import'])
    new_loggers = normalize_logger(info['logger'])
    new_tests =   normalize_test(info['test'])
    new_cores =   normalize_core(info['core'])
    new_footers = normalize_footer(info['footer'])

    # Create new data array then write to new file
    new_all_lines = []
    new_all_lines.extend(new_headers)
    new_all_lines.extend(new_imports)
    new_all_lines.extend(new_loggers)
    new_all_lines.extend(new_tests)
    new_all_lines.extend(new_cores)
    new_all_lines.extend(new_footers)

    # ss = "\n".join(new_all_lines)
    return new_all_lines


def normalize_header(file_name, lines):
    """Nomarlize Header block.
    Doc::
            
        
            Args input is a array of lines.
    """
    #### not need of regex, code easier to read 

    lines2 = []
    if len(lines) >= 3:
        # line 1
        if '# -*- coding: utf-8 -*-' not  in lines[0] :
            lines2.append('# -*- coding: utf-8 -*-\n')

        # line 2
        if 'MNAME' not in lines[1] :   ### MNAME = "utilmy.docs.format"
            nmane =  ".".join( os.path.abspath(file_name).split("\\")[-4:] )[:-3]
            lines2.append( f'MNAME = "{nmane}"\n')

        if 'HELP' not in lines[2] :   ### HELP
            lines2.append( f'HELP = "util"\n')

    else:
        lines2.append('# -*- coding: utf-8 -*-\n')
        nmane =  ".".join( os.path.abspath(file_name).split("\\")[-4:] )[:-3]
        lines2.append( f'MNAME = "{nmane}"\n')
        lines2.append( f'HELP = "util"\n')

    ### Add previous line
    lines2.extend(lines)
    # print(lines2)
    return lines2


def normalize_import(lines):
    """  merge all import in one line and append others.
    Doc::
            
        
    """
    import_list = []
    from_list = []
    lines2 = []
    for line in lines :
        if "import " in line :
            if "from " in line : from_list.append(line)
            else :               import_list.append(line)

    ### Merge all import in one line   ################################################
    llall = []
    for imp in import_list :
        imp = imp[6:] # remove import
        ll    = [ t.strip() for t in  imp.split(",") if 'import' not in t ]
        llall = llall + ll

    lall = sorted( llall )

    lines2 = []
    ss = "import "
    for mi in lall:
        ss =  ss + mi + ", "
        if len(ss) >  90 :
            lines2.append( f"{ss[:-2]}\n" )  
            ss = "import "
    lines2.append(f"{ss[:-2]}\n")  

    # lines2.extend(from_list)
    # print(lines2)

    #### Remaining import 
    for ii, line in enumerate(lines):
        if ii > 100 : break
        if line.startswith("import ") : continue  ### Remove Old import
        lines2.append(line)  

    #### 
    # print(lines2)
    return lines2


def normalize_logger(lines):
    """function normalize_logger.
    Doc::
            
            Args:
                lines:   
            Returns:
                
    """
    lines2 = []
    if len(lines) >0:
        if "from utilmy import log" not in lines[0]:
            lines2.append('from utilmy import log, log2, help_create\n')
    else:
        lines2.append('from utilmy import log, log2, help_create\n')
    # append all
    lines2.extend(lines)

    # check help function:
    is_exist_help = False
    for line in lines:
        if line.startswith("def help"):
            is_exist_help = True
            break
    
    if not is_exist_help:
        lines2.extend([
            'def help():\n',
            '   print( help_create(__file__) )\n',
            '\n',
            '\n'
        ])
    # print(lines2)
    return lines2


def normalize_test(lines):
    """function normalize_test.
    Doc::
            
            Args:
                lines:   
            Returns:
                
    """
    lines2 = []

    # check test_all function:
    is_exist_test_all = False
    for line in lines:
        if line.startswith("def test_all"):
            is_exist_test_all = True
            break
    
    if not is_exist_test_all:
        lines2.extend([
            'def test_all() -> None:\n',
            '    """function test_all"""\n',
            '    log(MNAME)\n',
            '    test1()\n',
            '    test2()\n',
            '\n',
            '\n',
        ])

    # check test1 function:
    is_exist_test1 = False
    for line in lines:
        if line.startswith("def test1"):
            is_exist_test1 = True
            break
    
    if not is_exist_test1:
        lines2.extend([
            'def test1() -> None:\n',
            '    """function test"""\n',
            '    pass\n',
            '\n',
            '\n',
        ])

    # # check test2 function:
    # is_exist_test2 = False
    # for line in lines:
    #     if line.startswith("def test2"):
    #         is_exist_test2 = True
    #         break
    
    # if not is_exist_test2:
    #     lines2.extend([
    #         'def test2() -> None:\n',
    #         '    """function test"""\n',
    #         '    pass\n',
    #         '\n',
    #         '\n',
    #     ])

    ###### Eztend lines
    lines2.extend(lines)
    return lines2


def normalize_core(lines):
    """function normalize_core.
    Doc::
            
            Args:
                lines:   
            Returns:
                
    """
    return lines


def normalize_footer(lines):
    """function normalize_footer.
    Doc::
            
            Args:
                lines:   
            Returns:
                
    """

    lines2 = []

    # check test_all function:
    main_start_line = 0
    is_exist_main = False
    for ii, line in enumerate(lines):
        if line.startswith("if __name__"):
            is_exist_main = True
            main_start_line = ii
            break
    if not is_exist_main:
        lines2.extend(lines)
        lines2.extend([
            'if __name__ == "__main__":\n',
            '   import fire\n',
            '   fire.Fire()\n',
        ])
    else:
        lines2.extend(lines)
        if  not ('import fire' in lines[main_start_line+1]  and 'fire.Fire()' in lines[main_start_line+2]):
            lines2.insert(main_start_line+1, '   import fire\n')
            lines2.insert(main_start_line+2, '   fire.Fire()\n')

    return lines2


#################################################################################################################
def get_file(file_path):
    """function _get_all_line.
    Doc::
            
            Args:
                file_path:   
            Returns:
                
    """
    # print(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        all_lines = (f.readlines())
    return all_lines
    

def extrac_block(lines):
    """ Split the code source into Code Blocks:.
    Doc::
            
                header
                import
                variable
                logger
                test
                core
        
                footer
        
    """
    dd = {}
    # lines = txt.split("/n")       
    lineblock = []

    flag_test= False

    ## BLOCK HEAD
    for ii,line in enumerate(lines) :
        # print(ii,line)
        # end of block header
        if (re.match(r"import\s+\w+", line) or \
            ((re.match(r"def\s+\w+", line) or re.match(r"class\s+\w+", line) or 'from utilmy import log' in line)) or \
                re.match(r'if __name__', line)) and ii < 20 :
            dd['header'] = lineblock
            dd['header_start_line'] = 0
            dd['header_end_line'] = ii - 1
            lineblock = []
            break
        else:
            lineblock.append(line)
            if ii >= 20:
                dd['header'] = []
                dd['header_start_line'] = 0
                dd['header_end_line'] = 0
                break
    # pprint(dd)
    lineblock = []
    
    # Block import
    dd['import_start_line'] = dd['header_end_line'] + 1 if dd['header_end_line'] else 0
    # print(dd['import_start_line'])
    for ii,line in enumerate(lines) :
        if ii >= dd['import_start_line']:
            # if ('def ' in line or 'class ' in line  or 'from utilmy import log' in line ) and ii < 50 and not 'import' in dd:
            if (re.match(r"def\s+\w+", line) or re.match(r"class\s+\w+", line) or 'from utilmy import log' in line or re.match(r'if __name__', line)) and ii < 50:
                dd['import'] = lineblock
                dd['import_end_line'] = ii - 1
                lineblock = []
                break
            else:
                # print(line)
                lineblock.append(line)
                if ii >= 50:
                    dd['import'] = []
                    dd['header_end_line'] = dd['header_start_line']
                    break
    # pprint(dd)
    lineblock = []

    ### Block Logger
    dd['logger_start_line'] = dd['import_end_line'] + 1 if dd['import_end_line'] else 0
    for ii,line in enumerate(lines) :
        if ii >= dd['logger_start_line']:
            if (re.match(r"def\s+\w+", line)) and ii < 50:
                if not('def help' in line or 'def log' in line):
                    dd['logger'] = lineblock
                    dd['logger_end_line'] = ii - 1
                    lineblock = []
                    break
                else:
                    lineblock.append(line)
            else:
                # print(line)
                lineblock.append(line)
                if ii >= 50:
                    dd['logger'] = []
                    dd['logger_end_line'] = dd['logger_start_line']
                    break
    # pprint(dd)
    lineblock = []

    ### Block Test
    dd['test_start_line'] = dd['logger_end_line'] + 1 if dd['logger_end_line'] else 0
    for ii,line in enumerate(lines) :
        if ii >= dd['test_start_line']:
            # new function / class / or main
            if (re.match(r"def\s+\w+", line) or \
                 re.match(r"class\s+\w+", line)) or \
                 re.match(r'if __name__', line):
                if not('def test' in line):
                    dd['test'] = lineblock
                    dd['test_end_line'] = ii - 1
                    lineblock = []
                    break
                else:
                    lineblock.append(line)
            else:
                # print(line)
                lineblock.append(line)
                if ii == len(lines)-1:
                    dd['test'] = []
                    dd['test_end_line'] = dd['test_start_line']
                    break
    # pprint(dd)

    lineblock = []

    # Block Core
    dd['core_start_line'] = dd['test_end_line'] + 1 if dd['test_end_line'] else 0
    for ii,line in enumerate(lines) :
        if ii >= dd['core_start_line']:
            # new function / class / or main
            if re.match(r'if __name__', line):
                # print('----------------')
                dd['core'] = lineblock
                dd['core_end_line'] = ii - 1
                lineblock = []
                break
            else:
                # print(line)
                lineblock.append(line)
                if ii == len(lines)-1:
                    dd['core'] = []
                    dd['core_end_line'] = dd['core_start_line']
                    break
    # pprint(dd)

    lineblock = []
    dd['footer_start_line'] = dd['core_end_line'] + 1 if dd['core_end_line'] else 0
    for ii,line in enumerate(lines):
        if ii >= dd['footer_start_line']:
            lineblock.append(line)
        if ii == len(lines) -1:
            dd['footer'] = lineblock
            dd['footer_end_line'] = ii
            break
    # pprint(dd)

    return dd


#############################################################################################
if 'check if .py compile':
    def batch_format_dir(dirin:str, dirout:str, format_list:list, nfile=10, direxclude=""):
        """function batch_format_dir
            
        """
        src_files = glob_glob_python(dirin, nfile=nfile, exclude=direxclude)
        #flist = glob_glob_python(dirin, suffix ="*.py", nfile=nfile, exclude="*zz*")

        for ii, fi in src_files:
            try :
                log(ii,fi)
                batch_format_file(fi, dirout, format_list)
            except Exception as e:
                log(e)   



    def batch_format_file(in_file:str, dirout:str, format_list:list):
        """function batch_format_file with Compile check        
        """
        # if input is a file and make sure it exits
        if os.path.isfile(in_file):
            with open(in_file) as f:
                text = f.read()

            ######## Apply formatting ###########################################
            # text_f = text
            text_f = []
            for fun_format in  format_list :
                # log(str(fun_format)) 
                text_f = fun_format(in_file)


            #####################################################################
            # get the base directory of source file for makedirs function
            file_path, file_name = os.path.split(in_file)
            print(os.path.join(dirout, file_path))
            if not os.path.exists(os.path.join(dirout, file_path)):
                os.makedirs(os.path.join(dirout, file_path))
            fpath2 = os.path.join(dirout, file_path, file_name)

            ### Temp file for checks  ######################################### 
            ftmp =   os.path.join(dirout, file_path, "ztmp.py")
            with open(ftmp, "w") as f:
                f.writelines(text_f)

            #### Compile check
            isok  = os_file_compile_check(ftmp)
            if isok :
                if os.path.isfile(fpath2):  os.remove(fpath2)
                os.rename(ftmp, fpath2)
                # log(fpath2)
                print(fpath2)
            else :    
                # log('Cannot compile', fpath2)
                print('Cannot compile', fpath2)
                os.remove(ftmp)
        else:
            # log(f"No such file exists {in_file}, make sure your path is correct")
            print(f"No such file exists {in_file}, make sure your path is correct")


    def os_file_compile_check_batch(dirin:str, nfile=10) -> dict:
        """
        """
        flist   = glob.glob( dirin + "/**/*.py")
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
            if verbose > 0 : 
                print(e)
                traceback.print_exc() # Remove to silence any errros
            return False


    def glob_glob_python(dirin, suffix ="*.py", nfile=10000, exclude=""):
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



if __name__ == '__main__':
    import fire 
    fire.Fire()
    # test1()


