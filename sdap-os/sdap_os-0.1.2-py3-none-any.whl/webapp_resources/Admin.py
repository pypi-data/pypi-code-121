from flask_restful import Resource

from .CollectionById import CollectionById


class Admin(Resource):
    OPERATION_CLEAR_CACHE = 'clear_cache'

    def get(self, operation):
        if operation == self.OPERATION_CLEAR_CACHE:
            CollectionById.clear_cache()
            return 'cache cleared'
