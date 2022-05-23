import subprocess

def execute(pine_path):
	subprocess.check_output(['npm', 'install', 'socket.io'])