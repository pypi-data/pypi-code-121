from typing import Callable
from typing import Dict

from enot_lite.benchmark.backend_runner import BackendRunner
from enot_lite.benchmark.backend_runner_builder import OpenvinoBackendRunnerBuilder
from enot_lite.benchmark.backend_runner_builder import OrtCpuBackendRunnerBuilder
from enot_lite.benchmark.backend_runner_builder import OrtCudaBackendRunnerBuilder
from enot_lite.benchmark.backend_runner_builder import OrtOpenvinoBackendRunnerBuilder
from enot_lite.benchmark.backend_runner_builder import OrtTensorrtBackendRunnerBuilder
from enot_lite.benchmark.backend_runner_builder import OrtTensorrtFp16BackendRunnerBuilder
from enot_lite.benchmark.backend_runner_builder import TensorrtBackendRunnerBuilder
from enot_lite.benchmark.backend_runner_builder import TensorrtFp16BackendRunnerBuilder
from enot_lite.benchmark.backend_runner_builder import TorchCpuBackendRunnerBuilder
from enot_lite.benchmark.backend_runner_builder import TorchCudaBackendRunnerBuilder
from enot_lite.type import BackendType

__all__ = [
    'BackendRunnerFactory',
]


class BackendRunnerFactory:
    """
    Produces :class:`~enot_lite.benchmark.backend_runner.BackendRunner` objects.

    To extend :class:`~enot_lite.benchmark.benchmark.Benchmark` for your own backend, create builder
    and register it with the help of :func:`register_builder`.
    Builder is a callable object that wraps your backend, model and input data into
    :class:`~enot_lite.benchmark.backend_runner.BackendRunner` object.
    You can see how we wrapped our and PyTorch backends in :mod:`enot_lite.benchmark.backend_runner_builder`
    module.

    Note, BackendRunnerFactory is a singleton, to get an instance call constructor: ``BackendRunnerFactory()``.
    """

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(BackendRunnerFactory, cls).__new__(cls)

            # Register new builders here.
            cls.__instance._builders = {}
            # Register CPU backend builders.
            cls.__instance.register_builder(BackendType.ORT_CPU, OrtCpuBackendRunnerBuilder)
            cls.__instance.register_builder(BackendType.ORT_OPENVINO, OrtOpenvinoBackendRunnerBuilder)
            cls.__instance.register_builder(BackendType.OPENVINO, OpenvinoBackendRunnerBuilder)

            # Register CUDA backend builders.
            cls.__instance.register_builder(BackendType.ORT_CUDA, OrtCudaBackendRunnerBuilder)
            cls.__instance.register_builder(BackendType.ORT_TENSORRT, OrtTensorrtBackendRunnerBuilder)
            cls.__instance.register_builder(BackendType.ORT_TENSORRT_FP16, OrtTensorrtFp16BackendRunnerBuilder)
            cls.__instance.register_builder(BackendType.TENSORRT, TensorrtBackendRunnerBuilder)
            cls.__instance.register_builder(BackendType.TENSORRT_FP16, TensorrtFp16BackendRunnerBuilder)

            # Register Torch backend builders.
            cls.__instance.register_builder(BackendType.TORCH_CPU, TorchCpuBackendRunnerBuilder)
            cls.__instance.register_builder(BackendType.TORCH_CUDA, TorchCudaBackendRunnerBuilder)

        return cls.__instance

    def __init__(self):
        self._builders: Dict[BackendType, Callable]  # For static type checking.

    def register_builder(self, backend_type: BackendType, builder: Callable) -> None:
        """
        Registers new :class:`~enot_lite.benchmark.backend_runner.BackendRunner` builder
        for backend with ``backend_type``.

        Parameters
        ----------
        backend_type : BackendType
            The type of the backend for which new builder will be registered.
        builder : Callable
            Builder that wraps backend, model and input data into
            :class:`~enot_lite.benchmark.backend_runner.BackendRunner` object.

        """
        self._builders[backend_type] = builder

    def create(self, backend_type: BackendType, **kwargs) -> BackendRunner:
        """
        Creates new :class:`~enot_lite.benchmark.backend_runner.BackendRunner` object
        by using registred builder for ``backend_type``.

        Parameters
        ----------
        backend_type : BackendType
            The type of the backend which factory should wrap and produce.
        **kwargs
            Arbitrary keyword arguments that will be passed to particular builder.
            This arguments should contain all information for successful object construction.
            :class:`~enot_lite.benchmark.benchmark.Benchmark` forms and passes
            these arguments to :class:`~enot_lite.benchmark.backend_runner_factory.BackendRunnerFactory`.

        Returns
        -------
        BackendRunner

        """
        builder = self._builders.get(backend_type)
        if not builder:
            raise ValueError(f'Got unregistered backend type {backend_type}')
        return builder()(**kwargs)
