from sys import modules
from halo import Halo
import lazy_import

sys = lazy_import.lazy_module("sys")
time = lazy_import.lazy_module("time")
re = lazy_import.lazy_module("re")
os = lazy_import.lazy_module("os")
scp = lazy_import.lazy_module("scp")
tarfile = lazy_import.lazy_module("tarfile")
itertools = lazy_import.lazy_module("itertools")
requests = lazy_import.lazy_module("requests")
bugsnag = lazy_import.lazy_module("bugsnag")

grpc = lazy_import.lazy_module("grpc")
#import grpc

import traceback

from pathlib import Path

from .pilotserver import PilotServer
from .sbc import Sbc

from .grpc_gen.pilotbuild_pb2 import BinaryType, BuildRequest, BuildStatus, BuildStep, TargetMcu, Module
from .grpc_gen.pilotbuild_pb2_grpc import PilotBuildStub

from shutil import copyfile
from gql import gql

from colorama import Fore
from colorama import Style
from colorama import init

from enum import Enum


class PilotDriver():
    MODULE_COUNT = 4
    retry_count = 2
    emptystr = '-'
    build_server = 'build.pilotnexus.io:50051'
    pilot_driver_root = '/proc/pilot'
    tmp_dir = '/tmp/pilot'
    kernmodule_list = [
        'pilot', 'pilot_plc', 'pilot_tty', 'pilot_rtc', 'pilot_fpga',
        'pilot_io', 'pilot_slcd'
    ]

    binpath = ''

    eeproms = {}
    modules = {}

    ps = None
    sbc = None

    def __init__(self, pilotserver: PilotServer, sbc: Sbc):
        self.ps = pilotserver
        self.sbc = sbc

        if sbc is not None:
            self.binpath = '{}/bin/{}'.format(
                os.path.join(os.path.abspath(os.path.dirname(__file__))),
                self.sbc.target['architecture'])

    def get_modules(self):
        memregs = ['uid', 'hid', 'fid']
        strmlist = list(
            filter(
                None,
                self.sbc.cmd(
                    'find /proc/pilot/module* -maxdepth 0 -printf "%f\\n"').
                split('\n')))
        matches = filter(None,
                         map(lambda x: re.match(r'module(\d+)', x), strmlist))
        modlist = {
            int(x.group(1)): {
                'uid': '',
                'hid': '',
                'fid': ''
            }
            for x in matches
        }
        for mod in modlist:
            for memreg in memregs:
                retry = self.retry_count
                errcount = 0
                while retry > 0:
                    retry = retry - 1
                    try:
                        regfile = self.sbc.cmd(
                            'cat {}/module{}/eeprom/{}'.format(
                                self.pilot_driver_root, mod, memreg), True)
                        modlist[mod][memreg] = ''.join(
                            char for char in regfile
                            if str.isprintable(char)).strip()

                        if memreg == 'fid':  # additional plausibility checks
                            if len(
                                    list(
                                        filter(lambda x: ord(x) > 255,
                                               regfile))) > 0:
                                modlist[mod][memreg] = ''
                            else:
                                break
                        else:
                            break
                    #except:
                    except Exception as e:
                        modlist[mod][memreg] = ''
                        errcount = errcount + 1
                        if errcount >= self.retry_count:
                            return modlist, False
                        #dbg('could not read {} of module {}'.format(memreg, mod))
        return modlist, True

    def set_module_fid(self, number, fid):
        self.sbc.setFileContent(
            self.pilot_driver_root + '/module{}/eeprom/fid'.format(number),
            fid + '       ')

    def getmodules(self, mod):
        self.eeproms = mod
        try:
            variables = {
                'fids': [
                    '{}'.format(value['fid']) for key, value in mod.items()
                    if value['fid'] != ''
                ],
                'hids': [
                    '{}'.format(value['hid']) for key, value in mod.items()
                    if value['hid'] != ''
                ]
            }

            obj = self.ps.query(
                gql("""
      query get_fids($fids: [bpchar!], $hids: [bpchar!]) {
        pilot_fid(where: {fid: {_in: $fids} }) {
          fid
          name
          usage
        }
        pilot_hid(where: {hid: {_in: $hids} }) {
          hid
          title
          subtitle
          description
          pinout
          hid2fids {
            fid {
              fid
              name
            }
            isdefault
          }
        }
      }
      """), variables, True)

            self.modules = [{
                'module':
                key,
                'currentfid': value['fid'],
                'hid': value['hid'],
                'currentfid_nicename':
                next(
                    iter(y['name'] for y in filter(
                        lambda x: x['fid'].strip() == value['fid'].strip(),
                        obj['pilot_fid'])), value['fid'].strip()),
                'usage':
                next(
                    iter(y['usage'] for y in filter(
                        lambda x: x['fid'].strip() == value['fid'].strip(),
                        obj['pilot_fid'])), value['fid'].strip()),
                'description':
                next(
                    iter(y['description'] for y in filter(
                        lambda x: x['hid'].strip() == value['hid'].strip(),
                        obj['pilot_hid'])), value['hid'].strip()),            
                'pinout':
                next(
                    iter(y['pinout'] for y in filter(
                        lambda x: x['hid'].strip() == value['hid'].strip(),
                        obj['pilot_hid'])), value['hid'].strip()),            
                'fids':
                next(
                    iter([{
                        'isdefault': x['isdefault'],
                        'fid': x['fid']['fid'],
                        'name': x['fid']['name']
                    } for x in y['hid2fids']] for y in filter(
                        lambda x: x['hid'].strip() == value['hid'].strip(),
                        obj['pilot_hid'])), []),
            } for key, value in mod.items()]

            return self.modules, True
        except:
            e = sys.exc_info()[0]
            print(e)
        return {}, False

    def load_pilot_defs(self):
        success = False
        try:
            eeproms, success = self.get_modules()
            return self.getmodules(eeproms)
        except:
            return {}, False

    def driver_loaded(self):
        return self.sbc.cmd_retcode('test -e {}'.format(
            self.pilot_driver_root)) == 0

    def getModuleEeprom(self, module, memregion):
        try:
            return self.sbc.getFileContent('{}/module{}/eeprom/{}'.format(
                self.pilot_driver_root, module, memregion))
        except:
            return ''

    def tryrun(self, text, retries, cmd):
        print(text + '...', end='')
        sys.stdout.flush()
        while retries > 0:
            retries = retries - 1
            try:
                if self.sbc.cmd_retcode(cmd) == 0:
                    print(Fore.GREEN + 'done')
                    return 0
            except:
                print('.', end='')
                sys.stdout.flush()
        print(Fore.RED + 'failed')
        return 1

    def reset_pilot(self, wait_bootmsg=False):
        try:
            if not wait_bootmsg:
                print('Resetting MCU...', end='')
            sys.stdout.flush()
            reset_pin = self.sbc.target['reset_pin']['number']
            boot_pin = self.sbc.target['boot_pin']['number']

            # set boot pin to 0 to avoid booting into bootloader
            self.sbc.cmd(
                'sudo sh -c \'[ ! -f /sys/class/gpio/gpio{0}/value ] && echo "{0}" > /sys/class/gpio/export\''
                .format(boot_pin))
            self.sbc.cmd(
                'sudo sh -c \'echo "out" > /sys/class/gpio/gpio{}/direction\''.
                format(boot_pin))
            self.sbc.cmd(
                'sudo sh -c \'echo -n "0" > /sys/class/gpio/gpio{}/value\''.
                format(boot_pin))

            self.sbc.cmd(
                'sudo sh -c \'[ ! -f /sys/class/gpio/gpio{0}/value ] && echo "{0}" > /sys/class/gpio/export\''
                .format(reset_pin))
            self.sbc.cmd(
                'sudo sh -c \'echo "out" > /sys/class/gpio/gpio{}/direction\''.
                format(reset_pin))
            self.sbc.cmd(
                'sudo sh -c \'echo -n "1" > /sys/class/gpio/gpio{}/value\''.
                format(reset_pin))
            time.sleep(2)
            if wait_bootmsg:
                missing_commands = ''
                if self.sbc.cmd_retcode('command -v stty') != 0:
                    missing_commands = missing_commands + 'stty '
                if self.sbc.cmd_retcode('command -v timeout') != 0:
                    missing_commands = missing_commands + 'timeout '

                if missing_commands == '':
                    return self.sbc.cmd(
                        "sudo sh -c 'stty -F {0} 921600;sleep 0.1;timeout 2 cat {0} & sleep 0.5; echo 0 > /sys/class/gpio/gpio{1}/value;wait'"
                        .format(self.sbc.target['tty'], reset_pin))
                else:
                    return self.sbc.cmd(
                        "/sys/class/gpio/gpio{0}/value".format(reset_pin))
            else:
                self.sbc.cmd(
                    'sudo sh -c \'echo -n "0" > /sys/class/gpio/gpio{}/value\''
                    .format(reset_pin))
                print(Fore.GREEN + 'done')
        except:
            print(Fore.RED + 'failed')
        return ''

    def install_driver(self):
        try:
            match = re.match(self.sbc.target['kernelversionre'],
                             self.sbc.cmd('uname -a'))
            if match:
                packagename = "pilot-{}{}".format(
                    match.group('version'),
                    match.group('buildnum')
                    if 'buildnum' in match.groupdict() else '')
                print('trying to install package '
                      '{}'
                      ''.format(packagename))
                if self.sbc.cmd_retcode(
                        """sudo sh -c 'echo "{}" > /etc/apt/sources.list.d/amescon.list'"""
                        .format(self.sbc.target['apt_source'])) != 0:
                    print(
                        'Could not add source to /etc/apt/sources.list.d/amescon.list'
                    )
                    return 1
                if self.sbc.cmd_retcode(
                        """sudo sh -c 'wget -qO - http://archive.amescon.com/amescon.asc | sudo apt-key add -'"""
                ) != 0:
                    print('Could not get signing keys from amescon keyserver')
                    return 1
                self.sbc.cmd_retcode('sudo apt-get update')
                self.sbc.cmd_retcode("sudo apt-get remove '^pilot-.*' -y")
                self.sbc.cmd('sudo apt-get install -y {}'.format(packagename),
                             True)
            else:
                print('Could not detect your linux version')
                return 1
        except Exception as e:
            # bugsnag.notify(e, user={
            #     "username": self.ps.pilotcfg['username']})
            return 1
        return 0

    def get_kernel_info(self):
        try:
            fwhash = self.sbc.cmd(
                "echo $(/bin/zgrep '* firmware as of' /usr/share/doc/raspberrypi-bootloader/changelog.Debian.gz | head -1 | awk '{ print $5 }') && /usr/bin/wget https://raw.github.com/raspberrypi/firmware/$FIRMWARE_HASH/extra/git_hash -O - 2> NUL",
                True)
            if self.sbc.cmd_retcode('sudo modprobe configs') == 0:
                print(
                    'If you want us to build a kernel for you, send us the following firmware hash AND the file on your Raspberry Pi located in: /proc/config.gz'
                )
                print('Firmware Hash: {}'.format(fwhash))
                return 0
            else:
                print(
                    'Could not load configs. Check if the target Hardware is a Raspberry Pi and your user is sudoer.'
                )
        except:
            print(
                "Could not get your Firmware Hash. Check if the target Hardware is a Raspberry Pi and it is online."
            )
        return 1

    def check_driver(self):
        if self.sbc.cmd_retcode('ls ' + self.pilot_driver_root) != 0:
            print('Pilot driver is not loaded. Trying to load')
            if self.reload_drivers(False):
                print('Drivers loaded')
            else:
                if self.install_driver() == 0:
                    print('Pilot driver installed.')
                    return 1
                else:
                    print('Could not install the pilot driver, most likely there is no pre-compiled driver for your kernel.')
                    ch = input("Do you want to try to build them locally? (needs a couple of minutes and plenty of disk space, be patient) [y/n]: ")
                    if (ch == 'y' or ch == 'yes'):
                        return self.try_build_drivers()
                    #self.get_kernel_info()
                    return -1
        return 0
    
    def try_build_drivers(self):
        print('Building Pilot Kernel Driver...', end='')
        sys.stdout.flush()
        ret = self.sbc.cmd_retcode("sudo apt-get install -y python2 git build-essential")
        if ret == 0:
            ret = self.sbc.cmd_retcode("git clone https://github.com/pilotnexus/pilotdriver.git ~/pilotdriver && cd ~/pilotdriver && make prepare && make && make package && sudo make install")
            if ret == 0:
                print(Fore.GREEN + 'done')
                return 1 # success, we built the drivers, returning 1 to indicate a reboot
        print(Fore.RED + 'failed')
        print("Could not install build tools")
        return ret 

    def reload_drivers(self, verbose=True, pdstopped=False):
        ok = True

        pnstopped = self.sbc.stop_service("pilotnode", verbose)
        if not pdstopped:
            pdstopped = self.sbc.stop_service("pilotd", verbose)

        if verbose:
            print('reloading drivers...', end='')
        sys.stdout.flush()
        for module in self.kernmodule_list[::-1]:
            try:
                self.sbc.cmd_retcode("sudo modprobe -r {}".format(module))
            except:
                pass

        for module in self.kernmodule_list:
            try:
                if self.sbc.cmd_retcode(
                        "sudo modprobe {}".format(module)) != 0:
                    ok = False
            except:
                ok = False

        if verbose:
            if ok:
                print(Fore.GREEN + 'done')
            else:
                print(Fore.RED + 'failed')

        if pdstopped:
            self.sbc.start_service("pilotd")

        if pnstopped:
            self.sbc.start_service("pilotnode")

        return ok

    def build(self, version):
        files = dict()
        try:
            if not os.path.exists(self.tmp_dir):
                os.makedirs(self.tmp_dir)
            if version is not None:
                print("Building Version {}".format(version))
            spinner = Halo(text='Connecting', spinner='dots')
            spinner.start()
            channel = grpc.insecure_channel(self.build_server)
            stub = PilotBuildStub(channel)
            modules = [
                Module(number=key, fid=value['fid'], hid=value['hid'], uid=value['uid'])
                for key, value in self.eeproms.items() if value['fid'] != ''
            ]
            request = BuildRequest(modules=modules,
                                   target=TargetMcu.STM32F103RC, version=version)
            for buildStatus in stub.Build(request=request):
                if (buildStatus.HasField('step')):
                    spinner.stop()
                    text = re.sub("([A-Z])", " \g<0>",
                                  str(BuildStep.Name(buildStatus.step)))
                    spinner = Halo(text=text, spinner='dots')
                    spinner.start()
                    #print(BuildStep.Name(buildStatus.step))
                elif (buildStatus.HasField('result')):
                    spinner.stop()
                    spinner = Halo(
                        text='Downloading ' +
                        str(BinaryType.Name(buildStatus.result.bintype)),
                        spinner='dots')
                    spinner.start()
                    filename = ''
                    extract = False
                    extractfname = ''
                    extractdir = ''
                    if (buildStatus.result.bintype == BinaryType.MCUFirmware):
                        filename = "stm.gz"
                        if buildStatus.result.version:
                            version = buildStatus.result.version
                        extract = True
                        extractdir = self.tmp_dir
                        extractfname = 'stm.bin'
                    elif (buildStatus.result.bintype == BinaryType.MCUSource):
                        filename = "stm_src.gz"
                    elif (buildStatus.result.bintype ==
                          BinaryType.FPGABitstream):
                        filename = "fpga.gz"
                        extract = True
                        extractdir = self.tmp_dir
                        extractfname = 'cpld.jam'
                    elif (buildStatus.result.bintype == BinaryType.FPGASource):
                        filename = "fpga_src.gz"

                    fname = '{}/{}'.format(self.tmp_dir, filename)
                    with open(fname, "wb") as file:
                        file.write(buildStatus.result.binary)

                    if extract:
                        with tarfile.open(fname, "r:gz") as tar:
                            tar.extractall(path=extractdir)
                            tar.close()
                            if extractfname:
                                files[buildStatus.result.
                                      bintype] = os.path.join(
                                          extractdir, extractfname)
                    else:
                        files[buildStatus.result.bintype] = fname

            spinner.stop()
            print("Done.")
            return version, files

        except Exception as error:
            print(Fore.RED + str(error))
            bugsnag.notify(Exception(error))
    
    def get_firmware_source(self, extractDir, version):
        try:
            version, files = self.build(version)
            mcu_src_expanded = False
            fpga_src_expanded = False
            if BinaryType.FPGASource in files:
                with tarfile.open(files[BinaryType.FPGASource], "r:gz") as tar:
                    tar.extractall(path=extractDir)
                    tar.close()
                    fpga_src_expanded = True
            if BinaryType.MCUSource in files:
                with tarfile.open(files[BinaryType.MCUSource], "r:gz") as tar:
                    tar.extractall(path=extractDir)
                    tar.close()
                    mcu_src_expanded = True
            return version, fpga_src_expanded and mcu_src_expanded
        except Exception as error:
            print(Fore.RED + str(error))
            bugsnag.notify(Exception(error))
        return None, False

    def program_cpld(self, binfile, erase=False):
        cmd = 'sudo chmod +x {0}/jamplayer; sudo {0}/jamplayer -a{1} -g{2},{3},{4},{5} {6}'.format(
            self.binpath, 'erase' if erase else 'program',
            self.sbc.target['tdi_pin']['number'],
            self.sbc.target['tms_pin']['number'],
            self.sbc.target['tdo_pin']['number'],
            self.sbc.target['tck_pin']['number'], binfile)
        return self.tryrun('erasing CPLD' if erase else 'programming CPLD', 3,
                           cmd)

    def serial_used(self):
        res = self.sbc.cmd('sudo fuser -v {0}'.format(self.sbc.target['tty']))
        if len(res.strip()) > 0:
            return self.tryrun(
                'killing process accessing tty', 2,
                'sudo fuser -k {0}; sleep 1'.format(self.sbc.target['tty']))
        return True

    def program_mcu( self, binfile):  #use 115200, 57600, 38400 baud rates sequentially
        return self.tryrun(
            'programming MCU', 4,
            'sudo chmod +x {0}/stm32flash; sudo {0}/stm32flash -w {1} -b 115200 -g 0 -x {2} -z {3} {4}'
            .format(self.binpath, binfile, self.sbc.target['reset_pin']['number'],
                    self.sbc.target['boot_pin']['number'],
                    self.sbc.target['tty']))

    def program(self,
                files,
                program_cpld=True,
                program_mcu=True,
                bootmsg=False,
                reload_driver=True):
        res = 0
        if self.sbc.remote_client:
            self.sbc.cmd_retcode('mkdir -p {}'.format(self.tmp_dir))
            if self.sbc.cmd_retcode('sudo chown -R $USER {}'.format(
                    self.tmp_dir)) == 0:
                with scp.SCPClient(
                        self.sbc.remote_client.get_transport()) as scp_client:
                    scp_client.put(self.binpath + '/jamplayer',
                                   remote_path=self.tmp_dir)
                    scp_client.put(self.binpath + '/stm32flash',
                                   remote_path=self.tmp_dir)
                    scp_client.put(self.binpath + '/stm32flash',
                                   remote_path=self.tmp_dir)
                    self.binpath = self.tmp_dir # set binpath to tmp_dir now that executables are copied there

                    # FPGA Bitstream
                    if BinaryType.FPGABitstream in files:
                        scp_client.put(files[BinaryType.FPGABitstream],
                                       remote_path=os.path.join(
                                           self.tmp_dir, 'cpld.jam'))
                    # MCU Firmware
                    if BinaryType.MCUFirmware in files:
                        scp_client.put(files[BinaryType.MCUFirmware],
                                       remote_path=os.path.join(
                                           self.tmp_dir, 'stm.bin'))

                    # Variable file
                    if BinaryType.Variables in files:
                        scp_client.put(files[BinaryType.Variables],
                                       remote_path=os.path.join(
                                           self.tmp_dir, 'variables'))
                    
                    # Docs file
                    if BinaryType.Docs in files:
                        scp_client.put(files[BinaryType.Docs],
                                       remote_path=os.path.join(
                                           self.tmp_dir, 'fwconfig.json'))
            else:
                print('Error setting permissions to folder {}'.format(
                    self.tmp_dir))
        else:
            src = ""
            target = ""
            if BinaryType.FPGABitstream in files:
                src = files[BinaryType.FPGABitstream]
                target = os.path.join(self.tmp_dir, 'cpld.jam')
            if BinaryType.MCUFirmware in files:
                src = files[BinaryType.MCUFirmware]
                target = os.path.join(self.tmp_dir, 'stm.bin')
            if BinaryType.Variables in files:
                src = files[BinaryType.Variables]
                target = os.path.join(self.tmp_dir, 'variables')
            if BinaryType.Docs in files:
                src = files[BinaryType.Docs]
                target = os.path.join(self.tmp_dir, 'fwconfig.json')

            if src != target:
                copyfile(src, target)

        if program_cpld and res == 0:
            res = self.program_cpld(
                Path(self.tmp_dir).joinpath('cpld.jam').as_posix(), True)

        if program_mcu and res == 0:
            pdstopped = self.sbc.stop_service("pilotd", True)
            self.serial_used()
            res = self.program_mcu(
                Path(self.tmp_dir).joinpath('stm.bin').as_posix())

        if program_cpld and res == 0:
            res = self.program_cpld(
                Path(self.tmp_dir).joinpath('cpld.jam').as_posix())

        print(self.reset_pilot(bootmsg))
        if res == 0 and BinaryType.Variables in files:
            res = self.tryrun(
                'setting PLC variables', 4,
                'sudo cp {}/variables /proc/pilot/plc/varconfig'.format(
                    self.tmp_dir))
            self.tryrun(
                'setting PLC variables permanently', 4,
                'sudo mkdir -p /etc/pilot; sudo cp {}/variables /etc/pilot/variables'
                .format(self.tmp_dir))

        if res == 0 and BinaryType.Docs in files:
            res = self.tryrun(
                'saving firmware configuration file', 4,
                'sudo mkdir -p /etc/pilot; sudo cp {}/fwconfig.json /etc/pilot/fwconfig.json'
                .format(self.tmp_dir))

        if reload_driver:
            self.reload_drivers(True, pdstopped)

        return res, pdstopped

    def get_help(self):
        try:
            query = u"""
      {{
        modulehelp(modules: [{}]) {{
          number
          help
          examples {{title  example}}
        }}
      }}
      """.format(','.join([
                '{{number: {}, fid: "{}"}}'.format(key, value['fid'])
                for key, value in self.eeproms.items() if value['fid'] != ''
            ]))
            ret, obj = self.ps.query_graphql(query)
            if ret == 200 and obj['data'] and obj['data']['modulehelp']:
                return obj['data']['modulehelp']
        except:
            e = sys.exc_info()[0]
            print('Could not contact Pilot Nexus API to get help data')
            bugsnag.notify(e)
        return None
