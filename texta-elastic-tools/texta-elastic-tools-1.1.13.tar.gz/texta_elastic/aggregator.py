import json
from typing import List, Union, Dict
from collections import defaultdict
from elasticsearch_dsl import Q, Search

from texta_elastic.core import ElasticCore
from texta_elastic.exceptions import DocPathsWithoutValuesAggregationError, KeyFieldEqualsValueFieldError, InvalidKeyFieldError, InvalidValueFieldError
from texta_elastic.settings import ALLOWED_KEY_FIELDS, ALLOWED_VALUE_FIELDS

class ElasticAggregator:
    """
    Everything related to performing aggregations in Elasticsearch
    """
    EMPTY_QUERY = {"query": {"match_all": {}}}



    def __init__(self, field_data=[], indices=[], query=EMPTY_QUERY):
        """
        field_data: list of decoded fields
        indices: list of index names (strings)
        """
        self.core = ElasticCore()
        self.field_data = field_data
        self.indices = indices
        self.query = query


    def _get_indices_string(self):
        return ",".join(self.indices)


    def update_query(self, query):
        self.query = query


    def update_field_data(self, field_data):
        """
        Updates field data. Expects list of decoded fields.
        """
        self.field_data = field_data


    def _aggregate(self, agg_query):
        self.query["aggregations"] = agg_query
        response = self.core.es.search(index=self.indices, body=self.query)
        return response


    def facts_abstract(self, key_field: str, value_field: str, filter_by_key: str = "", size: int = 30, min_count: int = 0, max_count: int = None) -> Union[Dict[str, List[str]], List[str]]:
        """
        For more dynamic fact aggregations. Returns either a dict, where keys = keys corresponding to `key_field` and
        values = values from `value_field` corresponding to a specific key. If `filter_by_key` is specified, only a list of
        values corresponding to that specific field are returned.
        Example: key_field = "doc_path", value_field="fact", filter_by_key="text_mlp.text" would return all fact names
        corresponding to doc_path "text_mlp.text".
        """

        if key_field not in ALLOWED_KEY_FIELDS:
            raise InvalidKeyFieldError(f"Invalid key field: '{key_field}'. Key field should be one of the following: {ALLOWED_KEY_FIELDS}.")
        if value_field not in ALLOWED_VALUE_FIELDS:
            raise InvalidValueFieldError(f"Invalid value field: '{value_field}'. Value field should be one of the following: {ALLOWED_VALUE_FIELDS}.")
        if key_field == value_field:
            raise KeyFieldEqualsValueFieldError(f"Error. key_field == value_field == '{key_field}'. Key and value fields must be different! ")

        agg_query = {
            "facts": {
                "nested": {"path": "texta_facts"},
                "aggs": {
                    "keys": {
                        "terms": {"field": f"texta_facts.{key_field}", "size": 10000}  # Get as many types of facts as possible.
                    }
                }
            }
        }

        if filter_by_key:
            agg_query["facts"]["aggs"]["keys"]["terms"]["include"] = [filter_by_key]


        agg_query["facts"]["aggs"]["keys"]["aggs"] = {"values": {"terms": {"field": f"texta_facts.{value_field}", "size": size}}}

        response = self._aggregate(agg_query)
        aggregations = response["aggregations"]

        entities = defaultdict(list)

        if aggregations["facts"]["doc_count"] > 0:
            keys = aggregations["facts"]["keys"]["buckets"]
            for key in keys:
                key_value = key["key"]
                if "values" in key:
                    for value in key["values"]["buckets"]:

                        value_key = value["key"]
                        value_count = value["doc_count"]

                        if value_key and value_count > min_count:
                            if max_count and value_count >= max_count:
                                continue

                            entities[key_value].append(value_key)

        if filter_by_key:
            if filter_by_key in entities:
                out = entities[filter_by_key]
            else:
                out = []
        else:
            out = dict(entities)

        return out


    def facts(self, size=30, filter_by_fact_name=None, min_count=0, max_count=None, include_values=True, include_doc_path=False, exclude_zero_spans=False):
        """
        For retrieving entities (facts) from ES.
        """
        agg_query = {
            "facts": {
                "nested": {"path": "texta_facts"},
                "aggs": {
                    "facts": {
                        "terms": {"field": "texta_facts.fact", "size": 10000}  # Get as many types of facts as possible.
                    }
                }
            }
        }

        if not include_values and include_doc_path:
            raise DocPathsWithoutValuesAggregationError("Cannot include doc path without including values! Please set `include_values=True`.")


        # filter by name if fact name present
        if filter_by_fact_name:
            agg_query["facts"]["aggs"]["facts"]["terms"]["include"] = [filter_by_fact_name]

        if include_values:
            agg_query["facts"]["aggs"]["facts"]["aggs"] = {"fact_values": {"terms": {"field": "texta_facts.str_val", "size": size}}}
            if include_doc_path:
                agg_query["facts"]["aggs"]["facts"]["aggs"]["fact_values"]["aggs"] = {"doc_paths": {"terms": {"field": "texta_facts.doc_path", "size": size}}}

            if exclude_zero_spans:
                if "aggs" in agg_query["facts"]["aggs"]["facts"]["aggs"]["fact_values"]:
                    agg_query["facts"]["aggs"]["facts"]["aggs"]["fact_values"]["aggs"].update({"fact_spans": {"terms": {"field": "texta_facts.spans", "size": 1}}})
                else:
                    agg_query["facts"]["aggs"]["facts"]["aggs"]["fact_values"]["aggs"] = {"fact_spans": {"terms": {"field": "texta_facts.spans", "size": 1}}}

        if exclude_zero_spans and not include_values:
            agg_query["facts"]["aggs"]["facts"]["aggs"] = {"fact_spans": {"terms": {"field": "texta_facts.spans", "size": 1}}}

        response = self._aggregate(agg_query)
        aggregations = response["aggregations"]

        entities = {}

        zero_span = json.dumps([[0, 0]])

        if aggregations["facts"]["doc_count"] > 0:
            fact_names = aggregations["facts"]["facts"]["buckets"]
            for fact_type in fact_names:
                fact_name = fact_type["key"]
                entities[fact_name] = []
                if "fact_values" in fact_type:
                    for fact_value in fact_type["fact_values"]["buckets"]:

                        fact_value_key = fact_value["key"]
                        fact_value_count = fact_value["doc_count"]

                        if exclude_zero_spans:
                            fact_span = fact_value["fact_spans"]["buckets"][0]["key"]

                        if include_doc_path:
                            fact_value_doc_path = fact_value["doc_paths"]["buckets"][0]["key"]
                            entity_to_add = {"value": fact_value_key, "doc_path": fact_value_doc_path}
                        else:
                            entity_to_add = fact_value_key

                        if fact_value_key and fact_value_count > min_count:
                            if max_count and fact_value_count >= max_count:
                                continue

                            if exclude_zero_spans:
                                if fact_span != zero_span:
                                    entities[fact_name].append(entity_to_add)

                            else:
                                entities[fact_name].append(entity_to_add)
                elif "fact_spans" in fact_type:
                    fact_span = fact_type["fact_spans"]["buckets"][0]["key"]
                    if fact_span == zero_span:
                        del entities[fact_name]


        # filter by name if fact name present
        if filter_by_fact_name:
            if filter_by_fact_name in entities:
                entities = entities[filter_by_fact_name]
            else:
                entities = []

        if not include_values:
            entities = list(entities.keys())
        return entities


    def filter_aggregation_maker(self, agg_type: str, field: str, filter_query: dict = None, size=1000, return_size=15, stop_words: List = None, exclude=""):

        container = []

        s = Search(using=self.core.es, index=self._get_indices_string())
        if filter_query:
            filter_query = Q(filter_query)
            s.aggs.bucket("limits", "filter", filter=filter_query).bucket("placekeeper", agg_type, field=field, size=size, exclude=exclude)
            r = s.execute()
            for hit in r.aggs.limits.placekeeper:
                container.append(hit.to_dict())
        else:
            s.aggs.bucket("placekeeper", agg_type, field=field)
            r = s.execute()
            for hit in r.aggs.limits.placekeeper:
                container.append(hit.to_dict())

        if stop_words:
            container = [item for item in container if item["key"] not in set(stop_words)]

        return container[:return_size]


    def get_significant_words(self, document_ids: List[str], field: str, stop_words: List = None, exclude="") -> List[dict]:
        """
        Args:
            stop_words: Optional parameter to remove stop words from significant words.
            document_ids: List of document ids to limit the range of the significant words.
            field: Path name of the field we're comparing text from for significant words.
            exclude: regex string for which values to exclude.

        Returns: List of dicts with the aggregation results.

        """
        query = {'ids': {'values': document_ids}}
        sw = self.filter_aggregation_maker(agg_type="significant_text", field=field, filter_query=query, stop_words=stop_words, exclude=exclude)
        sw = [{"key": hit["key"], "count": hit["doc_count"]} for hit in sw]
        return sw


    def get_fact_values_distribution(self, fact_name: str, fact_name_size: int = 30, fact_value_size: int = 30):
        """
        Returns a dictionary with fact values (labels) as keys and labels' quantities as values.
        """
        self.query["size"] = 0

        agg_query = {'fact_values': {'nested': {'path': 'texta_facts'},
                                     'aggs': {'fact_bucket': {'terms': {'field': 'texta_facts.fact', 'size': fact_name_size},
                                                              'aggs': {'value_bucket': {'terms': {'field': 'texta_facts.str_val', 'size': fact_value_size}}}}}}}
        # agg_query["size"] = 30

        fact_dist_dict = {}
        response = self._aggregate(agg_query)

        for fact in response["aggregations"]["fact_values"]["fact_bucket"]["buckets"]:
            if fact["key"] == fact_name:
                for fact_value in fact["value_bucket"]["buckets"]:
                    fact_dist_dict[fact_value["key"]] = fact_value["doc_count"]
        return fact_dist_dict
