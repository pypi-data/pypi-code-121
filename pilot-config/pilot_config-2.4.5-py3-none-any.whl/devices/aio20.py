import math
import copy

io_to_port = [
  3, 1, 2, 0, 
  6, 5, 9, 8,
  11, 10, 14, 13,
  16, 15, 18, 19,
  4, 7, 12, 17
]

ports = [
    { "io": 0,  "direction": "in", "averages": 128, "range": "0-10V" }, # PORT 3
    { "io": 1,  "direction": "in", "averages": 128, "range": "0-10V" }, # PORT 1
    { "io": 2,  "direction": "in", "averages": 128, "range": "0-10V" }, # PORT 2
    { "io": 3,  "direction": "in", "averages": 128, "range": "0-10V" }, # PORT 0
    { "io": 4,  "direction": "in", "averages": 128, "range": "0-10V" }, # PORT 6
    { "io": 5,  "direction": "in", "averages": 128, "range": "0-10V" }, # PORT 5
    { "io": 6,  "direction": "in", "averages": 128, "range": "0-10V" }, # PORT 9
    { "io": 7,  "direction": "in", "averages": 128, "range": "0-10V" }, # PORT 8
    { "io": 8,  "direction": "in", "averages": 128, "range": "0-10V" }, # PORT 11
    { "io": 9,  "direction": "in", "averages": 128, "range": "0-10V" }, # PORT 10
    { "io": 10, "direction": "in", "averages": 128, "range": "0-10V" }, # PORT 14
    { "io": 11, "direction": "in", "averages": 128, "range": "0-10V" }, # PORT 13
    { "io": 12, "direction": "in", "averages": 128, "range": "0-10V" }, # PORT 16
    { "io": 13, "direction": "in", "averages": 128, "range": "0-10V" }, # PORT 15
    { "io": 14, "direction": "in", "averages": 128, "range": "0-10V" }, # PORT 18
    { "io": 15, "direction": "in", "averages": 128, "range": "0-10V" }  # PORT 19
]

internalports = [
    { "io": 16, "direction": "in", "averages": 128, "range": "0-10V" }, # PORT 4
    { "io": 17, "direction": "in", "averages": 128, "range": "0-10V" }, # PORT 7
    { "io": 18, "direction": "in", "averages": 128, "range": "0-10V" }, # PORT 12
    { "io": 19, "direction": "in", "averages": 128, "range": "0-10V" }, # PORT 17
]

def getDevice(model, module, compiler, helpers):
  return AIO20Device(model, module, compiler, helpers)

def toGPIO(this, items):
  return 'GPIO' + chr(items+65)

def default_config():
  return { 'ports': ports }
