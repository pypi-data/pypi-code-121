_P='[red]Error:[/red] '
_O='--reset/--no-reset'
_N='--inject/--no-inject'
_M='Injects the state from a version into the application runtime'
_L='--remote'
_K='--message'
_J='--version'
_I='-v'
_H=False
_G='name'
_F='Name of the cloud pod'
_E='cpvcs'
_D='backend'
_C='--name'
_B='-n'
_A=True
import json,logging,os,sys,typing as t
from typing import Any
import click
from click import Context
from localstack.cli import LocalstackCli,LocalstackCliPlugin,console
from localstack.utils.analytics.cli import publish_invocation
class ProCliPlugin(LocalstackCliPlugin):
	name='pro'
	def should_load(self):e=os.getenv('LOCALSTACK_API_KEY');return _A if e else _H
	def is_active(self):return self.should_load()
	def attach(self,cli):group=cli.group;group.add_command(cmd_login);group.add_command(cmd_logout);group.add_command(daemons);group.add_command(dns);group.add_command(pod)
def required_if_not_cached(option_key):
	class PodConfigContext(click.Option):
		def handle_parse_result(self,ctx,opts,args):
			from localstack_ext.bootstrap import pods_client;is_present=self.name in opts
			if not is_present:
				config_cache=pods_client.get_pods_config();pod_name=config_cache.get(option_key)
				if pod_name is None:raise click.MissingParameter(f"Parameter `--{option_key}` unspecified. Call with `--{option_key}` or set the parameter with `set-context`")
				opts[self.name]=pod_name
			return super().handle_parse_result(ctx,opts,args)
	return PodConfigContext
@click.group(name='daemons',help='Manage local daemon processes')
def daemons():0
@click.command(name='login',help='Log in with your account credentials')
@click.option('--username',help='Username for login')
@click.option('--provider',default='internal',help='OAuth provider (default: localstack internal login)')
@publish_invocation
def cmd_login(username,provider):
	from localstack_ext.bootstrap import auth
	try:auth.login(provider,username);console.print('successfully logged in')
	except Exception as e:console.print('authentication error: %s'%e)
@click.command(name='logout',help='Log out and delete any session tokens')
@publish_invocation
def cmd_logout():
	from localstack_ext.bootstrap import auth
	try:auth.logout();console.print('successfully logged out')
	except Exception as e:console.print('logout error: %s'%e)
@daemons.command(name='start',help='Start local daemon processes')
@publish_invocation
def cmd_daemons_start():from localstack_ext.bootstrap import local_daemon;console.log('Starting local daemons processes ...');thread=local_daemon.start_in_background();thread.join()
@daemons.command(name='stop',help='Stop local daemon processes')
@publish_invocation
def cmd_daemons_stop():from localstack_ext.bootstrap import local_daemon;console.log('Stopping local daemons processes ...');local_daemon.kill_servers()
@daemons.command(name='log',help='Show log of daemon process')
@publish_invocation
def cmd_daemons_log():
	from localstack_ext.bootstrap import local_daemon;file_path=local_daemon.get_log_file_path()
	if not os.path.isfile(file_path):console.print('no log found')
	else:
		with open(file_path,'r')as fd:
			for line in fd:sys.stdout.write(line);sys.stdout.flush()
@click.group(name='dns',help='Manage DNS settings of your host')
def dns():0
@dns.command(name='systemd-resolved',help='Manage DNS settings of systemd-resolved (Ubuntu, Debian etc.)')
@click.option('--revert',is_flag=_A,help='Revert systemd-resolved settings for the docker interface')
@publish_invocation
def cmd_dns_systemd(revert):import localstack_ext.bootstrap.dns_utils;from localstack_ext.bootstrap.dns_utils import configure_systemd;console.print('Configuring systemd-resolved...');logger_name=localstack_ext.bootstrap.dns_utils.LOG.name;localstack_ext.bootstrap.dns_utils.LOG=ConsoleLogger(logger_name);configure_systemd(revert)
def _cloud_pod_initialized(pod_name):
	from localstack_ext.bootstrap import pods_client
	if not pods_client.is_initialized(pod_name=pod_name):console.print('[red]Error:[/red] Could not find local CloudPods instance');return _H
	return _A
@click.group(name='pod',help='Cloud Pods with elaborate versioning mechanism')
def pod():
	from localstack_ext.bootstrap.licensing import is_logged_in
	if not is_logged_in():console.print('[red]Error:[/red] not logged in, please log in first');sys.exit(1)
