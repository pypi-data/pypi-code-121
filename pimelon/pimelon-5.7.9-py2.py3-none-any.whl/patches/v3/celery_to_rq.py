import click, os
from pine.config.procfile import setup_procfile
from pine.config.supervisor import generate_supervisor_config
from pine.utils.app import get_current_melon_version, get_current_branch

def execute(pine_path):
	melon_branch = get_current_branch('melon', pine_path)
	melon_version = get_current_melon_version(pine_path)

	if not (melon_branch=='develop' or melon_version >= 7):
		# not version 7+
		# prevent running this patch
		return False

	click.confirm('\nThis update will remove Celery config and prepare the pine to use Python RQ.\n'
		'And it will overwrite Procfile and supervisor.conf.\n'
		'If you don\'t know what this means, type Y ;)\n\n'
		'Do you want to continue?',
		abort=True)

	setup_procfile(pine_path, yes=True)

	# if production setup
	if os.path.exists(os.path.join(pine_path, 'config', 'supervisor.conf')):
		generate_supervisor_config(pine_path, yes=True)
