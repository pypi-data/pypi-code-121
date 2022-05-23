# -*- coding: utf-8 -*-
import os,logging,datetime,pdb,inspect,time,six
from . singleton import Singleton

logger_dict = {'info':logging.INFO,
                'warning':logging.WARNING,
                'critical':logging.CRITICAL,
                'debug':logging.DEBUG,
                'error':logging.ERROR}


class BaseLogger(object):
    def __init__(self, logger_name, log_level='info', 
                 log_format=None, log_dir=None):
        self._init_setting(logger_name = logger_name, 
                           log_level=log_level, 
                           log_format=log_format, log_dir=log_dir)
        #self.logger = None
        
    def _init_setting(self, logger_name, log_level='info', 
                 log_format=None, log_dir=None):
        default_format = '%(asctime)s - [%(filename)s:%(lineno)d] - %(name)s - %(levelname)s - %(message)s'
        default_path = '/var/log/' if 'KD_LOG_PATH' not in os.environ else os.environ['KD_LOG_PATH']
        log_path = default_path if log_dir is None else log_dir
        log_format = default_format if log_format is None else log_format
        formatter = logging.Formatter(log_format)
        self.logger = logging.getLogger(logger_name)
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        self.logger.addHandler(console)
        self.set_level(log_level)
        self._config_file(log_level=log_level, logger_name=logger_name, 
                              log_path=log_path, log_format=log_format)
            
    def _config_file(self, log_level, logger_name, log_format, 
                     log_path=None):
        dir_name = os.path.join(log_path, logger_name)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        filename = datetime.datetime.now().date().strftime('%Y-%m-%d') + '.log'
        print(os.path.join(dir_name, filename))
        logging.basicConfig(level=logger_dict[log_level.lower()],
                           format=log_format,
                           datefmt='%m-%d %H:%M',
                           filename=os.path.join(dir_name, filename),
                           filemode='a')
        
    def reset(self, logger_name, log_level='info', 
                 log_format=None, log_dir=None):
        self._init_setting(logger_name = logger_name, 
                           log_level=log_level, 
                           log_format=log_format, log_dir=log_dir)
        return self
    
    def handle(self):
        return self.logger
    
    def set_level(self, log_level):
        self.logger.setLevel(logger_dict[log_level.lower()])
    
    def info(self, msg):
        self.logger.info(msg)
    
    def warning(self, msg):
        self.logger.warning(msg)
    
    def critical(self, msg):
        self.logger.critical(msg)
        
    def debug(self, msg):
        self.logger.debug(msg)
        
    def error(self, msg):
        self.logger.error(msg)
        
        
class RDLogger(object):
    def __init__(self, logger_name, log_level='info'):
        self._logger_name = logger_name
        self.logger = logging.getLogger(logger_name)
        console = logging.StreamHandler()
        self.logger.addHandler(console)
        self.set_level(log_level)
        
    def set_level(self, log_level):
        self.logger.setLevel(logger_dict[log_level.lower()])
        
    def message(self, level, message):
        _,file_name,line_no,function_name,_,_ = inspect.stack()[2]
        return "[%s line:%s] %s - %s - %s - %s" %(file_name, line_no,
                    time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                    self._logger_name, level.upper(), message)
    
    def info(self, msg):
        self.logger.info(self.message('info', msg))
    
    def warning(self, msg):
        self.logger.info(self.message('warning', msg))
    
    def critical(self, msg):
        self.logger.info(self.message('critical', msg))
        
    def debug(self, msg):
        self.logger.info(self.message('debug', msg))
        
    def error(self, msg):
        self.logger.info(self.message('error', msg))
        
        
class LoggerFactory(object):
    @classmethod
    def create_engine(self, name='custom'):
        if name == 'rd':
            return RDLogger
        else:
            return BaseLogger(name)

@six.add_metaclass(Singleton)
class CustomLogger():
    def __init__(self, name=None):
        self.logger = LoggerFactory.create_engine(name=name)
    
    def reset(self, name):
        self.logger = self.logger.reset(logger_name=name)
        global mlc_logger
        mlc_logger = self.handle()
        
    def handle(self):
        return self.logger.handle()
        
kd_logger = CustomLogger(
    'kd' if 'KD_LOG_NAME' not in os.environ else os.environ['KD_LOG_NAME']).handle()