@pod.command(name='set-context',help='Sets the context for all the pod commands')
@click.option(_B,_C,help='Name of the cloud pod to set in the context',required=_A)
@publish_invocation
def cmd_pod_set_context(name):from localstack_ext.bootstrap import pods_client;options=dict(locals());del options['pods_client'];pods_client.save_pods_config(options=options)
@pod.command(name='delete',help='Deletes the specified cloud pod. By default only locally')
@click.option(_B,_C,help=_F,cls=required_if_not_cached(_G))
@click.option('-r',_L,help='Whether the Pod should also be deleted remotely.',is_flag=_A,default=_H)
@publish_invocation
def cmd_pod_delete(name,remote):
	from localstack_ext.bootstrap import pods_client;result=pods_client.delete_pod(pod_name=name,remote=remote,pre_config={_D:_E})
	if result:console.print(f"Successfully deleted {name}")
	else:console.print(f"[yellow]{name} not available locally[/yellow]")
@pod.command(name='rename',help='Renames the pod. If the pod is remotely registered, change is also propagated to remote')
@click.option(_B,_C,help='Current Name of the cloud pod',required=_A)
@click.option('-nn','--new-name',help='New name of the cloud pod',required=_A)
@publish_invocation
def cmd_pod_rename(name,new_name):
	from localstack_ext.bootstrap import pods_client
	if _cloud_pod_initialized(pod_name=name):
		result=pods_client.rename_pod(current_pod_name=name,new_pod_name=new_name,pre_config={_D:_E})
		if result:console.print(f"Successfully renamed {name} to {new_name}")
		else:console.print(f"[red]Error:[/red] Failed to rename {name} to {new_name}")
@pod.command(name='commit',help='Commits the current expansion point and creates a new (empty) revision')
@click.option('-m',_K,help='Add a comment describing the revision')
@click.option(_B,_C,help=_F,cls=required_if_not_cached(_G))
@publish_invocation
def cmd_pod_commit(message,name):from localstack_ext.bootstrap import pods_client;pods_client.commit_state(pod_name=name,pre_config={_D:_E},message=message);console.print('Successfully committed the current state')
@pod.command(name='push',help='Creates a new version by using the state files in the current expansion point (latest commit)')
@click.option('--register/--no-register',default=_A,help='Registers a local Cloud Pod instance with platform')
@click.option('--squash',is_flag=_A,help='Squashes commits together, so only the latest commit is stored in the revision graph')
@click.option('--three-way',is_flag=_A,default=_H,help='')
@click.option('-m',_K,help='Add a comment describing the version')
@click.option(_B,_C,help=_F,cls=required_if_not_cached(_G))
@publish_invocation
def cmd_pod_push(squash,message,name,register,three_way):
	from localstack_ext.bootstrap import pods_client;result=pods_client.push_state(pod_name=name,pre_config={_D:_E},squash_commits=squash,comment=message,register=register);console.print('Successfully pushed the current state')
	if register:
		if result:console.print(f"Successfully registered {name} with remote!")
		else:console.print(f"[red]Error:[/red] Pod with name {name} is already registered")
@pod.command(name='push-overwrite',help='Overwrites a version with the content from the latest commit of the currently selected version')
@click.option(_B,_C,help=_F,cls=required_if_not_cached(_G))
@click.option(_I,_J,type=int)
@click.option('-m',_K,required=_H)
@publish_invocation
def cmd_pod_push_overwrite(version,message,name):
	from localstack_ext.bootstrap import pods_client
	if _cloud_pod_initialized(pod_name=name):
		result=pods_client.push_overwrite(version=version,pod_name=name,comment=message,pre_config={_D:_E})
		if result:console.print('Successfully overwritten state of version ')
@pod.command(name='inject',help=_M)
@click.option(_I,_J,default='-1',type=int,help='Loads the state of the specified version - Most recent one by default')
@click.option('--reset',is_flag=_A,default=_H,help='Will reset the application state before injecting')
@click.option(_B,_C,help=_F,cls=required_if_not_cached(_G))
@publish_invocation
def cmd_pod_inject(version,reset,name):
	from localstack_ext.bootstrap import pods_client;result=pods_client.inject_state(pod_name=name,version=version,reset_state=reset,pre_config={_D:_E})
	if result:console.print('[green]Successfully Injected Pod State[/green]')
	else:console.print('[red]Failed to Inject Pod State[/red]')
