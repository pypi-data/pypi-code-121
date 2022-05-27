#!/usr/bin/env python3
import os
import sys
import subprocess
import json
from distutils.dir_util import copy_tree
from shutil import copyfile, move
import yaml
import lazy_import
from sys import platform as _platform

#Pilot PLC and custom code scripts

Compiler = lazy_import.lazy_callable("pybars.Compiler")
# from pybars import Compiler

os = lazy_import.lazy_module("os")
json = lazy_import.lazy_module("json")
itertools = lazy_import.lazy_module("itertools")
string = lazy_import.lazy_module("string")
re = lazy_import.lazy_module("re")

#from collections import defaultdict
defaultdict = lazy_import.lazy_callable("collections.defaultdict")
fnmatch = lazy_import.lazy_module("fnmatch")

memregions = ['input', 'output', 'memory']
baseAddress        = 0x20000000
baseBitbandAddress = 0x22000000
alignment = 4

varsizes = {
        'BOOL': 1,
        'SINT': 1,
        'INT': 2,
        'DINT': 4,
        'LINT': 8,
        'USINT': 1,
        'UINT': 2,
        'UDINT': 4,
        'ULINT': 8,
        'BYTE': 1,
        'WORD': 2,
        'DWORD': 4,
        'LWORD': 8,
        'REAL': 4,
        'LREAL': 8,
        'TIME': 8, #??
        'DATE': 8, #??
        'DT': 8,   #??
        'TOD': 8,  #??
        'STRING': 126
        }

def iec2c_compile(iec2c_path, iecfile, temp_path):
  # resultfile=os.path.join(os.path.abspath(temp_path), 'result.txt')
  execute='{} -I {} -T {} {}'.format(os.path.join(iec2c_path, 'iec2c'), os.path.join(iec2c_path,'lib'), os.path.abspath(temp_path), iecfile)
  return os.system(execute)
  #with open(resultfile, 'r') as fin:
  #  print fin.read()

def init(config, model):
  configdef = { 'moduledefinitions': [] }
  for root, _dirnames, filenames in os.walk(os.path.dirname(os.path.realpath(__file__))):
    for filename in fnmatch.filter(filenames, 'configdefs.json'):
      with open(os.path.join(root, filename)) as obj:
        configdef['moduledefinitions'].extend( json.load(obj)['moduledefinitions'] )

  memmodules = config["modules"]
  if 'plugins' in config:
    memmodules = memmodules + config['plugins']

  #generate module config
  print('config:')
  print(config)
  modulelist = [dict(n[0], **n[1][0]) for n in map(lambda x: (x, list(filter(lambda y: x["fid"] == y["fid"],configdef["moduledefinitions"]))), memmodules) if n[1] != []]

  misalignedmodules = []
  #check if config and firmware align
  for module in model['Modules']:
    for confmod in modulelist:
      if confmod['slot'] == module['Slot'] + 1:
        if (confmod['fid'] != module['Name']):
          misalignedmodules.append(confmod['slot'])

  # generate start addresses if they are not configured
  for memregion in memregions:
    start = 0
    for module in modulelist:
      if (memregion+'address') not in module and (memregion+'size') in module and module[memregion+'size'] > 0:
        module[memregion+'address'] = start
        start = start + module[memregion+'size']

  #generate memory regions
  for memregion in memregions: map(lambda x: x.update({memregion+'bytes': range(x[memregion+'address'],x[memregion+'address']+x[memregion+'size'])}), filter(lambda x: (memregion+'address') in x and (memregion+'size') in x,modulelist))
  
  #calculate memory overlaps and sizes
  overlaps = []
  for memregion in memregions:
    for a, b in itertools.combinations(modulelist, 2): 
        if (memregion+'bytes') in a and (memregion+'bytes') in b:
            overlap = list(set(a[memregion+'bytes']).intersection(b[memregion+'bytes']))
            if overlap != []:
                overlaps.append({'elementa': a, 'elementb': b, 'memory' : memregion, 'address': overlap})

  mem = dict(map(lambda x: [x, {'region': x, 'size': 0, 'start': 0, 'absolute': 0}], memregions))
  for memregion in memregions:
    for module in modulelist:
      if (memregion+'address') in module and (memregion+'size') in module:
        size = module[memregion+'address'] + module[memregion+'size'] 
        mem[memregion]['size'] = size if size > mem[memregion]['size'] else size

  return (modulelist, overlaps, misalignedmodules, mem)

