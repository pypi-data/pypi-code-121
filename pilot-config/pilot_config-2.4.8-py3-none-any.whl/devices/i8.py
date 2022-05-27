def getDevice(model, module, compiler, helpers):
  return I8Device(model, module, compiler, helpers)

def toGPIO(this, items):
  return 'GPIO' + chr(items+65)

def default_config():
  return {}

class I8Device():
  size = 1
  ctype = 'uint8_t'
  rusttype = 'u8'
  include = ['stm32f10x.h'] 
  init_source = ''
  dev_to_mem_source = ''
  mem_to_dev_source = ''
  mem_doc = { "read": [], "write": [] }

  decl = {
    'c': { 'name': 'i8_t', 'decl': 'typedef uint8_t i8_t;' },
    'rust': { 'name': 'u8', 'decl': '' }
  }

  module = None
  model = None
  compiler = None
  helpers = None 
  
  def __init__(self, model, module, compiler, helpers):
    self.size = 1
    self.module = module
    self.helpers = {'gpio': toGPIO, **helpers}
    self.compiler = compiler
    self.model = model

  def compile(self):
    template = self.compiler.compile("""// source for device {{device.name}}
  {{#each device.hw.Inputs}}
  BITBAND_SRAM(&plc_mem_devices.m{{../device.slot}}, {{IO}}) = BITBAND_PERI({{gpio GPIO}}_BASE + 8, {{Pin}});
{{/each}}
  """)
    self.dev_to_mem_source = template(self.module, self.helpers)
    self.mem_doc['read'] = [{ "name": "i{}".format(i), "desc": "digital input {}".format(i), "byte": 0, "bit": i,"length": 1, "signed": False, "datatype": "bool"} for i in range(8)]