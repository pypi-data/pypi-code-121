import argparse

# class imports
from .pilotdriver import PilotDriver
from .pilotserver import PilotServer
from .sbc import Sbc

from colorama import Fore
from colorama import Style
from colorama import init


def arguments(parser):
  # parser.add_argument('--terminal', '-t', action='store_true', help='forces the terminal version instead of GUI')
  parser.add_argument('--help', '-h', default=None, dest='source',
                      help='Get help on modules')

def main(args):
  try:
    with Sbc(args) as sbc:
      pilotserver = PilotServer(sbc)
      if 'server' in args and args.server != None:
        pilotserver.pilot_server = args.server
      
      #PilotDriver
      pilotdriver = PilotDriver(pilotserver, sbc)

      if not pilotdriver.driver_loaded():
        print('Drivers are not loaded. Please use --node if you connect remotely or install pilot drivers first by running sudo pilot setup.')
        return 2

      #if not pilotdriver.check_raspberry() and not args.node:
      #  print('This does not seem to be a Raspberry Pi. Please use the --node option to remote connect to it.')
      #  return 2

      if sbc.need_sudo_pw():
        print('we need sudo on remote Node (without interactive authentication)')
        return 2

      modules, success = pilotdriver.load_pilot_defs()
      
      if not success:
        print('Could not get module data.')
        return 1

      #Print module help
      moduleinfos = pilotdriver.get_help()

      if moduleinfos:
        for module in moduleinfos:
          print()
          print(Fore.GREEN + 'Module [{}] {}:'.format(module['number'], modules[module['number']-1]['currentfid_nicename']))
          print(module['help'])
          if module['examples'] and len(module['examples']) > 0:
            for idx,example in enumerate(module['examples']):
              print(Fore.CYAN + 'Example {}: {}'.format(idx+1, example['title']))
              print(example['example'])
  except Exception as error:
    print(error)
    exit(1)
  return 0
        
if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Module Info')
  arguments(parser)
  main(parser.parse_args())