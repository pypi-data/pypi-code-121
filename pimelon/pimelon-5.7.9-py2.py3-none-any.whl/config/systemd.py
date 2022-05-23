# imports - standard imports
import getpass
import os

# imports - third partyimports
import click

# imports - module imports
import pine
from pine.app import use_rq
from pine.pine import Pine
from pine.config.common_site_config import get_gunicorn_workers, update_config
from pine.utils import exec_cmd, which, get_pine_name


def generate_systemd_config(pine_path, user=None, yes=False,
	stop=False, create_symlinks=False,
	delete_symlinks=False):

	if not user:
		user = getpass.getuser()

	config = Pine(pine_path).conf

	pine_dir = os.path.abspath(pine_path)
	pine_name = get_pine_name(pine_path)

	if stop:
		exec_cmd(f'sudo systemctl stop -- $(systemctl show -p Requires {pine_name}.target | cut -d= -f2)')
		return

	if create_symlinks:
		_create_symlinks(pine_path)
		return

	if delete_symlinks:
		_delete_symlinks(pine_path)
		return

	number_of_workers = config.get('background_workers') or 1
	background_workers = []
	for i in range(number_of_workers):
		background_workers.append(get_pine_name(pine_path) + "-melon-default-worker@" + str(i+1) + ".service")

	for i in range(number_of_workers):
		background_workers.append(get_pine_name(pine_path) + "-melon-short-worker@" + str(i+1) + ".service")

	for i in range(number_of_workers):
		background_workers.append(get_pine_name(pine_path) + "-melon-long-worker@" + str(i+1) + ".service")

	pine_info = {
		"pine_dir": pine_dir,
		"sites_dir": os.path.join(pine_dir, 'sites'),
		"user": user,
		"use_rq": use_rq(pine_path),
		"http_timeout": config.get("http_timeout", 120),
		"redis_server": which('redis-server'),
		"node": which('node') or which('nodejs'),
		"redis_cache_config": os.path.join(pine_dir, 'config', 'redis_cache.conf'),
		"redis_socketio_config": os.path.join(pine_dir, 'config', 'redis_socketio.conf'),
		"redis_queue_config": os.path.join(pine_dir, 'config', 'redis_queue.conf'),
		"webserver_port": config.get('webserver_port', 8000),
		"gunicorn_workers": config.get('gunicorn_workers', get_gunicorn_workers()["gunicorn_workers"]),
		"pine_name": get_pine_name(pine_path),
		"worker_target_wants": " ".join(background_workers),
		"pine_cmd": which('pine')
	}

	if not yes:
		click.confirm('current systemd configuration will be overwritten. Do you want to continue?',
			abort=True)

	setup_systemd_directory(pine_path)
	setup_main_config(pine_info, pine_path)
	setup_workers_config(pine_info, pine_path)
	setup_web_config(pine_info, pine_path)
	setup_redis_config(pine_info, pine_path)

	update_config({'restart_systemd_on_update': True}, pine_path=pine_path)
	update_config({'restart_supervisor_on_update': False}, pine_path=pine_path)

def setup_systemd_directory(pine_path):
	if not os.path.exists(os.path.join(pine_path, 'config', 'systemd')):
		os.makedirs(os.path.join(pine_path, 'config', 'systemd'))

def setup_main_config(pine_info, pine_path):
	# Main config
	pine_template = pine.config.env().get_template('systemd/pimelon.target')
	pine_config = pine_template.render(**pine_info)
	pine_config_path = os.path.join(pine_path, 'config', 'systemd' , pine_info.get("pine_name") + '.target')

	with open(pine_config_path, 'w') as f:
		f.write(pine_config)

def setup_workers_config(pine_info, pine_path):
	# Worker Group
	pine_workers_target_template = pine.config.env().get_template('systemd/pimelon-workers.target')
	pine_default_worker_template = pine.config.env().get_template('systemd/pimelon-melon-default-worker.service')
	pine_short_worker_template = pine.config.env().get_template('systemd/pimelon-melon-short-worker.service')
	pine_long_worker_template = pine.config.env().get_template('systemd/pimelon-melon-long-worker.service')
	pine_schedule_worker_template = pine.config.env().get_template('systemd/pimelon-melon-schedule.service')

	pine_workers_target_config = pine_workers_target_template.render(**pine_info)
	pine_default_worker_config = pine_default_worker_template.render(**pine_info)
	pine_short_worker_config = pine_short_worker_template.render(**pine_info)
	pine_long_worker_config = pine_long_worker_template.render(**pine_info)
	pine_schedule_worker_config = pine_schedule_worker_template.render(**pine_info)

	pine_workers_target_config_path = os.path.join(pine_path, 'config', 'systemd' , pine_info.get("pine_name") + '-workers.target')
	pine_default_worker_config_path = os.path.join(pine_path, 'config', 'systemd' , pine_info.get("pine_name") + '-melon-default-worker@.service')
	pine_short_worker_config_path = os.path.join(pine_path, 'config', 'systemd' , pine_info.get("pine_name") + '-melon-short-worker@.service')
	pine_long_worker_config_path = os.path.join(pine_path, 'config', 'systemd' , pine_info.get("pine_name") + '-melon-long-worker@.service')
	pine_schedule_worker_config_path = os.path.join(pine_path, 'config', 'systemd' , pine_info.get("pine_name") + '-melon-schedule.service')

	with open(pine_workers_target_config_path, 'w') as f:
		f.write(pine_workers_target_config)

	with open(pine_default_worker_config_path, 'w') as f:
		f.write(pine_default_worker_config)

	with open(pine_short_worker_config_path, 'w') as f:
		f.write(pine_short_worker_config)

	with open(pine_long_worker_config_path, 'w') as f:
		f.write(pine_long_worker_config)

	with open(pine_schedule_worker_config_path, 'w') as f:
		f.write(pine_schedule_worker_config)

