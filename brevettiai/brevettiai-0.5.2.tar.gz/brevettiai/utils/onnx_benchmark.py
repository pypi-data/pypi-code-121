"""
Benchmarks for onnx models
Example:
    python -m brevettiai.utils.onnx_benchmark [path_to_onnx] ...
"""
import argparse
import os
import time
from pydantic import BaseModel, Field
from typing import Optional

import cv2
import numpy as np
import pandas as pd
import onnxruntime


class Benchmark(BaseModel):
    """
    Collection of information about a benchmark
    """
    name: str
    timing: list
    warmup: int = 0
    producer: str = ""
    input_example: Optional[np.ndarray] = None
    output_example: Optional[np.ndarray] = None

    class Config:
        arbitrary_types_allowed = True

    @property
    def valid_timing(self):
        return self.timing[self.warmup:]

    @property
    def t0(self):
        return self.timing[0]

    @property
    def mean(self):
        return np.mean(self.valid_timing)

    @property
    def worst_case(self):
        return max(self.valid_timing)

    @staticmethod
    def _shape_and_dtype_str(array):
        if array is None:
            return "?"
        return f"{array.shape}[{array.dtype}]"

    def __str__(self):
        return f"{self.name}[{self.producer}] " \
               f"{self._shape_and_dtype_str(self.input_example)} -> " \
               f"{self._shape_and_dtype_str(self.output_example)}\n" \
               f"\taverage: {self.mean * 1000:.1f}ms, " \
               f"worst case: {self.worst_case * 1000:.1f}ms, " \
               f"first batch: {self.t0 * 1000:.1f}ms"


class BenchmarkCV2(Benchmark):
    layer_timing: np.ndarray
    layer_names: list = Field(default_factory=list)

    @property
    def layer_mean_performance(self):
        t = self.layer_timing[self.warmup:]
        t = pd.Series(np.mean(t, 0), self.layer_names)
        t.index.rename("layers")
        return t

    def __str__(self):
        layer_perf = self.layer_mean_performance.sort_values(ascending=False).head(10)
        return super().__str__() + f"\nLayer performance:\n{(layer_perf*1000).apply('{:.1f}ms'.format).to_string()}"


def _get_input_data_generator(path):
    model = onnxruntime.InferenceSession(path)
    input_ = model.get_inputs()[0]
    dtype_ = np.dtype(input_.type[7:-1])
    dtype_ = np.float32 if dtype_ == "float64" else dtype_
    while True:
        yield np.random.randn(*input_.shape).astype(dtype_)


def benchmark_onnx_with_onnxruntime(name: str, path: str, runs: int = 100, warmup_runs: int = 10) -> Benchmark:
    """
    Benchmark an onnx with onnxruntime

    Args:
        path:
        runs:
        warmup_runs:
        name:

    Returns:

    """
    assert runs > 0
    assert warmup_runs > 0
    sess_option = onnxruntime.SessionOptions()
    sess_option.graph_optimization_level = onnxruntime.GraphOptimizationLevel.ORT_ENABLE_EXTENDED

    providers = [
        ('CUDAExecutionProvider', {
            'device_id': 1,
            'arena_extend_strategy': 'kNextPowerOfTwo',
            'gpu_mem_limit': 6 * 1024 * 1024 * 1024,
            'cudnn_conv_algo_search': 'EXHAUSTIVE',
            'do_copy_in_default_stream': True,
        }),
        'CPUExecutionProvider',
    ]
    model = onnxruntime.InferenceSession(onnx, providers=providers, sess_options=sess_option)

    input_ = model.get_inputs()[0]
    output_ = model.get_outputs()[0]
    input_data_generator = _get_input_data_generator(path)

    input_data, output_data = None, None
    timing = []
    for i in range(runs + warmup_runs):
        input_data = {input_.name: next(input_data_generator)}
        ta = time.perf_counter()

        output_data = model.run([output_.name], input_data)[0]

        tb = time.perf_counter()
        timing.append((tb - ta))

    return Benchmark(name=name, timing=timing, warmup=warmup_runs, producer=f"onnxruntime-{onnxruntime.__version__}",
                        input_example=input_data[input_.name], output_example=output_data)


def benchmark_onnx_with_cv2(name: str, path: str, runs: int = 100, warmup_runs: int = 10) -> BenchmarkCV2:
    """
    Benchmark with cv2.dnn as runtime

    Args:
        name:
        path:
        runs:
        warmup_runs:

    Returns:

    """
    model = cv2.dnn.readNetFromONNX(path)

    input_data_generator = _get_input_data_generator(path)

    input_data, output_data = None, None
    timing, timing_perf_counter = [], []
    layer_timing = []
    for i in range(runs + warmup_runs):
        input_data = next(input_data_generator)
        ta = time.perf_counter()

        model.setInput(input_data)
        output_data = model.forward()

        tb = time.perf_counter()
        timing_perf_counter.append((tb - ta))
        dt, layer_dt = model.getPerfProfile()
        timing.append(dt / cv2.getTickFrequency())
        layer_timing.append(layer_dt / cv2.getTickFrequency())

    layer_timing = np.stack(layer_timing).squeeze()

    return BenchmarkCV2(name=name, timing=timing,
                        layer_timing=layer_timing, layer_names=model.getLayerNames(),
                        warmup=warmup_runs, producer=f"cv2.dnn-{cv2.version.opencv_version}",
                        input_example=input_data, output_example=output_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Performance tests for onnx models')
    parser.add_argument('onnx_path', nargs='+', help='Paths to onnx files')
    parser.add_argument('-N', "--runs", help='Number of batches to supply to model', type=int, default=100)
    parser.add_argument("--warmup-runs", help='Number of batches to supply to model for warmup', type=int, default=10)
    args = parser.parse_args()

    for onnx in args.onnx_path:
        name = os.path.basename(onnx)
        kwargs = dict(name=name, path=onnx, runs=args.runs, warmup_runs=args.warmup_runs)
        print(benchmark_onnx_with_cv2(**kwargs), "\n")
        print(benchmark_onnx_with_onnxruntime(**kwargs), "\n")
