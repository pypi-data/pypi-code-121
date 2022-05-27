from typing import Optional, Any, List, Sequence, Dict

from pydantic import BaseModel

from kikyo_api.nsclient.base import NamespacedClient
from kikyo_api.serializer import JsonSerializer
from kikyo_api.utils import read_json_data

_json = JsonSerializer()


class SearchClient(NamespacedClient):
    """
    提供全文检索服务
    """

    api_prefix = '/api/search'

    def search(self, index: str) -> 'IndexedQuery':
        """
        指定索引

        :param index: index名称
        """
        return IndexedQuery(index, self)

    def index(self, index: str) -> 'DataIndex':
        """
        指定索引

        :param index: index名称
        """
        return DataIndex(index, self)


class BaseResponse:
    def __init__(self, data: dict):
        self.response = data

    def __getitem__(self, key):
        return self.response.get(key)


class SearchResponse(BaseResponse):
    def hits_total(self) -> Optional[int]:
        total = self['hits'].get('total')
        if total:
            return total['value']

    def hits(self) -> List[dict]:
        return [h['_source'] for h in self['hits']['hits']]

    def raw_hits(self) -> List[dict]:
        return self['hits']['hits']

    def count(self) -> int:
        return self['count']

    def buckets(self, name: str) -> List[dict]:
        return self['aggregations'][name]['buckets']


class BulkResponse(BaseResponse):
    def errors(self) -> bool:
        return self['errors']


class DataIndex:
    """
    索引
    """

    def __init__(self, index: str, client: SearchClient):
        self._index = index
        self._client = client

    def exists(self, id: str) -> bool:
        """
        指定ID的数据是否存在

        :param id: 数据ID
        """

        resp = self._client.session.head(
            f'{self._client.api_prefix}/indices/{self._index}/data/{id}',
        )
        if resp.status_code == 404:
            return False
        resp.raise_for_status()
        return True

    def get(self, id: str) -> dict:
        """
        返回指定数据

        :param id: 数据的ID
        """

        data = read_json_data(
            self._client.session.get(
                f'{self._client.api_prefix}/indices/{self._index}/data/{id}',
            )
        )
        return data['_source']

    def put(self, id: str, data: dict, refresh: bool = None):
        """
        更新指定数据，指定ID不存在时自动创建数据

        :param id: 数据ID
        :param data: 数据内容
        :param refresh: 强制刷新索引
        """

        args = {
            'body': data,
        }
        if refresh is not None:
            args['refresh'] = refresh
        read_json_data(
            self._client.session.put(
                f'{self._client.api_prefix}/indices/{self._index}/data/{id}',
                data=_json.dumps(args).encode(),
                headers={
                    'content-type': _json.mimetype,
                },
            )
        )

    def update(self, id: str, data: str = None, refresh: bool = None):
        """
        更新数据的指定字段

        :param id: 数据ID
        :param data: 更新的数据内容
        :param refresh: 强制刷新索引
        """

        args = {
            'body': {
                'doc': data,
            },
        }
        if refresh is not None:
            args['refresh'] = refresh
        read_json_data(
            self._client.session.put(
                f'{self._client.api_prefix}/indices/{self._index}/update/{id}',
                data=_json.dumps(args).encode(),
                headers={
                    'content-type': _json.mimetype,
                },
            )
        )

    def delete(self, id: str, refresh: bool = None):
        """
        删除指定数据

        :param id: 数据ID
        :param refresh: 强制刷新索引
        """

        args = {}
        if refresh is not None:
            args['refresh'] = refresh
        read_json_data(
            self._client.session.delete(
                f'{self._client.api_prefix}/indices/{self._index}/data/{id}',
                data=_json.dumps(args).encode(),
                headers={
                    'content-type': _json.mimetype,
                },
            )
        )

    def search_by_dsl(self, query_body: dict) -> 'SearchResponse':
        data = read_json_data(
            self._client.session.post(
                f'{self._client.api_prefix}/indices/{self._index}/search-by-dsl',
                data=_json.dumps({
                    'body': query_body,
                }).encode(),
                headers={
                    'content-type': _json.mimetype,
                },
            )
        )
        return SearchResponse(data)

    def count_by_dsl(self, query_body: dict) -> 'SearchResponse':
        data = read_json_data(
            self._client.session.post(
                f'{self._client.api_prefix}/indices/{self._index}/count-by-dsl',
                data=_json.dumps({
                    'body': query_body,
                }).encode(),
                headers={
                    'content-type': _json.mimetype,
                },
            )
        )
        return SearchResponse(data)

    def update_by_dsl(self, query_body: dict) -> 'BaseResponse':
        data = read_json_data(
            self._client.session.post(
                f'{self._client.api_prefix}/indices/{self._index}/update-by-dsl',
                data=_json.dumps({
                    'body': query_body,
                }).encode(),
                headers={
                    'content-type': _json.mimetype,
                },
            )
        )
        return BaseResponse(data)

    def bulk(self, actions: List[dict], refresh: bool = None):
        data = {
            'actions': actions,
        }
        if refresh is not None:
            data['refresh'] = refresh
        data = read_json_data(
            self._client.session.post(
                f'{self._client.api_prefix}/indices/{self._index}/bulk',
                data=_json.dumps(data).encode(),
                headers={
                    'content-type': _json.mimetype,
                },
            )
        )
        return BulkResponse(data)

    def query(self, name: str = None) -> 'QueryBuilder':
        """
        基于筛选表达式检索数据，影响评分

        :param name: 筛选的字段名称
        """

        q = IndexedQuery(self._index, self._client)
        return QueryBuilder(name, q, q._queries)

    def filter(self, name: str = None) -> 'QueryBuilder':
        """
        基于筛选表达式检索数据，不影响评分

        :param name: 筛选的字段名称
        """

        q = IndexedQuery(self._index, self._client)
        return QueryBuilder(name, q, q._filters)


