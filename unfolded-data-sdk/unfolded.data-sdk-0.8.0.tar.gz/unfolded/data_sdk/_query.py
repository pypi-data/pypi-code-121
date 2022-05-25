import sys
from abc import ABC
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field

from unfolded.data_sdk.enums import NodeType
from unfolded.data_sdk.models import TimeInterval

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


class QueryNode(BaseModel, ABC):
    """Abstract base class for query nodes"""

    type: NodeType
    input: List["QueryNode"] = Field(default_factory=list)

    class Config:
        """Allows using aliases to set attributes (which we don't set, but prevents against
        validation errors where pydantic complains about the alias not set when the attribute is
        set using the model name)
        https://pydantic-docs.helpmanual.io/usage/model_config/
        """

        allow_population_by_field_name = True


class DatasetNode(QueryNode):
    """A QueryNode to represent FROM <Dataset>"""

    type: NodeType = NodeType.DATASET
    input: List[QueryNode] = Field(default_factory=list, min_items=0, max_items=0)
    uuid: UUID


class InlineDataFormat(str, Enum):
    """Format for which the InlineData is sent"""

    CSV = "CSV"
    JSON_RECORDS = "JSON_OBJECT"


class InlineDataNode(QueryNode):
    """A QueryNode to represent FROM <Inline Data>"""

    type: NodeType = NodeType.INLINE_DATA
    input: List[QueryNode] = Field(default_factory=list, min_items=0, max_items=0)
    format: InlineDataFormat
    data: Union[List[Dict], str]


class SelectNode(QueryNode):
    """A QueryNode to represent SELECT <COLUMN>, <EXPRESSION>"""

    type: NodeType = NodeType.SELECT
    input: List[QueryNode] = Field(min_items=1, max_items=1)
    expressions: List[str] = Field(min_items=1)


class FilterNode(QueryNode):
    """A QueryNode to represent WHERE <CONDITION>"""

    type: NodeType = NodeType.FILTER
    input: List[QueryNode] = Field(min_items=1, max_items=1)
    expression: str


class GroupNode(QueryNode):
    """A QueryNode to represent GROUP BY <COLUMN>"""

    type: NodeType = NodeType.GROUP
    input: List[QueryNode] = Field(min_items=1, max_items=1)
    by: List[str] = Field(min_items=1)
    expressions: List[str] = Field(min_items=1)


class JoinType(str, Enum):
    LEFT = "LEFT"
    INNER = "INNER"
    FULL = "FULL"


class JoinExpression(BaseModel):
    columns: List[str]


class JoinNode(QueryNode):
    """A QueryNode to represent <Table1> LEFT JOIN <Table2> ON <CONDITION>"""

    type: NodeType = NodeType.JOIN
    input: List[QueryNode] = Field(min_items=2, max_items=2)
    on: List[JoinExpression] = Field(min_items=1)
    join: JoinType


class LimitNode(QueryNode):
    """A QueryNode to represent LIMIT <OFFSET>, <LENGTH>"""

    type: NodeType = NodeType.LIMIT
    input: List[QueryNode] = Field(min_items=1, max_items=1)
    length: int = Field(gt=0)
    offset: int = 0


class SortNode(QueryNode):
    """A QueryNode to represent ORDER BY <COLUMN> <ASC|DESC>"""

    type: NodeType = NodeType.SORT
    input: List[QueryNode] = Field(min_items=1, max_items=1)
    by: List[str] = Field(min_items=1)


class EnrichmentTargetType(str, Enum):
    """Enum for types of columns used for enrichment"""

    H3 = "H3"
    LATLNG = "LATLNG"


class EnrichNode(QueryNode):
    type: NodeType = NodeType.ENRICH
    input: List[QueryNode] = Field(min_items=1, max_items=1)
    source_id: UUID = Field(..., alias="sourceId")
    source_column: Union[str, List[str]] = Field(..., alias="sourceColumn")
    time_column: str = Field(None, alias="timeColumn")


