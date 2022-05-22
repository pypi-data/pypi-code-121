LISTBOX_MIMETYPE = "application/x-item"


OP_NODE_INPUT = 10
OP_NODE_INPUT_P_h=20
OP_NODE_OUTPUT =30
OP_NODE_MIX = 40
OP_NODE_ADD = 50
OP_NODE_SUB = 60
OP_NODE_MUL = 70
OP_NODE_DIV = 80
OP_NODE_COMP = 90
OP_NODE_COMP_M = 100

OP_NODE_EVAP = 110
OP_NODE_DESU = 120
OP_NODE_COND = 130
OP_NODE_DET = 140
OP_NODE_TURB = 150
OP_NODE_HEXT = 160

OP_NODE_AIR_INPUT = 170
OP_NODE_RANDOM_METEO=180
OP_NODE_AIR_OUTPUT = 190
OP_NODE_HEATING_COIL = 200
OP_NODE_COOLING_COIL = 210
OP_NODE_HMD = 220
OP_NODE_AIRMIX = 230
OP_NODE_COOLING_COIL_SENSIBLE = 240
OP_NODE_COOLING_COIL_EXPERT = 250


CALC_NODES = {
}


class ConfException(Exception): pass
class InvalidNodeRegistration(ConfException): pass
class OpCodeNotRegistered(ConfException): pass


def register_node_now(op_code, class_reference):
    if op_code in CALC_NODES:
        raise InvalidNodeRegistration("Duplicate node registration of '%s'. There is already %s" %(
            op_code, CALC_NODES[op_code]
        ))
    CALC_NODES[op_code] = class_reference


def register_node(op_code):
    def decorator(original_class):
        register_node_now(op_code, original_class)
        return original_class
    return decorator

def get_class_from_opcode(op_code):
    if op_code not in CALC_NODES: raise OpCodeNotRegistered("OpCode '%d' is not registered" % op_code)
    return CALC_NODES[op_code]



# import all nodes and register them
from PyqtSimulator.nodes import *