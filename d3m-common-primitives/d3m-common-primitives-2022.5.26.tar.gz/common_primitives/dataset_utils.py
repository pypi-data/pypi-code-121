import typing

from d3m import container, deprecate
from d3m.base import utils as d3m_base_utils


@deprecate.function(message="use d3m.base.utils.sample_rows function instead")
def sample_rows(
    dataset: container.Dataset, main_resource_id: str, main_resource_indices_to_keep: typing.Set[int],
    relations_graph: typing.Dict[str, typing.List[typing.Tuple[str, bool, int, int, typing.Dict]]], *,
    delete_recursive: bool = False,
) -> container.Dataset:
    return d3m_base_utils.sample_rows(dataset, main_resource_id, main_resource_indices_to_keep, relations_graph, delete_recursive=delete_recursive)
