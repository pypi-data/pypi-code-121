'''

    __init__.py
 
    Copyright (C) 2022 by RStudio, PBC
 
'''

import json
from pathlib import Path

from .proxiedServersProvider import ProxiedServersProvider
from .handlers import ProxiedServersHandler, setup_handlers
from ._version import __version__
 

HERE = Path(__file__).parent.resolve()

with (HERE / "labextension" / "package.json").open() as fid:
    data = json.load(fid)


def _jupyter_labextension_paths():
    return [{"src": "labextension", "dest": data["name"]}]

def _jupyter_server_extension_points():
    return [{"module": "jupyterlab_rsw"}]

def _load_jupyter_server_extension(server_app):
    url_path = "jupyterlab-rsw"
    setup_handlers(server_app.web_app, url_path)
    server_app.log.info(
       f"Registered jupyterlab_rsw at URL path /{url_path}"
    )

load_jupyter_server_extension = _load_jupyter_server_extension
provider = ProxiedServersProvider()
