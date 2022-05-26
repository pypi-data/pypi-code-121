import logging

FORMAT = '%(message)s'

loggers = [
    'path',
]

logging.basicConfig(format=FORMAT)
for l in loggers:
    logging.getLogger(l).setLevel(logging.INFO)
