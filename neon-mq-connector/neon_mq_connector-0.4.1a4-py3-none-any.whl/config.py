# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2022 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import json
from typing import Optional


def load_neon_mq_config():
    """
    Locates and loads global MQ configuration. Priority is as follows:
    NEON_MQ_CONFIG_PATH environment variable
    {NEON_CONFIG_PATH}/mq_config.json
    ~/.local/share/neon/credentials.json
    """
    valid_config_paths = (
        os.path.expanduser(os.environ.get('NEON_MQ_CONFIG_PATH', "")),
        os.path.join(os.path.expanduser(os.environ.get("NEON_CONFIG_PATH", "~/.config/neon")), "mq_config.json"),
        os.path.expanduser("~/.local/share/neon/credentials.json")
    )
    config = None
    for conf in valid_config_paths:
        if conf and os.path.isfile(conf):
            config = Configuration().from_file(conf).config_data
            break
    if not config:
        return
    if "MQ" in config.keys():
        return config["MQ"]
    else:
        return config


class Configuration:
    def __init__(self, file_path: Optional[str] = None):
        self._config_data = dict()
        if file_path:
            self.from_file(file_path)

    def from_file(self, file_path: str):
        with open(os.path.expanduser(file_path)) as input_file:
            self._config_data = json.load(input_file)
        return self

    def from_dict(self, config_data: dict):
        self._config_data = config_data
        return self

    @property
    def config_data(self) -> dict:
        return self._config_data

    @config_data.setter
    def config_data(self, value):
        if not isinstance(value, dict):
            raise TypeError(f'Type: {type(value)} not supported')
        self._config_data = value