class AIO20Device():
  size = 40
  ctype = 'uint16_t[16]'
  rusttype = 'u8'
  include = ['aio20.h'] 
  init_source = ''
  dev_to_mem_source = ''
  mem_to_dev_source = ''
  mem_doc = {
    "read": [
    {
      "byte": 2,
      "bit": 0,
      "length": 16,
      "name": "aio0",
      "desc": "Analog I/O 0",
      "signed": False
    },
    {
      "byte": 0,
      "bit": 0,
      "length": 16,
      "name": "aio1",
      "desc": "Analog I/O 1",
      "signed": False
    },
    {
      "byte": 6,
      "bit": 0,
      "length": 16,
      "name": "aio2",
      "desc": "Analog I/O 2",
      "signed": False
    },
    {
      "byte": 4,
      "bit": 0,
      "length": 16,
      "name": "aio3",
      "desc": "Analog I/O 3",
      "signed": False
    },
    {
      "byte": 12,
      "bit": 0,
      "length": 16,
      "name": "aio4",
      "desc": "Analog I/O 4",
      "signed": False
    },
    {
      "byte": 10,
      "bit": 0,
      "length": 16,
      "name": "aio5",
      "desc": "Analog I/O 5",
      "signed": False
    },
    {
      "byte": 18,
      "bit": 0,
      "length": 16,
      "name": "aio6",
      "desc": "Analog I/O 6",
      "signed": False
    },
    {
      "byte": 16,
      "bit": 0,
      "length": 16,
      "name": "aio7",
      "desc": "Analog I/O 7",
      "signed": False
    },
    {
      "byte": 22,
      "bit": 0,
      "length": 16,
      "name": "aio8",
      "desc": "Analog I/O 8",
      "signed": False
    },
    {
      "byte": 20,
      "bit": 0,
      "length": 16,
      "name": "aio9",
      "desc": "Analog I/O 9",
      "signed": False
    },
    {
      "byte": 28,
      "bit": 0,
      "length": 16,
      "name": "aio10",
      "desc": "Analog I/O 10",
      "signed": False
    },
    {
      "byte": 26,
      "bit": 0,
      "length": 16,
      "name": "aio11",
      "desc": "Analog I/O 11",
      "signed": False
    },
    {
      "byte": 32,
      "bit": 0,
      "length": 16,
      "name": "aio12",
      "desc": "Analog I/O 12",
      "signed": False
    },
    {
      "byte": 30,
      "bit": 0,
      "length": 16,
      "name": "aio13",
      "desc": "Analog I/O 13",
      "signed": False
    },
    {
      "byte": 36,
      "bit": 0,
      "length": 16,
      "name": "aio14",
      "desc": "Analog I/O 14",
      "signed": False
    },
    {
      "byte": 38,
      "bit": 0,
      "length": 16,
      "name": "aio15",
      "desc": "Analog I/O 15",
      "signed": False
    },
    {
      "byte": 8,
      "bit": 0,
      "length": 16,
      "name": "r1",
      "desc": "Analog Frontend 1 Id Resistor",
      "signed": False
    },
    {
      "byte": 14,
      "bit": 0,
      "length": 16,
      "name": "r2",
      "desc": "Analog Frontend 2 Id Resistor",
      "signed": False
    },
    {
      "byte": 24,
      "bit": 0,
      "length": 16,
      "name": "r3",
      "desc": "Analog Frontend 3 Id Resistor",
      "signed": False
    },
    {
      "byte": 34,
      "bit": 0,
      "length": 16,
      "name": "r4",
      "desc": "Analog Frontend 4 Id Resistor",
      "signed": False
    }
  ],
  "write": []
  }

  decl = ''

  module = None
  model = None
  compiler = None
  helpers = None 
  
  def __init__(self, model, module, compiler, helpers):
    self.size = 40
    self.module = module
    self.helpers = {'gpio': toGPIO, **helpers}
    self.compiler = compiler
    self.model = model


  def compile(self):

    if "config" not in self.module:
      self.module['config'] = { 'ports': copy.deepcopy(ports) }

    if "custom" not in self.model:
      self.model["custom"] = { }
    
    if "aio20" not in self.model["custom"]:
      self.model["custom"]["aio20"] = []

    res, err = self.parse_port_config(self.module['config']['ports'])
    if err:
      print(err)
      exit(1)
    
    self.model["custom"]["aio20"].append({ 'index': self.module['slot']-1, 'config': res })

    dev_to_mem_str = """// source for device {{device.name}}
  get_module_info()->m{{device.index}}_status |= single_ended_adc_read_all({{device.index}}, (uint8_t *) &plc_mem_devices.m{{device.slot}}); 
  """

    init_str = "  // initialization for device {{device.name}}\n  int32_t status = 1;\n  if (aio20_get_device_id({{device.index}}) == 0x424)\n  {\n    status = 0;\n    AIO20_init({{device.index}});\n  }\n  return status;"
    init_template = self.compiler.compile(init_str)
    dev_to_mem_template = self.compiler.compile(dev_to_mem_str)

    self.dev_to_mem_source = dev_to_mem_template(self.module, self.helpers)
    self.init_source = init_template(self.module, self.helpers)

    c_decl_out = '\n'
    rust_decl_out = '\n'

    # DAC
    mem_to_dev_str = "  // source for device {{device.name}}\n"
    for out in res['port_out']:
      c_decl_out = c_decl_out + f"     uint16_t out{out['io']};\n"
      rust_decl_out = rust_decl_out + f"     pub out{out['io']}: u16, // {out['port']}\n"
      mem_to_dev_str = mem_to_dev_str + "  get_module_info()->m{{device.index}}_status |= single_ended_dac_write({{device.index}}, "+ str(out['io']) +", plc_mem_devices.m{{device.slot}}.out"+str(out['io'])+");\n"

    if len(res['port_out']) > 0:
      mem_to_dev_template = self.compiler.compile(mem_to_dev_str)
      self.mem_to_dev_source = mem_to_dev_template(self.module, self.helpers)

    # declarations
    self.decl = {
       'c': { 'name': 'aio20_' + str(self.module['slot']-1) + '_t', 'decl': """typedef struct { 
     uint16_t in3;
     uint16_t in1;
     uint16_t in2;
     uint16_t in0;
     uint16_t r1;
     uint16_t in5;
     uint16_t in4;
     uint16_t r2;
     uint16_t in7;
     uint16_t in6;
     uint16_t in9;
     uint16_t in8;
     uint16_t r3;
     uint16_t in11;
     uint16_t in10;
     uint16_t in13;
     uint16_t in12;
     uint16_t r4;
     uint16_t in14;
     uint16_t in15;""" + c_decl_out + """
   } aio20_""" + str(self.module['slot']-1) + """_t;
   """},
       'rust': { 'name': 'Aio20_'+ str(self.module['slot']-1), 'decl': """#[repr(C)]
   pub struct Aio20_""" + str(self.module['slot']-1) + """ { 
     pub in3: u16,  // 0
     pub in1: u16,  // 1
     pub in2: u16,  // 2
     pub in0: u16,  // 3
     r1: u16,        // 4
     pub in5: u16,  // 5
     pub in4: u16,  // 6
     r2: u16,        // 7
     pub in7: u16,  // 8
     pub in6: u16,  // 9
     pub in9: u16,  // 10
     pub in8: u16,  // 11
     r3: u16,        // 12
     pub in11: u16, // 13  
     pub in10: u16, // 14
     pub in13: u16, // 15
     pub in12: u16, // 16
     r4: u16,        // 17
     pub in14: u16, // 18 
     pub in15: u16, // 19""" + rust_decl_out + """
   }
   """ }
     }
  
  def parse_port_config(self, ports):
      port_cfgs = []
      port_dacs = []
      port_out = []
      for intport in internalports:
        ports.append(intport)
      
      # check if all items have io
      for port in ports:
        if not 'io' in port:
            return {}, "'io' missing in port" # Error format?
        port['port'] = io_to_port[port['io']]

      ports = sorted(ports, key=lambda item: item['port'])

      # check if ports are exhaustive
      ios = list(map(lambda p: p['port'], ports))
      all_ios = [i for i in range(0, 20)]
      if (len(ios) != len(all_ios) or ios != all_ios):
        return {}, f"IO list in configuration of '{self.module['fid_nicename']}' in slot {self.module['slot']} is not exhaustive. All 16 IOs need to be declared"

      for port in ports:
          # 1111xxxxxxxxxxxx PortCfgFuncID Port function / mode
          # xxxx1xxxxxxxxxxx funcprm_avrInv AVR / INV
          # xxxxx111xxxxxxxx funcprm_range DAC Range / ADC Range
          # xxxxxxxx111xxxxx funcprm_nsamples Number of samples / CAP
          # xxxxxxxxxxx11111 funcprm_port Associated port 0..31
  
          err, port_cfg, port_dac = parse_direction(port)
          if err != "":
              return {}, err

          if port_dac != 0: # dac configured
            port_out.append({'io': port['io'], 'port': port['port']})
      
          err, cfg = parse_averages(port)
          if err == "": # no error
              port_cfg = port_cfg | cfg
          else:
              return {}, err
      
          err, cfg = parse_range(port)
          if err == "": # no error
              port_cfg = port_cfg | cfg
          else:
              return {}, err
          port_cfgs.append(port_cfg)
          port_dacs.append(port_dac)
      
      return {
        "port_cfgs": ", ".join("0x{:02X}".format(p) for p in port_cfgs), 
        "port_dacs": ", ".join("0x{:02X}".format(p) for p in port_dacs),
        "port_out": port_out
        }, ""


