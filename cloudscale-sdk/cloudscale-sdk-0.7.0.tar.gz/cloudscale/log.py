import os
import logging

logging.basicConfig(
    level=os.environ.get('CLOUDSCALE_LOG_LEVEL', 'ERROR').upper(),
    format='%(asctime)s - %(name)s:%(levelname)s:%(message)s')

logger = logging.getLogger(__name__)
logger.debug('Init')
