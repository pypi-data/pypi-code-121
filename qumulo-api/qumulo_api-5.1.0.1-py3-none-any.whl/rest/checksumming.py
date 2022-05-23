# Copyright (c) 2022 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

# qumulo_python_versions = { 3.6, latest }

from typing import Optional

import qumulo.lib.request as request

from qumulo.lib.auth import Credentials


@request.request
def get_status(
    conninfo: request.Connection, credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'GET'
    uri = '/v1/checksumming/status'
    return request.rest_request(conninfo, credentials, method, uri)
