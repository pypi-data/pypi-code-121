import argparse
import enum
import string
from typing import Optional, List

import requests_unixsocket
import yaml
import zebr0

KEY_DEFAULT = "lxd-stack"
URL_DEFAULT = "http+unix://%2Fvar%2Fsnap%2Flxd%2Fcommon%2Flxd%2Funix.socket"


class ResourceType(enum.Enum):
    """
    Enumerates the various LXD resource types managed by the library.
    """

    STORAGE_POOLS = "storage-pools", "/1.0/storage-pools"
    VOLUMES = "volumes", "/1.0/storage-pools/${parent}/volumes/custom"
    NETWORKS = "networks", "/1.0/networks"
    PROFILES = "profiles", "/1.0/profiles"
    INSTANCES = "instances", "/1.0/instances"

    def name(self) -> str:
        return self.value[0]

    def path(self, config) -> str:
        """
        :param config: the resource's configuration
        :return: the corresponding path relative to the LXD API base URL
        """
        return string.Template(self.value[1]).substitute(config)


class Client:
    """
    A simple wrapper around the LXD REST API to manage resources either directly or via "stacks".

    This Client connects to the LXD API through the Unix socket (for now).
    Apart from how asynchronous operations are handled, it's mainly a convenient, idempotent passthrough.
    Therefore, the official documentation is where you'll find all the configuration details you'll need to create LXD resources:

    * storage-pools and volumes: https://linuxcontainers.org/lxd/docs/master/api/#/storage and https://linuxcontainers.org/lxd/docs/master/storage
    * networks: https://linuxcontainers.org/lxd/docs/master/api/#/networks and https://linuxcontainers.org/lxd/docs/master/networks
    * profiles: https://linuxcontainers.org/lxd/docs/master/api/#/profiles and https://linuxcontainers.org/lxd/docs/master/profiles
    * instances: https://linuxcontainers.org/lxd/docs/master/api/#/instances and https://linuxcontainers.org/lxd/docs/master/instances

    A "stack" is very a convenient way to manage a group of resources linked together.
    Heavily inspired by the LXD "preseed" format (see https://linuxcontainers.org/lxd/docs/master/preseed), the structure is almost identical, except:

    * "storage_pools" has been renamed "storage-pools" to match the API
    * the root "config" element is ignored (use a real preseed file if you want to configure LXD that way)
    * instances and volumes are managed through new root elements, "instances" and "volumes"

    A typical stack example can be found in tests/test_cli.py.
    Check the various functions to see what you can do with stacks and resources.

    :param url: URL of the LXD API (scheme is "http+unix", socket path is percent-encoded into the host field), defaults to "http+unix://%2Fvar%2Fsnap%2Flxd%2Fcommon%2Flxd%2Funix.socket"
    """

    def __init__(self, url: str = URL_DEFAULT):
        self.url = url
        self.session = requests_unixsocket.Session()

        # this "hook" will be executed after each request (see http://docs.python-requests.org/en/master/user/advanced/#event-hooks)
        def hook(response, **_):
            response_json = response.json()

            if not response.ok:
                raise Exception(response_json.get("error"))

            # some lxd operations are asynchronous, we have to wait for them to finish before continuing
            # see https://linuxcontainers.org/lxd/docs/master/rest-api/#background-operation
            if response_json.get("type") == "async":
                operation = self.session.get(self.url + response_json.get("operation") + "/wait").json().get("metadata")
                if operation.get("status_code") != 200:
                    raise Exception(operation.get("err"))

        self.session.hooks["response"].append(hook)

    def exists(self, config: dict, resource_type: ResourceType) -> bool:
        """
        :param config: the resource's configuration
        :param resource_type: the resource's type
        :return: whether the resource exists or not
        """

        type_path = resource_type.path(config)
        resource_path = type_path + "/" + config.get("name")

        print("checking", resource_path)
        return any(path == resource_path for path in self.session.get(self.url + type_path).json().get("metadata"))

    def create(self, config: dict, resource_type: ResourceType) -> None:
        """
        Creates a resource if it doesn't exist.
        The required configuration depends on the resource's type (see zebr0_lxd.Client).

        :param config: the resource's desired configuration
        :param resource_type: the resource's type
        """

        type_path = resource_type.path(config)
        resource_path = type_path + "/" + config.get("name")

        if not self.exists(config, resource_type):
            print("creating", resource_path)
            self.session.post(self.url + type_path, json=config)

    def delete(self, config: dict, resource_type: ResourceType) -> None:
        """
        Deletes a resource if it exists.

        :param config: the resource's configuration
        :param resource_type: the resource's type
        """

        resource_path = resource_type.path(config) + "/" + config.get("name")

        if self.exists(config, resource_type):
            print(f"deleting", resource_path)
            self.session.delete(self.url + resource_path)

    def is_running(self, config: dict, resource_type: ResourceType = ResourceType.INSTANCES) -> bool:
        """
        :param config: the resource's configuration
        :param resource_type: the resource's type, defaults to INSTANCES
        :return: whether the resource is running or not
        """

        resource_path = resource_type.path(config) + "/" + config.get("name")

        print("checking", resource_path)
        return self.session.get(self.url + resource_path).json().get("metadata").get("status") == "Running"

    def start(self, config: dict, resource_type: ResourceType) -> None:
        """
        Starts a resource if it's not running.

        :param config: the resource's configuration
        :param resource_type: the resource's type
        """

        resource_path = resource_type.path(config) + "/" + config.get("name")

        if not self.is_running(config, resource_type):
            print("starting", resource_path)
            self.session.put(self.url + resource_path + "/state", json={"action": "start"})

    def stop(self, config: dict, resource_type: ResourceType) -> None:
        """
        Stops a resource if it's running.

        :param config: the resource's configuration
        :param resource_type: the resource's type
        """

        resource_path = resource_type.path(config) + "/" + config.get("name")

        if self.is_running(config, resource_type):
            print("stopping", resource_path)
            self.session.put(self.url + resource_path + "/state", json={"action": "stop"})

    def create_stack(self, stack: dict) -> None:
        """
        Creates the resources in the given stack if they don't exist.
        The required configurations depend on the resource's type (see zebr0_lxd.Client).

        :param stack: the stack as a dictionary
        """

        for resource_type in ResourceType:
            for config in stack.get(resource_type.name()) or []:
                self.create(config, resource_type)

    def delete_stack(self, stack: dict) -> None:
        """
        Deletes the resources in the given stack if they exist.

        :param stack: the stack as a dictionary
        """

        for resource_type in reversed(ResourceType):
            for config in stack.get(resource_type.name()) or []:
                self.delete(config, resource_type)

    def start_stack(self, stack: dict) -> None:
        """
        Starts the resources in the given stack if they're not running.

        :param stack: the stack as a dictionary
        """

        for resource_type in [ResourceType.INSTANCES]:
            for config in stack.get(resource_type.name()) or []:
                self.start(config, resource_type)

    def stop_stack(self, stack: dict) -> None:
        """
        Stops the resources in the given stack if they're running.

        :param stack: the stack as a dictionary
        """

        for resource_type in [ResourceType.INSTANCES]:
            for config in stack.get(resource_type.name()) or []:
                self.stop(config, resource_type)