class H3EnrichNode(EnrichNode):
    """Node for enriching using an H3 column"""

    target_type: Literal[EnrichmentTargetType.H3] = Field(
        EnrichmentTargetType.H3, alias="targetType"
    )
    column: str


class LatLngEnrichNode(EnrichNode):
    """Node for enriching using latitude and longitude columns"""

    target_type: Literal[EnrichmentTargetType.LATLNG] = Field(
        EnrichmentTargetType.LATLNG, alias="targetType"
    )
    lat_column: str = Field(..., alias="latColumn")
    lng_column: str = Field(..., alias="lngColumn")


class HexifyNode(QueryNode):
    """Node for hexifying a GeoJSON at a given resolution"""

    type: NodeType = NodeType.HEXIFY
    geojson: Dict
    res: int
    column_name: Optional[str] = Field(None, alias="columnName")


class TileExtractNode(QueryNode):
    """Node for extracting data from a HexTile dataset"""

    type: NodeType = NodeType.TILE_EXTRACT
    source_id: UUID = Field(..., alias="sourceId")
    source_column: Optional[Union[str, List[str]]] = Field(None, alias="sourceColumn")
    geojson: Dict
    res: Optional[int] = None
    h3_column_name: Optional[str] = Field(None, alias="h3ColumnName")
    time_column_name: Optional[str] = Field(None, alias="timeColumnName")
    time_interval: Optional[TimeInterval] = Field(None, alias="timeInterval")


