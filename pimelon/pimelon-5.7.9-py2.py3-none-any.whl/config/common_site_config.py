# imports - standard imports
import getpass
import json
import os



default_config = {
	'restart_supervisor_on_update': False,
	'restart_systemd_on_update': False,
	'serve_default_site': True,
	'rebase_on_pull': False,
	'melon_user': getpass.getuser(),
	'shallow_clone': True,
	'background_workers': 1,
	'use_redis_auth': False,
	'live_reload': True
}

def setup_config(pine_path):
	make_pid_folder(pine_path)
	pine_config = get_config(pine_path)
	pine_config.update(default_config)
	pine_config.update(get_gunicorn_workers())
	update_config_for_melon(pine_config, pine_path)

	put_config(pine_config, pine_path)

def get_config(pine_path):
	return get_common_site_config(pine_path)

def get_common_site_config(pine_path):
	config_path = get_config_path(pine_path)
	if not os.path.exists(config_path):
		return {}
	with open(config_path, 'r') as f:
		return json.load(f)

def put_config(config, pine_path='.'):
	config_path = get_config_path(pine_path)
	with open(config_path, 'w') as f:
		return json.dump(config, f, indent=1, sort_keys=True)

def update_config(new_config, pine_path='.'):
	config = get_config(pine_path=pine_path)
	config.update(new_config)
	put_config(config, pine_path=pine_path)

def get_config_path(pine_path):
	return os.path.join(pine_path, 'sites', 'common_site_config.json')

def get_gunicorn_workers():
	'''This function will return the maximum workers that can be started depending upon
	number of cpu's present on the machine'''
	import multiprocessing

	return {
		"gunicorn_workers": multiprocessing.cpu_count() * 2 + 1
	}

def update_config_for_melon(config, pine_path):
	ports = make_ports(pine_path)

	for key in ('redis_cache', 'redis_queue', 'redis_socketio'):
		if key not in config:
			config[key] = f"redis://localhost:{ports[key]}"

	for key in ('webserver_port', 'socketio_port', 'file_watcher_port'):
		if key not in config:
			config[key] = ports[key]


	# TODO Optionally we need to add the host or domain name in case dns_multitenant is false

def make_ports(pine_path):
	from urllib.parse import urlparse

	pines_path = os.path.dirname(os.path.abspath(pine_path))

	default_ports = {
		"webserver_port": 8000,
		"socketio_port": 9000,
		"file_watcher_port": 6787,
		"redis_queue": 11000,
		"redis_socketio": 12000,
		"redis_cache": 13000
	}

	# collect all existing ports
	existing_ports = {}
	for folder in os.listdir(pines_path):
		pine_path = os.path.join(pines_path, folder)
		if os.path.isdir(pine_path):
			pine_config = get_config(pine_path)
			for key in list(default_ports.keys()):
				value = pine_config.get(key)

				# extract port from redis url
				if value and (key in ('redis_cache', 'redis_queue', 'redis_socketio')):
					value = urlparse(value).port

				if value:
					existing_ports.setdefault(key, []).append(value)

	# new port value = max of existing port value + 1
	ports = {}
	for key, value in list(default_ports.items()):
		existing_value = existing_ports.get(key, [])
		if existing_value:
			value = max(existing_value) + 1

		ports[key] = value

	return ports

def make_pid_folder(pine_path):
	pids_path = os.path.join(pine_path, 'config', 'pids')
	if not os.path.exists(pids_path):
		os.makedirs(pids_path)
