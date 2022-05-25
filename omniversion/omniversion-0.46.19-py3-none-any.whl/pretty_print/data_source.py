"""Pretty-printing for data source model classes"""
from typing import Union, List, Callable, Tuple

from colorama import Back, Style

from omniversion.models import ConfigDataSource, FileDataSource, DataSources
from omniversion.pretty_print.helpers import multiline_indent, traffic_light


def _pretty_print_data_source(obj: Union[DataSources, ConfigDataSource, FileDataSource],
                              recursive_format: Callable[[object], str]) -> str:
    if isinstance(obj, FileDataSource):
        color = "green"
        if obj.is_stale or obj.num_packages == 0:
            color = "amber"
        if obj.num_packages is None:
            color = "red"
        return traffic_light(obj, color)

    if isinstance(obj, ConfigDataSource):
        color = "green"
        if obj.num_packages == 0:
            color = "amber"
        return traffic_light(obj, color)

    # must be a `DataSources` object
    def host_summary(host_info: Tuple[str, List[FileDataSource], List[ConfigDataSource]]):
        sources = [recursive_format(file) for file in host_info[1]] + \
                  [recursive_format(config) for config in host_info[2]]
        formatted_sources = "\n".join(sources)
        return f"{Back.BLUE} {host_info[0]} {Style.RESET_ALL}\n{multiline_indent(formatted_sources)}\n"

    return "\n".join([host_summary(host_info) for host_info in obj.host_infos])
