import importlib
import platform
import re
import subprocess
from typing import Dict
from typing import Optional

import pkg_resources

import enot_lite

__all__ = [
    'system_info',
    'kernel_version',
    'cpu_model_name',
    'gpu_model_name',
    'nvidia_driver_version',
    'pytorch_cuda_version',
    'package_version',
]


def system_info() -> Dict:
    return {
        'CPU': cpu_model_name(),
        'GPU': gpu_model_name(),
        'ENOT-Lite': enot_lite.__version__,
        'ONNX': package_version('onnx'),
        'ONNX Runtime': package_version('onnxruntime'),
        'PyTorch': package_version('torch'),
        'CUDA (ONNX Runtime)': package_version('nvidia-cuda-runtime'),
        'CUBLAS (ONNX Runtime)': package_version('nvidia-cublas'),
        'CUDNN (ONNX Runtime)': package_version('nvidia-cudnn'),
        'CUDA (PyTorch)': pytorch_cuda_version(),
        'TensorRT': package_version('tensorrt'),
        'OpenVINO': package_version('openvino'),
        'NVIDIA Driver': nvidia_driver_version(),
        'Python': platform.python_version(),
        'Platform arch': platform.machine(),
        'Linux kernel': kernel_version(),
    }


def kernel_version() -> Optional[str]:
    try:
        return subprocess.check_output('uname -r', shell=True).strip().decode('utf-8')
    except:
        return None


def cpu_model_name() -> Optional[str]:
    try:
        cpuinfo = subprocess.check_output('cat /proc/cpuinfo', shell=True).strip().decode('utf-8')
        for line in cpuinfo.split('\n'):
            if 'model name' in line:
                return re.sub('.*model name.*: ', '', line, 1)
        return None
    except:
        return None


def gpu_model_name() -> Optional[str]:
    try:
        import torch
        return torch.cuda.get_device_name(0)
    except:
        return None


def nvidia_driver_version() -> Optional[str]:
    try:
        driver_version = subprocess.check_output(
            args='nvidia-smi --query-gpu=driver_version --format=csv',
            shell=True,
        ).strip().decode('utf-8')
        return driver_version.split('\n')[1]
    except:
        return None


def pytorch_cuda_version() -> Optional[str]:
    try:
        import torch
        return torch.version.cuda
    except:
        return None


def package_version(package_name: str) -> Optional[str]:  # pylint: disable=missing-function-docstring
    try:
        package = importlib.import_module(package_name)
        return package.__version__
    except (ModuleNotFoundError, AttributeError):
        try:
            return pkg_resources.get_distribution(package_name).version
        except pkg_resources.DistributionNotFound:
            packages = [
                str(package).replace(' ', '==') for package in pkg_resources.working_set if package_name in str(package)
            ]
            if packages:
                return ', '.join(packages)
            return None

