import logging
from blessings import Terminal; t = Terminal()
from datetime import datetime


class ColorFormatter(logging.Formatter):
	"""
	Example usage:
	
	LOGGING = {
		'version': 1,
		'disable_existing_loggers': False,
		'formatters': {
			'colors': {
				'()': 'util.colorlog.ColorFormatter',
			},
			'stamp': {
				'format': '%(asctime)s %(name)s [%(levelname)s] %(message)s',
				# 'format': '%(asctime)s %(name)s %(module)s [%(levelname)s] %(message)s',
			},
		},
		'handlers': {
			'console': {
				'class': 'logging.StreamHandler',
				'formatter': 'colors',
			},
		},
		'loggers': {
			# 'django': {
			# 	'handlers': ['console'],
			# 	'level': 'DEBUG',
			# },
			'dialer': {
				'handlers': ['console'],
				'level': 'DEBUG',
			},
		},
	}
	"""
	
	def __init__(self, *args, **kwargs):
		super(ColorFormatter, self).__init__()

	def format(self, record):
		lvl = record.levelname
		if record.levelname == 'DEBUG': lvl = t.white('DBG')
		if record.levelname == 'INFO': lvl = t.blue('INF')
		if record.levelname == 'WARNING': lvl = t.yellow('WRN')
		if record.levelname == 'ERROR': lvl = t.red('ERR')
		if record.levelname == 'CRITICAL': lvl = t.bright_red('CRT')

		NAME_LENGTH_MAX = 19
		name = record.name
		if len(name) > NAME_LENGTH_MAX:
			name = name[-NAME_LENGTH_MAX:]

		return f'{datetime.strftime(datetime.now(), "%H:%M:%S.%f")}|{name}[{lvl}] {record.getMessage()}'
