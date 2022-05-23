import statistics
from timeit import Timer
from typing import Tuple

from enot_lite.benchmark.backend_runner import BackendRunner

__all__ = [
    'BackendBenchmark',
]


class BackendBenchmark:
    """
    Benchmarks inference time of backends.

    This class is a building block of :class:`~enot_lite.benchmark.benchmark.Benchmark`,
    it measures inference time for one backend.

    All components: inference backend, model and input data should be wrapped into an object that implements
    :class:`~enot_lite.benchmark.backend_runner.BackendRunner` interface to work with :class:`BackendBenchmark`.
    We have already wrapped our and PyTorch backends, but you can extend benchmark by adding and registering
    builder in :class:`~enot_lite.benchmark.backend_runner_factory.BackendRunnerFactory` for your own backend.
    """

    def __init__(self, warmup: int, repeat: int, number: int):
        """
        To understand ctor parameters see :func:`benchmark` method.

        Parameters
        ----------
        warmup : int
            Number of warmup steps before benchmarking.
        repeat : int
            Number of repeat steps (see :class:`timeit.Timer`).
        number : int
            Number of inference calls in each ``repeat`` step (see :class:`timeit.Timer`).

        """
        self._warmup = warmup
        self._repeat = repeat
        self._number = number

    def benchmark(self, backend_runner: BackendRunner) -> Tuple[float, float]:
        """
        Benchmarks backend using :class:`~enot_lite.benchmark.backend_runner.BackendRunner` interface.

        There are two main steps:
         - warmup: calls :func:`~enot_lite.benchmark.backend_runner.BackendRunner.run` method of
           :class:`~enot_lite.benchmark.backend_runner.BackendRunner` ``warmup`` times
         - bechmark: calls :func:`~enot_lite.benchmark.backend_runner.BackendRunner.run` method ``number × repeat``
           times and stores execution time

        The results of benchmarking are measured mean time per one batch (in ms) and standard deviation per one batch.

        All measurements in ``benchmark`` step are done with the help of :class:`timeit.Timer` object.

        Parameters
        ----------
        backend_runner : BackendRunner
            Backend, model and input data wrapped in :class:`~enot_lite.benchmark.backend_runner.BackendRunner`
            interface.

        Returns
        -------
        Tuple[float, float]
            mean time per one batch (in ms),
            standard deviation per one batch (in ms).

        """
        # Warmup step.
        for _ in range(self._warmup):
            backend_runner.run()

        # Benchmarking step.
        measurements = Timer(backend_runner.run).repeat(repeat=self._repeat, number=self._number)

        # Cooking results.
        mean = self._s_to_ms(statistics.mean(measurements) / self._number)
        stdev = self._s_to_ms(statistics.stdev(measurements) / self._number)
        return mean, stdev

    @staticmethod
    def _s_to_ms(s: float) -> float:
        return s * 1000.0
