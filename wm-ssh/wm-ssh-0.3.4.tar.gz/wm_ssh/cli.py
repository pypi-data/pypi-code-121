#!/usr/bin/env python3
import json
import logging
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
import requests

LOGGER = logging.getLogger("wm-ssh" if __name__ == "__main__" else __name__)
DEFAULT_CONFIG_PATH = Path("~/.config/wm-ssh/config.json").expanduser()
DEFAULT_CACHE_PATH = Path("~/.cache/wm-ssh").expanduser()
DEFAULT_CONFIG = {
    "netbox_config_path": "~/.config/netbox/config.json",
    "known_hosts_url": "https://config-master.wikimedia.org/known_hosts.ecdsa",
    "openstack_browser_url": "https://openstack-browser.toolforge.org/api/dsh/servers",
}
DEFAULT_NETBOX_CONFIG = {
    "netbox_url": "https://netbox.local/api",
    "api_token": "IMADUMMYTOKEN",
}


@dataclass
class CacheFile:
    path: Path

    def __post_init__(self):
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def search_host(self, partial_host: str) -> Optional[str]:
        if self.path.exists():
            all_hosts = self.path.read_text().splitlines()
            for maybe_host in all_hosts:
                if maybe_host.startswith(partial_host):
                    return maybe_host

        return None

    def add_host(self, full_hostname: str) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.search_host(partial_host=full_hostname):
            return

        with self.path.open("a") as cache_fd:
            cache_fd.write(f"{full_hostname}\n")

    def replace_content(self, new_content: str) -> None:
        self.path.write_text(data=new_content)


class Resolver:
    pass


@dataclass
class NetboxResolver(Resolver):
    api_token: str
    netbox_url: str
    cachefile: Optional[CacheFile]

    def get_fqdn(
        self,
        device: Dict[str, Any],
    ) -> Optional[str]:
        if device["primary_ip"]:
            response = requests.get(
                url=device["primary_ip"]["url"],
                headers={"Authorization": f"Token {self.api_token}"},
            )
            response.raise_for_status()
            ip_info = response.json()
            dns_name = ip_info["dns_name"]
            if dns_name:
                return dns_name

        return f"{device['name']}.{device['site']['slug']}.wmnet"

    def get_vm(
        self,
        search_query: str,
    ) -> Optional[str]:
        response = requests.get(
            url=f"{self.netbox_url}/virtualization/virtual-machines/",
            params={"q": search_query},
            headers={"Authorization": f"Token {self.api_token}"},
        )
        response.raise_for_status()
        vm_infos = response.json()["results"]
        for vm_info in vm_infos:
            fqdn = self.get_fqdn(
                self.api_token,
                device=vm_info,
            )
            if fqdn:
                return fqdn

        return None

    def get_physical(
        self,
        search_query: str,
    ) -> Optional[str]:
        response = requests.get(
            url=f"{self.netbox_url}/dcim/devices/",
            params={"q": search_query},
            headers={"Authorization": f"Token {self.api_token}"},
        )
        response.raise_for_status()
        machine_infos = response.json()["results"]
        for machine_info in machine_infos:
            fqdn = self.get_fqdn(
                self.api_token,
                device=machine_info,
            )
            if fqdn:
                return fqdn

        return None

    def get_host(self, hostname: str) -> Optional[str]:
        if self.cachefile:
            maybe_host = self.cachefile.search_host(hostname)
            if maybe_host:
                return maybe_host

        full_hostname = self.get_physical(search_query=hostname)
        LOGGER.debug("netbox: found physical host %s", full_hostname)
        if not full_hostname:
            full_hostname = self.get_vm(search_query=hostname)
            LOGGER.debug("netbox: found vm: %s", full_hostname)

        if self.cachefile and full_hostname:
            self.cachefile.add_host(full_hostname=full_hostname)

        return full_hostname

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"NetboxResolver(api_token=*******, netbox_url='{self.netbox_url}', cache_file='{self.cachefile}')"


@dataclass
class OpenstackBrowserResolrver(Resolver):
    openstack_browser_url: str
    cachefile: Optional[CacheFile]

    def get_host(self, hostname: str) -> Optional[str]:
        if self.cachefile:
            maybe_vm = self.cachefile.search_host(hostname)
            if maybe_vm:
                return maybe_vm

        all_vms_response = requests.get(self.openstack_browser_url)
        all_vms_response.raise_for_status()
        if self.cachefile:
            self.cachefile.replace_content(all_vms_response.text)
            return self.cachefile.search_host(hostname)

        for maybe_vm in all_vms_response.text.splitlines():
            if maybe_vm.startswith(hostname):
                return maybe_vm.strip()

        return None


