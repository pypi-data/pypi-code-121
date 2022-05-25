import inspect
import numpy as np
import math
import os
import warnings
import traceback as tb
from time import time
from typing import Callable, Optional, Tuple, Union, Collection

from multiprocessing import get_context, cpu_count
import logging
from itertools import repeat
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from tempfile import gettempdir
import tracemalloc

from .decorators import classproperty

logger = logging.getLogger(__name__)

dask_client = None
"""Dask client must be global. Only used if using Dask or Dask-Kubernetes"""


def to_bool(s: str):
    s = s.replace(" ", "").split("#")[0]
    if s.lower() == "false" or s == "":
        return False
    if s.lower() == "true":
        return True
    raise ValueError(f"Can not convert string {s} to bool")


class _Job:
    def __init__(self, results, client, method_name, starttime, batched):
        self.futures = results
        self.client = client
        self.method_name = method_name
        self.starttime = starttime
        self.endtime = None
        self.runtime = None
        self.times = []
        self.peak_mem_allocations = []
        self.results = []
        self.batched = batched

    def gather(self):
        if self.client is not None:
            self.results = self.client.gather(self.futures)
        else:
            self.results = self.futures
        self.endtime = time()
        self.runtime = self.endtime - self.starttime
        self.results, self.times, self.peak_mem_allocations = zip(*self.results)
        if self.batched:
            self.results = [item for subl in self.results for item in subl]
            self.times = [item for subl in self.times for item in subl]
            self.peak_mem_allocations = [item / 1e9 for subl in self.peak_mem_allocations for item in subl]
        else:
            self.peak_mem_allocations = [item / 1e9 for item in self.peak_mem_allocations]


