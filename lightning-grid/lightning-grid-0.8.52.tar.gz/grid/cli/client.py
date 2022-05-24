# Copyright 2020 Grid AI Inc.
import asyncio
import csv
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlsplit

import click
import requests
import websockets
import yaspin
from gql import Client, gql
from gql.transport.exceptions import TransportProtocolError, TransportQueryError
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.websockets import WebsocketsTransport

from grid.cli.commands import CredentialsMixin, DependencyMixin, WorkflowChecksMixin
from grid.cli.observables import Experiment, InteractiveNode, Run
from grid.cli.types import ObservableType
from grid.metadata import __version__
from grid.sdk import env

_graphql_client: Client = None

CREDIT_CARD_ERROR_MESSAGE = "A credit card on file is needed in order to use a GPU"


@dataclass
class StaticCredentials:
    user_id: str
    api_key: str


def credentials_from_env(credential_path: Optional[str] = None) -> StaticCredentials:
    """Instantiates the GraphQL local client using local credentials."""
    # if user has environment variables, use that
    env.USER_ID = os.getenv('GRID_USER_ID')
    env.API_KEY = os.getenv('GRID_API_KEY')
    if env.USER_ID and env.API_KEY:
        return StaticCredentials(user_id=env.USER_ID, api_key=env.API_KEY)

    # otherwise overwrite look for credentials stored locally as a file
    credential_path = credential_path or os.getenv(
        'GRID_CREDENTIAL_PATH',
        Path.home() / ".grid" / "credentials.json",
    )

    P = Path(credential_path)
    if not P.exists():
        raise click.ClickException('No credentials available. Did you login?')

    with P.open() as f:
        credentials = json.load(f)

    return StaticCredentials(
        user_id=credentials['UserID'],
        api_key=credentials['APIKey'],
    )


