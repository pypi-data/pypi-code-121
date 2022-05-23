from collections import OrderedDict
from simple_term_menu import TerminalMenu
import getpass
import platform
import re
import requests
import subprocess
import sys
import urllib.parse
import json
import os
import traceback

#-------------------------------------------------------------------------------
class Plugin:
	def __init__(self, name, version, url, condition):
		self.name			= name
		self.version		= version
		self.raw_version	= re.sub(r'\+.*', '', version)
		self.url			= url
		self.condition		= condition

	def eval(self, mods):
		def eval_arch(condition):
			arch = condition.get('arch', None)
			if arch is None:			return True
			if isinstance(arch, str):	return arch == platform.machine()
			raise Exception('"arch" cannot be of type {}'.format(type(arch)))

		def eval_pkg(condition):
			pkg = condition.get('pkg', None)
			if pkg is None:	return True
			elif isinstance(pkg, str):	return pkg in mods
			elif isinstance(pkg, (tuple, list)):
				for _ in pkg:
					if _ in mods:
						return True
				return False
			raise Exception('"pkg" cannot be of type {}'.format(type(pkg)))

		def eval_condition(condition):
			if condition is None:
				return True
			if isinstance(condition, dict):
				return eval_arch(condition) and eval_pkg(condition)
			if isinstance(condition, (tuple, list)):
				for _ in condition:
					if eval_condition(_):
						return True
				return False
			raise Exception('"condition" cannot be of type {}'.format(type(condition)))

		return eval_condition(self.condition)
		
	def __repr__(self):
		return '[Plugin name={}, version={}, url={}, condition={}]'.format(self.name, self.version, self.url, self.condition)

L_EMPH  	= "\033[1m"
L_ERROR		= "\033[0;31m"
L_RESET 	= "\033[0m"

s_access			= OrderedDict()
s_available			= OrderedDict()
s_globally			= False
s_local_repo		= False
s_modules			= None
s_plugins			= None
s_trust				= False
s_user_access		= None
s_credentials		= None
s_prefix			= None
s_license_version	= None
s_version			= None
s_reverse			= None

#-------------------------------------------------------------------------------
def add(plugin, version, url, mod, conds=None):
	if mod not in s_available:
		s_available[mod] = {}
	s_available[mod][plugin] = Plugin(plugin, version, url, conds)
	
	if mod not in ('license', 'core'):
		if mod not in s_access:
			s_access[mod] = set()
		s_access[mod].add(url)

#-------------------------------------------------------------------------------
with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r') as f:
	data = json.load(f)
	assert isinstance(data, dict)
	s_prefix			= data.get('prefix')
	s_version			= data.get('version')
	s_license_version	= data.get('license_version')
	s_reverse			= data.get('reverse')
	for plugin in data.get('plugins'):
		add(*plugin)

#-------------------------------------------------------------------------------
# taken from: https://stackoverflow.com/questions/1871549/determine-if-python-is-running-inside-virtualenv
def is_virtualenv():
	return (hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))

#-------------------------------------------------------------------------------
def run(cmd):
	ret = subprocess.run(cmd)
	if ret.returncode != 0:
		raise Exception("PIP error detected")

#-------------------------------------------------------------------------------
def run_output(cmd):
	ret = subprocess.run(cmd, stdout=subprocess.PIPE)
	if ret.returncode != 0:
		raise Exception("PIP error detected")
	return ret.stdout.decode('utf-8')

#-------------------------------------------------------------------------------
def lookup_modules(plugins):
	assert isinstance(plugins, list)
	modules = set()
	for p in plugins:
		r = s_reverse.get(p)
		if r:
			modules.add(r)
	return modules

#-------------------------------------------------------------------------------
def initialize():
	def init_plugins():
		input = run_output(['python3', '-m', 'pip', 'list', 'installed']).split('\n')
		plugins = {}
		prog = re.compile(r'^({}-sol[a-z0-9-]+)\s+([0-9\.a-z]+)'.format(s_prefix))
		for x in input:
			match = prog.match(x)
			if match:
				plugins[match[1]] = match[2]
		return plugins
	
	global s_plugins, s_modules
	s_plugins = init_plugins()
	s_modules = lookup_modules(list(s_plugins.keys()))

