#! /usr/bin/env python
""" Dump configuration file """
import sys, os
from pydevmgr_elt import io 
from jinja2 import Template
from collections import namedtuple  
import argparse

usage = """%(prog)s DevType [dev_name] [options]

dump a yml configuration file to stdout. A device type is required e.g. Motor, Adc, etc ...
If no name is given %(prog)s will look at the current directory and increment the next available 
automatic name like motor1, motor2.

If the first argument start by "map" (e.g. "mapMotor") the matching map file is printed out 

If DevType is "Manager" a manager configuration file is printed with all the device present in the 
curent directory. So ``%(prog)s Manager` shall be called last. 

%(prog)s have some options but any config files has to be eddited to match device configuration.

Exemple 1 : Give a quick, but not transportable solution 

    > %(prog)s Motor motor1 > motor1.yml 
    > %(prog)s Motor motor2 > motor2.yml
    > %(prog)s Lamp > lamps.yml
    > %(prog)s Lamp >> lamps.yml 
    > %(prog)s Manager fcs1 > fcs1.yml

Exemple 2 :  define the relative directory to be transportable 

    > export CFGPATH=some/directory
    > mkdir $CFGPATH/fcs1
    > cd $CFGPATH/fcs1
    
    > %(prog)s mapMotor > mapMotor.yml
    > %(prog)s mapLamp > mapLamp.yml
    > %(prog)s Motor motor1 --address opc.tcp://192.168.1.28:4840 --cfgdir "fcs1" > motor1.yml
    > %(prog)s Motor motor2 --address opc.tcp://192.168.1.28:4840 --cfgdir "fcs1" > motor2.yml
    > %(prog)s Lamp  lamp1  --address opc.tcp://192.168.1.28:4840 --cfgdir "fcs1" > lamp.yml
    > %(prog)s Manager fcs1 --cfgdir "fcs1/server" > fcs1.yml 
 
"""

parser = argparse.ArgumentParser(prog='pydevmgr_dump', usage=usage)

parser.add_argument('args', nargs='+', help='type [name] e.g. "Motor"   "Motor motor1"')

parser.add_argument('--address', dest='address', default='opc.tcp://my_plc_address:4840', help='server opc-ua address')
parser.add_argument('--simaddr', dest='simaddr', default='opc.tcp://127.1.0.0:7578', help='simu server opc-ua address')
parser.add_argument('--prefix',  dest='prefix', default=None, help='OPC-UA device prefix e.g. MAIN.Motor1')
parser.add_argument('--cfgdir',  dest='cfgdir', default=None, help='Default config dir relative directory. If not given all path will be absolute and will point to the current directory. The map files will point to the default map file of pydevmgr package')
parser.add_argument('--fits_prefix',  dest='fits_prefix', default=None, help='fits prefix')
parser.add_argument('--iddentifier',  dest='iddentifier', default="PLC1", help='iddentifier shall be PLC1')


def explore_dir(cfgdir=None):
    
    Dev = namedtuple('Dev', ['name','type','file'])
    D = {}
    files = os.listdir(".")
    
    if cfgdir:
        cwd = cfgdir
    else: 
        cwd = os.getcwd()
    for file in files:
        _, ext = os.path.splitext(file)
        if ext not in [".yml", ".yaml"]: continue
        
        conf = io.read_config(file)
        if not isinstance(conf, dict): continue        
        if "server_id" in conf: continue # this is a manager 
        
        for name, subconf in conf.items():
            if not isinstance(subconf, dict): continue     
            try:
                tpe = subconf['type']
            except KeyError:
                continue 
            D.setdefault(tpe, {})[name] =  Dev(name, tpe, os.path.join(cwd, file))
    return D
        
             
def main():
    if len(sys.argv)==1:
        parser.print_help()        
        parser.exit()
    
    cargs = parser.parse_args()
    argv = cargs.args
    
    if not argv:
        parser.print_help()
        parser.exit()
    
    if argv[0].startswith('map'):
        if len(argv)>1:
            print("For a map file only one argument is needed")
            sys.exit(1)
        map_file = io.find_map(argv[0][3:])
        with open(map_file) as f:
            print(f.read())
            sys.exit(0)
    
    
    
    dev_type = argv[0].capitalize()
    template_file = io.find_template(dev_type)
    
    if dev_type=="Manager":
        d = explore_dir(cargs.cfgdir)
        devices = sum( (list(sub.values()) for sub in d.values()), [] )
    else:
        devices = []
    
    if cargs.cfgdir is None:
        cargs.cfgdir = os.getcwd()
        try:
            map_file = io.find_map(dev_type)
        except IOError:    
            map_file = "path/to/map"+dev_type+".yml"            
    else:
        map_file = os.path.join(cargs.cfgdir, "map"+dev_type+".yml")
    
        
    if len(argv)>=2:
        name = argv[1]
    elif dev_type=="Manager":
        name = "fcs"
    else:
        d = explore_dir(cargs.cfgdir)
        if dev_type not in d: 
            name = dev_type.lower()+"1"
        else:
            devs = list(d[dev_type].keys())
            num = 1
            while dev_type.lower()+str(num) in devs:
                num += 1 
            name = dev_type.lower()+str(num)    
    
    if cargs.prefix is None:
        cargs.prefix = "MAIN."+name.capitalize()
    
    if cargs.fits_prefix:
        cargs.fits_prefix = name.upper()    
                    
    with open(template_file, 'r') as f:
        print(Template(f.read()).render(name=name, address=cargs.address, prefix=cargs.prefix, 
                                        cfgdir=cargs.cfgdir, map_file=map_file, devices=devices))


if __name__ == "__main__":
    main()

