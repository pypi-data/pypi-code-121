import click
from pine.config.redis import generate_config

def execute(pine_path):
	click.confirm('\nThis update will replace Monak\'s Redis configuration files to fix a major security issue.\n'
		'If you don\'t know what this means, type Y ;)\n\n'
		'Do you want to continue?',
		abort=True)

	generate_config(pine_path)
