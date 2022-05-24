#!/usr/bin/env python3
import lazy_import

import argparse
import os
import sys
import cryptography

# needed until paramiko is fixed
import warnings
from cryptography import utils

try:
  warnings.simplefilter("ignore", cryptography.utils.CryptographyDeprecationWarning)
except:
  pass
  
bugsnag = lazy_import.lazy_module("bugsnag")

from . import arguments

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'VERSION'), 'r') as myfile:
    version=myfile.read().replace('\n', '')

def my_except_hook(exectype, value, traceback):
  if exectype == KeyboardInterrupt:
    print("Keyboard Interrupt, cancelling. Bye!")
    exit(3)
  else:
    bugsnag.notify(Exception('Unhandled Exception, type: {}, value: {}, traceback: {}'.format(exectype, value, traceback)))
    sys.__excepthook__(exectype, value, traceback)

sys.excepthook = my_except_hook

def main():
  with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'VERSION'), encoding='utf-8') as f:
    VERSION = f.read().strip()

  bugsnag.configure(
      api_key="2d614bb3561d92fbd3b6f371e39b554a",
      project_root=".",
      app_version=VERSION,
      release_stage='production'
  )

  sys.excepthook = my_except_hook

  # Parent parser for common arguments
  parent_parser = argparse.ArgumentParser(add_help=False)
  parent_parser.add_argument('--hardware', dest='hardware', #choices=[el['name'] for el in targethardwarelist],
                         help='set target hardware')
  parent_parser.add_argument('--server', '-s', default=None, dest='server',
                  help='Alternative URL for the pilot server API to contact')
  parent_parser.add_argument('--node', '-o', default=None, dest='node',
                         help='Node to configure remotely')
  parent_parser.add_argument('--user', '-u', default='pi', dest='user',
                         help='Remote SSH User')
  parent_parser.add_argument('--password', '-p', nargs='?', const='password_was_not_given', dest='password',
                         help='Remote SSH Password')
  parent_parser.add_argument('--sshkey', '-k', nargs='?', default='~/.ssh/id_rsa.pub', dest='sshkey_file',
                         help='public key file')

  argparser = argparse.ArgumentParser(description='Pilot Command-Line Interface')
  argparser.add_argument('-v', '--version', dest='version',action='store_true',
                         help='Get version')

  # Subparsers
  subparsers = argparser.add_subparsers(dest='subparser_name')

  # Setup Subparser
  parser_a = subparsers.add_parser('setup', parents=[parent_parser], help="Configure Pilot firmware")
  arguments.setup_arguments(parser_a)

  parser_r = subparsers.add_parser('reset', parents=[parent_parser], help="Reset Pilot Mainboard")
  arguments.reset_arguments(parser_r)

  parser_m = subparsers.add_parser('module', parents=[parent_parser], help="Get info on modules")
  arguments.module_arguments(parser_m)

  # Firmware subparser
  parser_b = subparsers.add_parser('fw', parents=[parent_parser], help="Init/Build/Program custom firmware")
  parser_b.add_argument('--show-toplevel', dest='show_toplevel', action='store_true',
                        help='show top level folder of firmware project')
  parser_b.add_argument('--show-compilers', dest='show_compilers', action='store_true', help='List all installed compilers for additional firmware (excluding C compiler, this compiler is always installed)')

  fw_subparser = parser_b.add_subparsers(dest='fw_subparser_name')

  parser_d_a = fw_subparser.add_parser('init', parents=[parent_parser], help="Initialize a new firmware project")
  arguments.project_arguments(parser_d_a)

  parser_d_b = fw_subparser.add_parser('update', parents=[parent_parser], help="Update base firmware in project")
  arguments.project_arguments(parser_d_b)

  parser_b_b = fw_subparser.add_parser('build', parents=[parent_parser], help="Compile additional software into firmware (IEC 61131-3 or Rust)")
  arguments.compiler_arguments(parser_b_b)

  parser_b_c = fw_subparser.add_parser('program', parents=[parent_parser], help="Remote program Pilot Mainboard")
  arguments.program_arguments(parser_b_c)

  args = argparser.parse_args()

  if args.version:
    print(VERSION)
  #elif args.modules:
  #  from . import moduleinfo
  #  sys.exit(moduleinfo.main(args))
  elif ('subparser_name' in args):
    if (args.subparser_name == 'setup'):
      from . import pilotsetup
      sys.exit(pilotsetup.main(args))
    elif (args.subparser_name == 'reset'):
      from . import reset
      sys.exit(reset.main(args))
    elif (args.subparser_name == 'module'):
      from .modulehelp  import ModuleHelp
      helper = ModuleHelp()
      sys.exit(helper.help(args))
    elif (args.subparser_name == 'fw'):
      if 'fw_subparser_name' in args and args.fw_subparser_name == 'build':
        from . import build
        sys.exit(build.main(args, VERSION))
      elif 'fw_subparser_name' in args and args.fw_subparser_name == 'program':
        from . import program
        sys.exit(program.main(args))
      elif 'fw_subparser_name' in args and (args.fw_subparser_name == 'init' or args.fw_subparser_name == 'update'):
        from . import project
        sys.exit(project.main(args, VERSION, args.fw_subparser_name))
    else:
      print('No parameters specified, running setup.')
      from . import pilotsetup
      sys.exit(pilotsetup.main(parser_a.parse_args()))

if __name__ == '__main__':
  main()
