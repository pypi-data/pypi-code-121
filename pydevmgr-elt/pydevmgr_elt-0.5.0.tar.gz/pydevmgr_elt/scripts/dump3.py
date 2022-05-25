#! /usr/bin/env python
""" Dump configuration file """
import sys, os
from pydevmgr_elt import io 
from jinja2 import Template
from collections import namedtuple  
from typer import Argument, echo, run , Option
from pydantic import BaseModel, Field
from pydantic_cli import run_and_exit, to_runner

print(sys.argv)
class Config(BaseModel):
    dtype: str
    #dtype: str = Field(..., description="Device type e.g. Manager, Motor, Lamp, ... if type start by map a map file is printed instead, e.g. mapMotor")
    name: str = Field(None, description="Device name")
    address: str = Field('opc.tcp://my_plc_address:4840', description="OPC-UA server address") 
    simaddr: str = Field('opc.tcp://127.1.0.0:7578', description="simulator address") 
    prefix: str = Field(None, description="Device prefix") 
    cfgdir: str = Field(None, description="Default configuration directory") 
    fits_prefix: str = Field(None, description="fits Prefix")
    iddentifier: str = Field("PLC1", description="PLC iddentifier")
    

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
        
             
def main(c: Config):
    
    if c.dtype.startswith('map'):
        if c.name:
            print("For a map file only one argument is needed")
            return 1
        map_file = io.find_map(c.dtype[3:])
        with open(map_file) as f:
            print(f.read())
            return 0
    
    
    
    template_file = io.find_template(c.dtype)
    
    if c.dtype=="Manager":
        d = explore_dir(c.cfgdir)
        devices = sum( (list(sub.values()) for sub in d.values()), [] )
    else:
        devices = []
    
    if c.cfgdir is None:
        c.cfgdir = os.getcwd()
        try:
            map_file = io.find_map(c.dtype)
        except IOError:    
            map_file = "path/to/map"+c.dtype+".yml"            
    else:
        map_file = os.path.join(c.cfgdir, "map"+c.dtype+".yml")
    
    if not c.name:
        if c.dtype=="Manager":    
            c.name = "fcs"
    
        else:
            d = explore_dir(c.cfgdir)
            if c.dtype not in d: 
                c.name = c.dtype.lower()+"1"
            else:
                devs = list(d[c.dtype].keys())
                num = 1
                while c.dtype.lower()+str(num) in devs:
                    num += 1 
                c.name = c.dtype.lower()+str(num)    
    
    if c.prefix is None:
        c.prefix = "MAIN."+c.name.capitalize()
    
    if c.fits_prefix:
        c.fits_prefix = c.name.upper()    
                    
    with open(template_file, 'r') as f:
        echo(
          Template(f.read()).render(
           name=c.name, 
           address=c.address, prefix=c.prefix, 
           cfgdir=c.cfgdir, map_file=map_file, 
           devices=devices
          )
        )


if __name__ == "__main__":
    run_and_exit(Config, main, description="dump yaml configuration file")

