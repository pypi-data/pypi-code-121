# Copyright 2020 The KaiJIN Authors. All Rights Reserved.
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
import time
import argparse
import torch
import torchvision
import tw


class BusyTasker():

  def __init__(self, config):
    self.config = config
    self.device = 'cuda:{}'.format(config.dist_rank)
    print(self.config, self.device)

  def __call__(self):
    model_cpu = torchvision.models.resnet18()
    model_gpu = torchvision.models.resnet152()
    model_gpu.to(self.device)

    count = 0
    while True:
      t1 = time.time()
      with torch.no_grad():
        inputs_cpu = torch.rand(128, 3, 224, 224).float()
        inputs_gpu = torch.rand(512, 3, 224, 224).float().to(self.device)
        model_gpu(inputs_gpu)
        if count % 5 == 0:
          model_cpu(inputs_cpu)
      t2 = time.time()
      torch.save(inputs_cpu, 'cpu.pth')
      torch.save(inputs_gpu, 'gpu.pth')
      # time.sleep(1.0)
      count += 1
      print('[Elapsed] {}: {}'.format(count, (t2 - t1) * 1000.0))


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  tw.runner.launch(parser, BusyTasker)
