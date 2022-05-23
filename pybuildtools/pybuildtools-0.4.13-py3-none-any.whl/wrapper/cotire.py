'''
COTIRE Wrapper (requires cmake)

Copyright (c) 2015 - 2022 Rob "N3X15" Nelson <nexisentertainment@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''
import os

from buildtools.bt_logging import log
from buildtools.os_utils import cmd, ENV

def configure_cotire(cfg, cmake):
    global ENV
    with log.info('Configuring cotire...'):
        if not cfg.get('env.cotire.enabled', False):
            log.info('cotire disabled, skipping.')
        else:
            ENV.set('CCACHE_SLOPPINESS', 'time_macros')
            cmake.setFlag('ENABLE_COTIRE', 'On')
            if cfg.get('env.make.jobs', 1) > 1:
                cmake.setFlag('COTIRE_MAXIMUM_NUMBER_OF_UNITY_INCLUDES', cfg.get('env.make.jobs', 1))
