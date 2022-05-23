from itertools import starmap
from logging import warning
from operator import attrgetter
from os import sched_getaffinity, sysconf
from re import compile
from types import MappingProxyType
from typing import Any, Callable, Iterator, List, Mapping, Optional, Tuple, \
    Union

from pylxd import Client
from pylxd.models import Container, VirtualMachine
from tabulate import tabulate

from .constant import ShowResource

__all__ = [
    'print_resources',
]

_DEFAULT_CPU_COUNT = len(sched_getaffinity(0))
_DEFAULT_MEMORY = sysconf('SC_PAGE_SIZE') * sysconf('SC_PHYS_PAGES')
_FACTOR_GB = 10 ** -9
_FACTOR_GIB = 2 ** -30
_DEFAULT_MEMORY_GB = _DEFAULT_MEMORY * _FACTOR_GB  # gigabytes
_DEFAULT_MEMORY_GIB = _DEFAULT_MEMORY * _FACTOR_GIB  # gibibytes

_PRINT_HEADERS = ('Name', 'CPU', 'Memory', 'HDD', 'Network', 'Profiles')
_PRINT_HEADERS_WITH_TYPE = ('Type',) + _PRINT_HEADERS
_PRINT_CONTAINER_LABEL = 'C'
_PRINT_VIRTUAL_MACHINE_LABEL = 'VM'
_PRINT_SUMMARY_LABEL = '=== SUMMARY ==='

_EMPTY_STRING = ''

_MEMORY_UNIT_MULTIPLICATION_MAP = MappingProxyType({
    'b': 1,
    'kib': 2 ** 10,
    'mib': 2 ** 20,
    'gib': 2 ** 30,
    'tib': 2 ** 40,
    'kb': 10 ** 3,
    'mb': 10 ** 6,
    'gb': 10 ** 9,
    'tb': 10 ** 12,
})

_MEMORY_PATTERN = compile(
    rf'^\s*(\d+(?:\.\d+)?)\s*'
    rf'(?i:({"|".join(_MEMORY_UNIT_MULTIPLICATION_MAP)}))?\s*$',
)


def _format_size(
    size_gb: Optional[float],
    gb_unit: str,
) -> str:
    """Format memory size in GB to string."""
    return f'{size_gb:.2f} {gb_unit}' if size_gb else 'UNKNOWN'


def _parse_size_to_gb(
    memory_size: str,
    warning_callback: Callable[[str], None],
    in_gibibytes: bool,
) -> Optional[float]:
    """Memory size string parsing to GB units."""
    try:
        memory_size, memory_unit = _MEMORY_PATTERN.match(memory_size).groups()

    except (ValueError, AttributeError):
        warning(warning_callback(memory_size))
        return

    try:
        memory_factor = _MEMORY_UNIT_MULTIPLICATION_MAP[memory_unit.lower()]

    except KeyError:
        warning(warning_callback(memory_size))
        return

    gb_factor = _FACTOR_GIB if in_gibibytes else _FACTOR_GB

    try:
        return memory_factor * float(memory_size) * gb_factor

    except (ValueError, TypeError):
        warning(warning_callback(memory_size))


def _iter_disk_devices(
    instance_name: str,
    devices: Mapping[str, Mapping[str, Any]],
    in_gibibytes: bool,
) -> Iterator[Tuple[str, Optional[float]]]:
    for device in devices.values():
        if device['type'] != 'disk':
            continue

        yield device['path'], _parse_size_to_gb(
            device.get('size', ''),
            # pylint: disable=consider-using-f-string
            f'Unknown disk units {{0!r}} for {instance_name!r}.'.format,
            in_gibibytes,
        )


def _iter_resources(
    instance_collection: List[Union[Container, VirtualMachine]],
    in_gibibytes: bool,
    show_instance_type: bool,
) -> Iterator[Tuple[str, ...]]:
    """Iterate over containers to fetch resources data."""
    total_memory_gb = 0.0
    total_disk_gb = 0.0

    gb_unit = 'GiB' if in_gibibytes else 'GB'

    def format_disk(path: str, disk_size_gb: Optional[float]):
        nonlocal total_disk_gb
        total_disk_gb += disk_size_gb or 0.0
        return f'{path!r}: {_format_size(disk_size_gb, gb_unit)}'

    default_memory_gb = (
        _DEFAULT_MEMORY_GIB if in_gibibytes else _DEFAULT_MEMORY_GB
    )
    default_limits_memory_gb = f'{default_memory_gb} {gb_unit}'

    for instance in instance_collection:
        config = instance.expanded_config
        devices = instance.expanded_devices

        instance_name = instance.name
        instance_status = instance.status

        memory_size_gb = _parse_size_to_gb(
            config.get('limits.memory', default_limits_memory_gb),
            # pylint: disable=consider-using-f-string
            f'Unknown memory units {{!r}} for {instance_name!r}.'.format,
            in_gibibytes,
        )
        if instance_status.lower() == 'running':
            total_memory_gb += memory_size_gb or 0.0

        row = (
            f'{instance_name} ({instance_status})',
            f'{config.get("limits.cpu", _DEFAULT_CPU_COUNT)} '
            f'(allowance: {config.get("limits.cpu.allowance", "100%")})',
            _format_size(memory_size_gb, gb_unit),
            '\n'.join(
                starmap(
                    format_disk,
                    _iter_disk_devices(instance_name, devices, in_gibibytes),
                ),
            ),
            '\n'.join(
                (
                    f'{device["nictype"]}: {device["parent"]}'
                    for device in devices.values()
                    if device['type'] == 'nic'
                )
            ),
            '\n'.join(instance.profiles),
        )

        if show_instance_type:
            row = (
                _PRINT_CONTAINER_LABEL if isinstance(
                    instance, Container,
                ) else _PRINT_VIRTUAL_MACHINE_LABEL,
            ) + row

        yield row

    row = (
        _PRINT_SUMMARY_LABEL,
        _EMPTY_STRING,
        f'{total_memory_gb:.2f} {gb_unit} '
        f'({total_memory_gb / default_memory_gb:.2%})',
        f'{total_disk_gb:.2f} {gb_unit}',
        _EMPTY_STRING,
        _EMPTY_STRING,
    )

    if show_instance_type:
        row = (_EMPTY_STRING, ) + row

    yield row


def print_resources(
    client: Client,
    in_gibibytes: bool,
    show_resource: ShowResource,
) -> None:
    """Print LXD resources."""
    if show_resource is ShowResource.CONTAINER:
        instance_collection = client.containers.all()

    elif show_resource is ShowResource.VIRTUAL_MACHINE:
        instance_collection = client.virtual_machines.all()

    else:
        instance_collection = (
            client.containers.all() + client.virtual_machines.all()
        )

    show_instance_type = show_resource is ShowResource.BOTH
    print(
        tabulate(
            tuple(
                _iter_resources(
                    sorted(instance_collection, key=attrgetter('name')),
                    in_gibibytes,
                    show_instance_type,
                ),
            ),
            _PRINT_HEADERS_WITH_TYPE if show_instance_type else _PRINT_HEADERS,
            tablefmt='grid',
        ),
    )
