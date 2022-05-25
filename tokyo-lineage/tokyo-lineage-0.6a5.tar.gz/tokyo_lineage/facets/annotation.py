import attr

from openlineage.client.facet import BaseFacet


@attr.s
class Annotation(BaseFacet):
    dataset_annotation: dict = attr.ib(init=False)
    column_annotation: dict = attr.ib(init=False)
    row_annotation: dict = attr.ib(init=False)