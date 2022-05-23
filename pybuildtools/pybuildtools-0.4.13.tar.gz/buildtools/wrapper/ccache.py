'''
ccache Wrapper

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
from buildtools.os_utils import cmd, ENV, which

def _which_if_basename(subject):
    if '/' in subject or ' ' in subject: return subject
    return which(subject)

def configure_ccache(cfg, cmake):
    global ENV
    with log.info('Configuring ccache...'):
        if not cfg.get('env.ccache.enabled', False):
            log.info('ccache disabled, skipping.')

            # Otherwise, strange things happen.
            ENV.set('CC', _which_if_basename(ENV.get('CC','gcc') + '.real'))
            ENV.set('CXX', _which_if_basename(ENV.get('CXX','g++') + '.real'))
        else:
            CCACHE = _which_if_basename(cfg.get('bin.ccache', 'ccache'))
            DISTCC = _which_if_basename(cfg.get('bin.distcc', 'distcc'))

            if cfg.get('env.distcc.enabled', False):
                ENV.set('CCACHE_PREFIX', DISTCC)

            # Fixes a bug where CMake sets this all incorrectly.
            # http://public.kitware.com/Bug/view.php?id=12274
            cmake.setFlag('CMAKE_CXX_COMPILER_ARG1', ENV.env['CXX'])
            # set_cmake_env('CMAKE_ASM_COMPILER_ARG1',ENV.env['ASM'])

            ENV.set('CC', CCACHE + ' ' + ENV.env['CC'])
            ENV.set('CXX', CCACHE + ' ' + ENV.env['CXX'])
            # ENV.set('ASM',CCACHE + ' ' + ENV.env['ASM'])
