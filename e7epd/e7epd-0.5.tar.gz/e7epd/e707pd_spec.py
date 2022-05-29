from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, Float, String, Text, JSON

default_string_len = 30


class Base(object):
    mfr_part_numb = Column(String(default_string_len), nullable=False, primary_key=True, autoincrement=False)
    stock = Column(Integer, nullable=False)
    manufacturer = Column(String(default_string_len))
    storage = Column(String(default_string_len))
    package = Column(String(default_string_len))
    comments = Column(Text)
    datasheet = Column(Text)
    user = Column(String(default_string_len))


GenericItem = declarative_base(cls=Base)
_AlchemyDeclarativeBase = declarative_base()


# Outline the different parts storage specifications
# {'db_name': "", 'showcase_name': "", 'db_type': "", 'show_as_type': "normal", 'required': False, },

"""
    The spec for components
"""
eedata_generic_spec = [
    {'db_name': 'stock', 'showcase_name': 'Stock', 'shows_as': 'normal', 'input_type': 'int', 'required': True, },
    {'db_name': 'mfr_part_numb', 'showcase_name': 'Mfr Part #', 'shows_as': 'normal', 'input_type': 'str', 'required': True, },
    {'db_name': 'manufacturer', 'showcase_name': 'Manufacturer', 'shows_as': 'normal', 'input_type': 'str', 'required': False, },
    {'db_name': 'package', 'showcase_name': 'Package', 'shows_as': 'normal', 'input_type': 'str', 'required': True, },
    {'db_name': 'storage', 'showcase_name': 'Storage Location', 'shows_as': 'normal', 'input_type': 'str', 'required': False, },
    {'db_name': 'comments', 'showcase_name': 'Comments', 'shows_as': 'normal', 'input_type': 'str', 'required': False, },
    {'db_name': 'datasheet', 'showcase_name': 'Datasheet', 'shows_as': 'normal', 'input_type': 'str', 'required': False, },
    {'db_name': 'user', 'showcase_name': 'User', 'shows_as': 'normal', 'input_type': 'str', 'required': False, },
]
eedata_generic_items = [i['db_name'] for i in eedata_generic_spec]
eedata_generic_items_preitems = ['stock', 'mfr_part_numb', 'manufacturer']
eedata_generic_items_postitems = ['package', 'storage', 'comments', 'datasheet', 'user']

eedata_resistors_spec = eedata_generic_spec + [
    {'db_name': 'resistance', 'showcase_name': 'Resistance', 'shows_as': 'engineering', 'input_type': 'float', 'required': True, },
    {'db_name': 'tolerance', 'showcase_name': 'Tolerance', 'shows_as': 'percentage', 'input_type': 'float', 'required': False, },
    {'db_name': 'power', 'showcase_name': 'Power Rating', 'shows_as': 'normal', 'input_type': 'float', 'required': False, }
]
eedata_resistor_display_order = eedata_generic_items_preitems+['resistance', 'tolerance', 'power']+eedata_generic_items_postitems

eedata_capacitor_spec = eedata_generic_spec + [
    {'db_name': 'capacitance', 'showcase_name': 'Capacitance', 'shows_as': 'engineering', 'input_type': 'float', 'required': True, },
    {'db_name': 'tolerance', 'showcase_name': 'Tolerance', 'shows_as': 'percentage', 'input_type': 'float', 'required': False, },
    {'db_name': 'max_voltage', 'showcase_name': 'Voltage Rating', 'shows_as': 'normal', 'input_type': 'float', 'required': False, },
    {'db_name': 'temp_coeff', 'showcase_name': 'Temperature Coefficient', 'shows_as': 'normal', 'input_type': 'str', 'required': False, },
    {'db_name': 'cap_type', 'showcase_name': 'Capacitor Type', 'shows_as': 'normal', 'input_type': 'str', 'required': False, },
]
eedata_capacitor_display_order = eedata_generic_items_preitems+['capacitance', 'tolerance', 'max_voltage', 'cap_type', 'temp_coeff']+eedata_generic_items_postitems

