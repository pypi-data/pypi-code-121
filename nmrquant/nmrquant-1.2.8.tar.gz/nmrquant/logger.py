"""Logger module containing the RMNQ logger setup"""

import logging

#Setup base logger

logger = logging.getLogger("RMNQ_logger")
logger.setLevel(logging.DEBUG)



#Initiate any extra loggers
#Other configs