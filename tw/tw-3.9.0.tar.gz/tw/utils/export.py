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
r"""Export"""
import os
import torch


def torch_to_onnx(model, args, output_path, export_params=True, training=False,
                  input_names=None, output_names=None, opset_version=11,
                  example_outputs=None, dynamic_axes=None, verbose=False):
  torch.onnx.export(model=model,
                    args=args,
                    f=output_path,
                    export_params=export_params,
                    verbose=verbose,
                    training=training,
                    input_names=input_names,
                    output_names=output_names,
                    aten=False,
                    export_raw_ir=False,
                    operator_export_type=None,
                    opset_version=opset_version,
                    _retain_param_name=True,
                    do_constant_folding=True,
                    example_outputs=example_outputs,
                    strip_doc_string=True,
                    dynamic_axes=dynamic_axes,
                    keep_initializers_as_inputs=False)


def onnx_to_trt(onnx_path,
                output_path='trt_model.engine',
                shapes={
                    'input': {'min': (1, 3, 112, 112),
                              'best': (1, 3, 224, 224),
                              'max': (1, 3, 256, 256)},
                },
                verbose=False,
                **kwargs):
  import tensorrt as trt
  assert os.path.exists(onnx_path)

  onnx_file = open(onnx_path, 'rb')

  if verbose:
    TRT_LOGGER = trt.Logger(trt.Logger.VERBOSE)
  else:
    TRT_LOGGER = trt.Logger(trt.Logger.WARNING)

  flag = 1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)

  builder = trt.Builder(TRT_LOGGER)
  network = builder.create_network(flag)
  parser = trt.OnnxParser(network, TRT_LOGGER)

  builder.max_workspace_size = 4 << 30  # 4GB

  onnx_file.seek(0)
  if not parser.parse(onnx_file.read()):
    print('[ERROR]', parser.get_error(0))
  onnx_file.close()

  config = builder.create_builder_config()
  profile = builder.create_optimization_profile()

  for key, shape in shapes.items():
    profile.set_shape(key, shape['min'], shape['best'], shape['max'])
  config.add_optimization_profile(profile)
  engine = builder.build_engine(network, config)

  with open(output_path, "wb") as f:
    f.write(engine.serialize())


def torch_to_trt(**kwargs):
  pass
