import os
import json
import lazy_import
import importlib.util

#from collections import defaultdict
defaultdict = lazy_import.lazy_callable("collections.defaultdict")
fnmatch = lazy_import.lazy_module("fnmatch")

class Plc():
  targetdevice = { 'flashaddress': 0x08000000, 'ramaddress': 0x20000000, 'bitbandaddress': 0x22000000, 'flash': 512, 'ram': 48 } # STM32F103CBxx
  model = {}
  config = {}
  compiler = None
  helpers = None
  args = {}

  def __init__(self, args, version, model, config, compiler, helpers):
    self.args = args
    self.config = config
    self.model = model
    self.compiler = compiler
    self.helpers = helpers

    self.model['version'] = version

    if 'config' in config:
      self.model['config'] = config['config']

    mem_modules = self.init_memory_mapped_modules()

  def init_memory_mapped_modules(self):
    allmodules = self.config["modules"]
    if 'plugins' in self.config:
      allmodules = allmodules + self.config['plugins']

    # Initialize device data 
    # create device properties
    # spec - hw specs (I/Os, GPIO banks, Interrupts, etc)
    # name - name to be used in code gen
    # absaddress - absolute RAM address in MCU
    # NOTE that 'Slot' in spec is zero based whereas 'slot' is 1 based.
    memmodules = []
    self.config['plc_memory_size'] = 0
    for mod in allmodules:
      dev = {}
      mod['device'] = dev
      try: # will fail if module is not supported by PLC firmware
        dev['hw'] = next(iter(next(iter([v for k, v in self.model.items() if isinstance(v, list) and 
               [x for x in v if k != 'Modules' and 'Slot' in x and 'slot' in mod and x['Slot']+1 == int(mod['slot'])]]))))
      except:
        dev['hw'] = {}
      dev['name'] = "m{}_{}".format(mod['slot'], mod['fid']) # TODO naming for plugins
      dev['slot'] = mod['slot']
      dev['index'] = int(mod['slot']) - 1
      dev['spec'] = self.getDevice(mod)
      if dev['spec'] == None:
        print("Warning: No device found for module firmware {}, this module firmware does not have PLC support".format(mod['fid']))
      else:
        self.config['plc_memory_size'] = self.config['plc_memory_size'] + dev['spec'].size
        dev['spec'].compile()
              
        memmodules.append(mod)

    # memory size in kb
    plcmemsize = int((self.config['plc_memory_size']  + 1024 - 1) / 1024)

    # memory mapped modules
    self.model['memmodules'] = memmodules 
    uniquemodules = []
    for m in memmodules:
      if len(list(filter(lambda x: x['fid'] == m['fid'], uniquemodules))) == 0:
        uniquemodules.append(m)
    self.model['uniquemodules'] = uniquemodules 

    # generate data for linker script
    self.model['memory'] = self.targetdevice
    self.model['ld'] = { 'flashaddress': hex(self.targetdevice['flashaddress']),
                          'plcaddress': hex(self.targetdevice['ramaddress']),
                          'ramaddress': hex(self.targetdevice['ramaddress'] + (plcmemsize * 1024)),
                          'flash': str(self.targetdevice['flash']) + 'k', 
                          'ram': str(int(self.targetdevice['ram']) - plcmemsize) + 'k',
                          'plc': str(int(plcmemsize)) + 'k'}
    
  def getDevice(self, module):
    devicefile = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'devices', module['fid'] + '.py') 
    if not os.path.isfile(devicefile) and 'plugin' in module: # not found in devices, check in plugins folder
      devicefile = os.path.join(self.args.workdir, 'plugins', module['plugin'] + '.py') 
      if (os.path.isfile(devicefile)): # plugin exists, add plugin to model
        if not 'plugins' in self.model:
          self.model['plugins'] = {}
        self.model['plugins']['dcmctrl'] = { 'module': module }

    if os.path.isfile(devicefile):
      spec = importlib.util.spec_from_file_location("module.name", devicefile)
      device = importlib.util.module_from_spec(spec)
      spec.loader.exec_module(device)
      return device.getDevice(self.model, module, self.compiler, self.helpers)
    return None