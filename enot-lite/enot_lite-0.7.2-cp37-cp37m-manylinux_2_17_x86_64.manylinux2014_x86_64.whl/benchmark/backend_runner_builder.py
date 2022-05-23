from typing import Any
from typing import Dict
from typing import Optional
from typing import Set
from typing import Type

from enot_lite.backend import BackendFactory
from enot_lite.benchmark.backend_runner import BackendRunner
from enot_lite.benchmark.backend_runner import EnotBackendRunner
from enot_lite.benchmark.backend_runner import TorchCpuRunner
from enot_lite.benchmark.backend_runner import TorchCudaRunner
from enot_lite.type import BackendType
from enot_lite.type import ModelType

__all__ = [
    'OrtCpuBackendRunnerBuilder',
    'OrtOpenvinoBackendRunnerBuilder',
    'OpenvinoBackendRunnerBuilder',
    'OrtCudaBackendRunnerBuilder',
    'OrtTensorrtBackendRunnerBuilder',
    'OrtTensorrtFp16BackendRunnerBuilder',
    'TensorrtBackendRunnerBuilder',
    'TensorrtFp16BackendRunnerBuilder',
    'TorchCpuBackendRunnerBuilder',
    'TorchCudaBackendRunnerBuilder',
]


class CommonEnotBackendRunnerBuilder:
    def __init__(self, backend_type: BackendType, kwargs_key_filter: Optional[Set[str]] = None):
        self._backend_type = backend_type
        self._kwargs_key_filter = kwargs_key_filter

    def __call__(
            self,
            onnx_model,
            onnx_input: Dict[str, Any],
            model_type: ModelType,
            enot_backend_runner: Type[EnotBackendRunner],
            **kwargs,
    ) -> BackendRunner:
        if self._kwargs_key_filter is not None:
            kwargs = {
                key: kwargs[key]
                for key in self._kwargs_key_filter
                if key in kwargs
            }

        backend = BackendFactory().create(
            model=onnx_model,
            backend_type=self._backend_type,
            model_type=model_type,
            input_example=onnx_input,
            **kwargs,
        )
        return enot_backend_runner(backend, onnx_input)


class OrtCpuBackendRunnerBuilder(CommonEnotBackendRunnerBuilder):  # pylint: disable=missing-class-docstring
    def __init__(self):
        kwargs_key_filter = {'inter_op_num_threads', 'intra_op_num_threads'}
        super().__init__(BackendType.ORT_CPU, kwargs_key_filter=kwargs_key_filter)


class OrtOpenvinoBackendRunnerBuilder(CommonEnotBackendRunnerBuilder):  # pylint: disable=missing-class-docstring
    def __init__(self):
        kwargs_key_filter = {'inter_op_num_threads', 'intra_op_num_threads', 'openvino_num_threads'}
        super().__init__(BackendType.ORT_OPENVINO, kwargs_key_filter=kwargs_key_filter)


class OpenvinoBackendRunnerBuilder(CommonEnotBackendRunnerBuilder):  # pylint: disable=missing-class-docstring
    def __init__(self):
        super().__init__(BackendType.OPENVINO, kwargs_key_filter=set())


class OrtCudaBackendRunnerBuilder(CommonEnotBackendRunnerBuilder):  # pylint: disable=missing-class-docstring
    def __init__(self):
        super().__init__(BackendType.ORT_CUDA, kwargs_key_filter=set())


class OrtTensorrtBackendRunnerBuilder(CommonEnotBackendRunnerBuilder):  # pylint: disable=missing-class-docstring
    def __init__(self):
        super().__init__(BackendType.ORT_TENSORRT, kwargs_key_filter=set())


class OrtTensorrtFp16BackendRunnerBuilder(CommonEnotBackendRunnerBuilder):  # pylint: disable=missing-class-docstring
    def __init__(self):
        super().__init__(BackendType.ORT_TENSORRT_FP16, kwargs_key_filter=set())


class TensorrtBackendRunnerBuilder(CommonEnotBackendRunnerBuilder):  # pylint: disable=missing-class-docstring
    def __init__(self):
        super().__init__(BackendType.TENSORRT, kwargs_key_filter=set())


class TensorrtFp16BackendRunnerBuilder(CommonEnotBackendRunnerBuilder):  # pylint: disable=missing-class-docstring
    def __init__(self):
        super().__init__(BackendType.TENSORRT_FP16, kwargs_key_filter=set())


class TorchCpuBackendRunnerBuilder:  # pylint: disable=missing-class-docstring
    def __call__(
            self,
            torch_model,
            torch_input,
            torch_cpu_runner: Type[TorchCpuRunner],
            **_ignored,
    ) -> BackendRunner:
        return torch_cpu_runner(torch_model=torch_model, torch_input=torch_input)


class TorchCudaBackendRunnerBuilder:  # pylint: disable=missing-class-docstring
    def __call__(
            self,
            torch_model,
            torch_input,
            torch_cuda_runner: Type[TorchCudaRunner],
            **_ignored,
    ) -> BackendRunner:
        return torch_cuda_runner(torch_model=torch_model, torch_input=torch_input)
