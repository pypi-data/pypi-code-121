# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import json
from contrast.agent.protect.rule.nosql_injection.mongo_nosql_scanner import (
    MongoNoSqlScanner,
)
from contrast.agent.protect.rule.sqli_rule import SqlInjection
from contrast.utils.decorators import fail_quietly


class NoSqlInjection(SqlInjection):
    """
    NoSQL Injection Protection rule
    """

    RULE_NAME = "nosql-injection"

    def build_sample(self, evaluation, query, **kwargs):
        sample = self.build_base_sample(evaluation)
        if query is not None:
            sample.no_sqli.query = query

        if "start_idx" in kwargs:
            sample.no_sqli.start_idx = int(kwargs["start_idx"])

        if "end_idx" in kwargs:
            sample.no_sqli.end_idx = int(kwargs["end_idx"])

        if "boundary_overrun_idx" in kwargs:
            sample.no_sqli.boundary_overrun_idx = int(kwargs["boundary_overrun_idx"])

        if "input_boundary_idx" in kwargs:
            sample.no_sqli.input_boundary_idx = int(kwargs["input_boundary_idx"])

        return sample

    def get_database_scanner(self, database):
        return MongoNoSqlScanner()

    def skip_protect_analysis(self, user_input, args, kwargs):
        """
        nosql-injection has many potential user input types so
        let's not skip analysis
        """
        return False

    def convert_input(self, user_input):
        if not isinstance(user_input, (str, bytes)):
            user_input = obj_to_str(user_input)

        return super().convert_input(user_input)

    def sample_dtm_to_json(self, sample):
        return {
            "start": sample.no_sqli.start_idx,
            "end": sample.no_sqli.end_idx,
            "boundaryOverrunIndex": sample.no_sqli.boundary_overrun_idx,
            "inputBoundaryIndex": sample.no_sqli.input_boundary_idx,
            "query": sample.no_sqli.query,
        }


@fail_quietly("Failed to convert nosql obj input to str", return_value="")
def obj_to_str(obj):
    """
    Convert one of the common obj types passed to pymongo methods into a string.

    :param obj: list, dict, bson or a type that inherits from collections.MutableMapping
    :return: str
    """
    try:
        return json.dumps(obj)
    except TypeError:
        # may encounter TypeError: Object of type ObjectId is not JSON serializable
        # so let's just make it a string
        return str(obj)
