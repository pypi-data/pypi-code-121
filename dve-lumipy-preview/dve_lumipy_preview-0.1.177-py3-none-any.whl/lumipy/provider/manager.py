import time
import uuid
from typing import NoReturn, Optional, List

import flask

from lumipy.common.string_utils import prettify_tree, connector, indent_str
from .base_provider import BaseProvider
from .thread import _ServerThread, _FactoryThread


class ProviderManager:
    """Manages config and operation of a local flask webserver that serves a provider set and the provider factory.
    The server creates a set of api endpoints for each local provider instance plus some at the server level.
    The factory will start luminesce providers that connect to the grid and hit the webserver endpoints.
    """

    def __init__(
            self,
            providers: List[BaseProvider],
            host: Optional[str] = 'localhost',
            port: Optional[int] = 5001,
            dry_run: Optional[bool] = False,
            user_id: Optional[str] = None,
            domain: Optional[str] = 'fbn-prd'
    ):
        """Constructor of the ProviderServer class.

        Args:
            providers (List[BaseProvider]): local provider instances (classes that inherit from BaseProvider) that
            the server should manage.
            host (Optional[str]): optional server host path. Defaults to localhost.
            port (Optional[int]): optional port for the server to use. Defaults to 5000.
            dry_run (Optional[bool]): whether to only run the web server and not start the local provider factory.
            user_id (Optional[str]): optional user id to run the providers for.
        """
        if len(providers) == 0:
            raise ValueError(
                "Nothing to run! No providers have been supplied to the provider server constructor"
            )

        self.name = str(uuid.uuid4())
        self.host = host
        self.port = port
        self.dry_run = dry_run

        self.provider_roots = []
        self.base_url = f'http://{self.host}:{self.port}'
        self.app = flask.Flask(self.name)

        self.providers = providers
        for p in providers:

            if not isinstance(p, BaseProvider):
                raise TypeError(
                    f"*providers arg was not an inheritor of {BaseProvider.__name__} "
                    f"but was {type(p).__name__}."
                )

            if p.path_name == 'index':
                raise ValueError("Can't have a provider called 'index'.")

            if p.name in [pr["Name"] for pr in self.provider_roots]:
                raise ValueError(f"Can't add a provider to the server under a name that's in use: {p.name}.")

            self.app.register_blueprint(p.blueprint())
            self.provider_roots.append({
                "Name": p.name,
                "ApiPath": f'{self.base_url}/api/v1/{p.path_name}/',
                "Type": type(p).__name__
            })

        @self.app.route('/api/v1/index/', methods=['GET'])
        def index():
            return flask.jsonify(self.provider_roots)

        @self.app.route('/', methods=['GET'])
        def home():
            content = '<h1>Luminesce Python Server</h1>'
            content += f'<h2>Running {len(self.provider_roots)} Providers at {self.base_url}</h2>'
            content += f'<p><a href="{self.base_url}/api/v1/index/">Index</a></p>'
            for pr in self.provider_roots:
                content += f'<h3>{pr["Name"]}</h3>'
                content += f'<p><a href="{pr["ApiPath"]}metadata">Metadata link</a></p>'
            return content

        self.server_thread = _ServerThread(self.app, self.host, self.port)
        self.factory_thread = _FactoryThread(self.host, self.port, user_id, domain)

    def start(self) -> None:
        """Start the local python provider web server and spin up local luminesce providers.

        """
        maxlen_name = max(len(name['Name']) for name in self.provider_roots)
        maxlen_url = max(len(name['ApiPath']) for name in self.provider_roots)

        def prov_str(pr):
            return f"{connector}{pr['Name'].ljust(maxlen_name)} {pr['ApiPath'].ljust(maxlen_url)} {pr['Type']}"

        provider_list = '\n'.join(map(prov_str, self.provider_roots))
        provider_list = prettify_tree(provider_list)
        print(f"Running {type(self).__name__} {self.name} at http://{self.host}:{self.port}")
        self.server_thread.start()
        print(f"Hosted python providers:\n{indent_str(provider_list, 2)}")

        if not self.dry_run:
            print('Registering providers with the Luminesce grid...')
            self.factory_thread.start()
        else:
            print('[DRY RUN] provider factory not started. No providers will be registered with the Luminesce grid.')

    def stop(self) -> None:
        """Stop the local python provider web server and the factory as well as dispose of all the running providers.

        """
        self.server_thread.join()
        for provider in self.providers:
            print(f"  shutting down {provider.name}")
            provider.shutdown()

        if not self.dry_run:
            self.factory_thread.join()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def run(self) -> NoReturn:
        """Run the manager instance in the foreground. The manager can be shut down with a KeyboardInterupt (ctrl+C).

        """

        self.start()
        while True:
            try:
                time.sleep(5)
            except KeyboardInterrupt:
                print("Received keyboard interrupt - shutting down...")
                self.stop()
                return
            except Exception as e:
                print("Unexpected error occurred - attempting to shut down before re-throwing...")
                self.stop()
                raise e
