import os
from .pilotdriver import PilotDriver

def setup_arguments(parser):
  parser.add_argument('--fw-version', '-f', dest='fwversion',
                  help='Specify firmware version, latest is used if not specified')
  parser.add_argument('--workdir', '-d', default=os.getcwd(), dest='workdir',
                  help='Set working directory')
  parser.add_argument('--wait_bootmsg', '-w', dest='wait_bootmsg', action='store_true',
                         help='Wait for Pilot boot message and display after reboot')
  parser.add_argument('--source', '-c', default=None, dest='source',
                      help='Download Sourcecode only')
  parser.add_argument('--regnode', '-n', dest='regnode', action='store_true',
                      help='Register node')
  #parser.add_argument('--reset', '-r', default=None, action='store_const', const='reset', dest='reset',
  #                    help='Resets the Pilot Mainboard')
  parser.add_argument('--yes', '-y', default=None, action='store_const', const='noninteractive', dest='noninteractive',
                      help='Confirms default action (non-interactive mode)')
  parser.add_argument('--driveronly', '-x', default=None, action='store_const', const='driveronly', dest='driveronly',
                      help='Installs driver only')
  for mod in range(1, PilotDriver.MODULE_COUNT+1):
    parser.add_argument('--module{}'.format(mod), '-m{}'.format(mod), dest='m{}'.format(mod), help='Firmware id of module {}'.format(mod))
    
def reset_arguments(parser):
  parser.add_argument('--wait_bootmsg', '-w', dest='wait_bootmsg', action='store_true',
                         help='Wait for Pilot boot message and display after reboot')

def module_arguments(parser):
  parser.add_argument('module', metavar='N', type=int,
                    help='module number')
  parser.add_argument('--pinout', help='Show Module Pinout', action='store_true')
  parser.add_argument('--usage', help='Show Module Usage Examples', action='store_true')

def program_arguments(parser):
  parser.add_argument('--fw-version', '-f', dest='fwversion',
                  help='Specify firmware version, latest is used if not specified')
  parser.add_argument('--workdir', '-d', default=os.getcwd(), dest='workdir',
                  help='Set working directory')
  parser.add_argument('--wait_bootmsg', '-w', dest='wait_bootmsg', action='store_true',
                         help='Wait for Pilot boot message and display after reboot')
  parser.add_argument('name', metavar='node', type=str, nargs='?',
                      help='Specify named node to program')
  parser.add_argument('--binary', '-b', default=None, dest='bin',
                      help='Write binary image to the Pilot Microcontroller')
  parser.add_argument('--logicbinary', '-l', default=None, dest='logicbin',
                      help='Write bitstream to the Pilot CPLD')
  parser.add_argument('--variables', '-v', default=None, dest='vars',
                      help='Set PLC variables')
  parser.add_argument('--doc', default=None, dest='doc',
                      help='set firmware config file')
  parser.add_argument('--config', dest='configfile',
                    default=None, help='module config file (.pilotfwconfig.json)')
  parser.add_argument('--mcuonly', action='store_const', default=False,
                      const=True, help='Program MCU only')

def compiler_arguments(parser):
  parser.add_argument('--fw-version', '-f', dest='fwversion',
                  help='Specify firmware version, latest is used if not specified')
  parser.add_argument('--workdir', '-d', default=os.getcwd(), dest='workdir',
                  help='Set working directory')
  parser.add_argument('--wait_bootmsg', '-w', dest='wait_bootmsg', action='store_true',
                         help='Wait for Pilot boot message and display after reboot')
  parser.add_argument('--config', dest='configfile',
                      default=None, help='module config file (.pilotfwconfig.json)')
  parser.add_argument('--iec2c', dest='iec2cdir',
                      default=None, help='directory of iec2c compiler')
  parser.add_argument('--source', dest='source',
                      default=None, help='source directory')
  parser.add_argument('--target', dest='target',
                      default=None, help='target directory')
  parser.add_argument('--verbose', action='store_const',
                      const=True, help='verbose output')
  parser.add_argument('files', nargs='*', default=None,
                      help='IEC Structured Text File')

def project_arguments(parser):
  parser.add_argument('--fw-version', '-f', dest='fwversion',
                  help='Set working directory')
  parser.add_argument('--workdir', '-d', default=os.getcwd(), dest='workdir',
                  help='Set working directory')
  parser.add_argument('--wait_bootmsg', '-w', dest='wait_bootmsg', action='store_true',
                         help='Wait for Pilot boot message and display after reboot')
  parser.add_argument('--compiler', dest='compiler', help='Specify compiler to use. Run --show-compilers to get a list of options')
  parser.add_argument('--config', dest='configfile',
                      default=None, help='module config file (.pilotfwconfig.json)')
  parser.add_argument('name', metavar='node', type=str, nargs='?',
                      help='Specify named node to update firmware code (node is not reprogrammed, it is just used to get the modules)')
  parser.add_argument('--local', '-l', dest='local', action='store_true',
                  help='Use local instead of github template')
  for mod in range(1, PilotDriver.MODULE_COUNT+1):
    parser.add_argument('--module{}'.format(mod), '-m{}'.format(mod), dest='m{}'.format(mod), help='Firmware id of module {}'.format(mod))
      