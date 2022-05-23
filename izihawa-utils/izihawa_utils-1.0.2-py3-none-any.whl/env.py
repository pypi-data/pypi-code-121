import os
import platform
import socket

hostname = socket.gethostname()
node_name = os.environ.get('NODE_NAME')
type = os.environ.get('ENV_TYPE', 'development')
name = os.environ.get('ENV_TYPE', 'development')
platform = platform.system().lower()