def main(args: Optional[List[str]] = None) -> None:
    """
    usage: zebr0-lxd [-h] [-u <url>] [-l [<level> [<level> ...]]] [-c <duration>] [-f <path>] [--lxd-url <url>] {create,delete,start,stop} [key]

    LXD provisioning based on zebr0 key-value system.
    Fetches a stack from the key-value server and manages it on LXD.

    positional arguments:
      {create,delete,start,stop}
                            operation to execute on the stack
      key                   the stack's key, defaults to 'lxd-stack'

    optional arguments:
      -h, --help            show this help message and exit
      -u <url>, --url <url>
                            URL of the key-value server, defaults to https://hub.zebr0.io
      -l [<level> [<level> ...]], --levels [<level> [<level> ...]]
                            levels of specialization (e.g. "mattermost production" for a <project>/<environment>/<key> structure), defaults to ""
      -c <duration>, --cache <duration>
                            in seconds, the duration of the cache of http responses, defaults to 300 seconds
      -f <path>, --configuration-file <path>
                            path to the configuration file, defaults to /etc/zebr0.conf for a system-wide configuration
      --lxd-url <url>       URL of the LXD API (scheme is "http+unix", socket path is percent-encoded into the host field), defaults to "http+unix://%2Fvar%2Fsnap%2Flxd%2Fcommon%2Flxd%2Funix.socket"
    """

    argparser = zebr0.build_argument_parser(description="LXD provisioning based on zebr0 key-value system.\nFetches a stack from the key-value server and manages it on LXD.", formatter_class=argparse.RawDescriptionHelpFormatter)
    argparser.add_argument("command", choices=["create", "delete", "start", "stop"], help="operation to execute on the stack")
    argparser.add_argument("key", nargs="?", default=KEY_DEFAULT, help="the stack's key, defaults to 'lxd-stack'")
    argparser.add_argument("--lxd-url", default=URL_DEFAULT, help='URL of the LXD API (scheme is "http+unix", socket path is percent-encoded into the host field), defaults to "http+unix://%%2Fvar%%2Fsnap%%2Flxd%%2Fcommon%%2Flxd%%2Funix.socket"', metavar="<url>")
    args = argparser.parse_args(args)

    value = zebr0.Client(args.url, args.levels, args.cache, args.configuration_file).get(args.key)
    if not value:
        print(f"key '{args.key}' not found on server {args.url}")
        exit(1)

    stack = yaml.load(value, Loader=yaml.BaseLoader)
    if not isinstance(stack, dict):
        print(f"key '{args.key}' on server {args.url} is not a proper yaml or json dictionary")
        exit(1)

    # creates a Client and calls the function corresponding to the given command
    getattr(Client(args.lxd_url), args.command + "_stack")(stack)
