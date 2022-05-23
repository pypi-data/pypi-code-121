# imports - standard imports
import os
import logging
import sys

# imports - module imports
import pine
from pine.config.nginx import make_nginx_conf
from pine.config.supervisor import generate_supervisor_config, update_supervisord_config
from pine.config.systemd import generate_systemd_config
from pine.pine import Pine
from pine.utils import exec_cmd, which, get_pine_name, get_cmd_output, log
from pine.utils.system import fix_prod_setup_perms
from pine.exceptions import CommandFailedError

logger = logging.getLogger(pine.PROJECT_NAME)


def setup_production_prerequisites():
	"""Installs ansible, fail2banc, NGINX and supervisor"""
	if not which("ansible"):
		exec_cmd(f"sudo {sys.executable} -m pip install ansible")
	if not which("fail2ban-client"):
		exec_cmd("pine setup role fail2ban")
	if not which("nginx"):
		exec_cmd("pine setup role nginx")
	if not which("supervisord"):
		exec_cmd("pine setup role supervisor")


def setup_production(user, pine_path='.', yes=False):
	print("Setting Up prerequisites...")
	setup_production_prerequisites()

	conf = Pine(pine_path).conf

	if conf.get('restart_supervisor_on_update') and conf.get('restart_systemd_on_update'):
		raise Exception("You cannot use supervisor and systemd at the same time. Modify your common_site_config accordingly." )

	if conf.get('restart_systemd_on_update'):
		print("Setting Up systemd...")
		generate_systemd_config(pine_path=pine_path, user=user, yes=yes)
	else:
		print("Setting Up supervisor...")
		update_supervisord_config(user=user, yes=yes)
		generate_supervisor_config(pine_path=pine_path, user=user, yes=yes)

	print("Setting Up NGINX...")
	make_nginx_conf(pine_path=pine_path, yes=yes)
	fix_prod_setup_perms(pine_path, melon_user=user)
	remove_default_nginx_configs()

	pine_name = get_pine_name(pine_path)
	nginx_conf = f'/etc/nginx/conf.d/{pine_name}.conf'

	print("Setting Up symlinks and reloading services...")
	if conf.get('restart_supervisor_on_update'):
		supervisor_conf_extn = "ini" if is_centos7() else "conf"
		supervisor_conf = os.path.join(get_supervisor_confdir(), f'{pine_name}.{supervisor_conf_extn}')

		# Check if symlink exists, If not then create it.
		if not os.path.islink(supervisor_conf):
			os.symlink(os.path.abspath(os.path.join(pine_path, 'config', 'supervisor.conf')), supervisor_conf)

	if not os.path.islink(nginx_conf):
		os.symlink(os.path.abspath(os.path.join(pine_path, 'config', 'nginx.conf')), nginx_conf)

	if conf.get('restart_supervisor_on_update'):
		reload_supervisor()

	if os.environ.get('NO_SERVICE_RESTART'):
		return

	reload_nginx()


def disable_production(pine_path='.'):
	pine_name = get_pine_name(pine_path)
	conf = Pine(pine_path).conf

	# supervisorctl
	supervisor_conf_extn = "ini" if is_centos7() else "conf"
	supervisor_conf = os.path.join(get_supervisor_confdir(), f'{pine_name}.{supervisor_conf_extn}')

	if os.path.islink(supervisor_conf):
		os.unlink(supervisor_conf)

	if conf.get('restart_supervisor_on_update'):
		reload_supervisor()

	# nginx
	nginx_conf = f'/etc/nginx/conf.d/{pine_name}.conf'

	if os.path.islink(nginx_conf):
		os.unlink(nginx_conf)

	reload_nginx()


def service(service_name, service_option):
	if os.path.basename(which('systemctl') or '') == 'systemctl' and is_running_systemd():
		exec_cmd(f"sudo systemctl {service_option} {service_name}")

	elif os.path.basename(which('service') or '') == 'service':
		exec_cmd(f"sudo service {service_name} {service_option}")

	else:
		# look for 'service_manager' and 'service_manager_command' in environment
		service_manager = os.environ.get("PINE_SERVICE_MANAGER")
		if service_manager:
			service_manager_command = (
				os.environ.get("PINE_SERVICE_MANAGER_COMMAND")
				or f"{service_manager} {service_option} {service}"
			)
			exec_cmd(service_manager_command)

		else:
			log(f"No service manager found: '{service_name} {service_option}' failed to execute", level=2)


def get_supervisor_confdir():
	possiblities = ('/etc/supervisor/conf.d', '/etc/supervisor.d/', '/etc/supervisord/conf.d', '/etc/supervisord.d')
	for possiblity in possiblities:
		if os.path.exists(possiblity):
			return possiblity


def remove_default_nginx_configs():
	default_nginx_configs = ['/etc/nginx/conf.d/default.conf', '/etc/nginx/sites-enabled/default']

	for conf_file in default_nginx_configs:
		if os.path.exists(conf_file):
			os.unlink(conf_file)


def is_centos7():
	return os.path.exists('/etc/redhat-release') and get_cmd_output("cat /etc/redhat-release | sed 's/Linux\ //g' | cut -d' ' -f3 | cut -d. -f1").strip() == '7'


def is_running_systemd():
	with open('/proc/1/comm') as f:
		comm = f.read().strip()
	if comm == "init":
		return False
	elif comm == "systemd":
		return True
	return False


def reload_supervisor():
	supervisorctl = which('supervisorctl')

	try:
		# first try reread/update
		exec_cmd(f'{supervisorctl} reread')
		exec_cmd(f'{supervisorctl} update')
		return
	except CommandFailedError:
		pass

	try:
		# something is wrong, so try reloading
		exec_cmd(f'{supervisorctl} reload')
		return
	except CommandFailedError:
		pass

	try:
		# then try restart for centos
		service('supervisord', 'restart')
		return
	except CommandFailedError:
		pass

	try:
		# else try restart for ubuntu / debian
		service('supervisor', 'restart')
		return
	except CommandFailedError:
		pass

def reload_nginx():
	try:
		exec_cmd(f"sudo {which('nginx')} -t")
	except Exception:
		raise

	service('nginx', 'reload')