class Query:
    """Query provides methods that can be chained to build an Unfolded query, and work with it
    seamlessly

    Example:
        q = Query() \
            .dataset(uuid='1da42194-a676-4e3c-99da-dca399905f11') \
            .filter(expression='metric > 100') \
            .group(by=["country"], expressions=['sum(metric1)', 'max(metric2)']) \
            .select(expressions=['country', 'metric1', 'metric1 * metric2']) \
            .sort(by=['desc(metric1)']) \
            .limit(length=10) \
            .json()

    """

    def __init__(self, node: Optional[QueryNode] = None):
        self.node = node

    def dataset(self, uuid: Union[UUID, str]) -> "Query":
        """Specifies the dataset source for which to apply the query

        Note:
            dataset() needs to be called as the first method in a query method chain, and cannot
            be applied on top of already chained query.

        Args:
            uuid: the dataset id (Unfolded dataset).

        Returns
            A Query object that can be chained with other query operators.
        """
        if self.node:
            raise RuntimeError(
                "dataset() cannot be chained to an existing query method"
            )
        node = DatasetNode(uuid=uuid)
        return Query(node)

    def inline_data(
        self,
        data: Union[List[Dict], str],
        *,
        # pylint:disable = redefined-builtin
        format: InlineDataFormat = InlineDataFormat.CSV,
    ) -> "Query":
        """Specifies the data to run the query with inline

        Args:
            data: the inline data, either as a string or a list of flat dictionaries (record array).

        Returns:
            A query object that can be chained with other query methods.
        """
        if self.node:
            raise RuntimeError("data() cannot be chained to an existing query method")

        node = InlineDataNode(format=format, data=data)
        return Query(node)

    def select(self, expressions: List[str]) -> "Query":
        """Selects columns or expression from a dataset

        Args:
            expressions: the list of expressions or columns to select from the dataset.

        Returns:
            A Query object that can be chained with other query methods.
        """
        node = SelectNode(expressions=expressions, input=[self.node])
        return Query(node)

    def filter(self, expression: str) -> "Query":
        """Applies a filter expression

        Args:
            expression: the expression to use to filter the dataset rows.

        Returns:
            A Query object that can be chained with other query methods.
        """
        node = FilterNode(expression=expression, input=[self.node])
        return Query(node)

    def group(self, by: List[str], expressions: List[str]) -> "Query":
        """Applies a group by aggregation

        Args:
            by: the columns to group by.
            expressions: the expressions to apply on the grouped values.

        Returns:
            A Query object that can be chained with other query methods.
        """
        node = GroupNode(by=by, expressions=expressions, input=[self.node])
        return Query(node)

    def sort(self, by: List[str]) -> "Query":
        """Sorts the dataset rows given a list of expressions

        Args:
            by: the list of sort expressions

        Returns:
            A Query object that can be chained with other query methods.
        """
        node = SortNode(by=by, input=[self.node])
        return Query(node)

    def limit(self, length: int, *, offset: int = 0) -> "Query":
        """Limits the number of rows returned by the query result

        Args:
            length: the number of rows to return.
            offset: the offset from which to limit the rows returned.

        Returns:
            A Query object that can be chained with other query methods.
        """
        node = LimitNode(length=length, offset=offset, input=[self.node])
        return Query(node)

    def enrich(
        self,
        source_id: Union[str, UUID],
        source_column: Union[str, List[str]],
        *,
        h3_column: Optional[str] = None,
        lat_column: Optional[str] = None,
        lng_column: Optional[str] = None,
        time_column: Optional[str] = None,
    ) -> "Query":
        """Enriches a dataset with a given enrichment source

        Enriches a dataset with a given enrichment source and column based on either a h3_column
        or a combination of lat_column and lng_column.

        Args:
            source_id: the uuid of the EnrichmentDataset to enrich with.
            source_column: the EnrichmentColumn to enrich with.
            h3_column: the dataset h3 column to use for enrichment (enrichment by h3).
            lat_column: the dataset latitude column to use for enrichment (enrichment by lat/lng).
            lng_column: the dataset longitude column to use for enrichment (enrichment by lat/lng).
            time_column: the dataset time column to use for temporal enrichment.

        Returns:
            A Query object that can be chained with other query methods.
        """

        node: Optional[EnrichNode] = None

        if h3_column:
            node = H3EnrichNode(
                source_id=source_id,
                source_column=source_column,
                column=h3_column,
                time_column=time_column,
                input=[self.node],
            )
        else:
            node = LatLngEnrichNode(
                source_id=source_id,
                source_column=source_column,
                lat_column=lat_column,
                lng_column=lng_column,
                time_column=time_column,
                input=[self.node],
            )
        return Query(node)

    def hexify(
        self, geojson: Union[Dict, str], res: int, column_name: Optional[str] = None
    ) -> "Query":
        """Polyfills a GeoJSON into H3 hexagons at a given resolution

        Args:
            geojson: the GeoJSON feature to polyfill.
            res: the H3 resolution used for hexification.
            column_name: the name of the column used in the resulting table.

        Returns:
            A Query object that can be chained with other query methods.
        """
        node = HexifyNode(geojson=geojson, res=res, column_name=column_name)
        return Query(node)

    def tile_extract(
        self,
        source_id: Union[str, UUID],
        geojson: Dict,
        *,
        source_column: Optional[Union[str, List[str]]] = None,
        res: Optional[int] = None,
        h3_column: Optional[str] = None,
        time_column: Optional[str] = None,
        time_interval: Optional[Union[Dict, TimeInterval]] = None,
    ) -> "Query":
        """

        Returns:
            A Query object that can be chained with other query methods.
        """
        node = TileExtractNode(
            source_id=source_id,
            source_column=source_column,
            geojson=geojson,
            res=res,
            h3_column_name=h3_column,
            time_column_name=time_column,
            time_interval=time_interval,
        )
        return Query(node)

    def dict(self, **kwargs: Any) -> Dict:
        """Returns a python dictionary representation of the query

        Returns:
            A python dictionary representing the query tree
        """
        if not self.node:
            raise RuntimeError("Cannot convert an empty query to a dictionary")

        return self.node.dict(**kwargs)

    def json(self, **kwargs: Any) -> str:
        """Returns a json representation of the query

        Returns:
            A json string representing the query tree
        """
        if not self.node:
            raise RuntimeError("Cannot convert an empty query to json")

        kwargs["exclude_none"] = True
        kwargs["by_alias"] = True

        return self.node.json(**kwargs)
