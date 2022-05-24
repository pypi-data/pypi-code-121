#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
import json
from distutils.dir_util import copy_tree
from shutil import copyfile, move
import yaml
import importlib.util
from .plc import Plc
from . import helper
import lazy_import
from colorama import Fore
Compiler = lazy_import.lazy_callable("pybars.Compiler")

def templateparser(args, dir, model, compiler, helpers):
  for subdir, dirs, files in os.walk(dir):
    outdir = os.path.join(args.workdir, os.path.relpath(subdir, dir))
    for file in files:
      infile = os.path.join(subdir, file)
      outfilename = os.path.basename(infile)
      with open(infile) as f:
        if infile.endswith('.templ'):
          template = compiler.compile(f.read())
          output = template(model, helpers)
          outfilename = outfilename[:-6] #.replace('.templ', '')
        else:
          output = f.read()
        with open(os.path.join(outdir, outfilename), 'w+') as f:
          f.write(output)  

def pluginparser(args, model, compiler, helpers):
  plugindir = os.path.join(args.workdir, 'plugins', 'template')
  if os.path.isdir(plugindir):
    #dirs = os.listdir(plugindir)
    #for dir in dirs:
    #  templateparser(args, os.path.join(plugindir, dir),  model, compiler, helpers )
    templateparser(args, plugindir,  model, compiler, helpers )

def _hex(this, items):
    return hex(items)

def parseplcvariables(varcsvfilepath ):
  with open(varcsvfilepath) as varcsvfile:
    content = [line.strip() for line in varcsvfile]

  mode = 'variables'
  variables = []
  for line in content:
    if line.startswith('//'): 
      mode = line[2:].strip().lower()
    else:
      columns = line.split(';')
      if mode == 'variables' and len(columns) >= 5:
        varname = columns[2].split('.')
        if len(varname) > 2 and varname[0].upper() == "CONFIG":
          var = {'number': int(columns[0]), 'location': columns[1], 'resource': varname[1], 'type': columns[4]}
          if len(varname) == 3:
            var['instance'] = None
            var['name'] = varname[2]
          elif len(varname) >= 4:
            var['instance'] = varname[2]
            var['name'] = '.'.join(varname[3:])
          variables.append(var)
  return variables

def createdoc(args, model, config):
  docfile = os.path.join(args.workdir, 'out/fwconfig.json') if args.workdir else './out/fwconfig.json'
  doc = { "modules": [], "variables": [] }

  # create module documentation
  for m in model['memmodules']:
    mod_cfg = next(iter([x for x in config['modules'] if x['slot'] == m['slot']]))
    n = mod_cfg['name'] if 'name' in mod_cfg else mod_cfg['device']['name']
    mem_doc = m['device']['spec'].mem_doc
    
    # add custom label
    if 'config' in mod_cfg and 'labels' in mod_cfg:
      for label in mod_cfg['labels']:
        was_found = False
        for dir in ['read', 'write']:
          found = next((x for x in mem_doc[dir] if x['name'] == label), None)
          if found:
            found['label'] = mod_cfg['labels'][label]
            was_found = True
        if not was_found:
          print(Fore.YELLOW + "Warning: Custom label '{}' defined in module {} could not be matched to a module property".format(label, m['slot']))
          print(Fore.YELLOW + "Possible label values are: " + ', '.join(list(map(lambda x: x['name'], mem_doc['read'])) + list(map(lambda x: x['name'], mem_doc['write']))))
  
    doc['modules'].append({
      "slot": m['slot'],
      "fid": m['fid'],
      "fid_nicename": m['fid_nicename'],
      "name": n,
      "doc": mem_doc
    })

  # create variable documentation
  varfile = os.path.join(args.workdir, 'out/VARIABLES.csv') if args.workdir else './out/VARIABLES.csv'
  doc['variables'] = parseplcvariables(varfile)

  with open((docfile), 'w') as f:
    json.dump(doc, f)

def main(args, version):
  parser = Compiler()
  helpers = {'hex': _hex}
  compilerdirectory = None
  if ('show_compilers' in args and args.show_compilers):
    helper.show_compilers()
  elif (args.fw_subparser_name == 'build'):

    # load config file
    config = helper.get_config(args)
    # load model file
    model = helper.get_model(args) 
    # get toplevel dir    
    projectdir = helper.find_fw_toplevel(args)

    if 'config' in config:
      model['config'] = config['config']

    for module in model['Modules']:
      configmodule = next( (x for x in config['modules'] if int(x['slot']) == module['Slot'] + 1 ), None)
      if configmodule:
        if configmodule['fid'] != module['Name']:
          print("Base firmware is not matching configuration on module {}. Basefirmware has '{}' but config has '{}'. Please update base firmware or change config.".format(module['Slot'] + 1, module['Name'], configmodule['fid']))
          exit(1)
      elif module['Name'] != 'None':
        print("WARNING: Base firmware has '{}' in module {}, but no configuration.".format(module['Name'], module['Slot'] + 1))

    compilers, directories = helper.get_compilers()
    for index, compiler in enumerate(compilers):
      if compiler['name'] == config['compiler']:
        compilerdirectory = directories[index]
    if compilerdirectory == None:
      print('Compiler {} defined in configuration file not found.'.format(config['compiler']))
      return 1

    # generate common C code for module I/O 
    plc = Plc(args, version, model, config, parser, helpers)
    templateparser(args, os.path.join(os.path.abspath(os.path.dirname(__file__)), 'compiler', 'template'), plc.model, parser, helpers)

    pluginparser(args, plc.model, parser, helpers)
    # language specific implementation for processing module I/O and custom logic
    spec = importlib.util.spec_from_file_location("module.name", os.path.join(compilerdirectory, 'compiler.py'))
    compiler = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(compiler)
    buildresult = compiler.main(args, config, model, projectdir, compilerdirectory)

    if buildresult == 0:
        #create documentation json
        createdoc(args, model, config)
     
  return buildresult      
