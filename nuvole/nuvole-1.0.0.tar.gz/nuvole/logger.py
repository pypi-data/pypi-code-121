import logging


log = logging.getLogger('nuvole')
logging.getLogger('tornado').setLevel(logging.ERROR)
logging.getLogger('asyncio').setLevel(logging.ERROR)