@click.option(_N,default=_A,help='Whether the latest version of the pulled pod should be injected')
@click.option(_O,default=_A,help='Whether the current application state should be reset after the pod has been pulled')
@click.option(_B,_C,help=_F,cls=required_if_not_cached(_G))
@click.option('--lazy/--eager',default=_A,help='Will only fetch references to existing versions, i.e. version state is only downloaded when required')
@pod.command(name='pull',help=_M)
@publish_invocation
def cmd_pod_pull(name,inject,reset,lazy):from localstack_ext.bootstrap import pods_client;pods_client.pull_state(pod_name=name,inject_version_state=inject,reset_state_before=reset,lazy=lazy,pre_config={_D:_E})
@pod.command(name='list',help='Lists all pods and indicates which pods exist locally and, by default, which ones are managed remotely')
@click.option(_L,'-r',is_flag=_A,default=_H)
@publish_invocation
def cmd_pod_list_pods(remote):
	from localstack_ext.bootstrap import pods_client;pods=pods_client.list_pods(remote=remote,pre_config={_D:_E})
	if not pods:console.print(f"[yellow]No pods available {'locally'if not remote else''}[/yellow]")
	else:console.print('\n'.join(pods))
@pod.command(name='versions',help='Lists all available version numbers')
@click.option(_B,_C,help=_F,cls=required_if_not_cached(_G))
@publish_invocation
def cmd_pod_versions(name):
	if _cloud_pod_initialized(pod_name=name):from localstack_ext.bootstrap import pods_client;version_list=pods_client.list_versions(pod_name=name,pre_config={_D:_E});result='\n'.join(version_list);console.print(result)
@pod.command(name='version-info')
@click.option(_I,_J,required=_A,type=int)
@click.option(_B,_C,help=_F,cls=required_if_not_cached(_G))
@publish_invocation
def cmd_pod_version_info(version,name):
	if _cloud_pod_initialized(pod_name=name):from localstack_ext.bootstrap import pods_client;info=pods_client.get_version_info(version=version,pod_name=name,pre_config={_D:_E});console.print_json(json.dumps(info))
@pod.command(name='metamodel',help='Displays the content metamodel as json')
@click.option(_I,_J,type=int,default=-1,help='Latest version by default')
@click.option(_B,_C,help=_F,cls=required_if_not_cached(_G))
@publish_invocation
def cmd_pod_version_metamodel(version,name):
	if _cloud_pod_initialized(pod_name=name):
		from localstack_ext.bootstrap import pods_client;metamodel=pods_client.get_version_metamodel(version=version,pod_name=name,pre_config={_D:_E})
		if metamodel:console.print_json(json.dumps(metamodel))
		else:console.print(f"[red]Could not find metamodel for pod {name} with version {version}[/red]")
@pod.command(name='set-version',help='Set HEAD to a specific version')
@click.option(_I,_J,required=_A,type=int,help='The version the state should be set to')
@click.option(_N,default=_A,help='Whether the state should be directly injected into the application runtime after changing version')
@click.option(_O,default=_A,help='Whether the current application state should be reset before changing version')
@click.option('--commit-before',is_flag=_H,help='Whether the current application state should be committed to the currently selected version before changing version')
@click.option(_B,_C,help=_F,cls=required_if_not_cached(_G))
@publish_invocation
def cmd_pod_set_version(version,inject,reset,commit_before,name):
	if _cloud_pod_initialized(pod_name=name):from localstack_ext.bootstrap import pods_client;pods_client.set_version(version=version,inject_version_state=inject,reset_state=reset,commit_before=commit_before,pod_name=name,pre_config={_D:_E})
@pod.command(name='commits',help='Shows the commit history of a version')
@click.option(_J,_I,default=-1)
@click.option(_B,_C,help=_F,cls=required_if_not_cached(_G))
@publish_invocation
def cmd_pod_commits(version,name):
	if _cloud_pod_initialized(pod_name=name):from localstack_ext.bootstrap import pods_client;commits=pods_client.list_version_commits(version=version,pod_name=name,pre_config={_D:_E});result='\n'.join(commits);console.print(result)
@pod.command(name='commit-diff',help='Shows the changes made by a commit')
@click.option(_J,_I,required=_A)
@click.option('--commit','-c',required=_A)
@click.option(_B,_C,help=_F,cls=required_if_not_cached(_G))
@publish_invocation
def cmd_pod_commit_diff(version,commit,name):
	if _cloud_pod_initialized(pod_name=name):
		from localstack_ext.bootstrap import pods_client;commit_diff=pods_client.get_commit_diff(version=version,commit=commit,pod_name=name,pre_config={_D:_E})
		if commit_diff:console.print_json(json.dumps(commit_diff))
		else:console.print(f"[red]Error:[/red] Commit {commit} not found for version {version}")
class ConsoleLogger(logging.Logger):
	def __init__(self,name):super(ConsoleLogger,self).__init__(name)
	def info(self,msg,*args,**kwargs):console.print(msg%args)
	def warning(self,msg,*args,**kwargs):console.print('[red]Warning:[/red] ',msg%args)
	def error(self,msg,*args,**kwargs):console.print(_P,msg%args)
	def exception(self,msg,*args,**kwargs):console.print(_P,msg%args);console.print_exception()