eedata_ic_spec = eedata_generic_spec + [
    {'db_name': 'ic_type', 'showcase_name': 'IC Type', 'shows_as': 'normal', 'input_type': 'str', 'required': True},
]
eedata_ic_display_order = eedata_generic_items_preitems+['ic_type']+eedata_generic_items_postitems

eedata_inductor_spec = eedata_generic_spec + [
    {'db_name': 'inductance', 'showcase_name': 'Inductance', 'shows_as': 'engineering', 'input_type': 'float', 'required': True, },
    {'db_name': 'tolerance', 'showcase_name': 'Tolerance', 'shows_as': 'percentage', 'input_type': 'float', 'required': False, },
    {'db_name': 'max_current', 'showcase_name': 'Max Current', 'shows_as': 'engineering', 'input_type': 'float', 'required': False, },
]
eedata_inductor_display_order = eedata_generic_items_preitems+['inductance', 'tolerance', 'max_current']+eedata_generic_items_postitems

eedata_diode_spec = eedata_generic_spec + [
    {'db_name': 'diode_type', 'showcase_name': 'Diode Type', 'shows_as': 'normal', 'input_type': 'str', 'required': True, },
    {'db_name': 'max_current', 'showcase_name': 'Peak Current', 'shows_as': 'engineering', 'input_type': 'float', 'required': False, },
    {'db_name': 'average_current', 'showcase_name': 'Average Current', 'shows_as': 'engineering', 'input_type': 'float', 'required': False, },
    {'db_name': 'max_rv', 'showcase_name': 'Max Reverse Voltage', 'shows_as': 'engineering', 'input_type': 'float', 'required': False, },
]
eedata_diode_display_order = eedata_generic_items_preitems+['diode_type', 'max_rv', 'average_current', 'max_current']+eedata_generic_items_postitems

eedata_crystal_spec = eedata_generic_spec + [
    {'db_name': 'frequency', 'showcase_name': 'Frequency', 'shows_as': 'engineering', 'input_type': 'float', 'required': True, },
    {'db_name': 'load_c', 'showcase_name': 'Load Capacitance (pF)', 'shows_as': 'engineering', 'input_type': 'float', 'required': False, },
    {'db_name': 'esr', 'showcase_name': 'ESR', 'shows_as': 'engineering', 'input_type': 'float', 'required': False, },
    {'db_name': 'stability_ppm', 'showcase_name': 'Stability (ppm)', 'shows_as': 'normal', 'input_type': 'float', 'required': False, },
]
eedata_crystal_display_order = eedata_generic_items_preitems+['frequency', 'load_c', 'esr', 'stability_ppm']+eedata_generic_items_postitems

eedata_mosfet_spec = eedata_generic_spec + [
    {'db_name': 'mosfet_type', 'showcase_name': 'Type', 'shows_as': 'normal', 'input_type': 'str', 'required': True, },
    {'db_name': 'vdss', 'showcase_name': 'Max Drain-Source Voltage', 'shows_as': 'engineering', 'input_type': 'float', 'required': False, },
    {'db_name': 'vgss', 'showcase_name': 'Max Gate-Source Voltage', 'shows_as': 'engineering', 'input_type': 'float', 'required': False, },
    {'db_name': 'vgs_th', 'showcase_name': 'Gate-Source Threshold Voltage', 'shows_as': 'engineering', 'input_type': 'float', 'required': False, },
    {'db_name': 'i_d', 'showcase_name': 'Max Drain Current', 'shows_as': 'engineering', 'input_type': 'float', 'required': False, },
    {'db_name': 'i_d_pulse', 'showcase_name': 'Max Drain Peak Current', 'shows_as': 'engineering', 'input_type': 'float', 'required': False, },
]
eedata_mosfet_display_order = eedata_generic_items_preitems+['mosfet_type', 'vdss', 'vgss', 'vgs_th', 'i_d', 'i_d_pulse']+eedata_generic_items_postitems

