import logging
import sys, os

from logging import Formatter
from logging import FileHandler

DEF_FMT='"%(asctime)-15s|%(levelname)s:%(name)s|%(filename)s:%(lineno)d|%(process)d:%(thread)d|%(message)s"'
DEF_FMT_JSON = '{"asctime":"%(asctime)-15s", "levelname":"%(levelname)s", "filename_and_line":"%(filename)s:%(lineno)d", "process_and_thread":"%(process)d:%(thread)d", "message":"%(message)s"}'
DATE_FMT = "%Y-%m-%d %H:%M:%S:%s"
LEVEL = logging.INFO




class FileLogger():
    @classmethod
    def make_logger(cls, client_id, 
                         level=LEVEL, 
                         fmt=DEF_FMT_JSON,
                         datefmt=DATE_FMT):
        logger = logging.getLogger(client_id)
        logger.setLevel(level)

        OUTPUT_EMULATION_DIR = os.getenv('OUTPUT_EMULATION_DIR', './out')
        os.makedirs(OUTPUT_EMULATION_DIR, exist_ok=True)
        
        h = FileHandler(f'{OUTPUT_EMULATION_DIR}/actors_{client_id}.log', 'w')
        f = Formatter(fmt=fmt, datefmt=datefmt)
        h.setFormatter(f)
        logger.addHandler(h)
        return logger

class StdOutLogger():
    @classmethod
    def make_logger(cls, client_id, 
                         level=LEVEL, 
                         fmt=DEF_FMT_JSON,
                         datefmt=DATE_FMT):
        logger = logging.getLogger()
        logger.setLevel(level)    
        h = logging.StreamHandler(sys.stdout)
        f = Formatter(fmt=fmt, datefmt=datefmt)
        h.setFormatter(f)
        logger.addHandler(h)
        return logger

Logger = FileLogger