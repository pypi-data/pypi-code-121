"""
The main ELBO entry points
"""
import os.path
import weakref
from abc import ABC, abstractmethod
import coloredlogs
import logging

logger = logging.getLogger("elbo.ai.client")
coloredlogs.install(level="DEBUG", logger=logger, fmt="%(name)s %(message)s")

__version__ = "0.1"


class ElboModel(ABC):
    def __init__(self):
        super(ElboModel, self).__init__()
        self._iterator_epoch = 0

    @property
    def iterator_epoch(self):
        """
        Get the iterator epoch
        :return: The iterator epoch
        """
        return self._iterator_epoch

    @iterator_epoch.setter
    def iterator_epoch(self, value):
        """
        Set the iterator epoch
        :param value: The value to set
        :return: None
        """
        self._iterator_epoch = value

    @abstractmethod
    def get_artifacts_directory(self):
        """
        Get the directory where all the artifacts will be saved. This includes model checkpoints, results and other
        files needed to resume the training
        :return: The directory path
        """
        pass

    @abstractmethod
    def save_state(self):
        """
        Save the model state to the artifacts directory. Along with model checkpoint any related data or files
        should also be saved
        :return: None
        """
        pass

    @abstractmethod
    def load_state(self, state_dir):
        """
        Load the model state from the state directory. The state directory will have all the files saved by the
        call to `save_state()`
        :return: The model
        """
        pass


class _ElboModelLoader:
    """
    The Elbo model loader. Used in the beginning of the loop to load model state if available
    """

    _epoch_file_name = ".__elbo__model__iterator__epoch.elbo"

    def __init__(self, model, artifacts_directory):
        self._model = model
        self._artifacts_directory = artifacts_directory
        os.makedirs(self._artifacts_directory, exist_ok=True)
        self._epoch_file_path = os.path.join(
            self._artifacts_directory, _ElboModelLoader._epoch_file_name
        )

    def load(self):
        """
        Load the model and the iteration epoch
        :return: None
        """
        if not os.path.exists(self._epoch_file_path):
            return

        with open(self._epoch_file_path, "r") as fd:
            contents = fd.read()

        try:
            epoch = int(contents)
        except ValueError as e:
            raise e

        logger.info(f"Loaded model training epoch = {epoch}")
        self._model.iterator_epoch = epoch

    def save(self):
        """
        Save any additional state for the ELBO model
        :return: None
        """
        with open(self._epoch_file_path, "w") as fd:
            fd.write(str(self._model.iterator_epoch))
        logger.info(f"Saved model training epoch = {self._model.iterator_epoch}")


class ElboEpochIterator:
    """
    ELBO decorator for an iterable object. This is usually the training data set over which we would iterate
    on in the training loop.
    """

    _lock = None
    _instances = weakref.WeakSet()

    def __new__(cls, *_, **__):
        instance = object.__new__(cls)
        # TODO:
        # Check for only one instance, do we need a l
        cls._instances.add(instance)

        return instance

    def __init__(self, iterable, model, save_state_interval: int = 10):
        """
        Instantiate an ELBO iterator. The iterator can be wrapped
        around other iterators like `tqdm`. The iterator takes the model as input and keeps saving its state
        every save_state_interval iterations. This allows
        :param iterable:
        :param model:
        """
        self._iterable = iterable
        self._model = model
        self._model_loader = _ElboModelLoader(
            self._model, self._model.get_artifacts_directory()
        )
        # Load the state of model
        self._model_loader.load()
        if self._model.iterator_epoch > 0:
            # Model has already been trained, try loading it..
            self._model.load_state(self._model.get_artifacts_directory())

        self._save_state_interval = save_state_interval
        self._start_epoch = self._model.iterator_epoch

    def _get_underlying_length(self):
        total_length = 0

        if hasattr(self._iterable, "__len__"):
            total_length = len(self._iterable)

        if hasattr(self._iterable, "shape"):
            total_length = self._iterable.shape[0]

        if hasattr(self._iterable, "__length_hint"):
            total_length = self._iterable.__length_hint()

        return total_length

    def __len__(self):
        total_length = self._get_underlying_length()
        current_length = self._model.iterator_epoch
        diff = total_length - current_length
        if diff > 0:
            return diff
        else:
            return 0

    def __str__(self):
        return (
            f"ElboModel(iteration_epoch={self._model.iterator_epoch}, "
            f"artifacts_dir={self._model.get_artifacts_directory()}, "
            f"model={self._model})"
        )

    def __iter__(self):
        """
        Iterator so we can use: for data in Elbo(iterable, model)

        :return:
        """
        diff = self._get_underlying_length() - self._start_epoch
        if diff <= 0:
            raise IndexError(f"Iterator epoch out of bounds")

        for epoch, obj in enumerate(self._iterable):
            if diff > 0 and epoch <= self._start_epoch:
                # Consume the first `current_epoch` elements from underlying
                logger.debug(f"Skipping epoch {epoch}")
                continue
            if epoch > 0 and epoch % self._save_state_interval == 0:
                # Save state
                self._model.save_state()
                self._model.iterator_epoch = epoch
                self._model_loader.save()

            yield obj