def parseplcvariables(temp_path, mem):
  global baseBitbandAddress
  varcsvfilepath=os.path.join(os.path.abspath(temp_path), 'VARIABLES.csv')
  with open(varcsvfilepath) as varcsvfile:
    content = [line.strip() for line in varcsvfile]

  mode = ''
  variables = []
  programs = []
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

          #add extra variable info
          var['isGlobal'] = True if var['instance'] == None else False
          var['extern'] = '{}__{}'.format(var['resource'], var['name'])
          var['isExternal'] = True if var['location'] == 'EXT' else False
          var['isString'] = True if var['type'] == 'STRING' else False
          var['plcVarName'] = '{}__{}'.format(var['resource'], var['name']) if var['isGlobal'] else '{}.{}'.format(var['instance'], var['name'])
          var['externdeclaration'] = 'extern __IEC_{}_p {};'.format(var['type'], var['extern']) if var['isGlobal'] else ''

          if var['isGlobal']:
            var['get'] = '{}.value'.format(var['plcVarName'])
          elif var['isExternal']:
            var['get'] = '(__GET_EXTERNAL_BY_REF({}))'.format(var['plcVarName'])
          else:
            var['get'] = '&(__GET_VAR({}))'.format(var['plcVarName'])

          if var['location'] == 'FB':
            if  var['isGlobal'] == True:
              programs.append(var)
          else:
            variables.append(var)

  #parse located variables
  regex = re.compile(r'__LOCATED_VAR\((?P<type>\w+),(?P<var>[^,]*),(?P<mem>\w),(?P<size>\w),(?P<byte>\d+)(,(?P<bit>\w))?\)')
  locatedvarfilepath=os.path.join(os.path.abspath(temp_path), 'LOCATED_VARIABLES.h')
  with open(locatedvarfilepath) as locatedvarfile:
    locatedvariables = [regex.match(line).groupdict() for line in locatedvarfile]

  for locvar in locatedvariables:
    locvar['externlocated'] = 'extern {0} * {1}_; extern IEC_BYTE * {2}_flags; extern {0} * {2}_changed;'.format(locvar['type'], locvar['var'].lower(), locvar['var'])
    #locvar['memoryaddress'] = 
    if locvar['mem'] == 'I':
      locvar['location'] = 'input' #from memregions var
    elif locvar['mem'] == 'Q':
      locvar['location'] = 'output' #from memregions var
    else:
      locvar['location'] = 'memory' #from memregions var

    #located memory
    memmax = int(locvar['byte']) + varsizes[locvar['type']]
    if memmax > mem[locvar['location']]['size']:
      mem[locvar['location']]['size'] = memmax

  #calc absolute memory position
  pos = 0
  for _key, value in mem.items():
    value['start'] = pos
    value['absolute'] = '0x{:X}'.format(pos + baseAddress)
    pos += value['size']

  #set variable memory positions
  for locvar in locatedvariables:
    reladdress = mem[locvar['location']]['start'] + int(locvar['byte'])
    absaddress = reladdress + baseAddress
    # print('location: {}, rel.addr. {:X}, abs.addr: {:X}'.format(locvar['var'], reladdress, absaddress))

    if locvar['bit'] != None:
      locvar['locatedaddressdeclaration'] = '{0} * {1}_ = ({0} *) 0x{2:X}; //bitband region\r#define {3} {1}_\r{0} * {3}_changed;\rIEC_BYTE * {3}_flags;\r'.format(locvar['type'], locvar['var'].lower(), baseBitbandAddress + (reladdress*32) + (int(locvar['bit'])*4), locvar['var'])
    else:
      locvar['locatedaddressdeclaration'] = '{0} * {1}_ = ({0} *) 0x{2:X};\r#define {3} {1}_\r{0} * {3}_changed;\rIEC_BYTE * {3}_flags;\r'.format(locvar['type'], locvar['var'].lower(), absaddress, locvar['var']) #TODO replace 0 with memorylocation


  locations = list(set(map(lambda x: x['location'], locatedvariables)))

  return programs, variables, locatedvariables, locations

def checkIfReplacementExists(key, module):
  if key in module:
    #TODO check if module is an array
    regex = re.compile(r"\{\{(.*?)+\}\}")
    m = regex.match(module[key])
    print(m)
    # TODO check that all replacements can be made, otherwise it cannot compile
    # that happens with wrong config file e.g.

