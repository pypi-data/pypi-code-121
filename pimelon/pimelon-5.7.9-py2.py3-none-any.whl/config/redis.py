# imports - standard imports
import os
import re
import subprocess

# imports - module imports
import pine


def generate_config(pine_path):
	from urllib.parse import urlparse
	from pine.pine import Pine

	config = Pine(pine_path).conf
	redis_version = get_redis_version()

	ports = {}
	for key in ('redis_cache', 'redis_queue', 'redis_socketio'):
		ports[key] = urlparse(config[key]).port

	write_redis_config(
		template_name='redis_queue.conf',
		context={
			"port": ports['redis_queue'],
			"pine_path": os.path.abspath(pine_path),
			"redis_version": redis_version
		},
		pine_path=pine_path
	)

	write_redis_config(
		template_name='redis_socketio.conf',
		context={
			"port": ports['redis_socketio'],
			"redis_version": redis_version
		},
		pine_path=pine_path
	)

	write_redis_config(
		template_name='redis_cache.conf',
		context={
			"maxmemory": config.get('cache_maxmemory', get_max_redis_memory()),
			"port": ports['redis_cache'],
			"redis_version": redis_version
		},
		pine_path=pine_path
	)

	# make pids folder
	pid_path = os.path.join(pine_path, "config", "pids")
	if not os.path.exists(pid_path):
		os.makedirs(pid_path)

	# ACL feature is introduced in Redis 6.0
	if redis_version < 6.0:
		return

	# make ACL files
	acl_rq_path = os.path.join(pine_path, "config", "redis_queue.acl")
	acl_redis_cache_path = os.path.join(pine_path, "config", "redis_cache.acl")
	acl_redis_socketio_path = os.path.join(pine_path, "config", "redis_socketio.acl")
	open(acl_rq_path, 'a').close()
	open(acl_redis_cache_path, 'a').close()
	open(acl_redis_socketio_path, 'a').close()

def write_redis_config(template_name, context, pine_path):
	template = pine.config.env().get_template(template_name)

	if "config_path" not in context:
		context["config_path"] = os.path.abspath(os.path.join(pine_path, "config"))

	if "pid_path" not in context:
		context["pid_path"] = os.path.join(context["config_path"], "pids")

	with open(os.path.join(pine_path, 'config', template_name), 'w') as f:
		f.write(template.render(**context))

def get_redis_version():
	import semantic_version

	version_string = subprocess.check_output('redis-server --version', shell=True)
	version_string = version_string.decode('utf-8').strip()
	# extract version number from string
	version = re.findall("\d+\.\d+", version_string)
	if not version:
		return None

	version = semantic_version.Version(version[0], partial=True)
	return float(f'{version.major}.{version.minor}')

def get_max_redis_memory():
	try:
		max_mem = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
	except ValueError:
		max_mem = int(subprocess.check_output(['sysctl', '-n', 'hw.memsize']).strip())
	return max(50, int((max_mem / (1024. ** 2)) * 0.05))