class Grid(CredentialsMixin, WorkflowChecksMixin, DependencyMixin):
    """
    Interface to the Grid API.

    Attributes
    ----------
    url: str
        Grid URL
    request_timeout: int
        Number of seconds to timeout a request by default.
    client: Client
        gql client object
    grid_credentials_path: str
        Path to the Grid credentials
    default_headers: Dict[str, str]
        Header used in the request made to Grid.
    acceptable_lines_to_print: int
        Total number of acceptable lines to print in
        stdout.
    request_cooldown_duration: float
        Number of seconds to wait between continuous
        requests.

    Parameters
    ----------
    local_credentials: bool, default True
        If the client should be initialized with
        credentials from a local file or not.
    """
    url: str = env.GRID_URL
    graphql_url: str = env.GRID_URL + '/graphql'

    #  TODO: Figure out a better timeout based on query type.
    request_timeout: int = 60
    default_headers: Dict[str, str] = {'Content-type': 'application/json', 'User-Agent': f'grid-api-{__version__}'}

    grid_settings_path: str = '.grid/settings.json'
    grid_credentials_path: str = '.grid/credentials.json'

    client: Client
    transport: RequestsHTTPTransport

    available_observables: Dict[ObservableType, Callable] = {
        ObservableType.EXPERIMENT: Experiment,
        ObservableType.RUN: Run,
        ObservableType.INTERACTIVE: InteractiveNode
    }

    acceptable_lines_to_print: int = 50
    request_cooldown_duration: int = 0.1
    credentials: StaticCredentials

    def __init__(
        self,
        credential_path: Optional[str] = None,
        load_local_credentials: bool = True,
        set_context_if_not_exists: bool = True
    ):
        self.headers = self.default_headers.copy()

        #  By default, we instantiate the client with a local
        #  set of credentials.
        if load_local_credentials or credential_path:
            self._set_local_credentials(credential_path)

            #  The client will be created with a set of credentials.
            #  If we change these credentials in the context of a
            #  call, for instance "login()" then we have to
            #  re-instantiate these credentials.
            self._init_client()
        super().__init__()

    def _set_local_credentials(self, credentials_path: Optional[str] = None):
        if credentials_path:
            self.credentials = credentials_from_env(credentials_path)
        else:
            self.credentials = credentials_from_env()
        self.__set_authentication_headers(user_id=self.credentials.user_id, key=self.credentials.api_key)

    def __set_authentication_headers(self, user_id: str, key: str) -> None:
        """Sets credentials header for a client."""
        self.user_id = user_id
        self.api_key = key
        self.headers['X-Grid-User'] = user_id
        self.headers['X-Grid-Key'] = key

    def _init_client(self, websocket: bool = False) -> None:
        """
        Initializes GraphQL client. This fetches the latest
        schema from Grid.
        """
        # Check version compatibility on client initialization.
        # TODO re-enable when versioning is fixed
        # self._check_version_compatibility()

        # Print non-default
        if self.url != env.GRID_URL:
            print(f"Grid URL: {self.url}")

        if websocket:
            _url = self.url.replace('http://', 'ws://')
            _url = _url.replace('https://', 'wss://')
            _url = _url + '/subscriptions'
            self.transport = WebsocketsTransport(url=_url, init_payload=self.headers)
        else:
            self.transport = RequestsHTTPTransport(
                url=self.graphql_url, use_json=True, headers=self.headers, timeout=self.request_timeout, retries=3
            )

        try:
            # Only create a client instance if there isn't one.
            # We also check if the instantiated transport is different.
            # We'll create a new client if it is.
            global _graphql_client
            if not isinstance(_graphql_client,
                              Client) or not isinstance(_graphql_client.transport, type(self.transport)):
                _graphql_client = Client(transport=self.transport, fetch_schema_from_transport=True)

                # Initiating the context to trigger the schema fetch. This was happening
                # on the class init previously (on the above Client(...)).
                # Probably a version upgrade screwed it up.
                # Not investigating further since we are changing this soon # TODO
                if isinstance(self.transport, RequestsHTTPTransport):
                    with _graphql_client:
                        pass

            self.client = _graphql_client

        except requests.exceptions.ConnectionError:
            raise click.ClickException(f'Grid is unreachable. Is Grid online at {env.GRID_URL} ?')
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise click.ClickException('Not authorized. Did you login?')
            if e.response.status_code == 500:
                raise click.ClickException('Grid is having issues. Please again later.')
            raise click.ClickException('We encountered an unknown error.')

        except requests.exceptions.Timeout:
            raise click.ClickException('Could not reach Grid. Are you online?')

        except TransportProtocolError:
            raise click.ClickException('Not authorized. Did you login?')

        except Exception as e:
            raise click.ClickException(f"{type(e).__name__}: {e}")

    def query(self, query: str, **kwargs) -> Dict:
        """Executes a GraphQL query against Grid's API."""
        # instantiate http transport
        if not hasattr(self, "transport") or not isinstance(self.transport, RequestsHTTPTransport):
            self._init_client(websocket=False)

        values = kwargs or {}
        try:
            result = self.client.execute(gql(query), variable_values=values)
        except TransportQueryError as e:
            raise click.ClickException(e.args)
        except Exception as e:
            raise click.ClickException(f"{type(e).__name__}: {e}")
        if 'error' in result:
            raise click.ClickException(json.dumps(result['error']))
        return result

    def subscribe(self, query: str, **kwargs) -> Dict:
        """Streams data from a GraphQL subscription"""
        # instantiate a websocket transport
        if not hasattr(self, "transport") or not isinstance(self.transport, WebsocketsTransport):
            self._init_client(websocket=True)

        values = kwargs or {}
        try:
            stream = self.client.subscribe(gql(query), variable_values=values)
            for element in stream:
                yield element

        # If connection is suddenly closed, indicate that a known
        # error happened.
        except websockets.exceptions.ConnectionClosedError:
            raise click.ClickException("Connection closed. No new messages available.")

        except websockets.exceptions.ConnectionClosedOK:
            raise click.ClickException("Connection closed. No new messages available.")

        except asyncio.exceptions.TimeoutError:
            raise click.ClickException("Timeout waiting for messages exceeded.")

        #  Raise any other errors that the backend may raise.
        except Exception as e:  # skipcq: PYL-W0703
            raise click.ClickException(str(e))

    # skipcq: PYL-W0102
    def status(
        self,
        kind: Optional[ObservableType] = None,
        identifiers: Optional[List[str]] = None,
        follow: Optional[bool] = False,
        export: Optional[str] = None,
        is_global: Optional[bool] = False
    ) -> None:
        """
        The status of an observable object in Grid. That can be a Cluster,
        a Run, or an Experiment.

        Parameters
        ----------
        kind: Optional[ObservableType], default None
            Kind of object that we should get the status from
        identifiers: List[str], default []
            Observable identifiers
        follow: bool, default False
            If we should generate a live table with results.
        export: Optional[str], default None
            What type of file results should be exported to, if any.
        is_global: Optional[bool], default False
            Returns status of resources from everyone in the team
        """
        #  We'll instantiate a websocket client when users
        #  want to follow an observable.
        if follow:
            self._init_client(websocket=True)

        kind = kind or ObservableType.RUN

        if kind == ObservableType.EXPERIMENT:
            observable = self.available_observables[kind](client=self.client, identifier=identifiers[0])

        elif kind == ObservableType.RUN:
            if not identifiers:
                observable = self.available_observables[ObservableType.RUN](client=self.client)
            else:
                #  For now, we only check the first observable.
                #  We should also check for others in the future.
                observable = self.available_observables[kind](client=self.client, identifier=identifiers[0])

        elif kind == ObservableType.INTERACTIVE:
            # Create observable.
            observable = self.available_observables[kind](client=self.client)

        elif kind == ObservableType.CLUSTER:
            raise click.BadArgumentUsage("It isn't yet possible to observe clusters.")

        else:
            raise click.BadArgumentUsage('No observable instance created.')

        if follow:
            result = observable.follow(is_global=is_global)
        else:
            result = observable.get(is_global=is_global)

        #  Save status results to a file, if the user has specified.
        if export:
            try:

                #  No need to continue if there are not results.
                if not result:
                    click.echo('\nNo run data to write to CSV file.\n')
                    return result

                #  The user may have requested a table of
                #  Runs or Experiments, use the key that is returned
                #  by the API.
                results_key = list(result.keys())[0]

                #  Initialize variables.
                path = None
                now = datetime.now()

                #  Basic format ISO 8601
                date_string = f'{now:%Y%m%dT%H%M%S}'

                if export == 'csv':
                    path = f'grid-status-{date_string}.csv'
                    with open(path, 'w') as csv_file:

                        #  We'll exclude any List or Dict from being
                        #  exported in the CSV. We do this to avoid
                        #  generating a CSV that contains JSON data.
                        #  There aren't too many negative sides to this
                        #  because the nested data isn't as relevant.
                        sample = result[results_key][0]
                        _sample = sample.copy()
                        for k, v in _sample.items():
                            if isinstance(v, (list, dict)):
                                del sample[k]  # skipcq: PTC-W0043

                        columns = sample.keys()
                        writer = csv.DictWriter(csv_file, fieldnames=columns)
                        writer.writeheader()
                        for data in result[results_key]:
                            writer.writerow({k: v for k, v in data.items() if k in columns})

                elif export == 'json':
                    path = f'grid_status-{date_string}.json'
                    with open(path, 'w') as json_file:
                        json_file.write(json.dumps(result[results_key]))

                if path:
                    click.echo(f'\nExported status to file: {path}\n')

            #  Catch possible errors when trying to create file
            #  in file system.
            except (IOError, TypeError) as e:
                if env.DEBUG:
                    click.echo(e)

                raise click.FileError('Failed to save grid status to file\n')

        return result

    @staticmethod
    def get_experiment_id(experiment_name: str) -> str:
        """
        Get experiment ID from name.

        Parameters
        ----------
        experiment_name: str
            Experiment name

        Returns
        --------
        experiment_id: str
            Experiment ID
        """
        spinner = yaspin.yaspin(text="Getting experiment info...", color="yellow")
        try:
            # TODO refactor this when we continue the work on SDK
            from grid.cli.core import Experiment as ExperimentGridObject
            spinner.start()
            exp = ExperimentGridObject(experiment_name)
            spinner.ok("✔")
        except Exception as e:
            spinner.fail("✘")
            raise click.ClickException(
                f"Could not find experiment: {e}. "
                f"If you meant to fetch experiment owned by "
                f"another person, use the format <username>:<experiment-name>"
            )
        finally:
            spinner.stop()
        return exp.identifier

    def experiment_details(self, experiment_id: str) -> Dict[str, Any]:
        """
        Get experiment details.

        Parameters
        ----------
        experiment_id: str
            Experiment ID

        Returns
        --------
        details: Dict[str, Any]
            Experiment details
        """
        # If job is queued, notify the user that logs aren't available yet
        query = gql(
            """
        query (
            $experimentId: ID!
        ) {
            getExperimentDetails(experimentId: $experimentId) {
                experimentId
                run {
                  name
                }
                status
            }
        }
        """
        )
        params = {'experimentId': experiment_id}
        result = self.client.execute(query, variable_values=params)

        return result

    def add_ssh_public_key(self, key: str, name: str):
        return self.query(
            """
            mutation (
                $publicKey: String!
                $name: String!
            ) {
            addSSHPublicKey(name: $name, publicKey: $publicKey) {
                message
                success
                id
              }
            }
        """,
            publicKey=key,
            name=name
        )

    def list_public_ssh_keys(self, limit: int) -> List[Dict[str, str]]:
        result = self.query(
            """
            query (
                $limit: Int!,
            ) {
                getPublicSSHKeys(limit: $limit) {
                    id
                    publicKey,
                    name
              }
            }
        """,
            limit=limit,
        )
        return result['getPublicSSHKeys']

    def delete_ssh_public_key(self, key_id: str):
        self.query(
            """
            mutation (
                $id: ID!
            ) {
              deleteSSHPublicKey(id: $id) {
                message
                success
              }
            }
        """,
            id=key_id
        )

    def list_interactive_node_ssh_setting(self):
        return self.query(
            """
        query {
            getInteractiveNodes {
                name: interactiveNodeName
                ssh_url: sshUrl
                status
            }
        }
        """
        )['getInteractiveNodes']

    @staticmethod
    def _gen_ssh_config(
        interactive_nodes: List[Dict[str, Any]],
        curr_config: str,
        start_marker: str = "### grid.ai managed BEGIN do not edit manually###",
        end_marker: str = "### grid.ai managed END do not edit manually###",
    ):

        content = curr_config.splitlines()
        sol = []
        managed_part = [start_marker]
        for node in interactive_nodes:
            if node["status"] != "running":
                continue

            ssh_url = urlsplit(node['ssh_url'])
            managed_part.extend([
                f"Host {node['name']}",
                f"    User {ssh_url.username}",
                f"    Hostname {ssh_url.hostname}",
                f"    Port {ssh_url.port}",
                "    StrictHostKeyChecking accept-new",
                "    CheckHostIP no",
                "    ServerAliveInterval 15",
                "    ServerAliveCountMax 4",
                # Workarounds until https://linear.app/gridai/issue/GI-6940/switch-client-ssh-gateway-communication-to-use-ed25519-keys-over-rsa
                # is fixed
                "    HostKeyAlgorithms=+ssh-rsa",
                "    PubkeyAcceptedKeyTypes +ssh-rsa",
                "    PasswordAuthentication no",
            ])
        managed_part.append(end_marker)

        within_section = False
        added_managed_part = False
        for line in content:
            if line == start_marker:
                if added_managed_part:
                    raise ValueError("Found 2 start markers")
                if within_section:
                    raise ValueError("Found 2 start markers in row")
                within_section = True
            elif end_marker == line:
                if added_managed_part:
                    raise ValueError("Found 2+ start end")
                if not within_section:
                    raise ValueError("End marker before start marker")
                within_section = False
                sol.extend(managed_part)
                added_managed_part = True
            elif not within_section:
                sol.append(line)
        if within_section:
            raise ValueError("Found only start marker, no end one found")
        if not added_managed_part:
            sol.extend(managed_part)
        return '\n'.join(sol)

    def sync_ssh_config(self) -> List[str]:
        """
        sync local ssh config with grid's interactive nodes config

        Returns
        -------
        list of interactive nodes present
        """
        interactive_nodes = self.list_interactive_node_ssh_setting()

        ssh_config = Path(env.GRID_SSH_CONFIG)
        if not ssh_config.exists():
            ssh_config.write_text("")

        ssh_config.write_text(
            self._gen_ssh_config(
                interactive_nodes=interactive_nodes,
                curr_config=ssh_config.read_text(),
            )
        )

        return interactive_nodes
