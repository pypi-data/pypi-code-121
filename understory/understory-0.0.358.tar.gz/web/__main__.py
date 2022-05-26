"""Command line tools for the web."""

import inspect
import json
import logging
import pathlib
import webbrowser

import clicks
from rich.pretty import pprint

import web
import web.host
from web.host import console, providers

__all__ = ["main"]


main = clicks.application("web", web.__doc__)


@main.register()
class MF:
    """Get a resource and parse it for Microformats."""

    def setup(self, add_arg):
        add_arg("uri", help="address of the resource")

    def run(self, stdin, log):
        pprint(web.get(self.uri).mf2json)
        return 0


@main.register()
class Apps:
    """Show installed web apps."""

    def setup(self, add_arg):
        pass

    def run(self, stdin, log):
        for pkg, apps in web.get_apps().items():
            for name, _, ns, obj in apps:
                print(f"{name} {ns}:{obj[0]}")
        return 0


@main.register()
class Dev:
    """Develop a web app locally."""

    def setup(self, add_arg):
        add_arg("app", help="name of web application")
        add_arg("--port", help="port to serve on")
        add_arg("--socket", help="file socket to serve on")
        add_arg("--watch", default=".", help="directory to watch for changes")

    def run(self, stdin, log):
        import asyncio

        if self.port:
            asyncio.run(web.serve(self.app, port=self.port, watch_dir=self.watch))
        elif self.socket:
            asyncio.run(web.serve(self.app, socket=self.socket, watch_dir=self.watch))
        else:
            print("must provide a port or a socket")
            return 1
        return 0

        # for pkg, apps in web.get_apps().items():
        #     for name, _, ns, obj in apps:
        #         if self.app == name:
        #             web.serve(ns, obj)
        #             return 0
        # return 1


def get_providers(provider_type):
    return [
        name.lower()
        for name, obj in inspect.getmembers(providers, inspect.isclass)
        if issubclass(obj, provider_type) and obj is not provider_type
    ]


@main.register()
class Config:
    """Config your environments."""

    def setup(self, add_arg):
        add_arg("token", help="API access token")
        add_arg(
            "--host",
            choices=get_providers(providers.Host),
            help="machine host",
        )
        add_arg(
            "--registrar",
            choices=get_providers(providers.Registrar),
            help="domain registrars",
        )

    def run(self, stdin, log):
        if self.host:
            update_config(host=self.host, host_token=self.token)
        elif self.registrar:
            update_config(registrar=self.registrar, registrar_token=self.token)
        return 0


@main.register()
class Publish:
    """Publish a web app."""

    def run(self, stdin, log):
        logging.basicConfig(
            level=logging.DEBUG, filename="debug.log", filemode="w", force=True
        )
        config = get_config()

        if config["host"] == "digitalocean":
            host = providers.DigitalOcean(config["host_token"])
        elif config["host"] == "linode":
            host = providers.Linode(config["host_token"])
        else:
            console.print(f"Host {config['host']} not available.")
            return 1

        if config["registrar"] == "dynadot":
            registrar = providers.Dynadot(config["registrar_token"])
        elif config["registrar"] == "linode":
            registrar = providers.Linode(config["registrar_token"])
        else:
            console.print(f"Registrar {config['registrar']} not available.")
            return 1

        machines = config.get("machines", [])
        if len(machines) == 0:
            console.print("No machines found")
            versions = web.host.Understory.versions
            with console.status(
                "[bold green]Creating new machine ([magenta]13 min[/magenta])"
            ):
                console.print(
                    f"Spawning virtual machine at {host.__class__.__name__} "
                    "([magenta]1 min[/magenta])"
                )
                machine = web.host.spawn_machine("understory", host)
                console.print("Setting up base system ([magenta]4 min[/magenta])")
                machine.setup_machine()
                console.print(
                    f"Installing Nginx {versions['nginx']} ([magenta]2 min[/magenta])"
                )
                machine.setup_nginx()
                webbrowser.open(f"http://{machine.address}")
                console.print(
                    f"Installing Python {versions['python']} ([magenta]6 min[/magenta])"
                )
                machine.setup_python()
                machines.append(machine.address)
                update_config(machines=machines)
        machine = web.host.Understory(machines[0], "root", "gaea_key")
        console.rule(f"[green]Using {machine.address}")
        with console.status("[bold blue]Installing/upgrading sites"):
            machine.install_project(registrar)
        return 0


@main.register()
class Host:
    """Manage your host."""

    def run(self, stdin, log):
        config = get_config()
        if config["host"] == "digitalocean":
            host = providers.DigitalOcean(config["host_token"])
        else:
            console.print(f"Host {config['host']} not available.")
            return 1
        for machine in host.machines:
            console.rule(f"[bold red]{machine['name']}")
            pprint(machine)
        return 0


@main.register()
class Registrar:
    """Manage your registrar."""

    def run(self, stdin, log):
        config = get_config()
        if config["registrar"] == "dynadot":
            registrar = providers.Dynadot(config["registrar_token"])
        else:
            console.print(f"Registrar {config['registrar']} not available.")
            return 1
        for domain in registrar.domains:
            print(domain)
        return 0


config_file = pathlib.Path("~/.understory").expanduser()


def get_config():
    """Get configuration."""
    try:
        with config_file.open() as fp:
            config = json.load(fp)
    except FileNotFoundError:
        config = {}
    return config


def update_config(**items):
    """Update configuration."""
    config = get_config()
    config.update(**items)
    with config_file.open("w") as fp:
        json.dump(config, fp, indent=2, sort_keys=True)
        fp.write("\n")
    return get_config()
