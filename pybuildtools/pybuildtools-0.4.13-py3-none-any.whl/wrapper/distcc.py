'''
DistCC stuff

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
from buildtools.utils import bool2yn


def configure_distcc(cfg, cmake):
    global ENV
    with log.info('Configuring distcc...'):
        if not cfg.get('env.distcc.enabled', False):
            log.info('distcc disabled, skipping.')
            return
        distcc_hosts = []
        english_hosts = []
        maxjobs = 0
        canpump = False
        for hostname, hostcfg in cfg['env']['distcc']['hosts'].items():
            h = hostname
            info_e = []
            if 'max-jobs' in hostcfg:
                njobs = hostcfg.get('max-jobs', 0)
                if njobs > 0:
                    h += '/' + str(njobs)
                    info_e += ['{} max jobs'.format(njobs)]
                    maxjobs += njobs
            if 'opts' in hostcfg:
                h += ',' + ','.join(hostcfg['opts'])
                info_e += ['with options: ({})'.format(', '.join(hostcfg['opts']))]
                # Check for lzo & cpp before permitting distcc-pump.
                if 'lzo' in hostcfg['opts'] and 'cpp' in hostcfg['opts']:
                    canpump = True
            if len(info_e) > 0:
                english_hosts += ['* {}: {}'.format(hostname, ', '.join(info_e))]

            distcc_hosts += [h]
        if len(distcc_hosts) > 0:
            with log.info('Compiling with {} hosts:'.format(len(distcc_hosts))):
                for hostline in english_hosts:
                    log.info(hostline)
            log.info('Max jobs    : {0}'.format(maxjobs))
            cfg['env']['make']['jobs'] = maxjobs

            pump_enabled = maxjobs > 0 and canpump and cfg.get('env.distcc.pump.enabled', False)
            with log.info('Pump enabled: {0}'.format(bool2yn(pump_enabled))):
                if pump_enabled:
                    pump = cfg.get('bin.pump', which('distcc-pump'))
                    make = cfg.get('bin.make', which('make'))
                    cfg['bin']['make'] = '{pump} {make}'.format(pump=pump, make=make)
                    log.info('DistCC Pump : ' + pump)
                    log.info('Make        : ' + make)

            ENV.set('DISTCC_HOSTS', ' '.join(distcc_hosts))
            #if not cfg.get('env.ccache.enabled', False):
            DISTCC = cfg.get('bin.distcc', which('distcc'))

            ENV.set('CC', DISTCC + ' ' + ENV.get('CC', 'gcc'))
            ENV.set('CXX', DISTCC + ' ' + ENV.get('CXX', 'g++'))