#-------------------------------------------------------------------------------
def get_plugins():		return s_plugins
def get_modules():		return s_modules
def get_available():	return s_available

#-------------------------------------------------------------------------------
# Callbacks
#-------------------------------------------------------------------------------
def install(plugins, is_install):
	assert isinstance(plugins, list)
	assert isinstance(is_install, bool)
	assert s_local_repo or (isinstance(s_credentials, tuple) and len(s_credentials) == 2)

	cmd = ['python3', '-m', 'pip', 'install' if is_install else 'download']

	if is_install and not is_virtualenv() and not s_globally:
		cmd.append('--user')

	for p in plugins:
		cmd.append('{}=={}'.format(p.name, p.version))

	if s_local_repo:
		cmd.append('-f')
		cmd.append('.')
	else:
		if s_trust:
			cmd.append('--trusted-host')
			cmd.append('sol.neclab.eu')

			# https://gitlab.neclab.eu/darp-git-SOL-CLOSED-BETA/sol-closed-beta/-/issues/436
			cmd.append('--trusted-host')
			cmd.append('download.pytorch.org')

		# https://pip.pypa.io/en/stable/topics/authentication/#percent-encoding-special-characters
		username = s_credentials[0]
		password = urllib.parse.quote(s_credentials[1].encode('utf8'))

		urls = set(p.url.replace('{USERNAME}', username).replace('{PASSWORD}', password) for p in plugins)

		for u in urls:
			cmd.append('-f')
			cmd.append(u)

	run(cmd)
	initialize() # update database

#-------------------------------------------------------------------------------
def uninstall(plugins=None):
	global s_modules

	if plugins is None:
		initialize()
		if len(get_plugins()) == 0:
			print('SOL is not installed on this machine')
			return

		options			= ['no, not really', 'yes of course!']
		terminal_menu	= TerminalMenu(options, title='Are you sure you want to uninstall SOL?\n')
		choice			= terminal_menu.show()
		if choice == 1:
			plugins		= list(get_plugins().keys())
		else:
			return
	
	assert isinstance(plugins, list)
	if len(plugins):
		run(['python3', '-m', 'pip', 'uninstall', '-y'] + plugins)

		# update lookups -------------------------------------------------------
		for p in plugins:
			get_plugins().pop(p)
		s_modules = lookup_modules(list(get_plugins().keys()))

#-------------------------------------------------------------------------------
def get_plugin_list(mods):
	assert isinstance(mods, list)
	plugins		= set()
	available	= get_available()

	for m in mods:
		for p in available.get(m).values():
			if p.eval(mods):
				plugins.add(p)

	return list(plugins)

#-------------------------------------------------------------------------------
def select_modules(is_install):
	assert isinstance(is_install, bool)
	if is_install:
		initialize()

	check_license	(is_install)
	upgrade			(is_install)

	assert isinstance(s_user_access, set)
	assert s_local_repo or (isinstance(s_credentials, tuple) and len(s_credentials) == 2)

	mods				= ['core', 'license']
	modules				= []
	already_installed	= []

	for m in get_available().keys():
		if m not in s_user_access:
			continue

		if is_install and m in get_modules():
			already_installed.append(len(modules))
		modules.append(m)

	terminal_menu = None

	def preview(_):
		mod_list = list(mods)
		for idx in terminal_menu._selection:
			mod_list.append(modules[idx])

		plugin_list = get_plugin_list(mod_list)
		plugins	= list('\n- {}=={}'.format(p.name, p.version) for p in plugin_list)
		
		out = ''
		if not s_local_repo:
			urls	= set()
			for p in plugin_list:
				url = p.url
				url = url.replace('{USERNAME}', '')
				url = url.replace('{PASSWORD}', '')
				url = url.replace(':@', '')
				urls.add(url)
			urls = list(urls)

			out += L_EMPH + 'Access to following URLs is required:' + L_RESET
			urls.sort()
			for u in urls:
				out += '\n{}'.format(u)
			out += '\n\n'

		out += L_EMPH + 'Following Python packages will be {}:'.format('installed' if is_install else 'downloaded') + L_RESET
		plugins.sort()
		for p in plugins:
			out += p

		return out

	terminal_menu = TerminalMenu(
		modules,
		multi_select					= True,
		show_multi_select_hint			= True,
		multi_select_empty_ok			= True,
		multi_select_select_on_accept	= False,
		preselected_entries				= already_installed,
		title							= "Please select the modules that you want to {}:".format('install' if is_install else 'download'),
		preview_title					= "",
		preview_command					= preview,
		preview_size					= 0.5
	)

	choices = terminal_menu.show()

	if choices:
		for i in choices:
			mods.append(modules[i])

		# get final list of plugins to install ---------------------------------
		plugins = get_plugin_list(mods)

		# uninstall unwanted packages ------------------------------------------
		if is_install:
			to_remove = []
			for k in get_plugins().keys():
				def run():
					for p in plugins:
						if p.name == k:
							return
					to_remove.append(k)
				run()
			uninstall(to_remove)

		# install/download plugins ---------------------------------------------
		install(plugins, is_install)