@dataclass
class KnownHostsResolver(Resolver):
    known_hosts_url: str
    cachefile: Optional[CacheFile]

    def get_host(self, hostname: str) -> Optional[str]:
        if self.cachefile:
            maybe_known_host = self.cachefile.search_host(hostname)
            if maybe_known_host:
                return maybe_known_host

        all_known_hosts_response = requests.get(self.known_hosts_url)
        all_known_hosts_response.raise_for_status()
        clean_hosts = [host_line.split(",", 1)[0] for host_line in all_known_hosts_response.text.splitlines()]
        if self.cachefile:
            self.cachefile.replace_content("\n".join(clean_hosts))
            return self.cachefile.search_host(hostname)

        for maybe_known_host in clean_hosts:
            if maybe_known_host.startswith(hostname):
                return maybe_known_host.strip()

        return None


def load_config_file(config_path: Path) -> Dict[str, str]:
    LOGGER.debug("Loading config file from %s", config_path)
    wm_ssh_config = DEFAULT_CONFIG.copy()
    if config_path.exists():
        wm_ssh_config.update(json.load(config_path.expanduser().open()))
        LOGGER.debug("Config file loaded from %s", config_path)
    else:
        LOGGER.debug("Config file '%s' not found, using default config.", config_path)

    if wm_ssh_config["netbox_config_path"] and Path(wm_ssh_config["netbox_config_path"]).expanduser().exists():
        netbox_config = json.load(Path(wm_ssh_config["netbox_config_path"]).expanduser().open())
        wm_ssh_config["netbox_config"] = netbox_config
        LOGGER.debug("Netbox config file loaded from '%s'", config_path)
    else:
        LOGGER.debug("Unable to load netbox config file '%s'", wm_ssh_config["netbox_config_path"])

    return wm_ssh_config


def _remove_duplicated_key_if_needed(stderr: str) -> bool:
    if "WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED" in stderr:
        if click.confirm("The host key has changed, remove the old one and retry?", err=True):
            remove_key_command = None
            next = False
            for line in stderr.splitlines():
                if next:
                    remove_key_command = line
                    break
                if line.strip().startswith("remove with:"):
                    next = True

            if remove_key_command is not None:
                subprocess.check_output(["/bin/bash", "-c", remove_key_command.strip()])
                return True
            else:
                raise Exception("Unable to find the command to remove a key from the output: \n{stderr}")

    return False


def try_ssh(hostname: str, cachefile: Optional[CacheFile], user: str = None) -> Optional[str]:
    LOGGER.debug("[direct] Looking up hostname %s%s", f"{user}@" if user else "", hostname)
    if cachefile:
        maybe_host = cachefile.search_host(hostname)
        if maybe_host:
            LOGGER.debug("[direct] Got host %s from the cache", maybe_host)
            return maybe_host

    res = subprocess.run(args=["ssh", f"{user}@{hostname}" if user else hostname, "hostname"], capture_output=True)
    if res.returncode == 0:
        LOGGER.debug("[direct] Hostname %s worked", hostname)
        if cachefile:
            LOGGER.debug("[direct] Adding %s in the cache", hostname)
            cachefile.add_host(full_hostname=hostname)

        return hostname

    if "Could not resolve hostname" in res.stderr.decode():
        LOGGER.debug("[direct] Hostname %s was unresolved", hostname)
        return None

    if _remove_duplicated_key_if_needed(stderr=res.stderr.decode()):
        return try_ssh(hostname=hostname, user=user, cachefile=cachefile)

    raise Exception(
        f"Unknown error when trying to ssh to {hostname}: \nstdout:\n{res.stdout.decode()}\n"
        f"stderr:\n{res.stderr.decode()}"
    )


