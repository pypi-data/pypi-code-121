# -*- coding: UTF-8 -*-
# Copyright©2020 xiangyuejia@qq.com All Rights Reserved
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
"""

"""
from typing import Dict, Tuple, Union, List, Iterator, Any, NoReturn
import random
import base64

max_name_lenth = 64  # 递增4来决定长度
name = str(base64.urlsafe_b64encode(
    random.randint(0, 2**(8*max_name_lenth//4*3)
                   ).to_bytes(max_name_lenth//4*3, "little") # 大端和小端在生成随机文件的时候就随意就可以了
), "utf-8")
print(name)

