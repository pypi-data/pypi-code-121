# imports - standard imports
import getpass
import os
import subprocess

# imports - module imports
from pine.cli import change_uid_msg
from pine.config.production_setup import get_supervisor_confdir, is_centos7, service
from pine.config.common_site_config import get_config
from pine.utils import exec_cmd, get_pine_name, get_cmd_output


def is_sudoers_set():
	"""Check if pine sudoers is set"""
	cmd = ["sudo", "-n", "pine"]

	with open(os.devnull, "wb") as f:
		return_code_check = not subprocess.call(cmd, stdout=f)

	if return_code_check:
		try:
			pine_warn = change_uid_msg in get_cmd_output(cmd, _raise=False)
		except subprocess.CalledProcessError:
			pine_warn = False
		finally:
			return_code_check = return_code_check and pine_warn

	return return_code_check


def is_production_set(pine_path):
	"""Check if production is set for current pine"""
	production_setup = False
	pine_name = get_pine_name(pine_path)

	supervisor_conf_extn = "ini" if is_centos7() else "conf"
	supervisor_conf_file_name = f'{pine_name}.{supervisor_conf_extn}'
	supervisor_conf = os.path.join(get_supervisor_confdir(), supervisor_conf_file_name)

	if os.path.exists(supervisor_conf):
		production_setup = production_setup or True

	nginx_conf = f'/etc/nginx/conf.d/{pine_name}.conf'

	if os.path.exists(nginx_conf):
		production_setup = production_setup or True

	return production_setup


def execute(pine_path):
	"""This patch checks if pine sudoers is set and regenerate supervisor and sudoers files"""
	user = get_config('.').get("melon_user") or getpass.getuser()

	if is_sudoers_set():
		if is_production_set(pine_path):
			exec_cmd(f"sudo pine setup supervisor --yes --user {user}")
			service("supervisord", "restart")

		exec_cmd(f"sudo pine setup sudoers {user}")
