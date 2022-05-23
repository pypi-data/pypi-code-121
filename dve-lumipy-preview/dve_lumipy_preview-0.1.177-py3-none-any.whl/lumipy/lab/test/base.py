import datetime as dt
import sys
import traceback
from abc import ABC, abstractmethod
from multiprocessing.context import ForkProcess
from typing import Union, List, Any, Dict, Optional

import numpy as np
import pandas as pd
from tqdm import tqdm


class BaseResult:
    """Base class for the internal representation of experimental observations and export to a dictionary of values.

    Each observation will be a collection of named values arising from a single run of an experiment.

    The basic attributes of start/end times, error states, and argument values are handled in this class. Subclasses
    must call super().__init__ in order to initialise these values properly.

    """

    def __init__(self):
        """Base constructor of the BaseResult class. Please call this in the constructor of your subclass.

        """
        self.execution_id = None
        self.start = pd.NaT
        self.end = pd.NaT
        self.errored = False
        self.force_stopped = False
        self.error_message = None
        self.args = None

    def to_dict(self) -> Dict[str, Any]:
        """Export the result values to a dictionary.

        Returns:
            Dict[str, Any]: dictionary of values derived from this result.
        """
        d = {}
        for k, v in self.__dict__.items():
            if k != 'args':
                d[k] = v
            else:
                for i, a in enumerate(v):
                    d[f'arg{i}'] = a
        return d


class BaseExperiment(ForkProcess, ABC):
    """Base class for experiments.

    This class encapsulates the core logic of running an experiment and logging results in a way that allows for
    concurrent experiments running in threads and for
    """

    def __init__(
            self,
            *ranges: Union[List[Union[int, float]], Union[int, float]],
            **kwargs: Any
    ):
        """Constructor for the experiment base class.

        Args:
            *ranges (Union[List[Union[int, float]], Union[int, float]]): single constant values or ranges to randomly
            sample for the experiment.

        Keyword Args:
            seed (int): random seed to set in numpy when selecting experiment arg values.
            quiet (bool): whether to suppress log printouts during the experiment.
        """

        self._ranges = ranges

        self._force_stop = False

        self._quiet = kwargs.get('quiet', True)
        self._seed = kwargs.get('seed', np.random.randint(1989))

        # observation values
        self._return = self._init_result()
        self.queue = None
        ForkProcess.__init__(self)

    def __str__(self):
        ranges_str = ', '.join(map(str, self._ranges))
        s = 's' if len(self._ranges) > 1 else ''
        return f"Range{s}: {ranges_str}  Quiet: {self._quiet}  Seed: {self._seed}"

    def attach_queue(self, queue):
        self.queue = queue

    @abstractmethod
    def copy(self, seed: int, quiet: bool):
        """Make a copy of the experiment so multiple copies of the experiment can be run in parallel.

        Args:
            seed (int): random seed to set in numpy when selecting experiment arg values.
            quiet (bool): whether to suppress log printouts during the experiment.

        Returns:
            BaseExperiment: an independent copy of this experiment.
        """
        pass

    def _generate_params(self) -> List[Union[int, float]]:

        np.random.seed(self._seed)
        args = []
        for rng in self._ranges:
            # Is it a constant value? If so, just add it to the args.
            if isinstance(rng, (int, float)):
                args.append(rng)
            else:
                arg = int(np.random.randint(rng[0], rng[1] + 1))
                args.append(arg)

        return args

    @abstractmethod
    def _init_result(self) -> BaseResult:
        """Initialise a result object for this experiment.

        Notes:
            If you're logging more stuff please subclass ExperimentResult and initialise it in this
            method's implementation.

        Returns:
            BaseResult: the result object filled with initial values.
        """
        return BaseResult()

    def run(self) -> None:
        """Run the experiment thread.

        """
        args = self._generate_params()

        self._return.args = args
        self._return.start = dt.datetime.utcnow()

        # noinspection PyBroadException
        # ^ That's sort of the point...
        try:
            # Run the experiment's core logic
            # You should log other aspects of the experiment inside this method's implementation
            self._job(args)
            self._return.end = dt.datetime.utcnow()
        except Exception:
            # If there's an exception, catch it and log its content.
            self._return.end = dt.datetime.utcnow()
            self._return.errored = True
            self._return.error_message = ''.join(traceback.format_exception(*sys.exc_info()))
        self.queue.put(self._return.to_dict())

    @abstractmethod
    def _job(self, args: List[Union[int, float]]) -> None:
        """Internal method that runs the experiment. Can contain anything you want to run and log to the result object
        at self._return.

        Args:
            args (List[Union[int, float]]): argument values to use in the experiment.

        """
        # modify the _return attribute
        pass

    def join(self, timeout: Optional[float] = None, force: Optional[bool] = False) -> None:
        """Wait until the experiment (process) terminates. This can be forced by passing in force=True.

        Args:
            timeout (Optional[int]): floating point number specifying a timeout for the experiment in seconds.
            force (Optional[bool]): whether to force

        """
        self._force_stop = force
        self._return.force_stopped = force
        ForkProcess.join(self, timeout)

    def should_stop(self):
        """This method can be used as a callback to check for cancellation inside the _job method and whatever it
        might call.

        Returns:
            bool: whether to force stop the experiment.
        """
        return self._force_stop