config = [
    { "io": 0, "direction": "in", "averages": 128, "range": "0-10V" } 
]

def parse_averages(port):
    if 'averages' in port:
        if isinstance(port['averages'], int) and port['averages'] <= 128:
            return "", int(math.log2(port['averages'])) << 5
        else:
            return f"port {port['io']} has unknown value '{port['average']}' for 'average'", 0
    else: # we assume 128
        return "",  7 << 5

def parse_range(port):
    if 'range' in port:
        if port['range'].lower() == '0-10v':
            return "", 0b00100000000
        elif port['range'].lower() == '0-2.5v':
            return "", 0b10000000000
        else:
            return f"port {port['io']} has unknown value '{port['range']}' in 'range'", 0
    else: # we assume 0-10V
        return "", 0b00100000000


def parse_direction(port):
    if 'direction' in port:
        if port['direction'].lower() == 'in': # adc
            return "", 0x7000, 0
        elif port['direction'].lower() == 'outmon': # dac with adc monitoring
            return "", 0x6000, 0x0800
        elif port['direction'].lower() == 'out': # dac
            return "", 0x5000, 0x0666
        else:
            return f"port {port['io']} has unknown value '{port['direction']}' in 'direction'", 0, 0
    else: # we assume in  (adc)
        return "", 0x7000, 0


    
    