from logging import getLogger, StreamHandler, DEBUG, INFO, Formatter
logger = getLogger(__name__)
formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

handler = StreamHandler()
handler.setLevel(INFO)
handler.setFormatter(formatter)
logger.setLevel(INFO)
logger.addHandler(handler)
logger.propagate = False