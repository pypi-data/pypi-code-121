from copy import deepcopy

from pydantic import BaseModel


class ModelSnapshot(BaseModel):
    """Class providing a container for a model snapshot created after an execution of a model.
    It provides a function to upcast itself to a hashed model snapshot used for caching purposes.
    """
    name: str
    abs_path: str
    execution_time: str
    modification_timestamp: int
    input_parameters: dict
    artefacts: dict
    figures_of_merit: dict

    def upcast_to_hashed_model_snapshot(self, model_snapshot_hash: str) -> "HashedModelSnapshot":
        """Method upcasting a model snapshot to its subclass with a model snapshot model_api

        :param model_snapshot_hash: a string with model snapshot model_api used for caching
        :return: an instance of HashedModelSnapshot
        """
        return HashedModelSnapshot(**self.__dict__, hash=model_snapshot_hash)


class HashedModelSnapshot(ModelSnapshot):
    """Class providing a container for hashed model snapshot used for communication with the model_api database.
    It provides a function to downcast a hashed model snapshot ot its superclass.

    """
    hash: str

    def downcast_to_model_snapshot(self) -> ModelSnapshot:
        """Method downcasting a HashedModelSnapshot instance into ModelSnapshot superclass to be used by PyMBSE

        :return: a ModelSnapshot instance
        """
        model_snapshot_dct = deepcopy(self.__dict__)
        del model_snapshot_dct['hash']
        return ModelSnapshot(**model_snapshot_dct)
