import logging
from os.path import dirname, join, isdir, isfile, basename

import docker
from docker.types import LogConfig
from paramiko import SSHClient, SSHException
from paramiko.ssh_exception import NoValidConnectionsError

from yog.host.manage_docker_utils import is_acceptable_container, my_format_to_run_ports_arg_format, build_volumes_dict
from yog.ssh_utils import check_call, check_stdout, ScopedProxiedRemoteSSHTunnel, compare_local_and_remote
from yog.host import necronomicon
from yog.host.necronomicon import Necronomicon

log = logging.getLogger(__name__)


def apply_necronomicon(host: str, root_dir):
    ssh = SSHClient()
    ssh.load_system_host_keys()
    try:
        log.info(f"[{host}]")
        ssh.connect(host)
        apply_necronomicon_for_host(host, ssh, root_dir)
    except RuntimeError as e:
        log.error(f"{host} error: {e.__class__.__name__}: {str(e)}")
    except SSHException as e:
        log.error(f"{host} error: {e.__class__.__name__}: {str(e)}")
    except NoValidConnectionsError as e:
        log.error(f"{host} error: {e.__class__.__name__}: {str(e)}")
    finally:
        ssh.close()


def load_necronomicons_for_host(host: str, root_dir):
    necronomicon_paths = []
    cur = join(root_dir, "domains")
    if isfile(join(cur, "_.yml")):
        necronomicon_paths.append(join(cur, "_.yml"))

    for part in reversed(host.split(".")):
        if not isdir(cur):
            break
        if isfile(join(cur, f"{part}.yml")):
            necronomicon_paths.append(join(cur, f"{part}.yml"))
        cur = join(cur, part)

    return [necronomicon.loadfile(basename(p), p) for p in necronomicon_paths]


def apply_necronomicon_for_host(host: str, ssh: SSHClient, root_dir):
    necronomicons = load_necronomicons_for_host(host, root_dir)
    if not necronomicons:
        raise RuntimeError(f"No necronomicons found for {host}")

    for n in necronomicons:
        if n.files.files:
            apply_files_section(host, n, ssh, root_dir)
        if n.docker.containers:
            apply_docker_section(host, n, ssh)
        if n.cron.crons:
            apply_cron_section(host, n, ssh)


def apply_cron_section(host: str, n: Necronomicon, ssh: SSHClient):
    cronfile_lines = []
    line1_length = max([len(c.expr) for c in n.cron.crons])
    line2_length = max([len(c.user) for c in n.cron.crons])
    for cron in n.cron.crons:
        cronfile_lines.append(f"{cron.expr.ljust(line1_length, ' ')}\t{cron.user.ljust(line2_length, ' ')}\t{cron.command}")
    cronfile_body = "\n".join(cronfile_lines + [""])
    ok, expected, found = compare_local_and_remote(bytes(cronfile_body, "utf-8"), "/etc/cron.d/yog.cron", ssh)
    if not ok:
        log.info(f"Writing /etc/cron.d/yog.cron version {expected[:10]}")
        check_call(ssh, "sudo bash -c 'cat - > /etc/cron.d/yog.cron'", send_stdin=cronfile_body)


def apply_docker_section(host: str, n: Necronomicon, ssh: SSHClient):
    log.info(f"Docker: {n.ident}")
    tunnels = []
    for tunnel_def in n.tunnels.tunnels:
        log.debug(f"Setting up tunnel {tunnel_def}")
        tunnel = ScopedProxiedRemoteSSHTunnel(
            host,
            tunnel_def.target_port,
            tunnel_def.host,
            "remote",
            force_random_port=tunnel_def.local_port)
        tunnels.append(tunnel)

    try:
        for tun in tunnels:
            tun.connect()
        with ScopedProxiedRemoteSSHTunnel(host, 4243) as tport:
            log.debug("Connecting docker client....")
            client = docker.DockerClient(base_url=f"tcp://localhost:{tport}", version="auto")
            log.debug("Docker connected.")

            for desired_container in n.docker.containers:
                log.debug(desired_container)

                desired_container_env = {}
                for name, value in desired_container.env.items():
                    value = str(value)
                    if value.startswith("yogreadfile:"):
                        try:
                            desired_container_env[name] = "\n".join(check_stdout(ssh, f"sudo cat {value[len('yogreadfile:'):]}")).strip()
                        except RuntimeError as err:
                            log.error(f"Error processing yogreadfile: {value}", exc_info=err)
                            raise RuntimeError(f"Error accessing file: {value[len('yogreadfile:'):]}")
                    else:
                        desired_container_env[name] = value

                log.debug(f"PULL: {desired_container.image}@{desired_container.fingerprint}")
                img = client.images.pull(f"{desired_container.image}@{desired_container.fingerprint}")

                cur = client.containers.list(all=True, filters={"name": desired_container.name})
                matches = []
                for c in cur:
                    log.debug(f"Existing container {c.id} is {c.status}")
                    if is_acceptable_container(c, img, desired_container, desired_container_env):
                        log.debug(f"{c.id} is image {c.image.id} which matches our target.")
                        matches.append(c)
                    else:
                        if c.status in ["running", "restarting"]:
                            log.info(f"STOP {c.name}:{c.id}")
                            c.stop()
                        log.info(f"RM: {c.name}:{c.id}")
                        c.remove()
                if len(matches) > 0:
                    log.debug("Existing container matches our desired state. No need to kill it.")
                else:
                    log.info(f"RUN: {desired_container.image}@{desired_container.fingerprint}")
                    ports_dict = my_format_to_run_ports_arg_format(desired_container.ports)
                    volumes_dict = build_volumes_dict(desired_container.volumes)
                    client.containers.run(f"{desired_container.image}@{desired_container.fingerprint}",
                                          name=desired_container.name,
                                          restart_policy={'Name': "always"},
                                          volumes=volumes_dict,
                                          ports=ports_dict,
                                          log_config=LogConfig(type=LogConfig.types.JOURNALD),
                                          environment=desired_container_env,
                                          detach=True,
                                          command=desired_container.command)
    finally:
        for tun in tunnels:
            try:
                tun.disconnect()
            except RuntimeError as e:
                log.warning("Error while disconnecting tunnel", exc_info=e)


def apply_files_section(host: str, n: Necronomicon, ssh: SSHClient, root_dir):
    log.info(f"Files: {n.ident}")
    hupcmds = set()
    for f in n.files.files:
        with open(join(root_dir, "files", f.src)) as fin:
            content = fin.read()
        ok, _, _ = compare_local_and_remote(content.encode("utf-8"), f.dest, ssh, f.root)
        if ok:
            log.debug(f"{f.src} is up-to-date.")
        else:
            log.info(f"[{host}]: put {f.src} -> {f.dest}")
            if f.hupcmd:
                hupcmds.add(f.hupcmd)

            if f.root:
                cmd_prefix = "sudo "
            else:
                cmd_prefix = ""

            check_call(ssh, f"{cmd_prefix}mkdir -p \"{dirname(f.dest)}\"")
            check_call(ssh, f"{cmd_prefix}bash -c 'cat - > \"{f.dest}\"'", send_stdin=content)
    for c in hupcmds:
        log.info(f"HUPCMD: {c}")
        check_call(ssh, c)
