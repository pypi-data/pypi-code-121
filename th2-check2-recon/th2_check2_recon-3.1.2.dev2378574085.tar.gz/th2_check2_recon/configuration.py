# Copyright 2020-2021 Exactpro (Exactpro Systems Limited)
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
import datetime


class RuleConfiguration:

    def __init__(self, name, enabled, match_timeout, match_timeout_offset_ns, autoremove_timeout=None, configuration=None) -> None:
        self.name = str(name)
        self.enabled = True if enabled.lower() == 'true' else False
        self.match_timeout = int(match_timeout)
        self.match_timeout_offset_ns = int(match_timeout_offset_ns)
        if autoremove_timeout is not None:
            try:
                self.autoremove_timeout = int(autoremove_timeout)
            except ValueError:
                self.autoremove_timeout = datetime.datetime.strptime(autoremove_timeout, '%H:%M')
                self.autoremove_timeout = self.autoremove_timeout.combine(datetime.datetime.now().date(), self.autoremove_timeout.time())
        else:
            self.autoremove_timeout = None
        self.configuration = configuration


class ReconConfiguration:
    def __init__(self, recon_name: str, cache_size: int, event_batch_max_size: int,
                 event_batch_send_interval: int, rules_package_path: str, rules: list,
                 configuration=None) -> None:
        self.recon_name = recon_name
        self.cache_size = int(cache_size)
        self.event_batch_max_size = int(event_batch_max_size)
        self.event_batch_send_interval = int(event_batch_send_interval)
        self.rules_package_path = rules_package_path
        self.rules = [RuleConfiguration(**rule) for rule in rules]
        self.configuration = configuration
