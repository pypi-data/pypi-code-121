import re
import typing as t

from docker.models.containers import Container
from docker.models.images import Image

from yog.host.necronomicon import DockerContainer


def my_format_to_run_ports_arg_format(port_section: t.Mapping[str, str]):
    def format_host_expr(host_expr: str) -> t.Tuple[str, str]:
        md: re.Match = re.fullmatch(r"((?P<addr>\d+\.\d+\.\d+\.\d+):)?(?P<port>\d+)(/(?P<proto>tcp|udp))?",
                                host_expr)  # 0.0.0.0:53/tcp

        return md.group("addr") if md.group("addr") else '0.0.0.0', md.group("port")

    def format_container_port_expr(container_port_expr: str) -> str:
        return container_port_expr if container_port_expr.endswith("/tcp") or container_port_expr.endswith(
            "/udp") else f"{container_port_expr}/tcp"

    ret = dict()
    for k, v in port_section.items():
        new_key = format_container_port_expr(v)
        new_value = format_host_expr(k)

        if new_key in ret:
            ret[new_key].append(new_value)
        else:
            ret[new_key] = [new_value]

    #print(ret)
    return ret


def build_volumes_dict(volumes_section: t.Mapping[str, str]):
    ret = {}
    for k, v in volumes_section.items():
        mode_data = re.search(r"\+(?P<mode>r[ow])$", v)
        if mode_data:
            ret[k] = {"bind": v[:-3], "mode": mode_data.group("mode").strip()}
        else:
            ret[k] = {"bind": v, "mode": "rw"}

    return ret


def my_format_to_ports_attr_format(port_section: t.Mapping[str, str]):
    """Converts my YAML format, which is the same as the docker CLI -p format, to what the docker API expects
    MY format is:
        key: <host addr>:<host port>/<proto>
        value: <dest container port>/<proto>
    What the API expects is:
    A dict where the keys are a str of format: "container port/proto"
           and the values are a list whose elements are
                              a dict that looks like {HostIp: <HostAddr>, HostPort: <HostPort>}
    Example:
        {
            '33200/tcp': [{'HostIp': '0.0.0.0', 'HostPort': '33200'}],
            '53/tcp': [{'HostIp': '192.168.1.103', 'HostPort': '53'}],
            '53/udp': [{'HostIp': '192.168.1.103', 'HostPort': '53'}]
        }
    """

    def format_host_expr(host_expr: str) -> t.List[t.Dict[str, str]]:
        md: re.Match = re.fullmatch(r"((?P<addr>\d+\.\d+\.\d+\.\d+):)?(?P<port>\d+)(/(?P<proto>tcp|udp))?",
                                host_expr)  # 0.0.0.0:53/tcp

        return [{'HostIp': md.group("addr") if md.group("addr") else '0.0.0.0',
                 'HostPort': md.group('port')}]

    def format_container_port_expr(container_port_expr: str) -> str:
        return container_port_expr if container_port_expr.endswith("/tcp") or container_port_expr.endswith(
            "/udp") else f"{container_port_expr}/tcp"

    #ret = {format_container_port_expr(v): format_host_expr(k) for k, v in port_section.items()}
    ret = dict()
    for k, v in port_section.items():
        key = format_container_port_expr(v)
        value = format_host_expr(k)

        if key not in ret:
            ret[key] = []

        ret[key].extend(value)
        ret[key] = sorted(ret[key], key=lambda entry: (entry["HostIp"], entry["HostPort"]))

    #print(ret)
    return ret


def _ports_match(desired: t.Mapping[int, t.Union[int, str]], ports: t.Mapping[str, t.Mapping[str, str]]):
    expected = my_format_to_ports_attr_format(desired)
    sorted_ports = dict()
    # TODO this breaks if the container EXPOSEs a port but I don't bind it
    for k, v in ports.items():
        if v:
            sorted_ports[k] = sorted(v, key=lambda entry: (entry["HostIp"], entry["HostPort"]))
    return expected == sorted_ports


def _envs_match(desired: DockerContainer, found: Container, desired_env):
    found_env_list: t.List[str] = found.attrs['Config']['Env']
    found_env = {l[0]: l[1] for l in (l.split("=", 1) for l in found_env_list) if l[0] in desired.env}
    return found_env == desired_env


def _volumes_match(desired: DockerContainer, found: Container):
    found_mounts_list: t.List[t.Dict[str, t.Any]] = found.attrs['Mounts']
    found_mounts_volume = {m['Name']: {"bind": m['Destination'], "mode": m["Mode"]} for m in found_mounts_list if m['Type'] == 'volume'}
    found_mounts_bind = {m['Source']: {"bind": m['Destination'], "mode": m["Mode"]} for m in found_mounts_list if m['Type'] == 'bind'}
    found_mounts = {}
    for k, v in found_mounts_volume.items():
        if k in desired.volumes:
            found_mounts[k] = v

    for k, v in found_mounts_bind.items():
        if k in desired.volumes:
            found_mounts[k] = v

    return found_mounts == build_volumes_dict(desired.volumes)


def _commands_match(desired: DockerContainer, found: Container):
    if desired.command:
        return desired.command.split(" ") == found.attrs["Config"]["Cmd"]
    else:
        return found.image.attrs['Config']['Cmd'] == found.attrs["Config"]["Cmd"]


def is_acceptable_container(c: Container, img_by_digest: Image, desired: DockerContainer, desired_env):
    return c.image.id == img_by_digest.id and \
           c.status in ["running"] and \
           _ports_match(desired.ports, c.ports) and \
           _envs_match(desired, c, desired_env) and \
           _volumes_match(desired, c) and \
           _commands_match(desired, c)


