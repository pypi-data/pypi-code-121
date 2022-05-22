import os
import argparse

from flask import Flask
from flask.json import JSONEncoder
from datetime import datetime
from flask_restful import Resource, Api

from sdap.data_access import CollectionLoader

from sdap.utils import get_log

from sdap.webapp_resources import Home
from sdap.webapp_resources import Collections
from sdap.webapp_resources import CollectionById
from sdap.webapp_resources import Admin

logger = get_log(__name__)


class Operators(Resource):

    def __init__(self, **kwargs):
        self._collection_loader = kwargs['collection_loader']

    def get(self):
        return "to be implemented"


class Jobs(Resource):

    def __init__(self, **kwargs):
        self._collection_loader = kwargs['collection_loader']

    def get(self):
        return "to be implemented"

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)


def create_parser():

    server_cmd_parser = argparse.ArgumentParser()
    cwd = os.path.dirname(__file__)
    conf_rel_path = './test/data_access/collection-config.yaml'
    server_cmd_parser.add_argument("--conf", required=False, default=os.path.join(cwd, conf_rel_path))
    server_cmd_parser.add_argument("--secrets", required=False, default=None)
    return server_cmd_parser

def main():
    parser = create_parser()
    args = parser.parse_args()
    collection_loader = CollectionLoader(args.conf, secret_file=args.secrets)

    app = Flask('sdap.webapp')
    app.config['BUNDLE_ERRORS'] = True
    app.json_encoder = CustomJSONEncoder
    api = Api(app)

    api.add_resource(Home, '/')

    api.add_resource(
         Collections,
         '/collections',
         resource_class_kwargs={'collection_loader': collection_loader}
    )

    api.add_resource(
        CollectionById,
        '/collections/<string:collection_id>',
        resource_class_kwargs={'collection_loader': collection_loader}
    )

    api.add_resource(
        Admin,
        '/admin/<string:operation>'
    )

    app.run(host='0.0.0.0', port=8083, debug=True)


if __name__ == '__main__':
    main()
