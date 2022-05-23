import subprocess as sp
import threading
from os.path import exists
from typing import Optional, Union

from flask import Flask
from werkzeug.serving import make_server


def get_bin_dir() -> str:
    return "/".join(__file__.split('/')[:-1]) + '/bin/'


def get_factory_dll_path() -> str:
    return get_bin_dir() + 'content/Finbourne.Honeycomb.Host.dll'


class _ServerThread(threading.Thread):
    """Class that represents a thread managing a flask app. Allows for the starting and stopping of the webserver
    in the background.

    """

    def __init__(self, app: Flask, host: str, port: int):
        """Constructor for the _ServerThread class.

        Args:
            app (Flask): the flask app to manage.
            host (str): the host to run at.
            port (int): the port to use.
        """
        threading.Thread.__init__(self)
        self.server = make_server(host, port, app)
        self.context = app.app_context()
        self.context.push()

    def run(self) -> None:
        """Start the provider webserver.

        """
        print("Starting provider server")
        self.server.serve_forever()

    def join(self, timeout: Union[float, None] = None) -> None:
        """Shut down the provider webserver.

        """
        print("Stopping provider server")
        self.server.shutdown()
        super().join(timeout)


class _FactoryThread(threading.Thread):
    """Class that represents a thread managing the Luminesce python provider factory process. Allows for the starting
    and stopping of the factory process in the background.

    """

    def __init__(self, host: str, port: int, user_id: Optional[str] = None, domain: Optional[str] = 'fbn-prd'):
        """Constructor for the _FactoryThread class.

        Args:
            host (str): the host that the provider webserver is running at.
            port (int): the port that the provider webserver is listening at.
            user_id (Optional[str]): optional user ID to run for.
            domain (Optional[str]): environment to run in (defaults to fbn-prd).
        """
        threading.Thread.__init__(self)

        self.factory_dll_path = get_factory_dll_path()

        self.cmd = f'dotnet {self.factory_dll_path} --quiet --authClientDomain={domain} '
        if user_id is not None:
            self.cmd += f'--localRoutingUserId "{user_id}" '
        self.cmd += f'--config "PythonProvider:BaseUrl=>http://{host}:{port}/api/v1/"'
        self.factory_process = None

    def run(self) -> None:
        """Start the factory process.

        """
        # Check factory dll and pem files exist. If not, throw error with instructions.
        if not exists(self.factory_dll_path):
            raise ValueError(
                f"Luminesce python provider factory dll was not found at {self.factory_dll_path}. "
                "You may need to run the setup helper via lumipy.setup_python_providers(<path to certs>).\n"
            )

        client_cert = get_bin_dir() + '/content/client_cert.pem'
        if not exists(client_cert):
            raise ValueError(f'Client Cert not found at {client_cert}')

        client_key = get_bin_dir() + '/content/client_key.pem'
        if not exists(client_key):
            raise ValueError(f'Client Cert not found at {client_key}')

        print("Starting local provider factory")
        print(self.cmd)
        self.factory_process = sp.Popen(
            args=self.cmd.split()
        )

    def join(self, timeout: Union[float, None] = None) -> None:
        """Terminate the factory process.

        """
        if self.factory_process is not None:
            print("Stopping local provider factory")
            self.factory_process.terminate()
            super().join(timeout)
        else:
            # No factory is running: no-op
            super().join(timeout)