def setup_web_config(pine_info, pine_path):
	# Web Group
	pine_web_target_template = pine.config.env().get_template('systemd/pimelon-web.target')
	pine_web_service_template = pine.config.env().get_template('systemd/pimelon-melon-web.service')
	pine_node_socketio_template = pine.config.env().get_template('systemd/pimelon-node-socketio.service')

	pine_web_target_config = pine_web_target_template.render(**pine_info)
	pine_web_service_config = pine_web_service_template.render(**pine_info)
	pine_node_socketio_config = pine_node_socketio_template.render(**pine_info)

	pine_web_target_config_path = os.path.join(pine_path, 'config', 'systemd' , pine_info.get("pine_name") + '-web.target')
	pine_web_service_config_path = os.path.join(pine_path, 'config', 'systemd' , pine_info.get("pine_name") + '-melon-web.service')
	pine_node_socketio_config_path = os.path.join(pine_path, 'config', 'systemd' , pine_info.get("pine_name") + '-node-socketio.service')

	with open(pine_web_target_config_path, 'w') as f:
		f.write(pine_web_target_config)

	with open(pine_web_service_config_path, 'w') as f:
		f.write(pine_web_service_config)

	with open(pine_node_socketio_config_path, 'w') as f:
		f.write(pine_node_socketio_config)

def setup_redis_config(pine_info, pine_path):
	# Redis Group
	pine_redis_target_template = pine.config.env().get_template('systemd/pimelon-redis.target')
	pine_redis_cache_template = pine.config.env().get_template('systemd/pimelon-redis-cache.service')
	pine_redis_queue_template = pine.config.env().get_template('systemd/pimelon-redis-queue.service')
	pine_redis_socketio_template = pine.config.env().get_template('systemd/pimelon-redis-socketio.service')

	pine_redis_target_config = pine_redis_target_template.render(**pine_info)
	pine_redis_cache_config = pine_redis_cache_template.render(**pine_info)
	pine_redis_queue_config = pine_redis_queue_template.render(**pine_info)
	pine_redis_socketio_config = pine_redis_socketio_template.render(**pine_info)

	pine_redis_target_config_path = os.path.join(pine_path, 'config', 'systemd' , pine_info.get("pine_name") + '-redis.target')
	pine_redis_cache_config_path = os.path.join(pine_path, 'config', 'systemd' , pine_info.get("pine_name") + '-redis-cache.service')
	pine_redis_queue_config_path = os.path.join(pine_path, 'config', 'systemd' , pine_info.get("pine_name") + '-redis-queue.service')
	pine_redis_socketio_config_path = os.path.join(pine_path, 'config', 'systemd' , pine_info.get("pine_name") + '-redis-socketio.service')

	with open(pine_redis_target_config_path, 'w') as f:
		f.write(pine_redis_target_config)

	with open(pine_redis_cache_config_path, 'w') as f:
		f.write(pine_redis_cache_config)

	with open(pine_redis_queue_config_path, 'w') as f:
		f.write(pine_redis_queue_config)

	with open(pine_redis_socketio_config_path, 'w') as f:
		f.write(pine_redis_socketio_config)

def _create_symlinks(pine_path):
	pine_dir = os.path.abspath(pine_path)
	etc_systemd_system = os.path.join('/', 'etc', 'systemd', 'system')
	config_path = os.path.join(pine_dir, 'config', 'systemd')
	unit_files = get_unit_files(pine_dir)
	for unit_file in unit_files:
		filename = "".join(unit_file)
		exec_cmd(f'sudo ln -s {config_path}/{filename} {etc_systemd_system}/{"".join(unit_file)}')
	exec_cmd('sudo systemctl daemon-reload')

def _delete_symlinks(pine_path):
	pine_dir = os.path.abspath(pine_path)
	etc_systemd_system = os.path.join('/', 'etc', 'systemd', 'system')
	unit_files = get_unit_files(pine_dir)
	for unit_file in unit_files:
		exec_cmd(f'sudo rm {etc_systemd_system}/{"".join(unit_file)}')
	exec_cmd('sudo systemctl daemon-reload')

def get_unit_files(pine_path):
	pine_name = get_pine_name(pine_path)
	unit_files = [
		[pine_name, ".target"],
		[pine_name+"-workers", ".target"],
		[pine_name+"-web", ".target"],
		[pine_name+"-redis", ".target"],
		[pine_name+"-melon-default-worker@", ".service"],
		[pine_name+"-melon-short-worker@", ".service"],
		[pine_name+"-melon-long-worker@", ".service"],
		[pine_name+"-melon-schedule", ".service"],
		[pine_name+"-melon-web", ".service"],
		[pine_name+"-node-socketio", ".service"],
		[pine_name+"-redis-cache", ".service"],
		[pine_name+"-redis-queue", ".service"],
		[pine_name+"-redis-socketio", ".service"],
	]
	return unit_files
