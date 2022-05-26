# Copyright 2017 The KaiJIN Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import glob
import os
import platform
from setuptools import setup
from setuptools import find_packages

try:
  import torch
  from torch.utils.cpp_extension import BuildExtension
  from torch.utils.cpp_extension import CppExtension
  from torch.utils.cpp_extension import CUDAExtension
except ImportError:
  BuildExtension = object

with open('README.md') as f:
  long_description = f.read()


class CustomedBuildExt(BuildExtension):
  r"""Avoid a gcc warning below:
  cc1plus: warning: command line option ‘-Wstrict-prototypes’ is valid
  for C/ObjC but not for C++
  """

  def build_extensions(self):
    if '-Wstrict-prototypes' in self.compiler.compiler_so:
      self.compiler.compiler_so.remove('-Wstrict-prototypes')
    self.compiler.compiler_so.append('-fopenmp')
    super().build_extensions()


if type(BuildExtension) != type(object):
  BuildExt = {'build_ext': CustomedBuildExt}
else:
  BuildExt = {}


def BuildPyTorchKernel():
  """building pytorch kernel

  Returns:
      [type]: [description]
  """
  if type(BuildExtension) == type(object):
    return []
  
  # disable compile on MacOS
  if 'Darwin' in platform.platform():
    return []

  # compile - default to cxx
  build_dir = os.path.dirname(os.path.abspath(__file__)) + '/tw/nn/csrc'
  source = glob.glob(build_dir + "/**/*.cc") + glob.glob(build_dir + "/*.cc")
  define_macros = []
  extra_compile_args = {"cxx": []}
  extension = CppExtension

  # build with cuda
  if torch.cuda.is_available():
    extension = CUDAExtension
    source += glob.glob(build_dir + "/**/*.cu")
    define_macros += [("TW_WITH_CUDA", None)]
    extra_compile_args.update({
        "nvcc": [
            "-DCUDA_HAS_FP16=1",
            "-D__CUDA_NO_HALF_OPERATORS__",
            "-D__CUDA_NO_HALF_CONVERSIONS__",
            "-D__CUDA_NO_HALF2_OPERATORS__",
        ]
    })

  # display
  for file in source:
    print('Add file:', file)
    
  # if without any c++ or cuda files
  if len(source) == 0:
    return []

  ext_modules = [
      extension(
          "tw._C",
          source,
          include_dirs=[build_dir],
          define_macros=define_macros,
          extra_compile_args=extra_compile_args,
      )
  ]
  return ext_modules


setup(
    name="tw",
    version="3.9.0",
    author="Kai Jin",
    author_email="atranitell@gmail.com",
    description="TorchWrapper is a deep learning helper.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/atranitell/TensorWrapper",
    license="Apache 2.0 Licence",
    packages=find_packages(),
    ext_modules=BuildPyTorchKernel(),
    cmdclass=BuildExt,
    classifiers=[
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    install_requires=[
        "matplotlib",
        # "opencv-python==3.*",
        "numpy",
        "tensorboard",
        "tqdm",
        "cython",
        "scipy",
        # "rawpy",
        # "exifread"
        # "kornia==0.2.2", # corresponding to torch==1.4.0
    ],
)