class IndexedQuery(DataIndex):
    def __init__(self, index: str, client: SearchClient):
        super().__init__(index, client)

        self._queries: List[NamedClause] = []
        self._filters: List[NamedClause] = []
        self._page = None
        self._size = None

    def query(self, name: str = None) -> 'QueryBuilder':
        return QueryBuilder(name, self, self._queries)

    def filter(self, name: str = None) -> 'QueryBuilder':
        return QueryBuilder(name, self, self._queries)

    def paginate(self, page: int = 0, size: int = 10) -> 'IndexedQuery':
        """
        分页查询

        :param page: 分页的页码，从0开始
        :param size: 分页的大小
        """

        self._page = page
        self._size = size
        return self

    def hits(self) -> List[dict]:
        """
        返回命中查询的所有数据，默认进行了分页。
        """

        body = {
            'query': self._build_query(),
        }
        if self._size is not None:
            body['size'] = self._size
            if self._page is not None:
                body['from'] = self._page * self._size

        return self.search_by_dsl(body).hits()

    def count(self) -> int:
        """
        返回命中查询的数据量
        """

        body = {
            'query': self._build_query(),
        }
        return self.count_by_dsl(body).count()

    def _build_query(self) -> dict:
        query = BoolQuery()
        for q in self._queries:
            q.build(query.must, query.must_not)
        for f in self._filters:
            f.build(query.filter, query.must_not)
        return {
            'bool': query.dict()
        }


class BoolQuery(BaseModel):
    must: List[Dict] = []
    filter: List[Dict] = []
    must_not: List[Dict] = []
    should: List[Dict] = []


class ClauseType:
    IS = object()
    IS_NOT = object()
    IS_ONE_OF = object()
    IS_BETWEEN = object()
    IS_NOT_BETWEEN = object()
    EXISTS = object()
    DOES_NOT_EXIST = object()
    MATCH = object()