#-------------------------------------------------------------------------------
def list_installed():
	initialize()
	if len(get_plugins()) == 0:
		print('SOL is not installed on this machine')
		return
		
	print(L_EMPH + 'Installed SOL Modules:' + L_RESET)
	for m in get_modules():
		print('- {}'.format(m))

	print('')
	print(L_EMPH + 'Installed SOL Plugins:' + L_RESET)
	for p, v in get_plugins().items():
		print('- {} v{}'.format(p, v))
	print('')

#-------------------------------------------------------------------------------
def check_license(is_install):
	global s_credentials, s_user_access

	# Helper Functions ---------------------------------------------------------		
	def less(text, step = 40):
		assert isinstance(text, list)
		cnt = len(text)
		for i in range(0, (cnt + step - 1) // step):
			start	= i * step
			end		= min(cnt, start + step)
			for n in range(start, end):
				print(text[n])

			if end < cnt:
				print('')
				input('Press <Enter> for more')
		print('')

	def convert(markdown):
		out	= []
		for l in markdown.split('\n'):
			l = l.replace('<br/>', ' ')
			l = re.sub(r'<[^>]+>', '', l) # removes HTML tags

			def find():
				i = 0
				for i in range(0, len(l)):
					if l[i] != '#' and l[i] != ' ' and l[i] != '*':
						return i
				return i

			r = l[:find()]
			if		r == '# ':	l = "\033[47m\033[1;30m"	+ l[2:] + "\033[0m"
			elif	r == '## ':	l = "\033[1;37m\033[4;37m"	+ l[3:] + "\033[0m"
			elif	r == '**':	l = "\033[1;37m"			+ l[2:-2] + "\033[0m"

			out.append(l)
		return out

	# Local installs can't check license ---------------------------------------
	if s_local_repo:
		plugins = []
		for file in os.listdir():
			match = re.search(r'{}_sol_[a-z0-9\_]+'.format(s_prefix), file)
			if match:
				plugins.append(match[0].replace('_', '-'))
		s_user_access = set(lookup_modules(plugins))
		s_user_access.remove('core')
		if len(s_user_access) == 0:
			raise Exception('Unable to find any SOL packages within this folder')
		return

	# Fetch License Agreement for this user ------------------------------------
	while s_credentials is None:
		print('Please authenticate using your SOL login for verifying your license status:')
		print('User for sol.neclab.eu: ', end='')
		username = input()
		password = getpass.getpass()
		s_credentials = (username, password)
		print()

		# Check if we can login ------------------------------------------------
		r = requests.get('https://sol.neclab.eu/license/', auth=s_credentials, verify=not s_trust)
		if r.status_code != 200:
			print(L_ERROR, 'Login failed!', L_RESET)
			s_credentials = None
			continue

		# Check which packages can be installed --------------------------------
		s_user_access = set()
		def add_access(urls):
			for url in urls:
				r = requests.get(url, auth=s_credentials, verify=not s_trust)
				if r.status_code != 200:
					return False
			return True

		for mod, urls in s_access.items():
			if add_access(urls):
				s_user_access.add(mod)

	# Check if license is installed and with correct version -------------------
	if is_install:
		v = get_plugins().get('{}-sol-license'.format(s_prefix))
		if v == s_license_version:
			return

		# If wrong version is installed, uninstall it before continuing --------
		if v:
			uninstall('{}-sol-license'.format(s_prefix))

	# Process license request --------------------------------------------------	
	r = requests.get('https://sol.neclab.eu/license/index.php/fetch-license', auth=s_credentials, verify=not s_trust)
	r.raise_for_status()
	try:
		msg = r.json()
	except Exception as e:
		raise Exception(r.content.decode('utf-8'))

	license_text			= msg.get('license')
	license_authorization	= msg.get('license_authorization')
	license_acceptance		= msg.get('license_acceptance')
	license_error			= msg.get('license_error')

	if license_text is None or license_authorization is None or license_acceptance is None:
		if license_error:
			raise Exception(msg['license_error'])
		raise Exception('invalid msg received from server')

	# Show license text --------------------------------------------------------
	less(convert(license_text))

	options			= ['no, I am not', 'yes, I am']
	terminal_menu	= TerminalMenu(options, title=license_authorization)
	choice			= terminal_menu.show()
	if choice != 1:	raise Exception('License declined!')

	options			= ['decline license', 'accept license']
	terminal_menu	= TerminalMenu(options, title=license_acceptance)
	choice			= terminal_menu.show()
	if choice != 1:	raise Exception('License declined!')

#-------------------------------------------------------------------------------
def options():
	global s_local_repo, s_globally, s_trust

	selected = []
	if s_local_repo:	selected.append(0)
	if s_trust:			selected.append(1)

	options = ['install SOL from current folder', 'don\'t check SOL repo server certificates (not recommended)']
	if not is_virtualenv():
		options.append('install SOL globally')
		if s_globally:
			selected.append(2)

	terminal_menu = TerminalMenu(
		options,
		multi_select					= True,
		show_multi_select_hint			= True,
		multi_select_empty_ok			= True,
		multi_select_select_on_accept	= False,
		preselected_entries				= selected,
		title							= "SOL Installation Options:",
	)

	choices	= terminal_menu.show()

	if choices is None:
		choices = []
	
	s_local_repo	= 0 in choices
	s_trust			= 1 in choices
	s_globally		= 2 in choices

#-------------------------------------------------------------------------------
def upgrade(is_install):
	if is_install:
		to_remove	= []
		to_install	= []

		def requires_upgrade(p, v):
			for a in get_available().values():
				info = a.get(p)
				if info:
					if info.raw_version != v:
						to_remove.append(p)
						to_install.append(p)
					return
			to_remove.append(p) # rogue/obsolete plugins so we can removed it

		for p, v in get_plugins().items():
			requires_upgrade(p, v)

		if len(to_remove) or len(to_install):
			options			= ['decline upgrade', 'accept upgrade']
			terminal_menu	= TerminalMenu(options, title='SOL needs to upgrade some packages before you can continue:')
			choice			= terminal_menu.show()

			if choice != 1:
				raise Exception('Upgrade declined')

			if len(to_remove):
				uninstall(to_remove)

			to_install = lookup_modules(to_install)
			to_install.append('license') # license is ALWAYS needed
			if len(to_install):
				print('')
				print('Detected installed SOL modules: {}'.format(to_install))
				print('')
				install(get_plugin_list(to_install), True)

#-------------------------------------------------------------------------------
if __name__ == '__main__':
	print('{}## NEC-SOL Package Manager v{}{}'.format(L_EMPH, s_version, L_RESET))

	try:
		while True:
			print('')
			terminal_menu	= TerminalMenu(['install/modify modules', 'download modules', 'list installed modules', 'uninstall all modules', 'options', 'exit installer'], title='Please choose an action:')
			choice			= terminal_menu.show()
			print('')

			if		choice == 0:	select_modules(True)
			elif	choice == 1:	select_modules(False)
			elif	choice == 2:	list_installed()
			elif	choice == 3:	uninstall()
			elif	choice == 4:	options()
			else:					break
	except Exception as e:
		print(str(e))
		for line in traceback.format_tb(e.__traceback__):
			print(line)
