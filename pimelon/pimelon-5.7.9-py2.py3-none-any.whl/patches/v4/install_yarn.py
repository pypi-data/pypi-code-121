import os
from pine.utils import exec_cmd

def execute(pine_path):
	exec_cmd('npm install yarn', os.path.join(pine_path, 'apps/melon'))
