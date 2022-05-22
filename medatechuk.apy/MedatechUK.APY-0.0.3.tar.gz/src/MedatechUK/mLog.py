######################################################
## si@medatechuk.com
## 30/10/21
## https://github.com/MedatechUK/Medatech.APY
## 
## Logging class
## https://docs.python.org/3/howto/logging.html
##
## Usage: Start the Logger: !!USE ONCE!! in entry file
## from MedatechUK.mLog import mLog
##
##      # Creates a log reference to the running file
##        log = mLog()
##      # Start the Logger: !!USE ONCE!! in entry file
##        log.start( os.path.dirname(__file__), "DEBUG" )
##
## Usage: 
## from MedatechUK.mLog import mLog
##
##      # Creates a log reference to the running file
##        log = mLog()
##      # Write to the log
##        log.logger.info("Hello test!")

import logging
import inspect
from datetime import datetime
import os

class mLog():

    ## Ctor
    def __init__(self):  

        ## Build stack trace of caller frame             
        tree = [] 
        previous_frame = inspect.currentframe().f_back
        (filename) = inspect.getframeinfo(previous_frame)        
        tree.append(os.path.basename(filename.filename))

        previous_frame = previous_frame.f_back        
        while previous_frame and os.path.basename(filename.filename)!='runpy.py':
            (filename) = inspect.getframeinfo(previous_frame)        
            if os.path.basename(filename.filename) != tree[-1] and os.path.basename(filename.filename)!='runpy.py':
                tree.append(os.path.basename(filename.filename))
            previous_frame = previous_frame.f_back
        
        t = tree[-1]
        for i in range(len(tree)-2, -1 , -1):
            t = "{} > {}".format(t , tree[i] )

        ## Start the logger with stack trace %(name)s
        self.logger = logging.getLogger(t)

    def start(self, path , level):
        ## Set the Log location
        now = datetime.now() # current date and time
        fn = '{}\log\{}-{}\{}.log'.format(
                path , 
                now.strftime("%Y") , 
                now.strftime("%m"), 
                now.strftime("%y%m%d")
            )
        try:
            os.makedirs(os.path.dirname(fn),exist_ok=True)
        except OSError as e:
            raise
            
        ## Set the configuration for the log
        logging.basicConfig(
            filename= fn, 
            encoding='utf-8', 
            format='%(asctime)s %(levelname)s %(name)s %(message)s', datefmt='%H:%M:%S',
            level=getattr(logging, level.upper())
        )        