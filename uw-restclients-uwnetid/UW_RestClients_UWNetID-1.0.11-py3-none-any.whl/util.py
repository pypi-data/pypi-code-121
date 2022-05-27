# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from restclients_core.util.decorators import use_mock
from uw_uwnetid.dao import UWNetID_DAO


fdao_uwnetid_override = use_mock(UWNetID_DAO())
