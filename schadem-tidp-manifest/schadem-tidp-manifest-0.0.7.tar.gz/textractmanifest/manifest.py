from dataclasses import dataclass, field
import marshmallow as m
import logging
from typing import List

logger = logging.getLogger(__name__)


class BaseSchema(m.Schema):
    """
    skip null values when generating JSON
    https://github.com/marshmallow-code/marshmallow/issues/229#issuecomment-134387999
    """
    SKIP_VALUES = set([None])

    @m.post_dump
    def remove_skip_values(self, data, many, pass_many=False):
        return {
            key: value
            for key, value in data.items()
            if isinstance(value, (dict, list, set, tuple, range,
                                  frozenset)) or value not in self.SKIP_VALUES
        }


@dataclass
class MetaData():
    key: str
    value: str


@dataclass
class Query():
    text: str
    alias: str
    pages: List[str]


@dataclass
class IDPManifest():
    s3_path: str = field(default=None)  #type: ignore
    document_pages: List[str] = field(default=None)  #type: ignore
    queries_config: List[Query] = field(default=None)  #type: ignore
    textract_features: List[str] = field(default=None)  #type: ignore
    classification: str = field(default=None)  #type: ignore
    meta_data: List[MetaData] = field(default=None)  #type: ignore


class MetaDataSchema(BaseSchema):
    key = m.fields.String(data_key="key", required=True)
    value = m.fields.String(data_key="value", required=False)


class QuerySchema(BaseSchema):
    text = m.fields.String(data_key="text", required=True)
    alias = m.fields.String(data_key="alias", required=False)
    pages = m.fields.List(m.fields.String, data_key="pages", required=False)

    @m.post_load
    def make_query(self, data, **kwargs):
        return Query(**data)


class IDPManifestSchema(BaseSchema):
    queries_config = m.fields.List(m.fields.Nested(QuerySchema),
                                   data_key="queriesConfig",
                                   required=False)
    textract_features = m.fields.List(m.fields.String,
                                      data_key="textractFeatures",
                                      required=False)
    s3_path = m.fields.String(data_key="s3Path", required=False)
    classification = m.fields.String(data_key="classification", required=False)
    document_pages = m.fields.List(m.fields.String,
                                   data_key="documentPages",
                                   required=False)
    meta_data = m.fields.List(m.fields.Nested(MetaDataSchema),
                              data_key="metaData",
                              required=False)

    @m.post_load
    def make_queries_config(self, data, **kwargs):
        return IDPManifest(**data)
