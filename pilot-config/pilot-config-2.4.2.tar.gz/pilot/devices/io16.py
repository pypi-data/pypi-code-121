def getDevice(model, module, compiler, helpers):
  return IO16Device(model, module, compiler, helpers)

def toGPIO(this, items):
  return 'GPIO' + chr(items+65)

def default_config():
  return { 'direction':  {'0-3': 'in', '4-7': 'in', '8-11': 'in', '12-15': 'in'} }

class IO16Device():
  size = 2
  include = ['io16.h'] 
  init_source = ''
  dev_to_mem_source = ''
  mem_to_dev_source = ''
  mem_doc = { "read": [], "write": [] }

  decl = {
    'c': { 'name': 'io16_t', 'decl': 'typedef uint16_t io16_t;' },
    'rust': { 'name': 'u16', 'decl': '' }
  }

  module = None
  model = None
  compiler = None
  helpers = None 
  
  directions = {'0-3': 'in', '4-7': 'in', '8-11': 'in', '12-15': 'in'}

  def __init__(self, model, module, compiler, helpers):
    self.size = 2
    self.type = 'uint16_t'
    self.length = 1
    self.module = module
    self.helpers = {'gpio': toGPIO, **helpers}
    self.compiler = compiler
    self.model = model
  

  def direction_to_enum(self, dir):
    if dir == 'out':
      return 'pilot_io16_direction_output'
    else:
      return 'pilot_io16_direction_input'

  def compile(self):
    if "config" not in self.module:
      self.module['config'] = { 'direction': directions }

    init_str = "  // initialization for device {{device.name}}\n  int32_t status = 0;\n"
    dev_to_mem_str = "// source for device {{device.name}}\n  int16_t {{device.name}}_value;\n"
    mem_to_dev_str = "// source for device {{device.name}}\n  int16_t {{device.name}}_value;\n"
    # iterate nibbles
    nibbles_read = [True, True, True, True]
    for nibble in self.module['config']['direction']:
      if nibble not in self.directions:
        print("directions in IO16 module {} misconfigured, '{}' is not valid".format(self.module['slot'], nibble))
        exit(1)
      dir = self.module['config']['direction'][nibble]
      if dir != 'in' and dir != 'out':
        print("direction needs to be 'in' or 'out' in '{}'".format(nibble))
        exit(1)
      offset = int(nibble.split('-')[0])
      offset_to = int(nibble.split('-')[1])

      nibbles_read[int(offset / 4)] = dir == 'in'
      init_str = init_str + "  status |= pilot_io16_{{device.index}}_set_direction(pilot_io16_block_" + str(offset) + "_to_" + str(offset_to) + ", " + self.direction_to_enum(dir) + ");\n"

      for i in range(4):
        self.mem_doc['read' if dir == 'in' else 'write'].append({ "name": "{}{}".format(dir[0], offset+i), "desc": "digital {} {}".format('input' if dir == 'in' else 'output', offset+i), "byte": int((offset+i) / 8), "bit": (offset+i) % 8, "length": 1, "signed": False, "datatype": "bool"})

    init_str = init_str + "  return status;"

    readmask = "0x" + "".join(map(lambda x: 'F' if x else '0', reversed(nibbles_read)))
    writemask = "0x" + "".join(map(lambda x: '0' if x else 'F', reversed(nibbles_read)))
    inv_readmask = "0x" + "".join(map(lambda x: '0' if x else 'F', reversed(nibbles_read)))
    inv_writemask = "0x" + "".join(map(lambda x: 'F' if x else '0', reversed(nibbles_read)))
    
    if readmask != '0x0000':
      dev_to_mem_str = dev_to_mem_str + """  get_module_info()->m{{device.index}}_status |= pilot_io16_{{device.index}}_read_register(pilot_io16_register_input_register_A, 2, (uint8_t *)&{{device.name}}_value);
  plc_mem_devices.m{{device.slot}} &= """ + inv_readmask + """; 
  plc_mem_devices.m{{device.slot}} |= {{device.name}}_value & """ + readmask + ";\n"

    if writemask != '0x0000':
      mem_to_dev_str = mem_to_dev_str + "  {{device.name}}_value = plc_mem_devices.m{{device.slot}} & " + writemask + ";\n  " + "get_module_info()->m{{device.index}}_status |= pilot_io16_{{device.index}}_write_register(pilot_io16_register_output_register_A, 2, (uint8_t *)&{{device.name}}_value);"

    # generate source 
    init_template = self.compiler.compile(init_str)
    dev_to_mem_template = self.compiler.compile(dev_to_mem_str)
    mem_to_dev_template = self.compiler.compile(mem_to_dev_str)

    self.init_source = init_template(self.module, self.helpers)
    self.dev_to_mem_source = dev_to_mem_template(self.module, self.helpers)
    self.mem_to_dev_source = mem_to_dev_template(self.module, self.helpers)