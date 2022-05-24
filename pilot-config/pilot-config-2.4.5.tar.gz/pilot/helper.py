import os
import json
import yaml
import hashlib
BLOCKSIZE = 65536

def get_node_from_config(args):
  #check if a .pilotfwconfig.json file exists and extract nodes
  config = get_config(args)
  if 'nodes' in config and isinstance(config['nodes'], list):

    specified_node = args.name if 'name' in args and args.name is not None else 'default'
    for node in config['nodes']:
      nodesfromconfig = True
      args.node = node['node']
      if 'user' in node:
        args.user = node['user']
      if 'user' in node:
        args.password = node['password']
      if 'hardware' in node:
        args.hardware = node['hardware']
      if specified_node == node['name']:
        print("Using node '{}'".format(specified_node))
        break
  
  return args
def update_firmware_version_in_config(args, version):
  config = get_config(args)
  config['firmware_version'] = version
  save_config(args, config)

def find_fw_toplevel(args):
  dir = args.workdir if args.workdir else os.getcwd() 
  olddir = ''
  while dir != olddir:
    olddir = dir
    if os.path.isfile(os.path.join(dir, '.pilotfwconfig.json')):
      return dir
    dir = os.path.abspath(os.path.join(dir, '..'))
  return ''

def get_compilers():
  compilers = []
  directories = []
  for subdir, dirs, files in os.walk(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'compiler')):
    for dir in dirs:
      if not dir.startswith("_"): #ignore dirs with underscore (to disable non-functioning compilers)
        compilerinfofile = os.path.join(subdir, dir, 'template.yml')
        if os.path.isfile(compilerinfofile):
          with open(compilerinfofile, 'r') as f:
            try:
              compilers.append(yaml.load(f.read(), Loader=yaml.FullLoader))
              directories.append(os.path.join(subdir, dir))
            except Exception as e: 
              print('Error parsing {}'.format(compilerinfofile))
              print(e)
  return compilers, directories

def show_compilers():
  compilers, _ = get_compilers()
  for compiler in compilers:
    print('{}: {} (extension: {})'.format(compiler['name'], compiler['description'], compiler['filter']))

def save_config(args, config):
    with open(os.path.join(args.workdir, '.pilotfwconfig.json') if args.workdir else './.pilotfwconfig.json', 'w') as configfile:
      json.dump(config, configfile)

def get_config(args):
  try:
    if args.configfile == None:
      configfile = os.path.join(args.workdir, '.pilotfwconfig.json') if args.workdir else './.pilotfwconfig.json'
      if os.path.isfile(configfile):
        args.configfile = configfile
      else:
        configfile = os.path.join(find_fw_toplevel(args), '.pilotfwconfig.json')
        if os.path.isfile(configfile):
          args.configfile = configfile
        else:
          args.configfile = os.environ['PILOT_CONFIG']
        
    if os.path.isfile(args.configfile):
      hasher = hashlib.sha1()
      with open(args.configfile) as configfile:
        config = json.load(configfile)

      with open(args.configfile, 'rb') as afile:
          buf = afile.read(BLOCKSIZE)
          while len(buf) > 0:
              hasher.update(buf)
              buf = afile.read(BLOCKSIZE)
      
      print('Using config file {}, SHA1={}'.format(args.configfile, hasher.hexdigest()))

      return config
    else:
      print("Configuration file (usually .pilotfwconfig.json) not found, exiting")
      exit(1)
  except:
    print("Error reading configuration file. Check if it is valid JSON")
    exit(1)

def get_model(args):
  model = {}
  #if no source path parameter is given try the environment var
  if args.source == None:
    try:
      source = os.path.join(args.workdir, 'basefw/stm') if args.workdir else './basefw/stm'
      if os.path.isdir(source):
        args.source = source
      else: 
        args.source = os.environ['PILOT_SOURCE']
    except:
      print("No parameter source directory given, no './basefw/stm' folder found and no PILOT_SOURCE environment variable defined, exiting")
      exit(1) 
  with open(os.path.join(os.path.abspath(args.source), 'stmmodel.json')) as stmmodelfile:
    model.update(json.load(stmmodelfile))
    model['devices'] = []
  return model