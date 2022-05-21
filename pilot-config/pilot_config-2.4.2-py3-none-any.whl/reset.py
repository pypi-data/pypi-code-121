import os
import lazy_import

from bugsnag.handlers import BugsnagHandler
from colorama import init

logging = lazy_import.lazy_module("logging")
# class imports
from .pilotdriver import PilotDriver
from .pilotserver import PilotServer
from .sbc import Sbc

############### INIT ###################

init(autoreset=True)  # colorama color autoreset

DEBUG = False
EXECVP_ENABLED = False

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

            if not args.node and os.getuid() != 0:
                print('Please run with sudo permissions.')
                return 2

            if sbc.need_sudo_pw():
                print(
                    'we need sudo on remote machine (without interactive authentication)'
                )
                return 2

            print('Resetting Pilot Mainboard')
            print(pilotdriver.reset_pilot(args.wait_bootmsg))
            return 0
    except:
        print("Error resetting Pilot Mainboard")
        return 1