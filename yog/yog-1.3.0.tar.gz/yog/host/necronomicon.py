import typing as t

import yaml


def loads(ident: str, necronomicon: str) -> 'Necronomicon':
    return load(ident, yaml.safe_load(necronomicon))


def loadfile(ident: str, path: str) -> 'Necronomicon':
    with open(path) as nin:
        return loads(ident, nin.read())


def load(ident: str, parsed_necronomicon) -> 'Necronomicon':
    if parsed_necronomicon is None:
        return Necronomicon(ident, NeededTunnelsSection([]), DockerSection([]), CronSection([]), FileSection([]))

    if 'files' in parsed_necronomicon:
        fs = FileSection([File(
            e['src'],
            e['dest'],
            e['hupcmd'] if 'hupcmd' in e else None,
            e['root'] if 'root' in e else False,
        ) for e in parsed_necronomicon['files']])
    else:
        fs = FileSection([])

    if 'docker' in parsed_necronomicon:
        ds = DockerSection([DockerContainer(
            e['image'],
            e['name'],
            e['fingerprint'],
            e['volumes'] if 'volumes' in e else {},
            {str(k): str(v) for k, v in (e['ports'] if 'ports' in e else {}).items()},
            e['env'] if 'env' in e else {},
            e['command'] if 'command' in e else None,
        ) for e in parsed_necronomicon['docker']])
    else:
        ds = DockerSection([])

    if 'cron' in parsed_necronomicon:
        cs = CronSection([CronJob(e['expr'], e['command'], e['user'] if 'user' in e else 'root') for e in parsed_necronomicon['cron']])
    else:
        cs = CronSection([])

    if 'needs_tunnels' in parsed_necronomicon:
        tunnels = NeededTunnelsSection([
            NeededTunnel(
                tun['host'],
                int(tun['target_port']),
                int(tun['local_port']),
            ) for tun in parsed_necronomicon['needs_tunnels']
        ])
    else:
        tunnels = NeededTunnelsSection([])

    return Necronomicon(ident, tunnels, ds, cs, fs)


class Necronomicon(t.NamedTuple):
    ident: str
    tunnels: 'NeededTunnelsSection'
    docker: 'DockerSection'
    cron: 'CronSection'
    files: 'FileSection'


class DockerSection(t.NamedTuple):
    containers: t.List['DockerContainer']


class DockerContainer(t.NamedTuple):
    image: str
    name: str
    fingerprint: str
    volumes: t.Mapping[str, str]
    ports: t.Mapping[str, str]
    env: t.Mapping[str, str]
    command: t.Optional[str]


class CronSection(t.NamedTuple):
    crons: t.List['CronJob']


class CronJob(t.NamedTuple):
    expr: str
    command: str
    user: str


class FileSection(t.NamedTuple):
    files: t.List['File']


class File(t.NamedTuple):
    src: str
    dest: str
    hupcmd: str
    root: bool


class NeededTunnel(t.NamedTuple):
    host: str
    target_port: int
    local_port: int


class NeededTunnelsSection(t.NamedTuple):
    tunnels: t.List[NeededTunnel]