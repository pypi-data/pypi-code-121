import abc
from typing import Any
from typing import Dict
from typing import Iterable

try:
    import torch
except ModuleNotFoundError:
    pass

from enot_lite import backend

__all__ = [
    'BackendRunner',
    'EnotBackendRunner',
    'TorchCpuRunner',
    'TorchCudaRunner',
]


class BackendRunner(abc.ABC):
    """
    Interface that is used by :class:`~enot_lite.benchmark.backend_benchmark.BackendBenchmark`.
    Only one method needs to be implemented: :func:`~BackendRunner.run`, which wraps inference call.
    """

    @abc.abstractmethod
    def run(self) -> None:
        """Wrapped inference call."""
        pass


class EnotBackendRunner(BackendRunner):
    """
    Common implementation of :class:`BackendRunner` interface for **ENOT Lite** backends.

    Do not override :func:`run` method, implement :func:`backend_run` instead.
    """

    def __init__(self, backend_instance: backend.Backend, onnx_input: Dict[str, Any]):
        """
        Parameters
        ----------
        backend_instance : backend.Backend
            **ENOT Lite** backend with embedded model.
        onnx_input : Dict[str, Any]
            Input for model inference (model is already wrapped in ``backend_instance``).

        """
        self._backend_instance: backend.Backend = backend_instance
        self._input = onnx_input

    def run(self) -> None:
        self.backend_run(self._backend_instance, self._input)

    def backend_run(self, backend: backend.Backend, onnx_input: Dict[str, Any]) -> Any:
        """
        Common implementation of how to infer ONNX model.

        Parameters
        ----------
        backend : backend.Backend
            **ENOT Lite** backend with embedded model.
        onnx_input : Dict[str, Any]
            Model input.

        Returns
        -------
        Any
            Prediction.

        """
        return backend.run(onnx_input)


class TorchCpuRunner(BackendRunner):
    """
    Common implementation of :class:`BackendRunner` interface for PyTorch on CPU.

    Do not override :func:`run` method, implement :func:`torch_run` instead.
    """

    def __init__(self, torch_model, torch_input: Any):
        """
        Parameters
        ----------
        torch_model : torch.nn.Module
            PyTorch model.
        torch_input : torch.Tensor or something suitable for ``torch_model``
            Input for ``torch_model``.

        """
        self._model = torch_model
        self._input = torch_input

    def run(self) -> None:
        with torch.no_grad():
            self.torch_run(self._model, self._input)

    def torch_run(self, model, inputs: Any) -> Any:
        """
        Common implementation of how to infer PyTorch model.

        Parameters
        ----------
        model : torch.nn.Module
            PyTorch model.
        inputs : Any
            Input for ``model``.

        Returns
        -------
        Any
            Prediction.

        """
        return model(inputs)


class TorchCudaRunner(BackendRunner):
    """
    Common implementation of :class:`BackendRunner` interface for PyTorch on CUDA.

    Do not override :func:`run` method, implement :func:`torch_run`, :func:`torch_input_to_cuda`,
    :func:`torch_output_to_cpu` to extend this class.

    Why are we explicitly transfering data from CPU to CUDA and from CUDA to CPU?

    In real-world application, data (images, sentences, etc) is on the CPU device
    (in RAM, hard drive or CPU-caches), in the moment when you started inference,
    input data should be transferred through north and south bridges on your motherboard to CUDA device (GPU)
    to perform computations more effectively and decrease model inference latency.
    When prediction is computed, the output data should be transferred back from CUDA to CPU
    for further processing.
    Sometimes the data transfer time can be comparable to the inference time, so it must be taken into account
    in the benchmarking.

    The data transfer described above is done automatically for **ENOT Lite** backends.
    For PyTorch on CUDA we explicitly measure the data transfer time from CPU to CUDA and
    back from CUDA to CPU to obtain consistent results.
    """

    def __init__(self, torch_model, torch_input):
        """
        Parameters
        ----------
        torch_model : torch.nn.Module
            PyTorch model.
        torch_input : torch.Tensor or something suitable for ``torch_model``
            Input for ``torch_model``.

        """
        self._model = torch_model
        self._input = torch_input
        self._model.to('cuda:0')
        self._model.eval()

    def run(self) -> None:
        with torch.no_grad():
            input_cuda = self.torch_input_to_cuda(self._input)  # Transfer input from CPU to CUDA.
            output_cuda = self.torch_run(self._model, input_cuda)  # Inference.
            self.torch_output_to_cpu(output_cuda)  # Transfer prediction from CUDA to CPU.

    def torch_run(self, model, inputs: Any) -> Any:
        """
        Common implementation of how to infer PyTorch model.

        Parameters
        ----------
        model : torch.nn.Module
            PyTorch model.
        inputs : Any
            Input for ``model``.

        Returns
        -------
        Any
            Prediction.

        """
        return model(inputs)

    def torch_input_to_cuda(self, torch_input) -> Any:
        """
        Common implementation of how to transfer PyTorch model input from CPU to CUDA.

        Parameters
        ----------
        torch_input : torch.Tensor
            Tensor on CPU device.

        Returns
        -------
        torch.Tensor
            Tensor on CUDA device.

        """
        if isinstance(torch_input, torch.Tensor):
            return torch_input.to(device='cuda:0')
        else:
            raise NotImplementedError

    def torch_output_to_cpu(self, torch_output) -> None:
        """
        Common implementation of how to transfer PyTorch output (prediction) from CUDA to CPU.

        Parameters
        ----------
        torch_output : Union[torch.Tensor, Iterable]
            PyTorch output on CUDA device.

        Returns
        -------
        None
            Irrespective of the results, this function only transfers them to CPU.

        Raises
        ------
        RuntimeError:
            If some part of ``torch_output`` is not ``torch.Tensor`` or Iterable
            In this case user should implement transfering of this object.

        """
        if isinstance(torch_output, torch.Tensor):
            torch_output.cpu()
        elif isinstance(torch_output, Iterable):
            for item in torch_output:
                self.torch_output_to_cpu(item)
        else:
            raise RuntimeError(f'Cannot transfer item to CPU: {torch_output}')