@click.command(name="wm-ssh", help="Wikimedia ssh wrapper that expands hostnames")
@click.option("-v", "--verbose", help="Show extra verbose output", is_flag=True)
@click.option("--print-config", help="Show the loaded configuration", is_flag=True)
@click.option(
    "--config-file",
    default=Path(str(DEFAULT_CONFIG_PATH)),
    help="Path to the configuration file with the wm-ssh settings.",
    type=Path,
)
@click.option(
    "--no-caches", help="Ignore the caches, this does not remove them, only ignores them for the run.", is_flag=True
)
@click.option("--flush-caches", help="Clean the caches, this removes any cached hosts.", is_flag=True, default=False)
@click.argument("hostname", required=False, default=None)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def wm_ssh(
    verbose: bool,
    print_config: bool,
    hostname: str,
    config_file: Path,
    no_caches: bool,
    flush_caches: bool,
    args: List[str],
) -> int:
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    config = load_config_file(config_path=Path(config_file))
    if print_config:
        print(json.dumps(config, indent=4))
        return 0

    known_hosts_cachefile = CacheFile(path=DEFAULT_CACHE_PATH / "known_hosts.txt")
    netbox_cachefile = CacheFile(path=DEFAULT_CACHE_PATH / "netbox.txt")
    openstack_cachefile = CacheFile(path=DEFAULT_CACHE_PATH / "openstackbrowser.txt")
    direct_cachefile = CacheFile(path=DEFAULT_CACHE_PATH / "direct.txt")

    if flush_caches and click.confirm("This will erase the caches permanently, are you sure?"):
        netbox_cachefile.replace_content("")
        openstack_cachefile.replace_content("")
        direct_cachefile.replace_content("")
        if not hostname:
            return 0

    if no_caches:
        netbox_cachefile = None
        openstack_cachefile = None
        direct_cachefile = None

    if not hostname:
        print("Error: Missing argument 'HOSTNAME'")
        return 1

    resolvers = [
        KnownHostsResolver(
            known_hosts_url=config["known_hosts_url"],
            cachefile=known_hosts_cachefile,
        )
    ]
    if not config.get("netbox_config"):
        LOGGER.info("Unable to find netbox config, disabling netbox resolver.")
    else:
        resolvers.append(
            NetboxResolver(
                netbox_url=config["netbox_config"]["netbox_url"],
                api_token=config["netbox_config"]["api_token"],
                cachefile=netbox_cachefile,
            )
        )

    resolvers.append(
        OpenstackBrowserResolrver(
            openstack_browser_url=config["openstack_browser_url"],
            cachefile=openstack_cachefile,
        )
    )

    if "@" in hostname:
        user, hostname = hostname.split("@", 1)
    else:
        user = None

    full_hostname = try_ssh(hostname, cachefile=direct_cachefile, user=user)
    if full_hostname:
        LOGGER.debug("I was able to ssh directly, just continuing.")
    else:
        LOGGER.debug("Direct ssh failed, trying to resolve.")
        LOGGER.debug("Using resolvers: %s", resolvers)
        for resolver in resolvers:
            LOGGER.debug("Trying resolver %s", resolver)
            try:
                full_hostname = resolver.get_host(hostname=hostname)
                if full_hostname:
                    break
            except Exception as error:
                LOGGER.warning(f"Got error when trying to fetch host from {resolver}: {error}")

        if not full_hostname:
            LOGGER.error("Unable to find a hostname for '%s'", hostname)
            sys.exit(1)

    LOGGER.info("Found full hostname %s", full_hostname)
    if user:
        full_hostname = f"{user}@{full_hostname}"

    LOGGER.debug("Waiting for ssh to finish...")
    _do_ssh(full_hostname=full_hostname, args=args)
    LOGGER.debug("Done")
    return 0


def _do_ssh(full_hostname: str, args: List[str]) -> None:
    cmd = ["ssh", full_hostname, *args]
    proc = subprocess.Popen(args=cmd, bufsize=0, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr, shell=False)
    proc.wait()
    if proc.returncode != 0:
        LOGGER.debug("First attempt failed with error, rerunning dummy ssh to get output...")
        capturing_proc = subprocess.run(args=["ssh", full_hostname, "hostname"], capture_output=True)
        if _remove_duplicated_key_if_needed(stderr=capturing_proc.stderr.decode()):
            LOGGER.debug("Found and removed duplicated key, retrying...")
            return _do_ssh(full_hostname=full_hostname, args=args)

        else:
            raise subprocess.CalledProcessError(returncode=proc.returncode, output=None, stderr=None, cmd=cmd)


if __name__ == "__main__":
    sys.exit(wm_ssh())