eedata_bjt_spec = eedata_generic_spec + [
    {'db_name': 'bjt_type', 'showcase_name': 'Type', 'shows_as': 'normal', 'input_type': 'str', 'required': True, },
    {'db_name': 'vcbo', 'showcase_name': 'Max Collector-Base Voltage', 'shows_as': 'engineering', 'input_type': 'float', 'required': False, },
    {'db_name': 'vceo', 'showcase_name': 'Max Collector-Emitter Voltage', 'shows_as': 'engineering', 'input_type': 'float', 'required': False, },
    {'db_name': 'vebo', 'showcase_name': 'Max Emitter-Base Voltage', 'shows_as': 'engineering', 'input_type': 'float', 'required': False, },
    {'db_name': 'i_c', 'showcase_name': 'Max Cont. Collector Current', 'shows_as': 'engineering', 'input_type': 'float', 'required': False, },
    {'db_name': 'i_c_peak', 'showcase_name': 'Max Peak Collector Current', 'shows_as': 'engineering', 'input_type': 'float', 'required': False, },
]
eedata_bjt_display_order = eedata_generic_items_preitems+['bjt_type', 'vcbo', 'vceo', 'vebo', 'i_c', 'i_c_peak']+eedata_generic_items_postitems

eedata_connector_spec = eedata_generic_spec + [
    {'db_name': 'conn_type', 'showcase_name': 'Type', 'shows_as': 'normal', 'input_type': 'str', 'required': True, },
]
eedata_connector_display_order = eedata_generic_items_preitems+['conn_type']+eedata_generic_items_postitems

eedata_led_spec = eedata_generic_spec + [
    {'db_name': 'led_type', 'showcase_name': 'LED Type', 'shows_as': 'normal', 'input_type': 'str', 'required': True, },
    {'db_name': 'vf', 'showcase_name': 'LED forward voltage', 'shows_as': 'engineering', 'input_type': 'float', 'required': False, },
    {'db_name': 'max_i', 'showcase_name': 'Max Current', 'shows_as': 'engineering', 'input_type': 'float', 'required': False, },
]
eedata_led_display_order = eedata_generic_items_preitems+['led_type', 'vf', 'max_i']+eedata_generic_items_postitems

eedata_fuse_spec = eedata_generic_spec + [
    {'db_name': 'fuse_type', 'showcase_name': 'Fuse Type', 'shows_as': 'normal', 'input_type': 'str', 'required': True, },
    {'db_name': 'max_v', 'showcase_name': 'Fuse Max Voltage', 'shows_as': 'engineering', 'input_type': 'float', 'required': False, },
    {'db_name': 'max_i', 'showcase_name': 'Max Current', 'shows_as': 'engineering', 'input_type': 'float', 'required': False, },
    {'db_name': 'trip_i', 'showcase_name': 'Trip Current', 'shows_as': 'engineering', 'input_type': 'float', 'required': False, },
    {'db_name': 'hold_i', 'showcase_name': 'Hold Current', 'shows_as': 'engineering', 'input_type': 'float', 'required': False, },
]
eedata_fuse_display_order = eedata_generic_items_preitems+['fuse_type', 'max_v', 'trip_i', 'hold_i', 'max_i']+eedata_generic_items_postitems

eedata_button_spec = eedata_generic_spec + [
    {'db_name': 'bt_type', 'showcase_name': 'Button Type', 'shows_as': 'normal', 'input_type': 'str', 'required': True},
    {'db_name': 'circuit_t', 'showcase_name': 'Button Circuit', 'shows_as': 'normal', 'input_type': 'str', 'required': False},
    {'db_name': 'max_v', 'showcase_name': 'Voltage Rating', 'shows_as': 'engineering', 'input_type': 'float', 'required': False, },
    {'db_name': 'max_i', 'showcase_name': 'Current Rating', 'shows_as': 'engineering', 'input_type': 'float', 'required': False, },
]
eedata_button_display_order = eedata_generic_items_preitems+['bt_type', 'circuit_t', 'max_v', 'max_i']+eedata_generic_items_postitems