class Engine:
    """Wrapper around several ways of doing parallel runs in Python

    Can be a 'serial' engine, which does not do parallel runs, can use concurrent.futures with processes or threads,
    can use Dask, Dask-Kubernetes and MPI.

    Attributes
    ----------
    kind: str
        Can be any of "serial", "mpi", "dask", "multiproc", "concurrent", "kubernetes", "multithread".
        "concurrent" and "multiproc" are synonymes.
    batch_multiplier: Optional[int]
         Number of items to pass to each process if doing batched multiprocessing
    docker_image: Optional[str]
        If using Dask-Kubernetes, docker image of the main program
    context: str
        Multiprocessing context. Can be "spawn" (default) or "fork", use "spawn" if your paralleled processes use
        numpy.
    processes_or_threads: str
        Can be "processes" (default) or "threads". Only relevent if `adparallelengine.adparallelengine.Engine.kind`
        is 'Dask'.
    print_percent: int
        If 'verbose' is True, processes matching 'print_percent' percent will say it when they finished. If None,
        processes do not say anything (Default value = 10).
    max_workers: Optional[int]
        To limit the number of CPUs to use. If < 1, uses os.cpu_count().
    path_shared: Optional["TransparentPath"]
        To save memory, one can decide to write heavy pd.Dataframe, pd.Series or np.ndarray to disk and make
        processes read them by sharing a path instead of the heavy object itself. 'path_shared' tells the engine
        where those shared objects should be written. Defaults to "tempfile.gettempdir() / adparallelengine_temp".
    k8s_spec_dict: Optional[dict]
        If using Dask-Kubernetes, the dictionary of specs to give to KubeCluster.
    verbose: bool
    times: dict
        Dictionnary of 'method_name': [run times]
    peak_mem_allocations: dict
        Dictionnary of 'method_name': [Max memory usage]
    """

    kinds = ["serial", "mpi", "dask", "multiproc", "concurrent", "kubernetes", "multithread"]
    _MPI, _MPIPOOLEXECUTOR = None, None
    _DASK_CLIENT = None
    _K8S_CLUSTER = None
    _PANDAS = None
    _PATH = None
    TRACEMALLOC = True

    # noinspection PyMethodParameters
    @classproperty
    def MPI(cls):
        if cls._MPI is None:
            cls.import_mpi()
        return cls._MPI

    # noinspection PyMethodParameters
    @classproperty
    def MPIPOOLEXECUTOR(cls):
        if cls._MPIPOOLEXECUTOR is None:
            cls.import_mpi()
        return cls._MPIPOOLEXECUTOR

    # noinspection PyMethodParameters
    @classproperty
    def PANDAS(cls):
        if cls._PANDAS is None:
            cls.import_pandas()
        return cls._PANDAS

    # noinspection PyMethodParameters
    @classproperty
    def PATH(cls):
        if cls._PATH is None:
            cls.import_transparentpath()
        return cls._PATH

    # noinspection PyMethodParameters
    @classproperty
    def DASK_CLIENT(cls):
        if cls._DASK_CLIENT is None:
            cls.import_dask()
        return cls._DASK_CLIENT

    # noinspection PyMethodParameters
    @classproperty
    def K8S_CLUSTER(cls):
        if cls._K8S_CLUSTER is None:
            cls.import_k8s()
        return cls._K8S_CLUSTER

    @classmethod
    def import_mpi(cls):
        try:
            import mpi4py.rc

            mpi4py.rc.threads = False
            from mpi4py import MPI
            from mpi4py.futures import MPIPoolExecutor

            cls._MPI, cls._MPIPOOLEXECUTOR = MPI, MPIPoolExecutor
        except ImportError as e:
            raise ImportError(
                "AdparallelEngine can't import mpi4py. You can do it by running `pip install adparallelengine[mpi]`."
                " Make sure also that MPI is installed on your computer (OpenMPI should work)\n\n"
                f"Original error was {str(e)}"
            )

    @classmethod
    def import_pandas(cls):
        try:
            import pandas as pd

            cls._PANDAS = pd
        except ImportError as e:
            raise ImportError(
                "AdparallelEngine can't import pandas. You can do it by running"
                f" `pip install adparallelengine[support_shared]`.\n\nOriginal error was {str(e)}"
            )

    @classmethod
    def import_transparentpath(cls):
        try:
            # noinspection PyUnresolvedReferences
            from transparentpath import Path

            cls._PATH = Path
        except ImportError as e:
            raise ImportError(
                "AdparallelEngine can't import transparentpath. You can do it by running"
                f"`pip install adparallelengine[support_shared]` .\n\nOriginal error was {str(e)}"
            )

    @classmethod
    def import_dask(cls):
        try:
            # noinspection PyUnresolvedReferences
            from dask.distributed import Client

            cls._DASK_CLIENT = Client
        except ImportError as e:
            raise ImportError(
                "AdparallelEngine can't import dask. You can do it by running `pip install adparallelengine[dask]`."
                f"\n\nOriginal error was {str(e)}"
            )

    @classmethod
    def import_k8s(cls):
        try:
            # noinspection PyUnresolvedReferences
            from dask_kubernetes import KubeCluster

            cls._K8S_CLUSTER = KubeCluster
        except ImportError as e:
            raise ImportError(
                "AdparallelEngine can not import dask_kubernetes. You can do it by running"
                f" `pip install adparallelengine[k8s]`.\n\nOriginal error was {str(e)}"
            )

    def __init__(
        self,
        kind: str,
        batch_multiplier: Optional[int] = None,
        docker_image: Optional[str] = None,
        context: str = "spawn",
        processes_or_threads: str = "processes",
        print_percent: int = 10,
        max_workers: Optional[int] = None,
        path_shared: Optional["TransparentPath"] = None,
        k8s_spec_dict: Optional[dict] = None,
        verbose: bool = True,
    ):
        """

        Parameters
        ----------
        kind: str
            Can be any of "serial", "mpi", "dask", "multiproc", "concurrent", "kubernetes", "multithread".
            "concurrent" and "multiproc" are synonymes.
        batch_multiplier: Optional[int]
             Number of items to pass to each process if doing batched multiprocessing
        docker_image: Optional[str]
            If using Dask-Kubernetes, docker image of the main program
        context: str
            Multiprocessing context. Can be "spawn" (default) or "fork", use "spawn" if your paralleled processes use
            numpy.
        processes_or_threads: str
            Can be "processes" (default) or "threads". Only relevent if `adparallelengine.adparallelengine.Engine.kind`
            is 'Dask'.
        print_percent: int
            If 'verbose' is True, processes matching 'print_percent' percent will say it when they finished. If None,
            processes do not say anything (Default value = 10).
        max_workers: Optional[int]
            To limit the number of CPUs to use. If < 1, uses os.cpu_count().
        path_shared: Optional["TransparentPath"]
            To save memory, one can decide to write heavy pd.Dataframe, pd.Series or np.ndarray to disk and make
            processes read them by sharing a path instead of the heavy object itself. 'path_shared' tells the engine
            where those shared objects should be written. Defaults to "tempfile.gettempdir() / adparallelengine_temp".
        k8s_spec_dict: Optional[dict]
            If using Dask-Kubernetes, the dictionary of specs to give to KubeCluster.
        verbose: bool
        """
        self._kind = None
        self._batch_multiplier = None
        self.docker_image = docker_image
        """If using Dask-Kubernetes, docker image of the main program"""
        self._context = None
        self._processes_or_threads = None
        self._print_percent = None
        self._max_workers = None

        self.kind = kind
        self.batch_multiplier = batch_multiplier
        self.context = context
        self.processes_or_workers = processes_or_threads
        self.print_percent = print_percent if verbose is True else None
        self._prev_print_percent = self.print_percent
        self.max_workers = max_workers
        self._verbose = verbose

        self.__new = True
        self.times = {}
        """Dictionnary of run times of the various methods that have been ran through this engine"""
        self.peak_mem_allocations = {}
        """Dictionnary of maximum memory usage of the various methods that have been ran through this engine"""

        self.path_shared = None
        """Where the shared objects should be written"""
        if path_shared is not None:
            self.path_shared = path_shared

        self.k8s_spec_dict = k8s_spec_dict
        """If using Dask-Kubernetes, the dictionary of specs to give to KubeCluster."""

    def clean_shared(self):
        """Removes 'path_shared' directory if exists"""
        if self.path_shared is not None:
            self.path_shared.rm(absent="ignore", ignore_kind=True)
            self.path_shared.mkdir()

    def close(self):
        """If using Dask or Dask-Kubernetes, closes the client. Also, removes 'path_shared' directory if exists"""
        if self.client is not None:
            self.client.close()

        self.clean_shared()

    @property
    def kind(self):
        """Can be "serial", "mpi", "dask", "multiproc", "concurrent", "kubernetes", "multithread" """
        return self._kind

    @kind.setter
    def kind(self, value):
        if value not in Engine.kinds:
            raise ValueError(f"Unknown engine kind {value}")
        self._kind = value

    @property
    def batch_multiplier(self):
        """Number of items to pass to each process if doing batched multiprocessing"""
        return self._kind

    @batch_multiplier.setter
    def batch_multiplier(self, value):
        if value is not None and not isinstance(value, int):
            raise TypeError("Argument 'batch_multiplier' must be None or an integer")
        self._batch_multiplier = value

    @property
    def context(self):
        """Can be "spawn" or "fork" """
        return self._context

    @context.setter
    def context(self, value):
        if value != "spawn" and value != "fork":
            raise ValueError(f"Invalid value '{value}' for 'context'. Can be 'spawn' or 'fork'")
        self._context = value

    @property
    def print_percent(self):
        """Which processes should print when they are done"""
        return self._print_percent

    @print_percent.setter
    def print_percent(self, value):
        if value is None:
            self._print_percent = value
            return
        if not isinstance(value, int):
            raise TypeError(
                f"Invalid type '{type(value)}' for 'print_percent'. Must be an integer between 1 and 100, or None."
            )
        if value > 100 or value < 1:
            raise ValueError(
                f"Invalid value '{value}' for 'print_percent'. Must be an integer between 1 and 100, or None"
            )
        self._print_percent = value

    @property
    def verbose(self):
        return self._verbose

    @verbose.setter
    def verbose(self, value):
        if value is False:
            self._prev_print_percent = self._print_percent
            self._print_percent = None
            self._verbose = False
        elif value is True:
            if self._print_percent is None:
                self._print_percent = self._prev_print_percent
            self._verbose = True
        else:
            raise ValueError(f"Invalid value '{value}' for 'verbose'. Must be True or False")

    @property
    def max_workers(self):
        """Max number of parallel processes that can run at the same time"""
        return self._max_workers

    @max_workers.setter
    def max_workers(self, value):
        if value is None:
            self._max_workers = value
            return
        if not isinstance(value, int):
            raise TypeError(
                f"Invalid type '{type(value)}' for 'max_workers'. Must be an integer greater or equal to 1, or None."
            )
        if value < 1:
            value = None
        self._max_workers = value

    @property
    def processes_or_workers(self):
        """If using Dask, whether processes or threds should be used"""
        return self._processes_or_threads

    @processes_or_workers.setter
    def processes_or_workers(self, value):
        if self.kind == "multithread":
            self._processes_or_threads = "threads"
            return
        if self.kind == "multiproc":
            self._processes_or_threads = "processes"
            return
        if value == "process":
            value = "processes"
        elif value == "thread":
            value = "threads"
        if value != "processes" and value != "threads":
            raise ValueError(f"Invalid value '{value}' for 'process_or_worker'. Can be 'processes' or 'workers'")
        self._processes_or_threads = value

    @property
    def is_parallel(self) -> bool:
        """True if `adparallelengine.adparallelengine.Engine.kind` is anything but 'serial'"""
        return self._kind != "serial"

    @property
    def client(self) -> Union[None, "Client"]:
        """Dask client, if using Dask or Dask-Kubernetes"""
        return dask_client

    def _make_counter(self, collection, method_name):
        """Determines which processes should say they are done based on
        `adparallelengine.adparallelengine.Engine.print_percent`"""
        if self._print_percent is None:
            return {}
        nitems = len(collection)
        dt = int(nitems / self._print_percent)
        if nitems < self._print_percent:
            dt = 1
        indexes_to_print = {
            i: f"{method_name} : {i}/{nitems}, {round(100 * i / nitems, 2)}%" for i in list(range(dt, nitems + 1, dt))
        }
        return indexes_to_print

    def _treat_serial(self, collection, method, kwargs) -> list:
        """Launches the method in a serial run"""
        if self.verbose is True:
            logger.info("Computation is not parallel")
        t = time()
        results = []
        for e in collection:
            results.append(self._pre_launch(e, method, False, kwargs))

        return self._finish_job(
            _Job(results=results, client=None, method_name=method.__name__, starttime=t, batched=False)
        )

    def _treat_dask(self, collection, method, batched, kwargs) -> list:
        """Launches the method in a dask run"""
        t = time()
        results = self.client.map(self._pre_launch, collection, method=method, batched=batched, kwargs=kwargs)

        return self._finish_job(
            _Job(results=results, client=self.client, method_name=method.__name__, starttime=t, batched=batched)
        )

    def _treat_mpi(self, max_workers, collection, method, batched, kwargs) -> list:
        """Launches the method in a MPI run"""
        if self.verbose is True:
            logger.info(f"Using at most {max_workers} mpi processes")
        t = time()

        # noinspection PyCallingNonCallable
        with Engine.MPIPOOLEXECUTOR(max_workers=max_workers) as executor:
            results = list(executor.map(self._pre_launch, collection, repeat(method), repeat(batched), repeat(kwargs)))

        return self._finish_job(
            _Job(results=results, client=None, method_name=method.__name__, starttime=t, batched=batched)
        )

    def _treat_concurrent_or_threads(self, max_workers, collection, method, batched, kwargs) -> list:
        """Launches the method in a multiprocess or multithread run"""
        t = time()

        if self._processes_or_threads == "processes":
            if self.verbose is True:
                logger.info(f"Using at most {max_workers} processes")
            with ProcessPoolExecutor(max_workers=max_workers, mp_context=get_context(self._context)) as executor:
                results = list(
                    executor.map(self._pre_launch, collection, repeat(method), repeat(batched), repeat(kwargs))
                )
        else:
            # No max cpus in using threads
            if self.verbose is True:
                logger.info(f"Using at most {len(collection)} threads")
            with ThreadPoolExecutor(max_workers=len(collection)) as executor:
                results = list(
                    executor.map(self._pre_launch, collection, repeat(method), repeat(batched), repeat(kwargs))
                )

        return self._finish_job(
            _Job(results=results, client=None, method_name=method.__name__, starttime=t, batched=batched)
        )

    def _finish_job(self, job: _Job) -> list:
        """Gathers the job results and some time and memory statistics"""
        job.gather()
        name = job.method_name
        i = 1
        while f"{name}_times" in self.times:
            i += 1
            name = f"{job.method_name}_{i}"
        self.times[f"{name}_times"] = job.times
        self.times[f"{name}_total_time"] = [job.runtime]
        self.peak_mem_allocations[f"{name}_mem"] = job.peak_mem_allocations
        return job.results

    def _init_dask(self, max_workers):
        """Creates the Dask or KubeCluster Client"""
        Engine.import_dask()
        global dask_client
        if self._kind == "dask":
            if self.__new:
                if self._processes_or_threads == "processes":
                    dask_client = Engine.DASK_CLIENT(n_workers=max_workers, threads_per_worker=1)
                else:
                    dask_client = Engine.DASK_CLIENT(n_workers=1, threads_per_worker=max_workers)
                if self.verbose is True:
                    logger.info(
                        f"Using dask with {max_workers} {self._processes_or_threads}:"
                        f" visit {self.client.dashboard_link} to monitor progression."
                    )
                self.__new = False

            current_workers = len(self.client.scheduler_info()["workers"])
            if current_workers < max_workers:
                if self.verbose is True:
                    logger.warning(
                        f"Current Dask client has {current_workers} workers, but {max_workers}"
                        " can be used. Creating a new client."
                    )
                self.client.close()
                if self._processes_or_threads == "processes":
                    dask_client = Engine.DASK_CLIENT(n_workers=max_workers, threads_per_worker=1)
                else:
                    dask_client = Engine.DASK_CLIENT(n_workers=max_workers)
        else:
            Engine.import_k8s()
            if self.verbose is True:
                logger.info("Using kubernetes cluster")
            if self.__new:
                self.docker_image = f"{os.environ['ADLEARN_DOCKER_IMAGE']}:{os.environ['ADLEARN_TAG']}"
                cluster = Engine.K8S_CLUSTER.from_dict(self.k8s_spec_dict)
                cluster.adapt(minimum=1, maximum=int(os.getenv("ADLEARN_DASK_KUBE_MAX_PODS", "50")))
                dask_client = Engine.DASK_CLIENT(cluster)
                if self.verbose is True:
                    logger.info(f"Using dask kubernetes: visit {self.client.dashboard_link} to monitor progression.")
                self.__new = False

    def __call__(self, method: Callable, collection: Collection, **kwargs) -> list:
        """
        kwargs reserved for the engine:
        * batched (bool), to batch the items in 'collection'. Uses
        `adparallelengine.adparallelengine.Engine.batch_multiplier`.
        * gather (bool). If True, expects the method to return a collection, and flattens all the returned collections
        into one.
        * gather_method (Callable). If 'gather' is True, use this method to gather the object intead of a basis list
        comprehension
        * shared (dict). Dictionnary of pd.DataFrame, pd.Series or np.ndarray that should be written to disk and shared
        by giving a path to the method.
        * init_method (dict). Dictionnary of the form {"method": a_method, "kwargs": {...}}. The given method will be
        executed in each process using given "kwargs"

        All other kwargs will be passed to the method

        Parameters
        ----------
        method: Callable
            The method to run
        collection: Collection
            The collection object containing the items to pass to the method
        kwargs

        Returns
        -------
        list
            The list of all indiviudal returns of the given method
        """

        # Make str for progress monitoring

        if self.verbose is True:
            logger.info(f"Iterable has a length of {len(collection)}")
        indexes_to_print = self._make_counter(collection, method.__name__)
        collection = [
            (item, None) if i not in indexes_to_print else (item, indexes_to_print[i])
            for i, item in enumerate(collection)
        ]
        if len(collection) == 0:
            if self.verbose is True:
                logger.info(f"Iterable is empty. Not calling method '{method.__name__}'.")
            return []

        # get 'batch' argument

        batched = False
        if "batched" in kwargs:
            batched = kwargs["batched"]
            del kwargs["batched"]

        gather = False
        gather_method = None
        if "gather" in kwargs:
            gather = kwargs["gather"]
            del kwargs["gather"]
            if "gather_method" in kwargs:
                gather_method = kwargs["gather_method"]
                del kwargs["gather_method"]

        # Get number of workers

        cpu_limit = int(os.getenv("ADLEARN_LIMIT_CPU", "0"))
        if cpu_limit == 1:
            self._kind = "serial"

        max_workers = None
        if self._kind != "mpi" and self.is_parallel:
            max_workers = min(
                cpu_count() - 1 if not cpu_limit > 0 else cpu_limit - 1, max(len(collection), 1)
            )  # -1 because main process will need one
        elif self._kind == "mpi":
            # noinspection PyUnresolvedReferences
            Engine.import_mpi()
            if self.verbose is True:
                logger.info(f"MPI comm world size is {Engine.MPI.COMM_WORLD.size}")
            # noinspection PyUnresolvedReferences
            max_workers = min(Engine.MPI.COMM_WORLD.size, max(len(collection), 1))

        if self._max_workers is not None and max_workers is not None:
            max_workers = min(max_workers, self._max_workers)

        # Dask must be initialised before _manage_shared, for self._client must not be None

        if self._kind == "dask" or self.kind == "kubernetes":
            self._init_dask(max_workers)

        # Manage shared kwargs

        self._manage_shared(kwargs)

        # Check if must and can be batched

        collection, batched = self._manage_batched_before(collection, batched, max_workers)

        # Launch computation depending on engine kind

        if not self.is_parallel or max_workers == 1:
            # noinspection PyTypeChecker
            result = self._treat_serial(collection, method, kwargs)
        elif self._kind == "dask":
            # noinspection PyTypeChecker
            result = self._treat_dask(collection, method, batched, kwargs)
        elif self._kind == "mpi":
            # noinspection PyTypeChecker
            result = self._treat_mpi(max_workers, collection, method, batched, kwargs)
        elif self._kind == "concurrent" or self._kind == "multiproc" or self._kind == "multithread":
            # noinspection PyTypeChecker
            result = self._treat_concurrent_or_threads(max_workers, collection, method, batched, kwargs)
        else:
            raise ValueError(f"Unexpected kind {self._kind}")

        if gather is True:
            if gather_method is not None:
                return gather_method(result)
            else:
                return [e for ee in result for e in ee]
        return result

    def _manage_shared(self, kwargs):
        """If 'shared' was given in the kwargs when using `adparallelengine.adparallelengine.Engine.__call__`, manages
        it.

        * If the engine is not parallel, just ignore the sharing process since it would be useless
        * If using Dask or Dask-Kubernetes, puts each item in kwargs with for value the return of the 'scatter' method
        of the client
        * Else, writes each item on disk in `adparallelengine.adparallelengine.Engine.path_shared` and replaces
        kwargs['shared'][item] by the path to the written data
        """
        if not self.is_parallel:
            if "share" in kwargs:
                for item in kwargs["share"]:
                    kwargs[item] = kwargs["share"][item]
                del kwargs["share"]
        else:
            if "share" in kwargs:
                for item in kwargs["share"]:

                    if not isinstance(
                        kwargs["share"][item],
                        (self.__class__.PANDAS.Series, self.__class__.PANDAS.DataFrame, np.ndarray),
                    ):
                        raise TypeError(
                            "Can only share pd.DataFrames, pd.Series or np.ndarray objects across processes"
                        )

                    thetype = type(kwargs["share"][item])
                    if isinstance(kwargs["share"][item], np.ndarray):
                        kwargs["share"][item] = self.__class__.PANDAS.DataFrame(kwargs["share"][item])

                    if self.path_shared is None:
                        self.path_shared = self.__class__.PATH(gettempdir(), fs="local") / "adparallelengine_temp"
                    if not self.path_shared.isdir():
                        self.path_shared.mkdir()
                    p = (self.path_shared / item).with_suffix(".parquet")
                    if not p.isfile():
                        p.write(kwargs["share"][item])
                    kwargs["share"][item] = (p, thetype)

    def _manage_batched_before(
        self, collection: Collection, batched: Union[int, bool], workers: int
    ) -> Tuple[Collection, bool]:
        """If 'batched' was given to the kwargs when using `adparallelengine.adparallelengine.Engine.__call__`, manages
        it.

        * If the engine is not parallel, just ignore the batching process since it is meaningless
        * If 'batched' is an integer and not a boolean, it is interpreted as the number of batches to use. This number
        is adjusted with respect to the length of the collection, and
        `adparallelengine.adparallelengine.Engine.batch_multiplier` is ignored.
        * If 'batched' is True, then the number of batches if the number of available workers times
        `adparallelengine.adparallelengine.Engine.batch_multiplier`.

        Parameters
        ----------
        collection: Collection
        batched: Union[int, bool]
        workers: int

        Returns
        -------
        Tuple[Collection, bool]
            ('terable, False) unchanged if the number of batches ends up being 1, or if 'batched' is False, else
            returns (np.array_split(collection, nbatches), True)
        """
        if workers is None:
            return collection, False
        use_batch_multiplier = True
        if isinstance(batched, int) and not isinstance(batched, bool):
            chunksize = min(len(collection), abs(batched))
            if chunksize <= 0:
                chunksize = 1
            if chunksize == 1:
                batched = False
            else:
                batched = True
            nbatches = math.ceil(len(collection) / chunksize)
            use_batch_multiplier = False
            if self.verbose is True:
                logger.info(
                    f"Batching {len(collection)} objects into {nbatches}"
                    f" batched of user-specified chunk size~{chunksize}"
                )
        else:
            nbatches = workers
        if batched is True:
            if len(collection) <= nbatches or nbatches == 1:
                return collection, False
            else:
                if self._batch_multiplier is not None and use_batch_multiplier:
                    nbatches = min(len(collection), self._batch_multiplier * nbatches)
                if self.verbose is True:
                    logger.info(f"Batching {len(collection)} objects into {nbatches} batches")
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", category=np.VisibleDeprecationWarning)
                    collection = np.array_split(collection, nbatches)
                return collection, True
        return collection, False

    def _pre_launch(self, elements, method, batched, kwargs):
        """Method passed to the underlying engine (multiproc, dask, mpi...)

        Parameters
        ----------
        elements: Collection
            The collection of batches if dong batch run, or the original collection of elements
        method: Callable
        batched: bool
        kwargs: dict
            If 'share' is present, will replace each kwargs['shared'][item] by the read data.
            If 'init_method' in present, will call it and remove it from kwargs. Then **kwargs is passed to 'method'.
        """
        try:
            if "share" in kwargs:
                for item in kwargs["share"]:

                    in_method = False
                    in_init_method = False
                    if item in dict(inspect.signature(method).parameters):
                        in_method = True
                    if "init_method" in kwargs and item in dict(
                        inspect.signature(kwargs["init_method"]["method"]).parameters
                    ):
                        in_init_method = True
                    if not in_init_method and not in_method:
                        raise ValueError(
                            f"Shared keyword argument {item} is not valid for the given method and init_method"
                        )

                    item_loaded = kwargs["share"][item][0].read()
                    if kwargs["share"][item][1] == self.__class__.PANDAS.Series:
                        item_loaded = item_loaded.iloc[:, 0]
                    elif kwargs["share"][item][1] == np.ndarray:
                        item_loaded = item_loaded.values
                    if in_method:
                        kwargs[item] = item_loaded
                    if in_init_method:
                        if "kwargs" in kwargs["init_method"]:
                            kwargs["init_method"]["kwargs"][item] = item_loaded
                        else:
                            kwargs["init_method"]["kwargs"] = {item: item_loaded}
                del kwargs["share"]

            for item in kwargs:
                if item == "init_method":
                    continue
                in_method = False
                in_init_method = False
                if item in dict(inspect.signature(method).parameters):
                    in_method = True
                if "init_method" in kwargs and item in dict(
                    inspect.signature(kwargs["init_method"]["method"]).parameters
                ):
                    in_init_method = True
                if not in_init_method and not in_method:
                    raise ValueError(f"Keyword argument {item} is not valid for the given method and init_method")
                if in_init_method:
                    if "kwargs" in kwargs["init_method"]:
                        kwargs["init_method"]["kwargs"][item] = kwargs[item]
                    else:
                        kwargs["init_method"]["kwargs"] = {item: kwargs[item]}

            if "init_method" in kwargs:
                if "kwargs" in kwargs["init_method"]:
                    kwargs["init_method"]["method"](**kwargs["init_method"]["kwargs"])
                else:
                    kwargs["init_method"]["method"]()
                del kwargs["init_method"]

            if not batched:
                return _launch(method, elements, kwargs)

            to_ret, times, mems = np.array([_launch(method, element, kwargs) for element in elements]).T

            return to_ret, times, mems
        except Exception as e:
            logger.critical(f"Process caught an error : {''.join(tb.format_exception(None, e, e.__traceback__))}")
            raise e


def _launch(method, element, kwargs):
    """Where the method is actually called on an element of the original collection"""
    element, toprint = element
    t = time()
    if Engine.TRACEMALLOC is True:
        if tracemalloc.is_tracing():
            try:
                tracemalloc.reset_peak()
            except AttributeError:  # Before python3.9, tracemalloc had no "reset_peak" method
                tracemalloc.stop()
                tracemalloc.start()
        else:
            tracemalloc.start()
    to_ret = method(element, **kwargs)
    if toprint is not None:
        logger.info(toprint)
    if Engine.TRACEMALLOC is True:
        mem = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()
    else:
        mem = math.nan
    return to_ret, time() - t, mem
