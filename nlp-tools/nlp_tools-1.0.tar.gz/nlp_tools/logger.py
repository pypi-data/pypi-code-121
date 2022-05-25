import os
import logging

logger = logging.Logger('nlp_tools',level='DEBUG')
stream_handler = logging.StreamHandler()

if os.environ.get("NLPTOOLS_DEV") == 'True' :
    log_format =  '%(asctime)s [%(levelname)s] %(name)s:%(filename)s:%(lineno)d - %(message)s'
else:
    log_format = '%(asctime)s [%(levelname)s] %(name)s - %(message)s'

stream_handler.setFormatter(logging.Formatter(log_format))
logger.addHandler(stream_handler)
