#!flask/bin/python
import os, argparse

from utils.api import route, api, Parameter

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Alpha', description='', epilog='')
    parser.add_argument('--prod', '-p', action='store_true', help='Prod mode')
    parser.add_argument('--debug', '-d', action='store_true', help='Debug mode')
    parser.add_argument('--test', '-t', action='store_true', help='Test mode')
    parser.add_argument('--start', '-s', action='store_true', help='Start api')
    parser.add_argument('--stop', '-k', action='store_true', help='Stop api')
  
    args                    = parser.parse_args()

    if args.start:
        api.start(config_path='api',debug=True)
        
    if args.stop:
        api.stop(config_path='api')