import os
import json
import argparse

from pilot.grpc_gen.pilotbuild_pb2 import BinaryType
from . import arguments
from . import helper 
from .sbc import Sbc
from .pilotserver import PilotServer
from .pilotdriver import PilotDriver


def main(args):
  args = helper.get_node_from_config(args)
  program(args)

def program(args):
  try:
    with Sbc(args) as sbc:
      # PilotServer
      pilotserver = PilotServer(sbc)
      if args.server != None:
        pilotserver.pilot_server = args.server
      
      #PilotDriver
      pilotdriver = PilotDriver(pilotserver, sbc)

      if not pilotdriver.driver_loaded():
        print('Drivers are not loaded. Please use --node to specify node IP if you connect remotely or install pilot drivers first by running sudo pilot setup.')
        return 2

      #if not pilotdriver.check_raspberry() and not args.node:
      #  print('This does not seem to be a Raspberry Pi. Please use the --node option to remote connect to it.')
      #  return 2

      if args.vars:
        if not os.path.isfile(args.vars):
          print('You need to specify a valid file for the --variables attribute.')
          exit(1)
      else:
        args.vars = os.path.join(args.workdir, 'out/VARIABLES.csv') if args.workdir else './out/VARIABLES.csv'
        if os.path.isfile(args.vars):
          print('Using variable file ' + args.vars)

      if args.doc:
        if not os.path.isfile(args.doc):
          print('You need to specify a valid doc (fwconfig.json) file for the --doc attribute.')
          exit(1)
      else:
        args.doc = os.path.join(args.workdir, 'out/fwconfig.json') if args.workdir else './out/fwconfig.json'
        if os.path.isfile(args.doc):
          print('Using documentation file ' + args.doc)

      if args.bin:
        if not os.path.isfile(args.bin):
          print('You need to specify a valid file for the --binary attribute.')
          exit(1)
      elif os.path.isfile(os.path.join(args.workdir, 'out/stm.bin') if args.workdir else './out/stm.bin'):
        args.bin = os.path.join(args.workdir, 'out/stm.bin') if args.workdir else './out/stm.bin'
      else:
        print('You need to specify an image file to write with the --binary attribute.')
        exit(1)

      if args.logicbin:
        if not os.path.isfile(args.logicbin):
          print('You need to specify a valid CPLD file for the --logicbinary attribute.')
          exit(1)
      elif os.path.isfile(os.path.join(args.workdir, 'basefw/cpld/output_files/cpld.jam') if args.workdir else './basefw/cpld/output_files/cpld.jam'):
        args.logicbin = os.path.join(args.workdir, 'basefw/cpld/output_files/cpld.jam') if args.workdir else './basefw/cpld/output_files/cpld.jam'
      else:
        print('You need to specify an image file to write with the --logicbinary attribute.')
        exit(1)

      files = {
          BinaryType.MCUFirmware: args.bin,
          BinaryType.FPGABitstream: args.logicbin,
          BinaryType.Variables: args.vars,
          BinaryType.Docs: args.doc
      }
      pilotdriver.program(files, program_cpld=not (args.mcuonly==True), program_mcu=True, bootmsg=args.wait_bootmsg, reload_driver=not (args.mcuonly==True)) #only reload driver if cpld is programmed (indicates hardware change)
  except Exception as error:
    print(error)

if (__name__ == "__main__"):
  parser = argparse.ArgumentParser(
    description='Write custom firmware')
  arguments.program_arguments(parser)
  main(parser.parse_args())