class NamedClause(BaseModel):
    type: Any
    name: Optional[str]
    value: Any = None

    def build(self, must: list, must_not: list):
        if self.type == ClauseType.IS:
            assert isinstance(self.value, Sequence)
            if self.name is None:
                must.append({
                    'simple_query_string': {
                        'query': ' '.join([f'"{i}"' for i in self.value]),
                        'default_operator': 'and',
                    }
                })
            else:
                for i in self.value:
                    must.append(self._match_phrase(self.name, i))
        elif self.type == ClauseType.IS_NOT:
            assert isinstance(self.value, Sequence)
            if self.name is None:
                must_not.append({
                    'simple_query_string': {
                        'query': ' '.join([f'"{i}"' for i in self.value]),
                    }
                })
            else:
                for i in self.value:
                    must_not.append(self._match_phrase(self.name, i))
        elif self.type == ClauseType.IS_ONE_OF:
            assert isinstance(self.value, Sequence)
            b = BoolQuery()
            if self.name is None:
                for v in self.value:
                    b.should.append({
                        'simple_query_string': {
                            'query': f'"{v}"',
                        }
                    })
            else:
                for v in self.value:
                    b.should.append(self._match_phrase(self.name, v))
            must.append({
                'bool': b.dict(),
            })
        elif self.type in (ClauseType.IS_BETWEEN, ClauseType.IS_NOT_BETWEEN):
            assert isinstance(self.value, tuple)
            if self.name is not None:
                q = {}
                if self.value[0] is not None:
                    q['gte'] = self.value[0]
                if self.value[1] is not None:
                    q['lte'] = self.value[1]
                if q:
                    _q = {
                        'range': {
                            self.name: q
                        }
                    }
                    if self.type == ClauseType.IS_BETWEEN:
                        must.append(_q)
                    else:
                        must_not.append(_q)
        elif self.type == ClauseType.EXISTS:
            if self.name is not None:
                must.append(self._exists(self.name))
        elif self.type == ClauseType.DOES_NOT_EXIST:
            if self.name is not None:
                must_not.append(self._exists(self.name))
        elif self.type == ClauseType.MATCH:
            assert isinstance(self.value, Sequence)
            if self.name is None:
                must.append({
                    'simple_query_string': {
                        'query': ' '.join([i for i in self.value]),
                    }
                })
            else:
                for i in self.value:
                    must.append(self._match(self.name, i))

    @staticmethod
    def _match_phrase(name: str, value: Any) -> dict:
        if ',' in name:
            s = name.split(',')
            return {
                "multi_match": {
                    "type": "phrase",
                    "query": value,
                    "fields": [i.strip() for i in s]
                }
            }
        return {
            'match_phrase': {
                name: value
            }
        }

    @staticmethod
    def _match(name: str, value: Any) -> dict:
        if ',' in name:
            s = name.split(',')
            return {
                "multi_match": {
                    "query": value,
                    "fields": [i.strip() for i in s]
                }
            }
        return {
            'match': {
                name: value,
            }
        }

    @staticmethod
    def _exists(name: str) -> dict:
        return {
            'exists': {
                'field': name
            }
        }


class QueryBuilder:
    def __init__(self, name: Optional[str], query: IndexedQuery, query_set: list):
        self._name = name
        self._query = query
        self._query_set = query_set

    def is_(self, *values: Any) -> IndexedQuery:
        """
        是某个值

        :param values: 具体值的列表
        """

        self._query_set.append(
            NamedClause(
                type=ClauseType.IS,
                name=self._name,
                value=values,
            )
        )
        return self._query

    def is_not(self, *values: Any) -> IndexedQuery:
        """
        不是某个值

        :param values: 具体值的列表
        """

        self._query_set.append(
            NamedClause(
                type=ClauseType.IS_NOT,
                name=self._name,
                value=values
            )
        )
        return self._query

    def is_one_of(self, *values: Any) -> IndexedQuery:
        """
        是其中某个值

        :param values: 具体值的列表
        """

        self._query_set.append(
            NamedClause(
                type=ClauseType.IS_ONE_OF,
                name=self._name,
                value=values,
            )
        )
        return self._query

    def is_between(self, lower_bound: Any = None, upper_bound: Any = None) -> IndexedQuery:
        """
        在区间范围内

        :param lower_bound: 最低值
        :param upper_bound: 最高值
        """

        self._query_set.append(
            NamedClause(
                type=ClauseType.IS_BETWEEN,
                name=self._name,
                value=(lower_bound, upper_bound),
            )
        )
        return self._query

    def is_not_between(self, lower_bound: Any = None, upper_bound: Any = None) -> IndexedQuery:
        """
        不在区间范围内

        :param lower_bound: 最低值
        :param upper_bound: 最高值
        """

        self._query_set.append(
            NamedClause(
                type=ClauseType.IS_NOT_BETWEEN,
                name=self._name,
                value=(lower_bound, upper_bound),
            )
        )
        return self._query

    def exists(self) -> IndexedQuery:
        """
        字段存在
        """

        self._query_set.append(
            NamedClause(
                type=ClauseType.EXISTS,
                name=self._name,
            )
        )
        return self._query

    def does_not_exists(self) -> IndexedQuery:
        """
        字段不存在
        """

        self._query_set.append(
            NamedClause(
                type=ClauseType.DOES_NOT_EXIST,
                name=self._name,
            )
        )
        return self._query

    def match(self, *values: Any) -> IndexedQuery:
        """
        模糊匹配

        :param values: 具体值的列表
        """

        self._query_set.append(
            NamedClause(
                type=ClauseType.MATCH,
                name=self._name,
                value=values,
            )
        )
        return self._query
