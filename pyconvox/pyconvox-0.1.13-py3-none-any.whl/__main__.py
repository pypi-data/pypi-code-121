import argparse
import configparser
import os
import sys
import json
import subprocess
import re
import pyconvox


def Apps(args,apps,parser):
    stream = os.system(f"xovnoc apps")


def Env(args,apps,parser):
    if args.app:
        if args.app in apps:
            if args.set:
                stream = os.system(f"xovnoc env set {' '.join([ vars for vars in args.set])} -a {args.app}")
            else:
                stream = os.popen(f"xovnoc env -a {args.app}")
                envs = str(stream.read()).strip().split('\n')
                for envvar in envs:
                    print(f'{envvar}')
                # print(args.app)
        else:
            print("Wrong Application Name!!..\nPlease provide application name from the below")
            for index,appname in enumerate(apps):
                print(f"{index+1}. {appname}")
            print()
            parser.print_help()
    else:
        print('Please specify the application name using --app / -a <application_name>')


def Scale(args,apps,parser):
    if args.app:
        if args.app in apps:
            stream = os.system(f"xovnoc scale -a {args.app}")
        else:
            print("Wrong Application Name!!..\nPlease provide application name from the below")
            for index,appname in enumerate(apps):
                print(f"{index+1}. {appname}")
            print()
            parser.print_help()
    else:
        print('Please specify the application name using --app / -a <application_name>')

def PS(args,apps,parser):
    if args.app:
        if args.app in apps:
            stream = os.system(f"xovnoc ps -a {args.app}")
        else:
            print("Wrong Application Name!!..\nPlease provide application name from the below")
            for index,appname in enumerate(apps):
                print(f"{index+1}. {appname}")
            print()
            parser.print_help()
    else:
        print('Please specify the application name using --app / -a <application_name>')

def Releases(args,apps,parser):
    if args.app:
        if args.app in apps:
            stream = os.system(f"xovnoc releases -a {args.app}")
        else:
            print("Wrong Application Name!!..\nPlease provide application name from the below")
            for index,appname in enumerate(apps):
                print(f"{index+1}. {appname}")
            print()
            parser.print_help()
    else:
        print('Please specify the application name using --app / -a <application_name>')

def Logs(args,apps,parser):
    if args.app:
        if args.app in apps:
            stream = os.system(f"xovnoc logs -a {args.app}")
        else:
            print("Wrong Application Name!!..\nPlease provide application name from the below")
            for index,appname in enumerate(apps):
                print(f"{index+1}. {appname}")
            print()
            parser.print_help()
    else:
        print('Please specify the application name using --app / -a <application_name>')

def Instances(args,apps,parser):
        stream = os.system(f"xovnoc instances")



def RailsC(args,apps,parser):
    if args.app:
        if args.app in apps:
            if args.service:
                service=str(args.service)
            else:
                stream = os.popen(f"xovnoc scale -a {args.app} | grep -v SERVICE | grep -E 'web|rake' | awk '"+"{print $1}' | head -n 1")
                service = str(stream.read()).strip()
            print(service)
            stream = os.system(f"xovnoc run {service} 'rails c' -a {args.app}")
            # console = str(stream.read()).strip()
            print(stream)
        else:
            print("Wrong Application Name!!..\nPlease provide application name from the below")
            for index,appname in enumerate(apps):
                print(f"{index+1}. {appname}")
            print()
            parser.print_help()
    else:
        print('Please specify the application name using --app / -a <application_name>')

def Bash(args,apps,parser):
    if args.app:
        if args.app in apps:
            if args.service:
                service=str(args.service)
            else:
                stream = os.popen(f"xovnoc scale -a {args.app} | grep -v SERVICE | grep -E 'web|rake' | awk '"+"{print $1}' | head -n 1")
                service = str(stream.read()).strip()
            print(service)
            stream = os.system(f"xovnoc run {service} bash -a {args.app}")
            # console = str(stream.read()).strip()
            print(stream)
        else:
            print("Wrong Application Name!!..\nPlease provide application name from the below")
            for index,appname in enumerate(apps):
                print(f"{index+1}. {appname}")
            print()
            parser.print_help()
    else:
        print('Please specify the application name using --app / -a <application_name>')

def main():
    parser = argparse.ArgumentParser(prog="pyconvox",description='pyconvox - a wrapper for the convox application')
    parser.add_argument("--version","-V",action="version",version=f"%(prog)s version {pyconvox.__version__}",
    )
    subparsers = parser.add_subparsers(help='Commands')

    parser_a = subparsers.add_parser('env', help='list/set env vars')
    parser_a.add_argument('set', metavar='set', nargs='*', help='set environment variables KEY=VALUE')
    parser_a.add_argument('--app', '-a', help='application name')
    parser_a.set_defaults(which='env')

    parser_b = subparsers.add_parser('railsconsole', help='run rails console')
    parser_b.add_argument('--app', '-a', help='application name')
    parser_b.add_argument('--service', '-s', help='Service name')
    parser_b.set_defaults(which='railsconsole')
    parser_b.set_defaults(service='')

    parser_b = subparsers.add_parser('bash', help='run bash')
    parser_b.add_argument('--app', '-a', help='application name')
    parser_b.add_argument('--service', '-s', help='Service name')
    parser_b.set_defaults(which='bash')
    parser_b.set_defaults(service='')

    parser_c = subparsers.add_parser('scale', help='scale of a application')
    parser_c.add_argument('--app', '-a', help='application name')
    parser_c.set_defaults(which='scale')
    
    parser_d = subparsers.add_parser('instances', help='instances details of the rack')
    parser_d.set_defaults(which='instances')

    parser_d = subparsers.add_parser('apps', help='apps details of the rack')
    parser_d.set_defaults(which='apps')
    
    parser_e = subparsers.add_parser('logs', help='logs of a service')
    parser_e.add_argument('--app', '-a', help='application name')
    parser_e.set_defaults(which='logs')
    
    parser_f = subparsers.add_parser('releases', help='releases of a application')
    parser_f.add_argument('--app', '-a', help='application name')
    parser_f.set_defaults(which='releases')
    
    parser_g = subparsers.add_parser('ps', help='processes running for application')
    parser_g.add_argument('--app', '-a', help='application name')
    parser_g.set_defaults(which='ps')

    args = parser.parse_args()
    stream = os.popen("xovnoc apps | grep -v APP | awk '{print $1}'")
    apps = str(stream.read()).strip().split('\n')
    # print(apps)

    if hasattr(args, 'which'):
        if args.which == 'env':
            Env(args,apps,parser)
        elif args.which == 'railsconsole':
            RailsC(args,apps,parser)
        elif args.which == 'bash':
            Bash(args,apps,parser)
        elif args.which == 'scale':
            Scale(args,apps,parser)
        elif args.which == 'logs':
            Logs(args,apps,parser)
        elif args.which == 'instances':
            Instances(args,apps,parser)
        elif args.which == 'releases':
            Releases(args,apps,parser)
        elif args.which == 'ps':
            PS(args,apps,parser)
        elif args.which == 'apps':
            Apps(args,apps,parser)
        else:
            parser.print_help()


if __name__ == '__main__':
    main()