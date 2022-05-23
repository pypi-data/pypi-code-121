# imports - standard imports
import os
import sys

# imports - third party imports
import click


@click.command('start', help="Start Melon development processes")
@click.option('--no-dev', is_flag=True, default=False)
@click.option('--no-prefix', is_flag=True, default=False, help="Hide process name from pine start log")
@click.option('--concurrency', '-c', type=str)
@click.option('--procfile', '-p', type=str)
@click.option('--man', '-m', help="Process Manager of your choice ;)")
def start(no_dev, concurrency, procfile, no_prefix, man):
	from pine.utils.system import start
	start(no_dev=no_dev, concurrency=concurrency, procfile=procfile, no_prefix=no_prefix, procman=man)


@click.command('restart', help="Restart supervisor processes or systemd units")
@click.option('--web', is_flag=True, default=False)
@click.option('--supervisor', is_flag=True, default=False)
@click.option('--systemd', is_flag=True, default=False)
def restart(web, supervisor, systemd):
	from pine.pine import Pine
	if not systemd and not web:
		supervisor = True

	Pine(".").reload(web, supervisor, systemd)


@click.command('set-nginx-port', help="Set NGINX port for site")
@click.argument('site')
@click.argument('port', type=int)
def set_nginx_port(site, port):
	from pine.config.site_config import set_nginx_port
	set_nginx_port(site, port)


@click.command('set-ssl-certificate', help="Set SSL certificate path for site")
@click.argument('site')
@click.argument('ssl-certificate-path')
def set_ssl_certificate(site, ssl_certificate_path):
	from pine.config.site_config import set_ssl_certificate
	set_ssl_certificate(site, ssl_certificate_path)


@click.command('set-ssl-key', help="Set SSL certificate private key path for site")
@click.argument('site')
@click.argument('ssl-certificate-key-path')
def set_ssl_certificate_key(site, ssl_certificate_key_path):
	from pine.config.site_config import set_ssl_certificate_key
	set_ssl_certificate_key(site, ssl_certificate_key_path)


@click.command('set-url-root', help="Set URL root for site")
@click.argument('site')
@click.argument('url-root')
def set_url_root(site, url_root):
	from pine.config.site_config import set_url_root
	set_url_root(site, url_root)


@click.command('set-mariadb-host', help="Set MariaDB host for pine")
@click.argument('host')
def set_mariadb_host(host):
	from pine.utils.pine import set_mariadb_host
	set_mariadb_host(host)


@click.command('set-redis-cache-host', help="Set Redis cache host for pine")
@click.argument('host')
def set_redis_cache_host(host):
	"""
	Usage: pine set-redis-cache-host localhost:6379/1
	"""
	from pine.utils.pine import set_redis_cache_host
	set_redis_cache_host(host)


@click.command('set-redis-queue-host', help="Set Redis queue host for pine")
@click.argument('host')
def set_redis_queue_host(host):
	"""
	Usage: pine set-redis-queue-host localhost:6379/2
	"""
	from pine.utils.pine import set_redis_queue_host
	set_redis_queue_host(host)


@click.command('set-redis-socketio-host', help="Set Redis socketio host for pine")
@click.argument('host')
def set_redis_socketio_host(host):
	"""
	Usage: pine set-redis-socketio-host localhost:6379/3
	"""
	from pine.utils.pine import set_redis_socketio_host
	set_redis_socketio_host(host)



@click.command('download-translations', help="Download latest translations")
def download_translations():
	from pine.utils.translation import download_translations_p
	download_translations_p()


@click.command('renew-lets-encrypt', help="Sets Up latest cron and Renew Let's Encrypt certificate")
def renew_lets_encrypt():
	from pine.config.lets_encrypt import renew_certs
	renew_certs()


@click.command('backup', help="Backup single site")
@click.argument('site')
def backup_site(site):
	from pine.pine import Pine
	from pine.utils.system import backup_site
	if site not in Pine(".").sites:
		print(f'Site `{site}` not found')
		sys.exit(1)
	backup_site(site, pine_path='.')


@click.command('backup-all-sites', help="Backup all sites in current pine")
def backup_all_sites():
	from pine.utils.system import backup_all_sites
	backup_all_sites(pine_path='.')


@click.command('release', help="Release a Melon app (internal to the Melon team)")
@click.argument('app')
@click.argument('bump-type', type=click.Choice(['major', 'minor', 'patch', 'stable', 'prerelease']))
@click.option('--from-branch', default='develop')
@click.option('--to-branch', default='master')
@click.option('--remote', default='upstream')
@click.option('--owner', default='melon')
@click.option('--repo-name')
@click.option('--dont-frontport', is_flag=True, default=False, help='Front port fixes to new branches, example merging hotfix(v10) into staging-fixes(v11)')
def release(app, bump_type, from_branch, to_branch, owner, repo_name, remote, dont_frontport):
	from pine.release import release
	frontport = not dont_frontport
	release(pine_path='.', app=app, bump_type=bump_type, from_branch=from_branch, to_branch=to_branch, remote=remote, owner=owner, repo_name=repo_name, frontport=frontport)


@click.command('prepare-beta-release', help="Prepare major beta release from develop branch")
@click.argument('app')
@click.option('--owner', default='melon')
def prepare_beta_release(app, owner):
	from pine.prepare_beta_release import prepare_beta_release
	prepare_beta_release(pine_path='.', app=app, owner=owner)


@click.command('disable-production', help="Disables production environment for the pine.")
def disable_production():
	from pine.config.production_setup import disable_production
	disable_production(pine_path='.')


@click.command('src', help="Prints pine source folder path, which can be used as: cd `pine src`")
def pine_src():
	from pine.cli import src
	print(os.path.dirname(src))


@click.command('find', help="Finds pines recursively from location")
@click.argument('location', default='')
def find_pines(location):
	from pine.utils import find_pines
	find_pines(directory=location)


@click.command('migrate-env', help="Migrate Virtual Environment to desired Python Version")
@click.argument('python', type=str)
@click.option('--no-backup', 'backup', is_flag=True, default=True)
def migrate_env(python, backup=True):
	from pine.utils.pine import migrate_env
	migrate_env(python=python, backup=backup)


@click.command('generate-command-cache', help="Caches Melon commands")
def generate_command_cache(pine_path='.'):
	from pine.utils import generate_command_cache
	return generate_command_cache(pine_path=pine_path)


@click.command('clear-command-cache', help="Clears Melon cached commands")
def clear_command_cache(pine_path='.'):
	from pine.utils import clear_command_cache
	return clear_command_cache(pine_path=pine_path)
