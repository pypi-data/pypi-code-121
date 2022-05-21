#!/usr/bin/env python3

from __future__ import print_function  # disables annoying pylint print warning

import lazy_import

from pilot.grpc_gen.pilotbuild_pb2 import BinaryType
from . import arguments

sys = lazy_import.lazy_module("sys")
json = lazy_import.lazy_module("json")
re = lazy_import.lazy_module("re")
shlex = lazy_import.lazy_module("shlex")
time = lazy_import.lazy_module("time")
os = lazy_import.lazy_module("os")
argparse = lazy_import.lazy_module("argparse")
base64 = lazy_import.lazy_module("base64")
gettext = lazy_import.lazy_module("gettext")
bugsnag = lazy_import.lazy_module("bugsnag")
logging = lazy_import.lazy_module("logging")
paramiko = lazy_import.lazy_module("paramiko")

from uuid import getnode as get_mac
from bugsnag.handlers import BugsnagHandler
from threading import Thread
from colorama import Fore
from colorama import Style
from colorama import init

# class imports
from .pilotdriver import PilotDriver
from .pilotserver import PilotServer
from .sbc import Sbc

############### INIT ###################

init(autoreset=True)  # colorama color autoreset

DEBUG = False
EXECVP_ENABLED = False

############## PROC FILE ACCESS #####################


def main(args):

    logger = logging.getLogger()
    handler = BugsnagHandler()
    # send only ERROR-level logs and above
    handler.setLevel(logging.ERROR)
    logger.addHandler(handler)

    logging.getLogger("paramiko").setLevel(logging.ERROR)

    trywritedefaultfirmware = False
    result = 0
    try:
        with Sbc(args) as sbc:
            # PilotServer
            pilotserver = PilotServer(sbc)
            if args.server != None:
                pilotserver.pilot_server = args.server

            #PilotDriver
            pilotdriver = PilotDriver(pilotserver, sbc)

            #if not pilotdriver.check_raspberry() and not args.node:
            #  print('This does not seem to be a Raspberry Pi. Please use the --node option to remote connect to it.')
            #  return 2

            if not args.node and os.getuid() != 0:
                print('Please run with sudo permissions.')
                return 2

            if not args.regnode:
                if sbc.need_sudo_pw():
                    print(
                        'we need sudo on remote machine (without interactive authentication)'
                    )
                    return 2

                ret = pilotdriver.check_driver()
                if ret != 0:
                    if ret == 1:
                        if args.node:
                            print('Reboot of remote Node required')
                        else:
                            print('Reboot required')
                        ch = input("Do you want to reboot now? [y/n]: ")
                        if (ch == 'y' or ch == 'yes'):
                            sbc.reboot()
                        return 0
                    return 1

                # do not continue if driveronly is specified
                if args.driveronly:
                    return 0

                modules, success = pilotdriver.load_pilot_defs()
                if not success:
                    print(
                        Fore.YELLOW + 
                        'Could not read module data. Maybe the firmware is outdated, trying to write base firmware image.'
                    )
                    trywritedefaultfirmware = True
                if modules != None:
                    if args.source == None:
                        while (True):
                            print()
                            modules_with_multiple_fids = []
                            for module in modules:
                                multiple_fids = len(module['fids']) > 1
                                if multiple_fids:
                                    modules_with_multiple_fids.append(
                                        int(module['module']))
                                if not trywritedefaultfirmware:
                                    print('Module {}: {}{} {}'.format(
                                        module['module'], Fore.GREEN,
                                        module['currentfid_nicename'],
                                        '*' if multiple_fids else ''))

                            ch = ''
                            modsel = '/'.join(
                                [str(x) for x in modules_with_multiple_fids])
                            if len(modules_with_multiple_fids) > 0:
                                print(
                                    'Modules marked with an Asterisk (*) have multiple firmware configurations'
                                )
                                print(
                                    'Press Module Number [{}] to change selected firmware.'
                                    .format(modsel))
                            if (args.noninteractive
                                    or trywritedefaultfirmware):
                                ch = 'y'
                            else:
                                ch = input(
                                    'Do you want to build and program the Pilot Nexus Firmware? [y/n{}]: '
                                    .format('/' + modsel if
                                            len(modules_with_multiple_fids) > 0
                                            else '')).strip().lower()
                            if ch == 'y' or ch == 'yes':
                                version, files = pilotdriver.build(args.fwversion)
                                print('Firmware version: {}'.format(version))
                                if BinaryType.MCUFirmware in files:
                                    result = pilotdriver.program(
                                        files,
                                        bootmsg=args.wait_bootmsg)
                                else:
                                    print('Could not write firmware, no MCU firmware found')

                                break
                            elif ch.isdigit() and int(ch) in range(
                                    1, pilotdriver.MODULE_COUNT +
                                    1) and len(modules_with_multiple_fids) > 0:
                                changemodulenr = int(ch)
                                print()
                                print('Select Firmware for Module {}:'.format(
                                    changemodulenr))
                                for idx, fid in enumerate(
                                        modules[changemodulenr - 1]['fids']):
                                    print('{}. {}{}'.format(
                                        idx + 1, Fore.GREEN, fid['name']))
                                ch = input('0=Cancel, [1-{}]: '.format(
                                    len(modules[changemodulenr - 1]['fids'])))
                                if (ch.isdigit() and int(ch) > 0 and
                                        int(ch) <= len(modules[changemodulenr -
                                                               1]['fids'])):
                                    pilotdriver.set_module_fid(
                                        changemodulenr,
                                        modules[changemodulenr -
                                                1]['fids'][int(ch) - 1]['fid'])
                                    modules, success = pilotdriver.load_pilot_defs(
                                    )
                            else:
                                break

                    else:
                        version, success = pilotdriver.get_firmware_source(os.path.abspath(args.source), args.fwversion)

                else:
                    print('No modules found, is the driver loaded?')
                fwconfig = {}
                fwconfig['modules'] = modules

                #check if node is registered
                #if not trywritedefaultfirmware:
                #  if pilotserver.decoded == None:
                #    ch = input("You not logged in to access the Pilot Nexus Cloud, do you want to authenticate? [y/n]: ")
                #    if (ch == 'y' or ch == 'yes'):
                #      pilotserver.authenticate()

                #  if pilotserver.decoded != None:
                #    node = pilotserver.getnode()
                #    if node != None:
                #      print("Your node is registered as '{}'".format(node['name']))
                #      pilotserver.updatenode(fwconfig)

                #    elif not args.noninteractive and not trywritedefaultfirmware:
                #      ch = input("Node is not registered, do you want to register it with the Pilot Cloud? [y/n]: ")
                #      if (ch == 'y' or ch == 'yes'):
                #        pilotserver.registernode(fwconfig)

            #elif not args.noninteractive: # --regnode param
            #  pilotserver.registernode(None)
    except Exception as error:
        print(error)
        exit(1)

    if result == 0:
        if trywritedefaultfirmware:
            print(
                "Default firmware written. Run the setup tool again to program firmware for your modules"
            )
        #else:
        #  print ("To get help on how to use the modules, run 'pilot --module'")
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Setup Pilot Nexus')
    arguments.setup_arguments(parser)
    sys.exit(main(parser.parse_args()))
