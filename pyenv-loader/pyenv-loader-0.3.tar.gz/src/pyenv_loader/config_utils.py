import logging, os


class EnvNames:
	LOCAL = 'local'
	DEV = 'developement'
	TEST = 'testing'
	STAGE = 'staging'
	PROD = 'production'


def initialize_required_dirs(dir_list: list ):
	for directory in dir_list:
		try:
			if not os.path.isdir(directory):
				os.mkdir(directory, mode=0o777)
		except Exception as e:
			logging.error(f"Exception occurred while creating directory[{directory}] :\n {e}")