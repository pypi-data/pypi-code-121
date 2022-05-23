"""Module for setting up system and respective pine configurations"""


def env():
	from jinja2 import Environment, PackageLoader
	return Environment(loader=PackageLoader('pine.config'))
