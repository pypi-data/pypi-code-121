from xpipe.server.run_server import get_app, prepare_bokeh_dependencies
import os
from .models import init_db
from mongoengine import connect

artifacts_dir = os.environ.get("ARTIFACTS_DIR", None)
host = os.environ.get("HOST", None)
port = os.environ.get("PORT", None)
db_host = os.environ.get("DB_HOST", None)
db_port = os.environ.get("DB_PORT", None)

connect("xpipe", host=db_host, port=int(db_port)) # Connect to mongodb
init_db() # Initialize models
prepare_bokeh_dependencies() # Copy bokeh js dependancies into ./frontend/public

print("""
     ██╗  ██╗██████╗ ██╗██████╗ ███████╗
     ╚██╗██╔╝██╔══██╗██║██╔══██╗██╔════╝
      ╚███╔╝ ██████╔╝██║██████╔╝█████╗  
      ██╔██╗ ██╔═══╝ ██║██╔═══╝ ██╔══╝  
     ██╔╝ ██╗██║     ██║██║     ███████╗
     ╚═╝  ╚═╝╚═╝     ╚═╝╚═╝     ╚══════╝""")

app = get_app(artifacts_dir) # Create the flask app