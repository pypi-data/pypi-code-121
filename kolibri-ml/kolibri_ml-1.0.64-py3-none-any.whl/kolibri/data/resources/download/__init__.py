# coding=utf-8
# Copyright 2022 The TensorFlow Datasets Authors.
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


from kolibri.data.resources.download.checksums import add_checksums_dir
from kolibri.data.resources.download.download_manager import DownloadConfig
from kolibri.data.resources.download.download_manager import DownloadManager
from kolibri.data.resources.download.downloader import DownloadError
from kolibri.data.resources.download.extractor import iter_archive
from kolibri.data.resources.download.resource import ExtractMethod
from kolibri.data.resources.download.resource import Resource
from kolibri.data.resources.download.util import ComputeStatsMode
from kolibri.data.resources.download.util import GenerateMode

__all__ = [
    "add_checksums_dir",
    "DownloadConfig",
    "DownloadManager",
    "DownloadError",
    "ComputeStatsMode",
    "GenerateMode",
    "Resource",
    "ExtractMethod",
    "iter_archive",
]