#TODO: move to plugins
def io16_init_gen(nibble, direction, module):
  print('nibble:')
  print(nibble)
  print('direction:')
  print(direction)
  print('module:')
  print(module)

  return 'rpc_io16_{}_set_direction({}, {}); '.format(
    module['index'],
    module['codegen']['nibbles'][nibble]['selector'],
    module['codegen']['direction'][direction])

#TODO: move to plugins
def io16_read_gen(calls, module):
  if module['fid'] == 'io16' and 'config' in module and 'direction' in module['config']:
    gen = defaultdict(lambda : {})
    for k,v in module['config']['direction'].items():
      if not module['codegen']['nibbles'][k][v]['offset'] in gen[v]:
        gen[v][module['codegen']['nibbles'][k][v]['offset']] = []
      gen[v][module['codegen']['nibbles'][k][v]['offset']].append({ 'selector': module['codegen']['nibbles'][k]['selector'],  
        'data': module['codegen']['nibbles'][k][v] })

    #generate inputs
    if 'in' in gen:
      for offset in gen['in']:
        nibbleCalls = []
        for nibble in gen['in'][offset]:
          nibbleCalls.append("(rpc_io16_{}_get_byte({}) >> {})".format(
          module['index'],
          nibble['data']['register'],
          nibble['data']['shift']))
        calls['read'].append("*((unsigned char *)({} + {})) = {}; ".format(
                              module['input'+'absoluteaddress'], offset,
                              ' | '.join(nibbleCalls)))

    #generate outputs
    if 'out' in gen:
      for offset in gen['out']:
        nibbleCalls = []
        registerlist = []
        for nibble in gen['out'][offset]:
          if nibble['data']['register'] not in registerlist:
            calls['write'].append("rpc_io16_{}_set_byte({}, (*((unsigned char *)({} + {}))) >> {}); ".format(
                  module['index'],
                  nibble['data']['register'],
                  module['output'+'absoluteaddress'], offset, nibble['data']['shift']))
            registerlist.append(nibble['data']['register'])
                              
  return calls

def helper_markdown(this, options):
  md = options['fn'](this)
  # md - is a raw markdown string. You could handle it with MD-compiler
  # or just forward it to the result "as is"
  return md

def parsemodules(mem, modules):
  global baseAddress

  for module in modules:
    module['index'] = int(module['slot'])-1

  calls = {'read': [], 'write': [], 'init': [], 'include': []}
  compiler = Compiler()

  for key, value in mem.items():
    for module in modules:
        if (key+'address') in module:
          module[key+'absoluteaddress'] = '0x{:X}'.format(module[key+'address'] + value['start'] + baseAddress)

  for key, value in calls.items():
    for module in modules:
      if key in module and module[key] != '':
        checkIfReplacementExists(key, module)
        template = compiler.compile(module[key])
        calls[key].append(template(module))


  # module config specific calls
  for module in modules:
    if module['fid'] == 'io16' and 'config' in module and 'direction' in module['config']:
      directions = module['config']['direction']
      print('directions:')
      calls['init'].extend(list(map((lambda x: io16_init_gen(x, directions[x], module)), directions.keys())))
    calls = io16_read_gen(calls, module)

  return calls

def parsesubscriptions(subscriptions):
  subs = []
  for sub in subscriptions:
    subs.append(sub.replace('.', '__').upper() + '.flags = __IEC_SUBSCRIBE_FLAG; ')
  return subs

def parsetemplate(out_path, templatedata):
  #printable = set(string.printable)
  #filecontent = filter(lambda x: x in printable, templatefile.read())
  template_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'template')

  for _root, _dirs, files in os.walk(template_path):
    templfiles = map(lambda x: os.path.join(template_path, x) ,filter(lambda x: x.endswith('.templ'), files))

    for templfile in templfiles:
      with open(templfile) as f:
        compiler = Compiler()
        template = compiler.compile(f.read())

        output = template(templatedata)

        with open(os.path.join(out_path, os.path.splitext(os.path.basename(templfile))[0]), 'w') as f:
          f.write(output)          

