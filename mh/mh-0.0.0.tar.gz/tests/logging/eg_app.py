# eg_app.py

import sys
import logging
import logging.config
import yaml

#mypath = "/Users/markhallett/notgoogledrive/github/mh/src"
#mypath = "../../../src"
#sys.path.insert(0, mypath)

import mh

logging.config.dictConfig(yaml.load(open('logging_config.ymal', 'r'), Loader=yaml.FullLoader ))
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("START")
    logger.info(mh)
    try:
        1/0
    except ZeroDivisionError as e:
        logger.error('eg', exc_info = True)

    logger.info(mh.__version__)
    mh.Mh().runMh()

    logger.debug("END")
