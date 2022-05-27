_A='[red]Error:[/red] '
import logging,os,sys
from typing import Any
import click
from localstack.cli import LocalstackCli,LocalstackCliPlugin,console
from localstack.utils.analytics.cli import publish_invocation
from .cloud_pods import pod
class ProCliPlugin(LocalstackCliPlugin):
	name='pro'
	def should_load(B):A=os.getenv('LOCALSTACK_API_KEY');return True if A else False
	def is_active(A):return A.should_load()
	def attach(B,cli):A=cli.group;A.add_command(cmd_login);A.add_command(cmd_logout);A.add_command(daemons);A.add_command(dns);A.add_command(pod)
@click.group(name='daemons',help='Manage local daemon processes')
def daemons():0
@click.command(name='login',help='Log in with your account credentials')
@click.option('--username',help='Username for login')
@publish_invocation
def cmd_login(username):
	from localstack_ext.bootstrap import auth
	try:auth.login(username);console.print('successfully logged in')
	except Exception as A:console.print('authentication error: %s'%A)
@click.command(name='logout',help='Log out and delete any session tokens')
@publish_invocation
def cmd_logout():
	from localstack_ext.bootstrap import auth
	try:auth.logout();console.print('successfully logged out')
	except Exception as A:console.print('logout error: %s'%A)
@daemons.command(name='start',help='Start local daemon processes')
@publish_invocation
def cmd_daemons_start():from localstack_ext.bootstrap import local_daemon as A;console.log('Starting local daemons processes ...');B=A.start_in_background();B.join()
@daemons.command(name='stop',help='Stop local daemon processes')
@publish_invocation
def cmd_daemons_stop():from localstack_ext.bootstrap import local_daemon as A;console.log('Stopping local daemons processes ...');A.kill_servers()
@daemons.command(name='log',help='Show log of daemon process')
@publish_invocation
def cmd_daemons_log():
	from localstack_ext.bootstrap import local_daemon as B;A=B.get_log_file_path()
	if not os.path.isfile(A):console.print('no log found')
	else:
		with open(A,'r')as C:
			for D in C:sys.stdout.write(D);sys.stdout.flush()
@click.group(name='dns',help='Manage DNS settings of your host')
def dns():0
@dns.command(name='systemd-resolved',help='Manage DNS settings of systemd-resolved (Ubuntu, Debian etc.)')
@click.option('--revert',is_flag=True,help='Revert systemd-resolved settings for the docker interface')
@publish_invocation
def cmd_dns_systemd(revert):import localstack_ext.bootstrap.dns_utils;from localstack_ext.bootstrap.dns_utils import configure_systemd as A;console.print('Configuring systemd-resolved...');B=localstack_ext.bootstrap.dns_utils.LOG.name;localstack_ext.bootstrap.dns_utils.LOG=ConsoleLogger(B);A(revert)
class ConsoleLogger(logging.Logger):
	def __init__(A,name):super(ConsoleLogger,A).__init__(name)
	def info(B,msg,*A,**C):console.print(msg%A)
	def warning(B,msg,*A,**C):console.print('[red]Warning:[/red] ',msg%A)
	def error(B,msg,*A,**C):console.print(_A,msg%A)
	def exception(B,msg,*A,**C):console.print(_A,msg%A);console.print_exception()