def main(args, config):
  config = None

  #if _platform == "linux2":
  #  _platform = "linux"

  if args.iec2cdir == None:
    args.iec2cdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'matiec', _platform)
  
  if not os.path.isdir(args.iec2cdir):
    print('Matiec IEC2C Compiler not found in {}. Maybe there is no compiler for your platform?'.format(args.iec2cdir))
    exit(1)

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

  stmmodel = {}
  modules = {}

  with open(os.path.join(os.path.abspath(args.source), 'stmmodel.json')) as stmmodelfile:
    stmmodel.update(json.load(stmmodelfile))

  #if no target path parameter is given try the environment var
  if args.target == None:
    args.target = os.path.join(args.workdir, "out") if args.workdir else os.path.join(os.getcwd(), "out")
    if not os.path.exists(args.target):
      os.makedirs(args.target)

  print("Writing output to " + args.target)

  if args.configfile != None:
    print("loading configfiles")
    with open(args.configfile) as configfile:
      if (args.configfile.endswith('.json')):
        config = json.load(configfile)
    modules, overlaps, misalignedmodules, mem = init(config, stmmodel)

    for overlap in overlaps:
      print("Overlapping memory regions! Module in slot {} and slot {} overlap in {} memory at byte position {}".format(overlap['elementa']['slot'], overlap['elementb']['slot'], overlap['memory'], ', '.join(str(s) for s in overlap['address'])))
      exit(2)

    if misalignedmodules != []:
      print("Modules in Firmware Source do not match modules in config file:")
      print("   Firmware   Config File")
      for module in stmmodel['Modules']:
        m = list(filter(lambda x: x['slot'] - 1 == module['Slot'] ,config['modules']))
        print("{0:1}: {1:10} {2:10}".format(module['Slot']+1, module['Name'], m[0]['fid'] if len(m) == 1 else 'None'))
      exit(2)

  #print(mem)
  #print(modules)

  copy_tree(args.source, args.target)
  copy_tree(os.path.join(os.path.abspath(os.path.dirname(os.path.realpath(__file__))), 'template', 'inc'), os.path.join(args.target, 'inc'))

  #additional model data
  if config and 'includes' in config:
    stmmodel['includes'] = config['includes']

  stfiles = []
  codefilearr = []
  if len(args.files) != 0 or 'ignore_files' in args:
    stfiles = list(filter(lambda x: x.endswith('.st'), args.files))
    codefilearr = list(filter(lambda x: not x.endswith('.st'), args.files))
  else:
    for file in os.listdir(os.path.join(args.workdir, 'src')):
      if file.endswith(".st"):
        stfiles.append(os.path.join(args.workdir, 'src', file))
      elif file.endswith(".c"):
        codefilearr.append(os.path.join(args.workdir, 'src', file))
  codefiles = ' '.join(codefilearr)
 
  plcfiles = ''
  if len(stfiles) > 0:
    plcfiles = 'config.h config.c resource1.c POUS.h ' # TODO - check if hardcoded files make sense here. can't use make plc with that. always use make default
    stfile = stfiles[0]
    if len(stfiles) > 1:
      stfile = os.path.join(args.target, '__program.st')
      with open(stfile, 'w') as outfile:
        for fname in stfiles:
          with open(fname) as infile:
            for line in infile:
              outfile.write(line)

    #iec2c compile and extract variables
    if iec2c_compile(args.iec2cdir, stfile, args.target) == 0:
      print('parsing variables')
      programs, variables, locatedvariables, locations = parseplcvariables(args.target, mem)

      if args.verbose:
        print(yaml.dump(mem, Dumper=yaml.Dumper, default_flow_style=False))

      calls = parsemodules(mem, modules)
      stmmodel['PLC'] = {'programs': programs, 'variables': variables, 'locatedvariables': locatedvariables, 'locations': locations, 'mem': mem, 'calls': calls}
      stmmodel['PLC']['modules'] = modules
      if 'subscriptions' in config:
        stmmodel['PLC']['subscriptions'] = parsesubscriptions(config['subscriptions'])
      parsetemplate(args.target, stmmodel)

      with open(os.path.join(args.workdir, "out", 'stmmodel.json'), 'w') as stmmodelfile:
        json.dump(stmmodel, stmmodelfile)

    else:
      print("Error executing IEC2C Compiler")
      exit(1)

  # codefiles
  for codefile in codefilearr:
    copyfile(codefile, os.path.join(args.target, os.path.basename(os.path.abspath(codefile))))

  # extra compilation files
  newMakefile = os.path.join(args.target, 'newMakefile')
  makefile = os.path.join(args.target, 'Makefile')
  with open(newMakefile, 'w') as new:
    new.write('EXCLUDE_SRCS=POUS.c\n')
    with open(makefile) as old:
      new.write(old.read())

  move(newMakefile, makefile)

  #run make - only works with installed arm-none-eabi-gcc
  #TODO - enable using docker container for the compiler
  subprocess.call(['make', '-C', args.target])

  return 0