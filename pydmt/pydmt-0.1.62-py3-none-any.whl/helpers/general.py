import datetime
import os
import socket

current_folder = os.path.basename(os.getcwd())
current_year = datetime.datetime.now().year
homedir = os.path.expanduser("~")
hostname = socket.gethostname()
