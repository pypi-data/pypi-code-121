from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import Union

from onnx import ModelProto
from tabulate import tabulate

from enot_lite.benchmark.backend_benchmark import BackendBenchmark
from enot_lite.benchmark.backend_runner import BackendRunner
from enot_lite.benchmark.backend_runner import EnotBackendRunner
from enot_lite.benchmark.backend_runner import TorchCpuRunner
from enot_lite.benchmark.backend_runner import TorchCudaRunner
from enot_lite.benchmark.backend_runner_factory import BackendRunnerFactory
from enot_lite.benchmark.utils import system_info
from enot_lite.type import BackendType
from enot_lite.type import Device
from enot_lite.type import ModelType
from enot_lite.utils.common import normalize_input_example

__all__ = [
    'Benchmark',
]

_CPU_BACKENDS = [  # Corresponds to Device.CPU.
    BackendType.ORT_CPU,
    BackendType.ORT_OPENVINO,
    BackendType.OPENVINO,
    BackendType.TORCH_CPU,
]

_GPU_BACKENDS = [  # Corresponds to Device.GPU.
    BackendType.ORT_CUDA,
    BackendType.ORT_TENSORRT,
    BackendType.ORT_TENSORRT_FP16,
    BackendType.TORCH_CUDA,
]


class Benchmark:
    """
    Open extendable tool for benchmarking inference.

    It supports **ENOT Lite** and PyTorch backends out of the box, but can be extended for your own backends.

    It measures inference time of ONNX models on **ENOT Lite** backends,
    PyTorch native inference time and transforms it to FPS (frame-per-second, the bigger the better) metric.

    All benchmark source code is available in :mod:`~enot_lite.benchmark` module.
    """

    def __init__(
            self,
            batch_size: Optional[int],
            onnx_model: Optional[Union[str, ModelProto]] = None,
            onnx_input: Optional[Any] = None,
            enot_backend_runner: Optional[Type[BackendRunner]] = EnotBackendRunner,
            torch_model: Optional[Any] = None,
            torch_input: Optional[Any] = None,
            torch_cpu_runner: Optional[Type[BackendRunner]] = TorchCpuRunner,
            torch_cuda_runner: Optional[Type[BackendRunner]] = TorchCudaRunner,
            backends: Union[Device, List[Union[Tuple, BackendType]]] = Device.CPU,
            warmup: int = 50,
            repeat: int = 50,
            number: int = 50,
            inter_op_num_threads: Optional[int] = None,
            intra_op_num_threads: Optional[int] = None,
            openvino_num_threads: Optional[int] = None,
            verbose: bool = True,
    ):
        """
        Parameters
        ----------
        batch_size : Optional[int]
            Batch size value.
            This value should equals to ``onnx_input`` and ``torch_input`` batch sizes.
            Pass None if the model input does not contain batch size (for example natural language processing networks),
            in this case ``batch_size`` will be 1.
        onnx_model : str, ModelProto or None
            Path to ONNX model for benchmarking on **ENOT Lite** backends.
            Omit this parameter to skip benchmarking of **ENOT Lite** backends.
        onnx_input : Optional[Any]
            Input for ONNX model.
            If the model has only one input pass input as one value: ``onnx_input=np.random(...)`` for example.
            There are two options for passing the input when model has multiple inputs: as list (or tuple),
            or as mapping (dict), where the keys are input names, values are input tensors.
            Keys correspond to input names, values to input values.
        enot_backend_runner : Optional[Type[BackendRunner]]
            :class:`~enot_lite.benchmark.backend_runner.BackendRunner` subclass that will be used for **ENOT Lite**
            backends.
            Default is :class:`~enot_lite.benchmark.backend_runner.EnotBackendRunner`.
        torch_model : Optional[Any]
            PyTorch model for native benchmarking (torch.nn.Module).
            Omit this parameter to skip benchmarking of PyTorch backends.
        torch_input : Optional[Any]
            Input for PyTorch model.
        torch_cpu_runner : Optional[Type[BackendRunner]]
            :class:`~enot_lite.benchmark.backend_runner.BackendRunner` subclass that will be used for PyTorch backends.
            Default is :class:`~enot_lite.benchmark.backend_runner.TorchCpuRunner`.
        torch_cuda_runner : Optional[Type[BackendRunner]]
            :class:`~enot_lite.benchmark.backend_runner.BackendRunner` subclass that will be used for PyTorch backends.
            Default is :class:`~enot_lite.benchmark.backend_runner.TorchCudaRunner`.
        backends : Union[Device, List[Union[Tuple, BackendType]]]
            Selects backends for benchmarking:
            ``Device.CPU`` - all CPU backends,
            ``Device.GPU`` - all GPU backends,
            Also you can specify backends by type or Tuple, for example:
            ``[BackendType.ORT_CUDA, (BackendType.ORT_TENSORRT, ModelType.YOLO_V5)]``.
            Default is ``Device.CPU``.
        warmup : int
            Number of warmup iterations (see :class:`~enot_lite.benchmark.backend_benchmark.BackendBenchmark`).
            Default is 50.
        repeat : int
            Number of repeat iterations (see :class:`~enot_lite.benchmark.backend_benchmark.BackendBenchmark`).
            Default is 50.
        number : int
            Number of iterations in each ``repeat`` iteration
            (see :class:`~enot_lite.benchmark.backend_benchmark.BackendBenchmark`).
            Default is 50.
        inter_op_num_threads : Optional[int]
            Number of threads used to parallelize the execution of the graph (across nodes).
            Default is None (will be set by backend automatically).
            Affects on CPU backends only.
        intra_op_num_threads : Optional[int]
            Number of threads used to parallelize the execution within nodes.
            Default is None (will be set by backend automatically).
            Affects on CPU backends only.
        openvino_num_threads : Optional[int]
            Lenght of async task queue which is used in OpenVINO backend.
            Increase of this parameter can both improve performance and degrade it.
            Change it last to fine tune performance.
            Default is None (will be set by backend).
            Affects on CPU backends only.
        verbose : bool
            Print status while benchmarking or not. Default is True.

        Examples
        --------
        ResNet-50 benchmarking.

        >>> import numpy as np
        >>> import torch
        >>> from torchvision.models import resnet50
        >>> from enot_lite.benchmark import Benchmark
        >>> from enot_lite.type import BackendType

        Create PyTorch ResNet-50 model.

        >>> resnet50 = resnet50()
        >>> resnet50.cpu()
        >>> resnet50.eval()
        >>> torch_input=torch.ones((8, 3, 224, 224)).cpu()

        Export it to ONNX.

        >>> torch.onnx.export(
        ...     model=resnet50,
        ...     args=torch_input,
        ...     f='resnet50.onnx',
        ...     opset_version=11,
        ...     input_names=['input'],
        >>> )

        Configure :class:`Benchmark`.

        >>> benchmark = Benchmark(
        ...     batch_size=8,
        ...     onnx_model='resnet50.onnx',
        ...     onnx_input={'input': np.ones((8, 3, 224, 224), dtype=np.float32)},
        ...     torch_model=resnet50,
        ...     torch_input=torch_input,
        ...     backends=[BackendType.ORT_CUDA, BackendType.ORT_TENSORRT_FP16],
        >>> )

        Run :class:`Benchmark` and print results.

        >>> benchmark.run()
        >>> benchmark.print_results()

        """
        self._batch_size = batch_size if batch_size is not None else 1

        self._onnx_model = onnx_model
        self._onnx_input = onnx_input
        if self._onnx_model is not None and self._onnx_input is not None:
            self._onnx_input = normalize_input_example(self._onnx_input, self._onnx_model)

        self._torch_model = torch_model
        self._torch_input = torch_input

        if isinstance(backends, Device):
            if backends == Device.CPU:
                self._backends = [self._parse_backend(backend) for backend in _CPU_BACKENDS]
            if backends == Device.GPU:
                self._backends = [self._parse_backend(backend) for backend in _GPU_BACKENDS]
        else:
            self._backends = [self._parse_backend(backend) for backend in backends]

        if self._torch_input is None or self._torch_input is None:
            try:
                self._backends.remove((BackendType.TORCH_CPU, None))
            except ValueError:
                pass
            try:
                self._backends.remove((BackendType.TORCH_CUDA, None))
            except ValueError:
                pass

        self._warmup = warmup
        self._repeat = repeat
        self._number = number
        self._verbose = verbose
        self._results = {}
        self._datetime: Optional[datetime] = None

        self._config = {
            'onnx_model': self._onnx_model,
            'onnx_input': self._onnx_input,
            'torch_model': self._torch_model,
            'torch_input': self._torch_input,

            'enot_backend_runner': enot_backend_runner,
            'torch_cpu_runner': torch_cpu_runner,
            'torch_cuda_runner': torch_cuda_runner,

            'intra_op_num_threads': intra_op_num_threads,
            'inter_op_num_threads': inter_op_num_threads,
            'openvino_num_threads': openvino_num_threads,
        }

    def run(self) -> None:
        """
        Starts benchmarking.

        """
        self._results = {}
        self._datetime = datetime.now()
        backend_benchmark = BackendBenchmark(warmup=self._warmup, repeat=self._repeat, number=self._number)

        for backend in self._backends:
            backend_name = self._backend_name(backend)
            if self._verbose:
                print(f'Benchmarking: {backend_name}...', flush=True, end=' ')

            backend_type, model_type = backend
            try:
                backend = BackendRunnerFactory().create(
                    backend_type=backend_type,
                    model_type=model_type,
                    **self._config,
                )
                mean, stdev = backend_benchmark.benchmark(backend)
                normalized = mean / self._batch_size  # normalize per sample.
                qps = 1000.0 / normalized
                self._results[backend_name] = (qps, normalized, mean, stdev)
                status = 'OK'
            except BaseException as err:  # pylint: disable=broad-except
                self._results[backend_name] = None
                status = f'FAILED ({err.__class__.__name__}={err})'

            if self._verbose:
                print(status)

    @property
    def results(self) -> Dict:
        """
        Benchmarking results.

        Returns
        -------
        Dict
            Keys are backend names, values are tuples with the following structure:
            FPS, normalized time in `ms` per sample, mean time in `ms` per batch, standard deviation in `ms`.
            Value can be None if benchmarking failed.

        """
        return self._results

    def print_results(self) -> None:
        """
        Prints table with benchmarking results and environment information.

        """
        print(tabulate(
            tabular_data=self._system_info().items(),
            tablefmt='orgtbl',
            colalign=('left', 'center'),
        ))
        print('\n')
        print(tabulate(
            tabular_data=[
                (bcnd_name, *metrics) if metrics is not None else (bcnd_name + ' (FAILED)', )
                for bcnd_name, metrics in self._results.items()
            ],
            headers=['backend', 'FPS', 'normalized time per sample (ms)', 'mean time per batch (ms)', 'stdev (ms)'],
            tablefmt='orgtbl',
            colalign=('left', 'center', 'center', 'center', 'center'),
            floatfmt=('', '.1f', '.3f', '.3f', '.3f'),
        ))

    def _system_info(self) -> Dict:
        """
        Collects and returns environment (system) information.

        """
        dt = self._datetime if self._datetime else datetime.now()
        benchmark_info = {
            'Batch size': str(self._batch_size),
            'Warmup': str(self._warmup),
            'Repeat': str(self._repeat),
            'Number': str(self._number),
            'Date': dt.strftime('%d/%m/%Y %H:%M:%S'),
        }
        if self._config['inter_op_num_threads']:
            benchmark_info['inter_op_num_threads'] = str(self._config['inter_op_num_threads'])
        if self._config['intra_op_num_threads']:
            benchmark_info['intra_op_num_threads'] = str(self._config['intra_op_num_threads'])
        if self._config['openvino_num_threads']:
            benchmark_info['openvino_num_threads'] = str(self._config['openvino_num_threads'])
        if isinstance(self._onnx_model, str):
            benchmark_info['ONNX Model'] = self._onnx_model
        if isinstance(self._onnx_model, ModelProto):
            benchmark_info['ONNX Model'] = f'ModelProto ({self._onnx_model.graph.name})'
        if self._onnx_input is not None and len(self._onnx_input) == 1:
            try:
                benchmark_info['Input shape'] = [*self._onnx_input.values()][0].shape
            except:
                pass

        return {**benchmark_info, **system_info()}

    @staticmethod
    def _parse_backend(backend: Union[Tuple, BackendType]) -> Tuple[BackendType, Optional[ModelType]]:
        if isinstance(backend, BackendType):
            return (backend, None)

        # Backend is a tuple.
        if len(backend) not in range(1, 3):
            raise ValueError('Expected length of {backend} should be in range [1, 2], got {len(backend)}')

        backend_type = next(filter(lambda param: isinstance(param, BackendType), backend), None)
        model_type = next(filter(lambda param: isinstance(param, ModelType), backend), None)

        if backend_type is None:
            raise ValueError('No backend type found for {backend}')

        return (backend_type, model_type)


    @staticmethod
    def _backend_name(backend: Tuple[BackendType, Optional[ModelType]]) -> str:
        backend_type, model_type = backend
        name = backend_type.name
        if model_type:
            name += ' ' + model_type.name
        return name
