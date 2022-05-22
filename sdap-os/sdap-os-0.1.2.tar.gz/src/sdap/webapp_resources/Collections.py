from flask_restful import Resource



class Collections(Resource):

    def __init__(self, **kwargs):
        self._collection_loader = kwargs['collection_loader']

    def get(self):
        return self._collection_loader.get_collections()