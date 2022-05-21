"""The grapmaster based on MongoDB."""
from typing import Union, Any

import bson.objectid
import dill
import pymongo

from pyaiml21.botconfig import BotConfig
from .graphmaster import GraphMaster, PolicyFn, KEEP_LAST_POLICY


class MongoGraphMaster(GraphMaster):
    """Store the template nodes in the MongoDB."""

    _PICKLED_OBJ_KEY = "_pickled_obj"

    def __init__(
            self,
            bot_config: 'BotConfig',
            collection: pymongo.collection.Collection[Any],
            policy: Union[str, PolicyFn] = KEEP_LAST_POLICY
    ):
        """
        Create mongo graphmaster.

        :param collection: collection to which the templates will be stored
        :param bot_config: configuration of the bot with sets and predicates
        :param policy: merge policy to use
        """
        super().__init__(bot_config, policy)
        self.collection = collection

    def save_obj(self, obj: Any) -> bson.objectid.ObjectId:
        """Save `obj` to the database."""
        pickled_obj = dill.dumps(obj)
        result = self.collection.insert_one({
            self._PICKLED_OBJ_KEY: pickled_obj
        })
        assert isinstance(result.inserted_id, bson.objectid.ObjectId)
        return result.inserted_id

    def load_obj(self, saved_obj: bson.objectid.ObjectId) -> Any:
        """Load template from the database."""
        result = self.collection.find_one({
            "_id": saved_obj
        })
        assert result is not None, ("expected to find the stored object, "
                                    "but found nothing")
        return dill.loads(result[self._PICKLED_OBJ_KEY])