eedata_misc_spec = eedata_generic_spec
eedata_misc_display_order = eedata_generic_items_preitems+eedata_generic_items_postitems

eedata_pcb_spec = [
    {'db_name': 'stock', 'showcase_name': 'Stock', 'shows_as': 'normal', 'input_type': 'int', 'required': True, },
    {'db_name': 'rev', 'showcase_name': 'Revision', 'shows_as': 'normal', 'input_type': 'str', 'required': True, },
    {'db_name': 'comments', 'showcase_name': 'Comments', 'shows_as': 'normal', 'input_type': 'str', 'required': False, },
    {'db_name': 'storage', 'showcase_name': 'Storage Location', 'shows_as': 'normal', 'input_type': 'str', 'required': False, },
    {'db_name': 'board_name', 'showcase_name': 'Board Name', 'shows_as': 'normal', 'input_type': 'str', 'required': True},
    {'db_name': 'parts', 'showcase_name': 'Parts', 'shows_as': 'normal', 'input_type': 'parts_json', 'required': True},
]
eedata_pcb_display_order = ['stock', 'board_name', 'rev', 'parts', 'storage', 'comments']


class Resistor(GenericItem):
    __tablename__ = 'resistance'

    resistance = Column(Float, nullable=False)
    tolerance = Column(Float)
    power = Column(Float)


class Capacitor(GenericItem):
    __tablename__ = 'capacitor'

    capacitance = Column(Float, nullable=False)
    tolerance = Column(Float)
    max_voltage = Column(Float)
    temp_coeff = Column(String(default_string_len))
    cap_type = Column(String(default_string_len))


class Inductor(GenericItem):
    __tablename__ = 'inductor'

    inductance = Column(Float, nullable=False)
    tolerance = Column(Float)
    max_current = Column(Float)


class Diode(GenericItem):
    __tablename__ = 'diode'

    diode_type = Column(String(default_string_len), nullable=False)
    max_current = Column(Float)
    average_current = Column(Float)
    max_rv = Column(Float)


class IC(GenericItem):
    __tablename__ = 'ic'

    ic_type = Column(String(default_string_len), nullable=False)


class Crystal(GenericItem):
    __tablename__ = 'crystal'

    frequency = Column(Float, nullable=False)
    load_c = Column(Float)
    esr = Column(Float)
    stability_ppm = Column(Float)


class MOSFET(GenericItem):
    __tablename__ = 'mosfet'

    mosfet_type = Column(String(default_string_len), nullable=False)
    vdss = Column(Float)
    vgss = Column(Float)
    vgs_th = Column(Float)
    i_d = Column(Float)
    i_d_pulse = Column(Float)


class BJT(GenericItem):
    __tablename__ = 'bjt'

    bjt_type = Column(String(default_string_len), nullable=False)
    vcbo = Column(Float)
    vceo = Column(Float)
    vebo = Column(Float)
    i_c = Column(Float)
    i_c_peak = Column(Float)


class LED(GenericItem):
    __tablename__ = 'led'

    led_type = Column(String(default_string_len), nullable=False)
    vf = Column(Float)
    max_i = Column(Float)


class Fuse(GenericItem):
    __tablename__ = 'fuse'

    fuse_type = Column(String(default_string_len), nullable=False)
    max_v = Column(Float)
    max_i = Column(Float)
    trip_i = Column(Float)
    hold_i = Column(Float)


class Connector(GenericItem):
    __tablename__ = 'connector'

    conn_type = Column(String(default_string_len), nullable=False)


class Button(GenericItem):
    __tablename__ = 'button'

    bt_type = Column(String(default_string_len), nullable=False)
    circuit_t = Column(String(default_string_len))
    max_v = Column(Float)
    max_i = Column(Float)


