import logging
import os
from pathlib import Path
from dotenv import find_dotenv, load_dotenv, dotenv_values
from .config_variable import ConfigVariable
from .config_utils import *


# TODO : Convert to singleton
class Config:
	__is_loaded = False

	__required_dir_list: list = []

	# environment name [local|dev|test|stage|live]
	_name = None

	# project root dir
	_root_dir = None

	# the dir where env file is located
	_env_dir = None

	# .env file location [where environment name is mentioned]
	_env_file = None

	# {envirnment_name}.env file location [where environment variables will be found]
	_env_config_file = None

	# var
	_is_debug = False

	def __load_config_from_env_file(self):
		try:
			load_dotenv(self._env_file)
			self._name = os.environ.get('ENV_NAME', default=None)
			if self._name:
				self._env_config_file = os.path.join(self._env_dir, f"{self._name}.env")

				#
				if os.path.isfile(self._env_config_file):
					load_dotenv(self._env_config_file)
					logging.debug(f"Config loaded from : '{self._env_config_file}';")
				else:
					raise Exception(f"Config file doesnt exist : {self._env_config_file}")
			else:
				raise Exception(f"Invalid ENV_NAME '{self._name}' in File :'{self._env_file}'")
		except Exception as e:
			logging.error(e)
			exit()

	def __init__(self, rootdir: str = '', envdir: str = 'config',
	             base_env_file='.env', *req_dirs
	             ):

		try:

			self.__required_dir_list = list(req_dirs)
			self._root_dir = rootdir
			self._env_dir = envdir

			if not os.path.isdir(self._root_dir):
				raise Exception(f"Parameter 'rootdir' in Config(), cannot be empty")

			if not os.path.isdir(self._env_dir):
				self._env_dir = os.path.join(self._root_dir, envdir)
				self.__required_dir_list.append(self._env_dir)

			self._env_file = os.path.join(self._env_dir, base_env_file)

		except Exception as e:
			logging.error(e)
			exit()

	def load(self, force=False):
		if not self.__is_loaded or force:
			initialize_required_dirs(self.__required_dir_list)
			self.__load_config_from_env_file()
			self.__is_loaded = True
		return self

	def get(self, key: str = '', default=None) -> ConfigVariable:
		self.load()
		return ConfigVariable(key=key, default=default)

	def get_all(self, as_dict=True):
		self.load()
		config = dotenv_values(self._env_config_file)
		return config if as_dict else {key: ConfigVariable(key=key) for key in config}

	@property
	def env_name(self):
		return self._name

	@property
	def root_dir(self):
		return self._root_dir

	@property
	def debug(self):
		return self._is_debug or self.get('DEBUG').bool(default=False)

	@property
	def is_local_env(self):
		return self.env_name in [EnvNames.LOCAL]

	@property
	def is_loaded(self):
		return self.__is_loaded