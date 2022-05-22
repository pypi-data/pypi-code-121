from datetime import datetime
from flask import jsonify
from flask import request
from flask_restful import Resource
from marshmallow import Schema
from webargs import fields
import xarray
import time
from typing import Dict, Any
import hashlib
import json
from flask import current_app as app
import threading


from sdap.operators import Identity
from sdap.operators import get_operator


class CollectionsByIdQuerySchema(Schema):
    collection_id = fields.String(),
    bbox = fields.DelimitedList(fields.Float, required=True)
    crs = fields.String(required=False, default='EPSG:4326')
    time_range = fields.DelimitedList(fields.String, required=True)
    operator = fields.String(required=False, default=Identity)
    operator_args = fields.List(fields.String,  required=False, default=None)


request_schema = CollectionsByIdQuerySchema()


class RequestCache:

    MAX_AGE_SECONDS = 600

    def __init__(self, iterator, consolidate_func):
        """

        :param iterator:
        :param consolidate_func: a function which takes as a argument
        a list [result, new_result] of xarrays and
        return a new consolidated xarray
        """
        self.consolidate_func = consolidate_func
        self.iterator = iterator
        self.result = xarray.DataArray()
        self.last_retrieved = time.time()
        self.complete_evt = threading.Event()

    def run(self):
        for xa in self.iterator:
            self.result = self.consolidate_func([self.result, xa])
            del xa
        self.complete_evt.set()

    def start(self):
        t = threading.Thread(target=self.run)
        t.start()

    def get_result(self):
        response = jsonify(self.result.to_dict())
        response.status = 200 if self.complete_evt.is_set() else 206
        return response


class CollectionById(Resource):
    _cached_requests = {}

    def __init__(self, **kwargs):
        self._collection_loader = kwargs['collection_loader']

    @classmethod
    def clear_cache(cls):
        # TODO check if request cache is used before deleting it.
        cls._cached_requests.clear()

    @staticmethod
    def dict_hash(dictionary: Dict[str, Any]) -> str:
        """MD5 hash of a dictionary."""
        dhash = hashlib.md5()
        encoded = json.dumps(dictionary, sort_keys=True).encode()
        dhash.update(encoded)
        return dhash.hexdigest()

    def get(self, collection_id):
        app.logger.debug(request.args)
        args = request_schema.load(request.args)
        request_hash = collection_id + self.dict_hash(args)
        app.logger.info("processing request with hash %s", request_hash)
        if request_hash not in self._cached_requests:
            app.logger.debug("initialize request %s", request_hash)
            app.logger.debug("get driver for collection %s", collection_id)
            driver = self._collection_loader.get_driver(collection_id)
            operator = get_operator(args['operator'], args.get('operator-args', None))
            request_iterator = driver.get(args['bbox'],
                    [datetime.fromisoformat(t) for t in args['time_range']],
                    operator,
                    request_crs=args['crs'])

            self._cached_requests[request_hash] = RequestCache(
                request_iterator,
                operator.consolidate
            )
            self._cached_requests[request_hash].start()

        self._cached_requests[request_hash].complete_evt.wait(10)
        return self._cached_requests[request_hash].get_result()


        # result = driver.get_all(
        #      args['bbox'],
        #      [datetime.fromisoformat(t) for t in args['time_range']],
        #      operator,
        #      crs=args['crs'])
        #
        # return jsonify(result.to_dict())


