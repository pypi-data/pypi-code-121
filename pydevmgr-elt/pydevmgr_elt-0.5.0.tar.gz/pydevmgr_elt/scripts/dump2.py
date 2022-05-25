#! /usr/bin/env python
""" Dump configuration file """
import sys, os
from pydevmgr_elt import io 
from jinja2 import Template
from collections import namedtuple  
from typer import Argument, echo, run , Option

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
        
             
def _main(
      dtype: str = Argument(..., help="Device type e.g. Manager, Motor, Lamp, ... if type start by map a map file is printed instead, e.g. mapMotor"),
      name: str = Argument(None, help="Device name, default will be dtype# "),
      address: str = Option('opc.tcp://my_plc_address:4840', help="OPC-UA server address"), 
      simaddr: str = Option('opc.tcp://127.1.0.0:7578', help="simulator address"), 
      prefix: str = Option(None, help="Device prefix"), 
      cfgdir: str = Option(None, help="Default configuration directory"), 
      fits_prefix: str = Option(None, help="fits Prefix"),
      iddentifier: str = Option("PLC1", help="PLC iddentifier"),  
    ):
    """
    dump a yml configuration file to stdout. 

    If the first argument start by "map" (e.g. "mapMotor") the matching map file is printed out 

    If DevType is "Manager" a manager configuration file is printed with all the device present in the 
    curent directory. 
        
    """
    if dtype.startswith('map'):
        if name:
            print("For a map file only one argument is needed")
            return 1
        map_file = io.find_map(dtype[3:])
        with open(map_file) as f:
            print(f.read())
            return 0
    
    dtype = dtype.capitalize()
    
    template_file = io.find_template(dtype)
    
    if dtype=="Manager":
        d = explore_dir(cfgdir)
        devices = sum( (list(sub.values()) for sub in d.values()), [] )
    else:
        devices = []
    
    if cfgdir is None:
        cfgdir = os.getcwd()
        try:
            map_file = io.find_map(dtype)
        except IOError:    
            map_file = "path/to/map"+dtype+".yml"            
    else:
        map_file = os.path.join(cfgdir, "map"+dtype+".yml")
    
    if not name:
        if dtype=="Manager":    
            name = "fcs"
    
        else:
            d = explore_dir(cfgdir)
            if dtype not in d: 
                name = dtype.lower()+"1"
            else:
                devs = list(d[dtype].keys())
                num = 1
                while dtype.lower()+str(num) in devs:
                    num += 1 
                name = dtype.lower()+str(num)    
    
    if prefix is None:
        prefix = "MAIN."+name.capitalize()
    
    if fits_prefix:
        fits_prefix = name.upper()    
                    
    with open(template_file, 'r') as f:
        echo(
          Template(f.read()).render(
           name=name, 
           address=address, prefix=prefix, 
           cfgdir=cfgdir, map_file=map_file, 
           devices=devices
          )
        )
_main.__doc__ = _main.__doc__ .format(prog="pydevmgr_dump")


def main():
    run(_main)

if __name__ == "__main__":
    main()

