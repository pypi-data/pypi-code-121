import datetime

from chaingrep.api_resources.requester import Requester
from chaingrep.exceptions import InvalidQueryError


class Query:
    def __init__(self, auth):
        self._query = None
        self._timeframe = None
        self.auth = auth

    def _format_query(self, _query):
        for element in _query:
            if not isinstance(_query[element], str):
                _query[element] = str(_query[element]).lower()

        return _query

    def query(self, _query):
        self._query = self._format_query(_query)

    def timeframe(self, after, before):
        after_type = type(after)
        before_type = type(before)

        if after_type != before_type:
            raise InvalidQueryError("'after' and 'before' must be of the same type.")

        if after_type not in [int, datetime.datetime]:
            raise InvalidQueryError("'after' and 'before' must be of type: 'int' or 'datetime.datetime'.")

        if isinstance(after, datetime.datetime):
            after = int(after.timestamp())
            before = int(before.timestamp())

        _timeframe = [after, before]

        self._timeframe = _timeframe

    def execute(self, skip=0, sort=None):
        if not self._query:
            raise InvalidQueryError("Missing query.")

        if not sort:
            sort = ["timestamp", "descending"]

        if skip > 90:
            raise InvalidQueryError("Skip limit is 90.")

        if not isinstance(sort, list):
            raise InvalidQueryError("Sort condition must be passed as a list with the format: [key, order].")

        method_endpoint = "/query"
        payload = {
            "action": "query",
            "query": self._query,
            "skip": skip,
            "timeframe": self._timeframe,
            "sort": sort,
            "chain": "ethereum",
        }
        query_result = Requester(self.auth).post(method_endpoint, body=payload)

        status_code = query_result.get("status_code")
        response = query_result.get("response")

        if status_code != 200:
            raise InvalidQueryError(response)

        return response

    def count(self):
        if not self._query:
            raise InvalidQueryError("Missing query.")

        method_endpoint = "/query"
        payload = {"action": "count", "query": self._query, "timeframe": self._timeframe, "chain": "ethereum"}
        query_result = Requester(self.auth).post(method_endpoint, body=payload)

        status_code = query_result.get("status_code")
        response = query_result.get("response")

        if status_code != 200:
            raise InvalidQueryError(response)

        return response