class MiscComp(GenericItem):
    __tablename__ = 'misc_c'


class PCB(_AlchemyDeclarativeBase):
    __tablename__ = 'pcb'

    id = Column(Integer, primary_key=True)
    stock = Column(Integer, nullable=False)
    comments = Column(String(default_string_len))
    storage = Column(String(default_string_len))
    board_name = Column(String(default_string_len), nullable=False)
    rev = Column(String(default_string_len), nullable=False)
    parts = Column(JSON, nullable=False)


"""
    While not part of the spec, but these are handly for autofills
"""
autofill_helpers_list = {
    'ic_manufacturers': ["MICROCHIP", "TI", "ANALOG DEVICES", "ON-SEMI", "STMICROELECTRONICS",
                         "CYPRESS SEMI", "INFINEON"],
    'ic_types': ["Microcontroller", "Boost Converter", "Buck Converter", "FPGA", "Battery Charger", "Battery Management",
                 "LED Driver", "Multiplexer"],
    'capacitor_types': ['Electrolytic', 'Ceramic', 'Tantalum', 'Paper', 'Film'],
    'diode_type': ['Regular', 'Zener', 'Schottky', 'TSV'],
    'passive_manufacturers': ['STACKPOLE', 'MURATA ELECTRONICS', 'SAMSUNG ELECTRO-MECHANICS', 'TAIYO YUDEN', 'TDK'],
    'passive_packages': ['0201', '0603', '0805', '1206'],
    'ic_packages': ['SOT23', 'SOT23-5', 'SOT23-6',
                    'DIP-4', 'DIP-8', 'DIP-14', 'DIP-16', 'DIP-18', 'DIP-28',
                    'SOIC-8', 'SIOC-14', 'SOIC-16', 'SOIC-18'],
    'mosfet_types': ['N-Channel', 'P-Channel'],
    'bjt_types': ['NPN', 'PNP'],
    'fuse_types': ['PTC', 'Fast Blow', 'Slow Blow'],
    'led_types': ['Red', 'Green', 'Blue', 'RGB', 'Addressable']
}

"""
    If this is ran it itself, do a test where it checks if the display order for each spec has all keys
"""
if __name__ == '__main__':
    print("Running Test")
    spec_and_disp_arr = [['resistor', eedata_resistors_spec, eedata_resistor_display_order, Resistor],
                         ['capacitor', eedata_capacitor_spec, eedata_capacitor_display_order, Capacitor],
                         ['ic', eedata_ic_spec, eedata_ic_display_order, IC],
                         ['inductor', eedata_inductor_spec, eedata_inductor_display_order, Inductor],
                         ['diode', eedata_diode_spec, eedata_diode_display_order, Diode],
                         ['pcb', eedata_pcb_spec, eedata_pcb_display_order, PCB],
                         ['crystal', eedata_crystal_spec, eedata_crystal_display_order, Crystal],
                         ['mosfet', eedata_mosfet_spec, eedata_mosfet_display_order, MOSFET],
                         ['bjt', eedata_bjt_spec, eedata_bjt_display_order, BJT],
                         ['connectors', eedata_connector_spec, eedata_connector_display_order, Connector],
                         ['led', eedata_led_spec, eedata_led_display_order, LED],
                         ['fuse', eedata_fuse_spec, eedata_fuse_display_order, Fuse],
                         ['button', eedata_button_spec, eedata_button_display_order, Button],
                         ['misc', eedata_misc_spec, eedata_misc_display_order, MiscComp]]
    for spec in spec_and_disp_arr:
        for i in spec[1]:
            if i['db_name'] not in spec[2]:
                raise AssertionError("Spec '{}' not in {}".format(i['db_name'], spec[0]))

            if not hasattr(spec[3], i['db_name']):
                raise AssertionError("Extra name in spec dict for {} = {}".format(spec[0], i['db_name']))
    print("Done with test")
