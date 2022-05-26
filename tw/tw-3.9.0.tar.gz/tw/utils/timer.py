# Copyright 2021 The KaiJIN Authors. All Rights Reserved.
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
from datetime import datetime


def pid():
  return datetime.strftime(datetime.now(), '%y%m%d%H%M%S')


def eta(latency, counts):
  r"""eta(2, 1000) -> '01 day, 08:16:40"""
  _elapsed = int(latency * counts)
  _days = _elapsed // (60 * 60 * 24)
  _remains = _elapsed - _days * 60 * 60 * 24
  _hours = _remains // (60 * 60)
  _remains = _remains - _hours * 60 * 60
  _mins = _remains // 60
  _secs = _remains - _mins * 60
  return '%02d day, %02d:%02d:%02d' % (_days, _hours, _mins, _secs)


def remain_eta(current_step, total_step, start_time, initial_step):
  remains = total_step - current_step
  # average time over all steps
  since_start = duration(start_time, tic(), 's')
  per_step = since_start / (current_step + 1 - initial_step)
  return eta(per_step, remains)


def tic():
  return time.time() * 1000


def duration(start, end, fmt='ms'):
  if fmt == 's':
    return (end - start) / 1000.0
  elif fmt == 'ms':
    return (end - start)
  else:
    raise NotImplementedError(fmt)


def throughput(elapsed, samples):
  r"""compute throughput per seconds

  Args:
    elapsed (float/int): time to elapsed for total samples
    samples (int): the number of sample processed

  Return:
    throughput (float)

  """
  return float(samples) / elapsed
