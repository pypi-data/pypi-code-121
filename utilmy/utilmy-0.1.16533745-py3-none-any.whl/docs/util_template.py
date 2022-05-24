
#### BLOCK HEADER  ###########################
# -*- coding: utf-8 -*-
MNAME = "utilmy."
""" utils for

can you see here ?????

yes

can you see the blocks I put ?
yes, let me check again

Let me write pseudo definition :

HEADER :
   from top .... until the 1st  'import '


IMPORT :
   from 1st 'import '     to   
                              import log   OR   def help   OR    def test  OR  def XXXXX

LOGGER:
  from  import log OR  def log()    TO       def test(   OR   def XXXXX


TEST :
  from  1st def test(           TO      def XXXXX


FOOTER:
  from    if __name__ == "__main__":    to bottom of file


End Goal is to normalize the structure of the .py following this pattern:

   HEADER_NEW  = normalize_header(HEADER)
   IMPORT_NEW  = ....
   LOGGER_NEW
   TEST_NEW
   FOOTER_NEW =  normalize_footer(FOOTER)
Ok ?

Steps:
        1) Grab/parse the different blocks
        2) apply normaliztion for each block (ie ad hoc pre-defined functions)
        3) write down into a big string code_all,  and then on disk


Ok ?

So, the .py file will have this struct and we parse it, or we need to check if
the line in in what block?


Sure :
  In some .py file,  some block may be missing :
      block['LOGGER'] = ""      
      block['TEST'] = ""

   that's ok, because 
      block_new['LOGGER'] = normalize_logger( block['LOGGER'] )


      code_all_new = block_new['HEADER'] + "/" + block_new['IMPORT'] ... 

 Ok ?
 
      
so I will code here?
You can start coding here (== for question it's easy)
after you feel confident, you can copy paste to your local and finish it.

or will code in my window and push it
ok

ok
ok


"""

#### Protoptype


def reformat_code(txt):

    lines = txt.split("\n")

    BLOCK = get_all_blocks(lines)

    ### normalize block
    BLOCK_NEW = {}
    BLOCK_NEW['HEADER'] =  normalize_header(BLOCK['HEADER'] )


    ### merge all
    code_new =  code_new + BLOCK_NEW['HEADER'] +"/n"
    code_new =  code_new + BLOCK_NEW['IMPORT'] +"/n"


   ## write on disk
   with open(dirout , mode='w') as fp:
       fp.writelines(code_new)



def normalize_header(txt):
   lines = txt.split("\n")

   lines2 = ""
   if '# -*- coding: utf-8 -*-' not  in txt :
       lines2.append('# -*- coding: utf-8 -*-')

   if 'MNAME' not  in txt :   ### MNAME = "utilmy.docs.format"
       nmane =  ".".join( os.path.abspath(__file__).split("/") )
       lines2.append( f'MNAME="{mname}"')

   if 'HELP' not  in txt :   ### HELP
       lines2.append( f'HELP="" ')

   return lines2

## Ok ?
YES !



ok, so the format of the header is:
# -*- coding: utf-8 -*-
MNAME = "xx."
HELP = """
xxxx
"""
?


so we need to check and add these lines

But for the other blocks. what we need to do >


"""
### I will create normalize_XXXX after

for empty block, we just add FIXED pre-determined pattern like 

ss= "def test_all():
          log(MNAME)
          test1()

       def test1():
           pass   
    "


we can do it after.


YES, let's parse the blocl


ok. I will add the code to parse the blocks first.


Cannot run here, no interpreter
you need to copy to your local


I will create and run on my PC then copy to here

You can ping here 
Am doing other things in parallel.


ok. 
"""

########## Formatters #######################################################################
####  here a pseudo prototype
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
    dd = Box({})  ## storage of block
    lines = txt.split("/n")       ### code
    lineblock = []

    flag_test= False

    ## do you see a bit ?
    ## no need to havve a perfect parser, but somwthing for 95% of files....

    for ii,line in enumerate(lines) :
                # ['lock I']mport
      els
:
        dd['header'] = lineblock        if 'import ' in''
         reakii < 20 :  ## ii<20  is trick...
            dd['header'] = lineblock[:-1] ## we need to remove the last one which is import
            lineblock = [lineblock[-1]]

        ### Block import
        if ('def ' in line or 'class ' in line  or 'from utilmy import log' in line ) and ii < 50 and not 'import' in dd:
            dd['import'] = lineblock[:-1]   ## we need to remove the last one which is not in import
            lineblock = [lineblock[-1]]

        ### Block Test
        if ('def test' in line ) and ii < 50 and not 'logger' in dd :
            flag_test = True
            dd['logger'] = lineblock


        ### Block Core
        if 'def ' in line and 'def test' not in line and flag_test and ii >10 :
            ####  functions    
            dd['test'] = lineblock
            lineblock = []


        ### Block Footer
        if 'if main ==  ' in line and  ii >10 :
            dd['core'] = lineblock
            lineblock = []

        lineblock.append(line)  ### Can you see here ?

    ### outside loop
    dd['footer'] = lineblock    
    return dd  






#### BLOCK IMPORT  ####################################################
import os, sys, glob, time,gc, datetime, numpy as np, pandas as pd
from typing import List, Optional, Tuple, Union
from numpy import ndarray
from box import Box





#### BLOCK logger  ###########################
from utilmy import log, log2

def help():
    """function help"""
    from utilmy import help_create
    print( HELP + help_create(MNAME) )


#### BLOCK test  ####################################
def test_all() -> None:
    """function test_all

    """
    log(MNAME)
    test1()
    test2()


def test1() -> None:
    """function test1
    Args:
    Returns:

    """
    pass




def test2() -> None:
    """function test2
    Args:
    Returns:

    """
    pass


#### BLOCK CORE  ###########################
"""
All cusotm code here

"""






#### BLOCK FOOTER  ###########################
if __name__ == "__main__":
    import fire
    fire.Fire()


