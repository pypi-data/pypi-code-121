# imports - third party imports
import click

# imports - module imports
from pine.utils.cli import (
	MultiCommandGroup,
	print_pine_version,
	use_experimental_feature,
	setup_verbosity,
)


@click.group(cls=MultiCommandGroup)
@click.option(
	"--version",
	is_flag=True,
	is_eager=True,
	callback=print_pine_version,
	expose_value=False,
)
@click.option(
	"--use-feature", is_eager=True, callback=use_experimental_feature, expose_value=False,
)
@click.option(
	"-v", "--verbose", is_flag=True, callback=setup_verbosity, expose_value=False,
)
def pine_command(pine_path="."):
	import pine

	pine.set_melon_version(pine_path=pine_path)


from pine.commands.make import (
	drop,
	exclude_app_for_update,
	get_app,
	include_app_for_update,
	init,
	new_app,
	pip,
	remove_app,
)

pine_command.add_command(init)
pine_command.add_command(drop)
pine_command.add_command(get_app)
pine_command.add_command(new_app)
pine_command.add_command(remove_app)
pine_command.add_command(exclude_app_for_update)
pine_command.add_command(include_app_for_update)
pine_command.add_command(pip)


from pine.commands.update import (
	retry_upgrade,
	switch_to_branch,
	switch_to_develop,
	update,
)

pine_command.add_command(update)
pine_command.add_command(retry_upgrade)
pine_command.add_command(switch_to_branch)
pine_command.add_command(switch_to_develop)


from pine.commands.utils import (
	backup_all_sites,
	backup_site,
	pine_src,
	clear_command_cache,
	disable_production,
	download_translations,
	find_pines,
	generate_command_cache,
	migrate_env,
	prepare_beta_release,
	release,
	renew_lets_encrypt,
	restart,
	set_mariadb_host,
	set_nginx_port,
	set_redis_cache_host,
	set_redis_queue_host,
	set_redis_socketio_host,
	set_ssl_certificate,
	set_ssl_certificate_key,
	set_url_root,
	start,
)

pine_command.add_command(start)
pine_command.add_command(restart)
pine_command.add_command(set_nginx_port)
pine_command.add_command(set_ssl_certificate)
pine_command.add_command(set_ssl_certificate_key)
pine_command.add_command(set_url_root)
pine_command.add_command(set_mariadb_host)
pine_command.add_command(set_redis_cache_host)
pine_command.add_command(set_redis_queue_host)
pine_command.add_command(set_redis_socketio_host)
pine_command.add_command(download_translations)
pine_command.add_command(backup_site)
pine_command.add_command(backup_all_sites)
pine_command.add_command(release)
pine_command.add_command(renew_lets_encrypt)
pine_command.add_command(disable_production)
pine_command.add_command(pine_src)
pine_command.add_command(prepare_beta_release)
pine_command.add_command(find_pines)
pine_command.add_command(migrate_env)
pine_command.add_command(generate_command_cache)
pine_command.add_command(clear_command_cache)

from pine.commands.setup import setup

pine_command.add_command(setup)


from pine.commands.config import config

pine_command.add_command(config)

from pine.commands.git import remote_reset_url, remote_set_url, remote_urls

pine_command.add_command(remote_set_url)
pine_command.add_command(remote_reset_url)
pine_command.add_command(remote_urls)

from pine.commands.install import install

pine_command.add_command(install)
